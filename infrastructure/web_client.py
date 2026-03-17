"""
Cliente web profesional para obtener datos de internet en tiempo real.
Este módulo se encarga de hacer todas las consultas HTTP a APIs y sitios web.
"""

import os
import re
import json
import requests
from typing import Optional, Dict, List, Any
from pathlib import Path
from urllib.parse import quote_plus, urlencode
from datetime import datetime

from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


class WebClient:
    """
    Cliente web profesional para obtener datos en tiempo real.
    Maneja todas las conexiones a internet.
    """
    
    def __init__(self):
        # Cargar API keys desde .env
        self.serpapi_key = os.getenv("SERPAPI_KEY", "")
        self.openai_key = os.getenv("API_KEY", "")
        
        # Headers para evitar bloqueos
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        }
        
        print(f"[WebClient] Inicializado con SerpAPI: {bool(self.serpapi_key)}")
    
    def buscar_en_web(self, consulta: str, num_resultados: int = 10) -> List[Dict[str, str]]:
        """
        Realiza una búsqueda web general.
        
        Args:
            consulta: Término de búsqueda
            num_resultados: Número de resultados a obtener
        
        Returns:
            Lista de resultados con título, descripción, URL y fuente
        """
        print(f"[WebClient] Buscando: {consulta}")
        
        if self.serpapi_key:
            return self._buscar_con_serpapi(consulta, num_resultados)
        else:
            return self._buscar_gratis(consulta, num_resultados)
    
    def _buscar_con_serpapi(self, consulta: str, num_resultados: int) -> List[Dict[str, str]]:
        """Busca usando SerpAPI."""
        url = "https://serpapi.com/search"
        params = {
            "q": consulta,
            "api_key": self.serpapi_key,
            "num": num_resultados,
            "gl": "mx",
            "hl": "es"
        }
        
        try:
            print(f"[WebClient] URL: https://serpapi.com/search?{urlencode(params)}")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                resultados = []
                
                for item in data.get("organic_results", [])[:num_resultados]:
                    resultados.append({
                        "titulo": item.get("title", ""),
                        "descripcion": item.get("snippet", ""),
                        "url": item.get("link", ""),
                        "fuente": self._extraer_fuente(item.get("link", ""))
                    })
                
                print(f"[WebClient] Encontrados {len(resultados)} resultados")
                return resultados
            else:
                print(f"[WebClient] Error SerpAPI: {response.status_code}")
        except Exception as e:
            print(f"[WebClient] Excepción: {e}")
        
        return []
    
    def _buscar_gratis(self, consulta: str, num_resultados: int) -> List[Dict[str, str]]:
        """Búsqueda gratuita como fallback."""
        # Usar DuckDuckGo como fallback
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(consulta)}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                resultados = []
                
                for item in soup.select('.result')[:num_resultados]:
                    link = item.select_one('a')
                    snippet = item.select_one('.result__snippet')
                    
                    if link:
                        resultados.append({
                            "titulo": link.get_text(strip=True),
                            "descripcion": snippet.get_text(strip=True) if snippet else "",
                            "url": link.get('href', ''),
                            "fuente": self._extraer_fuente(link.get('href', ''))
                        })
                
                return resultados
        except Exception as e:
            print(f"[WebClient] Fallback falló: {e}")
        
        return []
    
    def _extraer_fuente(self, url: str) -> str:
        """Extrae el nombre del sitio de una URL."""
        if not url:
            return "Desconocido"
        
        fuentes = {
            "toyota": "Toyota México",
            "honda": "Honda México",
            "nissan": "Nissan México",
            "ford": "Ford México",
            "chevrolet": "Chevrolet México",
            "kia": "Kia México",
            "hyundai": "Hyundai México",
            "mazda": "Mazda México",
            "volkswagen": "VW México",
            "bmw": "BMW México",
            "mercedes": "Mercedes-Benz México",
            "audi": "Audi México",
            "lexus": "Lexus México",
            "mercadolibre": "MercadoLibre",
            "autocosmos": "Autocosmos",
            "kavak": "Kavak",
            "carrosycamionetas": "Carros y Camionetas",
            "motoryvalta": "MotoryValta",
        }
        
        url_lower = url.lower()
        for patron, nombre in fuentes.items():
            if patron in url_lower:
                return nombre
        
        if "/" in url:
            dominio = url.split("/")[2]
            return dominio.replace("www.", "").split(".")[0].title()
        
        return "Desconocido"
    
    def extraer_precio(self, texto: str) -> Optional[Dict[str, Any]]:
        """
        Extrae precios de un texto.
        
        Args:
            texto: Texto que puede contener precios
        
        Returns:
            Dict con precio, moneda y formato
        """
        # Patrones para MXN
        patrones = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*MXN',
            r'(\d{1,3}(?:,\d{3})*)\s*MXN',
            r'\$\s*(\d{1,3}(?:,\d{3})*)',
            r'desde\s*\$\s*(\d{1,3}(?:,\d{3})*)',
            r'precio\s*\$\s*(\d{1,3}(?:,\d{3})*)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:pesos?|mxn)',
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                precio_str = match.group(1).replace(",", "")
                try:
                    precio = float(precio_str)
                    if 50000 < precio < 10000000:  # Rango razonable
                        return {
                            "precio": precio,
                            "formato": f"${precio:,.0f} MXN",
                            "moneda": "MXN"
                        }
                except ValueError:
                    continue
        
        return None
    
    def buscar_precios_auto(
        self, 
        marca: str, 
        modelo: str, 
        anio: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Busca precios de un auto específico.
        
        Args:
            marca: Marca del auto
            modelo: Modelo del auto
            anio: Año (opcional)
        
        Returns:
            Dict con precios nuevos, usados y especificaciones
        """
        year = anio or "2024"
        
        print(f"[WebClient] Buscando precios para: {marca} {modelo} {year}")
        
        resultados = {
            "busqueda": {
                "marca": marca,
                "modelo": modelo,
                "anio": year,
                "timestamp": datetime.now().isoformat(),
                "url_usada": "https://serpapi.com/search"
            },
            "precios_nuevos": [],
            "precios_usados": [],
            "especificaciones": {},
            "fuentes": []
        }
        
        # Consulta 1: Precios nuevos
        consulta_nueva = f"{marca} {modelo} {year} precio Mexico nuevo"
        resultados_nuevos = self.buscar_en_web(consulta_nueva, 10)
        
        for r in resultados_nuevos:
            precio = self.extraer_precio(r.get("descripcion", "") + " " + r.get("titulo", ""))
            if precio:
                resultados["precios_nuevos"].append({
                    "precio": precio["formato"],
                    "fuente": r.get("fuente", ""),
                    "url": r.get("url", ""),
                    "version": self._extraer_version(r.get("titulo", "") + " " + r.get("descripcion", ""))
                })
        
        # Consulta 2: Precios usados
        consulta_usada = f"{marca} {modelo} {year} usado precio Mexico"
        resultados_usados = self.buscar_en_web(consulta_usada, 10)
        
        for r in resultados_usados:
            precio = self.extraer_precio(r.get("descripcion", "") + " " + r.get("titulo", ""))
            if precio:
                resultados["precios_usados"].append({
                    "precio": precio["formato"],
                    "fuente": r.get("fuente", ""),
                    "url": r.get("url", "")
                })
        
        # Consulta 3: Especificaciones
        consulta_specs = f"{marca} {modelo} {year} especificaciones motor hp"
        resultados_specs = self.buscar_en_web(consulta_specs, 5)
        
        specs = {"motor": "", "potencia": "", "consumo": ""}
        
        for r in resultados_specs:
            texto = (r.get("descripcion", "") + " " + r.get("titulo", "")).lower()
            
            # Motor
            match = re.search(r'(\d+\.?\d*)\s*(?:L|ltros?)', texto)
            if match and not specs["motor"]:
                specs["motor"] = match.group(1) + "L"
            
            # HP
            match = re.search(r'(\d+)\s*(?:hp|caballos?|cv)', texto)
            if match and not specs["potencia"]:
                specs["potencia"] = match.group(1) + " hp"
            
            # Consumo
            match = re.search(r'(\d+\.?\d*)\s*(?:km/?l|mpg)', texto)
            if match and not specs["consumo"]:
                specs["consumo"] = match.group(1) + " km/L"
        
        resultados["especificaciones"] = specs
        
        # Recopilar fuentes únicas
        fuentes = set()
        for r in resultados_nuevos + resultados_usados:
            if r.get("fuente"):
                fuentes.add(r.get("fuente"))
        resultados["fuentes"] = list(fuentes)
        
        return resultados
    
    def _extraer_version(self, texto: str) -> str:
        """Extrae la versión del auto."""
        versiones = ["base", "le", "xle", "se", "sport", "touring", "limited", "premium", "gt", "sr"]
        texto_lower = texto.lower()
        
        for v in versiones:
            if v in texto_lower:
                return v.upper()
        
        return "General"
    
    def comparar_autos(self, auto1: str, auto2: str) -> Dict[str, Any]:
        """Compara dos autos."""
        consulta = f"comparar {auto1} vs {auto2} Mexico"
        resultados = self.buscar_en_web(consulta, 10)
        
        return {
            "auto1": auto1,
            "auto2": auto2,
            "resultados": resultados,
            "url_usada": "https://serpapi.com/search"
        }


# Instancia global
_web_client: Optional[WebClient] = None


def get_web_client() -> WebClient:
    """Obtiene el cliente web global."""
    global _web_client
    # Siempre crear nueva instancia para obtener API key actualizada
    _web_client = WebClient()
    return _web_client
