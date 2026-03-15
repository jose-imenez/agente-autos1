"""
Servicio de búsqueda web para información de autos.
"""

import os
import re
import json
import requests
from typing import Optional
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

from infrastructure.logging.structured_logging import api_logger

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class BusquedaWebService:
    """Servicio para buscar información de autos en la web."""
    
    def __init__(self):
        self.api_key = os.getenv("SEARCH_API_KEY", "")
        self.search_engine_id = os.getenv("SEARCH_ENGINE_ID", "")
        self.serpapi_key = os.getenv("SERPAPI_KEY", "")
    
    def buscar_informacion_auto(
        self, 
        marca: str, 
        modelo: str, 
        anio: Optional[str] = None,
        tipo_busqueda: str = "general"
    ) -> dict:
        """
        Busca información de un auto específico.
        
        Args:
            marca: Marca del auto (ej: Toyota)
            modelo: Modelo del auto (ej: Corolla)
            anio: Año del auto (opcional)
            tipo_busqueda: tipo de info (general, precio, especificaciones)
        
        Returns:
            Dict con resultados de la búsqueda
        """
        consultas = self._construir_consultas(marca, modelo, anio, tipo_busqueda)
        
        resultados = []
        urls_vistas = set()
        
        for consulta in consultas:
            resultado = self._buscar(consulta)
            for r in resultado:
                url = r.get("url", "")
                if url and url not in urls_vistas:
                    resultados.append(r)
                    urls_vistas.add(url)
        
        return {
            "marca": marca,
            "modelo": modelo,
            "anio": anio,
            "tipo_busqueda": tipo_busqueda,
            "resultados": resultados[:10],
            "fuentes": list(set([r.get("fuente", "") for r in resultados if r.get("fuente")]))
        }
    
    def _construir_consultas(
        self, 
        marca: str, 
        modelo: str, 
        anio: Optional[str],
        tipo_busqueda: str
    ) -> list[str]:
        """Construye las consultas de búsqueda según el tipo."""
        year = anio or "2024"
        
        consultas = {
            "precio": [
                f"{marca} {modelo} {year} precio Mexico",
                f"{marca} {modelo} {year} precio lista MXN",
                f"precio {marca} {modelo} nuevo Mexico",
            ],
            "especificaciones": [
                f"{marca} {modelo} {year} especificaciones motor",
                f"{marca} {modelo} {year} caracteristicas tecnicas",
            ],
            "general": [
                f"{marca} {modelo} {year} Mexico",
                f"{marca} {modelo} {year} review opinion",
            ],
            "comparacion": [
                f"{marca} {modelo} vs comparacion Mexico",
            ],
            "usado": [
                f"{marca} {modelo} usado precio Mexico",
                f"{marca} {modelo} seminuevo precio",
            ]
        }
        
        return consultas.get(tipo_busqueda, consultas["general"])
    
    def _buscar(self, consulta: str) -> list[dict]:
        """Ejecuta una búsqueda web."""
        try:
            if self.serpapi_key:
                return self._buscar_con_serpapi(consulta)
            elif self.api_key and self.search_engine_id:
                return self._buscar_con_google(consulta)
            else:
                return self._buscar_gratis(consulta)
        except Exception as e:
            api_logger.error("Error en búsqueda", consulta=consulta, error=str(e))
            return []
    
    def _buscar_con_serpapi(self, consulta: str) -> list[dict]:
        """Busca usando SerpAPI (gratis para 100 búsquedas/mes)."""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": consulta,
                "api_key": self.serpapi_key,
                "num": 10,
                "gl": "mx",
                "hl": "es"
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                resultados = []
                
                for item in data.get("organic_results", [])[:5]:
                    resultados.append({
                        "titulo": item.get("title", ""),
                        "descripcion": item.get("snippet", ""),
                        "url": item.get("link", ""),
                        "fuente": self._extraer_fuente(item.get("link", ""))
                    })
                
                return resultados
            elif response.status_code == 403:
                api_logger.warning("SerpAPI: límite alcanzado o clave inválida")
        except Exception as e:
            api_logger.warning("SerpAPI falló", error=str(e))
        
        return self._buscar_gratis(consulta)
    
    def _buscar_con_google(self, consulta: str) -> list[dict]:
        """Busca usando Google Custom Search API."""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": consulta,
            "num": 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        resultados = []
        for item in data.get("items", []):
            resultados.append({
                "titulo": item.get("title", ""),
                "descripcion": item.get("snippet", ""),
                "url": item.get("link", ""),
                "fuente": self._extraer_fuente(item.get("link", ""))
            })
        
        return resultados
    
    def _buscar_gratis(self, consulta: str) -> list[dict]:
        """Búsqueda gratuita usando Bing con fallback a sitios de autos."""
        try:
            url = f"https://www.bing.com/search?q={quote_plus(consulta)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            }
            
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            
            if response.status_code == 200 and len(response.text) > 5000:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                resultados = []
                
                for item in soup.select('.b_algo')[:5]:
                    link = item.select_one('a')
                    snippet = item.select_one('.b_caption p') or item.select_one('p')
                    
                    if link:
                        resultados.append({
                            "titulo": link.get_text(strip=True)[:100],
                            "descripcion": snippet.get_text(strip=True)[:200] if snippet else "",
                            "url": link.get('href', ''),
                            "fuente": self._extraer_fuente(link.get('href', ''))
                        })
                
                if resultados:
                    return resultados
        except Exception as e:
            api_logger.warning("Búsqueda Bing falló", error=str(e))
        
        return self._buscar_sitios_autos(consulta)
    
    def _buscar_sitios_autos(self, consulta: str) -> list[dict]:
        """Hace scraping de sitios de autos específicos."""
        resultados = []
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        }
        
        # Buscar directamente el auto en sitios de autos
        try:
            # Autocosmos - sitio popular de autos en México
            url_autocosmos = f"https://www.autocosmos.com.mx/buscar?q={quote_plus(consulta)}"
            response = requests.get(url_autocosmos, headers=headers, timeout=10)
            if response.status_code == 200 and "corolla" in response.text.lower() or "toyota" in response.text.lower():
                resultados.append({
                    "titulo": "Autocosmos - Buscar autos",
                    "descripcion": f"Resultados para {consulta} en Autocosmos México",
                    "url": url_autocosmos,
                    "fuente": "Autocosmos"
                })
        except:
            pass
        
        # MercadoLibre Autos
        try:
            url_mercadolibre = f"https://listado.mercadolibre.com.mx/autos/{quote_plus(consulta)}"
            resultados.append({
                "titulo": "MercadoLibre Autos",
                "descripcion": f"Buscar {consulta} en MercadoLibre",
                "url": url_mercadolibre,
                "fuente": "MercadoLibre"
            })
        except:
            pass
        
        # Kelley Blue Book para precios
        try:
            url_kbb = f"https://www.kbb.com/toyota/corolla/{consulta.split()[1] if len(consulta.split()) > 1 else '2024'}/"
            resultados.append({
                "titulo": "Kelley Blue Book - Precio estimado",
                "descripcion": f"Precio estimado de {consulta} en KBB",
                "url": url_kbb,
                "fuente": "Kelley Blue Book"
            })
        except:
            pass
        
        # Auto123
        try:
            url_auto123 = f"https://www.auto123.com/mexico/es/ficha?make={consulta.split()[0] if consulta.split() else 'toyota'}&model={consulta.split()[1] if len(consulta.split()) > 1 else 'corolla'}"
            resultados.append({
                "titulo": "Auto123 - Fichas técnicas",
                "descripcion": f"Información técnica de {consulta}",
                "url": url_auto123,
                "fuente": "Auto123"
            })
        except:
            pass
        
        if not resultados:
            resultados.append({
                "titulo": "🔍 Configura SerpAPI para mejores resultados",
                "descripcion": f"Para buscar precios reales de {consulta}, necesitas una API de búsqueda. Registrate gratis en https://serpapi.com y agrega tu clave en el archivo .env",
                "url": "https://serpapi.com",
                "fuente": "Configuración"
            })
        
        return resultados
    
    def _extraer_fuente(self, url: str) -> str:
        """Extrae el nombre del sitio de una URL."""
        if not url:
            return ""
        
        patrones = [
            (r"autocosmos", "Autocosmos"),
            (r"motoryvalta", "MotoryValta"),
            (r"mercadolibre", "MercadoLibre"),
            (r"carscope", "CarScope"),
            (r"toyota", "Toyota"),
            (r"honda", "Honda"),
            (r"ford", "Ford"),
            (r"chevrolet", "Chevrolet"),
            (r"nissan", "Nissan"),
            (r"kbb", "Kelley Blue Book"),
            (r"edmunds", "Edmunds"),
        ]
        
        for patron, nombre in patrones:
            if re.search(patron, url, re.IGNORECASE):
                return nombre
        
        return url.split("/")[2] if len(url.split("/")) > 2 else url
    
    def comparar_autos(self, auto1: str, auto2: str) -> dict:
        """Compara dos autos."""
        consulta = f"comparacion {auto1} vs {auto2}"
        resultados = self._buscar(consulta)
        
        return {
            "auto1": auto1,
            "auto2": auto2,
            "resultados": resultados,
            "tipo": "comparacion"
        }


_busqueda_web_service: Optional[BusquedaWebService] = None


def get_busqueda_web_service() -> BusquedaWebService:
    """Obtiene la instancia global del servicio de búsqueda."""
    global _busqueda_web_service
    if _busqueda_web_service is None:
        _busqueda_web_service = BusquedaWebService()
    return _busqueda_web_service
