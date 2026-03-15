"""
Servicio de carga y gestión de Skills.

Carga automáticamente las skills desde la carpeta 'skills' y permite
ejecutarlas cuando sea necesario.
"""

import os
import json
import re
from typing import Optional, Any
from pathlib import Path
from dataclasses import dataclass, field

from infrastructure.logging.structured_logging import api_logger


@dataclass
class Skill:
    """Representa una skill cargada."""
    nombre: str
    descripcion: str
    contenido: str
    ruta: Path
    proveedor: str = ""
    comandos: list = field(default_factory=list)
    metadatos: dict = field(default_factory=dict)


class SkillsLoader:
    """
    Cargador de skills desde la carpeta skills.
    
    Busca archivos SKILL.md en subdirectorios y los carga como skills.
    """
    
    def __init__(self, skills_path: Optional[str | Path] = None):
        if skills_path is None:
            # Por defecto, buscar en la raíz del proyecto
            base_path = Path(__file__).parent.parent.parent
            self.skills_path = base_path / "skills"
        else:
            self.skills_path = Path(skills_path)
        
        self.skills: dict[str, Skill] = {}
        self._cargar_skills()
    
    def _cargar_skills(self) -> None:
        """Carga todas las skills desde la carpeta skills."""
        if not self.skills_path.exists():
            api_logger.warning(
                "Carpeta de skills no encontrada",
                path=str(self.skills_path)
            )
            return
        
        api_logger.info("Cargando skills desde", path=str(self.skills_path))
        
        # Buscar todos los archivos SKILL.md
        for skill_file in self.skills_path.rglob("SKILL.md"):
            try:
                skill = self._cargar_skill(skill_file)
                if skill:
                    self.skills[skill.nombre] = skill
                    api_logger.info(f"Skill cargada: {skill.nombre}")
            except Exception as e:
                api_logger.error(
                    f"Error al cargar skill",
                    path=str(skill_file),
                    error=str(e)
                )
        
        api_logger.info(
            "Skills cargadas",
            total=len(self.skills)
        )
    
    def _cargar_skill(self, skill_file: Path) -> Optional[Skill]:
        """Carga una skill desde un archivo SKILL.md."""
        try:
            contenido = skill_file.read_text(encoding="utf-8")
            
            # Extraer metadatos del YAML frontmatter
            nombre = ""
            descripcion = ""
            
            if contenido.startswith("---"):
                # Encontrar el fin del frontmatter
                fin_frontmatter = contenido.find("---", 3)
                if fin_frontmatter > 0:
                    frontmatter = contenido[3:fin_frontmatter].strip()
                    
                    # Extraer nombre
                    match = re.search(r"name:\s*(.+)", frontmatter)
                    if match:
                        nombre = match.group(1).strip()
                    
                    # Extraer descripción
                    match = re.search(r'description:\s*["\'](.+)["\']', frontmatter)
                    if match:
                        descripcion = match.group(1).strip()
            
            if not nombre:
                # Usar el nombre de la carpeta como nombre
                nombre = skill_file.parent.name
            
            # Limpiar el contenido (quitar frontmatter para el contenido)
            if contenido.startswith("---"):
                fin_frontmatter = contenido.find("---", 3)
                if fin_frontmatter > 0:
                    contenido = contenido[fin_frontmatter + 3:].strip()
            
            return Skill(
                nombre=nombre,
                descripcion=descripcion,
                contenido=contenido,
                ruta=skill_file,
                proveedor=skill_file.parent.parent.name
            )
            
        except Exception as e:
            api_logger.error(f"Error al parsear skill: {skill_file}", error=str(e))
            return None
    
    def obtener_skill(self, nombre: str) -> Optional[Skill]:
        """Obtiene una skill por nombre."""
        return self.skills.get(nombre)
    
    def buscar_skills(self, query: str) -> list[Skill]:
        """Busca skills que coincidan con la query."""
        query = query.lower()
        resultados = []
        
        for skill in self.skills.values():
            if (query in skill.nombre.lower() or 
                query in skill.descripcion.lower()):
                resultados.append(skill)
        
        return resultados
    
    def listar_skills(self) -> list[dict]:
        """Lista todas las skills disponibles."""
        return [
            {
                "nombre": skill.nombre,
                "descripcion": skill.descripcion,
                "proveedor": skill.proveedor,
                "ruta": str(skill.ruta)
            }
            for skill in self.skills.values()
        ]
    
    def _es_query_coches(self, query: str) -> bool:
        """
        Detecta si la query es sobre coches.
        
        Returns:
            True si es sobre coches, False si no
        """
        query_lower = query.lower()
        
        # Palabras que indican que es sobre COCHES
        palabras_coche = [
            "coche", "carro", "auto", "vehículo", "vehiculo", "automóvil", "automovil",
            "toyota", "honda", "ford", "bmw", "mercedes", "audi", "chevrolet", "nissan",
            "mazda", "volkswagen", "kia", "hyundai", "porsche", "tesla", "jeep",
            "sedán", "suv", "camioneta", "pickup", "deportivo", "hatchback",
            "precio", "costar", "valor", "modelo", "marca", "año", "motor",
            "hp", "caballos", "consumo", "combustible", "transmisión", "transmision",
            "comprar", "vender", "usado", "nuevo", "km", "kilometraje",
            "versiones", "specs", "especificaciones", "garantía", "garantia"
        ]
        
        return any(palabra in query_lower for palabra in palabras_coche)
    
    def obtener_skill_relevante(self, query: str) -> tuple[Optional[Skill], str]:
        """
        Obtiene la skill más relevante según la query.
        
        Args:
            query: Query del usuario
        
        Returns:
            Tupla de (skill, tipo_ruta)
            - tipo_ruta puede ser: "coche", "no_coche", "desconocido"
        """
        query_lower = query.lower()
        
        # Primero: detectar si es sobre coches
        if not self._es_query_coches(query):
            # No es sobre coches - usar skill de no disponible
            skill = self.obtener_skill("no_disponible")
            api_logger.info("Query no es sobre coches - usando no_disponible")
            return skill, "no_coche"
        
        # Es sobre coches - determinar qué skill usar
        api_logger.info("Query es sobre coches - determinando skill específica")
        
        # Mapeo de palabras clave a skills de coches
        mapeo_palabras = {
            "buscar_coche": ["busca", "buscar", "dame", "información", "busco", "quiero"],
            "obtener_precios": ["precio", "cuánto", "cuesta", "valor", "costo", "precios"],
            "comparar_coches": ["compara", "comparar", "diferencia", "vs", "versus"],
        }
        
        for skill_name, keywords in mapeo_palabras.items():
            if any(kw in query_lower for kw in keywords):
                skill = self.obtener_skill(skill_name)
                if skill:
                    api_logger.info(f"Skill seleccionada: {skill_name}")
                    return skill, "coche"
        
        # Por defecto, usar buscar_coche
        skill = self.obtener_skill("buscar_coche")
        return skill, "coche"
    
    def ejecutar_skill_auto(self, query: str) -> dict:
        """
        Ejecuta automáticamente la skill correcta según la query.
        Detecta si es sobre coches o no.
        
        Args:
            query: Query del usuario
        
        Returns:
            Resultado con la skill ejecutada
        """
        skill, tipo = self.obtener_skill_relevante(query)
        
        if not skill:
            return {
                "error": "No se encontró skill disponible",
                "query": query
            }
        
        return {
            "skill": skill.nombre,
            "tipo": tipo,
            "descripcion": skill.descripcion,
            "instrucciones": skill.contenido,
            "query": query,
            "ruta": str(skill.ruta)
        }
    
    def ejecutar_skill(
        self, 
        nombre_skill: str, 
        contexto: str,
        **kwargs
    ) -> dict:
        """
        Ejecuta una skill específica con el contexto dado.
        
        Args:
            nombre_skill: Nombre de la skill a ejecutar
            contexto: Contexto/tarea para la skill
        
        Returns:
            Resultado de la ejecución
        """
        skill = self.obtener_skill(nombre_skill)
        
        if not skill:
            return {
                "error": f"Skill '{nombre_skill}' no encontrada",
                "skills_disponibles": [s.nombre for s in self.skills.values()]
            }
        
        api_logger.info(
            "Ejecutando skill",
            skill=nombre_skill,
            contexto=contexto[:100]
        )
        
        # Retornar las instrucciones de la skill
        return {
            "skill": skill.nombre,
            "descripcion": skill.descripcion,
            "instrucciones": skill.contenido[:1000] + "..." if len(skill.contenido) > 1000 else skill.contenido,
            "contexto": contexto,
            "ruta": str(skill.ruta)
        }


# Instancia global del loader
_skills_loader: Optional[SkillsLoader] = None


def get_skills_loader() -> SkillsLoader:
    """Obtiene la instancia global del loader de skills."""
    global _skills_loader
    if _skills_loader is None:
        _skills_loader = SkillsLoader()
    return _skills_loader


def recargar_skills() -> None:
    """Recarga todas las skills."""
    global _skills_loader
    _skills_loader = SkillsLoader()
    api_logger.info("Skills recargadas")
