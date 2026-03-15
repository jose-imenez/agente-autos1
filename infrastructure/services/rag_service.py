"""
Servicio de RAG (Retrieval Augmented Generation) para autos.
Usa embeddings para buscar información relevante.
"""

import os
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from infrastructure.services.base_conocimientos import get_base_conocimientos


class EmbeddingsService:
    """Servicio de embeddings para búsqueda semántica."""
    
    def __init__(self):
        self.model = None
        self.embeddings = None
        self.documentos = None
    
    def _cargar_modelo(self):
        """Carga el modelo de embeddings."""
        if self.model is not None:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except ImportError:
            # Fallback: crear embeddings simples
            self.model = "simple"
    
    def _crear_embedding_simple(self, texto: str) -> np.ndarray:
        """Crea un embedding simple basado en palabras clave."""
        # Crear vector de características simple
        palabras_clave = texto.lower().split()
        vector = np.zeros(100)
        
        # Palabras clave comunes
        keywords = {
            "precio": 0, "costo": 0, "motor": 1, "hp": 1, "kw": 1,
            "sedan": 2, "suv": 3, "pickup": 4, "hatchback": 5,
            "toyota": 10, "honda": 11, "nissan": 12, "ford": 13,
            "chevrolet": 14, "kia": 15, "hyundai": 16, "mazda": 17,
            "volkswagen": 18, "bmw": 19, "mercedes": 20,
            "corolla": 30, "civic": 31, "sentra": 32, "mustang": 33,
            "rav4": 40, "cr-v": 41, "kicks": 42, "sportage": 43,
        }
        
        for palabra in palabras_clave:
            if palabra in keywords:
                vector[keywords[palabra]] = 1
        
        # Normalizar
        return vector / (np.linalg.norm(vector) + 1e-10)
    
    def _crear_embeddings(self, textos: List[str]) -> np.ndarray:
        """Crea embeddings para una lista de textos."""
        self._cargar_modelo()
        
        if self.model == "simple":
            return np.array([self._crear_embedding_simple(t) for t in textos])
        
        return self.model.encode(textos, show_progress_bar=False)
    
    def inicializar(self, documentos: List[Dict[str, Any]]):
        """Inicializa los embeddings con documentos."""
        self.documentos = documentos
        textos = [d.get("contenido", "") for d in documentos]
        
        self._cargar_modelo()
        self.embeddings = self._crear_embeddings(textos)
    
    def buscar(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Busca los documentos más relevantes para la query."""
        if self.embeddings is None or self.documentos is None:
            return []
        
        # Crear embedding de la query
        if self.model == "simple":
            query_embedding = self._crear_embedding_simple(query)
        else:
            query_embedding = self.model.encode([query], show_progress_bar=False)[0]
        
        # Calcular similitud coseno
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding) + 1e-10
        )
        
        # Obtener los top_k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        resultados = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Umbral mínimo
                resultados.append({
                    **self.documentos[idx],
                    "similitud": float(similarities[idx])
                })
        
        return resultados


class RAGService:
    """Servicio de RAG para el agente de autos."""
    
    def __init__(self):
        self.embeddings_service = None
        self._inicializado = False
    
    def _inicializar(self):
        """Inicializa el servicio RAG."""
        if self._inicializado:
            return
        
        base_conocimientos = get_base_conocimientos()
        documentos = base_conocimientos.obtener_todos()
        
        self.embeddings_service = EmbeddingsService()
        self.embeddings_service.inicializar(documentos)
        
        self._inicializado = True
    
    def buscar_informacion(self, query: str, top_k: int = 3) -> str:
        """
        Busca información relevante para la query y la retorna como contexto.
        
        Args:
            query: La pregunta del usuario
            top_k: Número de documentos a retrieve
        
        Returns:
            Contexto formateado para el LLM
        """
        self._inicializar()
        
        resultados = self.embeddings_service.buscar(query, top_k)
        
        if not resultados:
            return ""
        
        contexto = "Información relevante de la base de conocimientos:\n\n"
        
        for i, doc in enumerate(resultados, 1):
            contexto += f"--- Opción {i} ---\n"
            contexto += f"Marca: {doc.get('marca', 'N/A')}\n"
            contexto += f"Modelo: {doc.get('modelo', 'N/A')}\n"
            if doc.get('anio') and doc['anio'] != 'general':
                contexto += f"Año: {doc.get('anio')}\n"
            if doc.get('tipo'):
                contexto += f"Tipo: {doc.get('tipo')}\n"
            contexto += f"Información: {doc.get('contenido', '')}\n"
            contexto += f"Fuente: {doc.get('fuente', 'N/A')}\n\n"
        
        return contexto
    
    def buscar_auto_especifico(self, marca: str, modelo: str) -> Optional[Dict[str, Any]]:
        """Busca un auto específico en la base de conocimientos."""
        self._inicializar()
        
        if not self.embeddings_service or not self.embeddings_service.documentos:
            return None
        
        query = f"{marca} {modelo}"
        resultados = self.embeddings_service.buscar(query, top_k=1)
        
        if resultados and resultados[0].get("similitud", 0) > 0.3:
            return resultados[0]
        
        return None


# Instancia global
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Obtiene el servicio RAG."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
