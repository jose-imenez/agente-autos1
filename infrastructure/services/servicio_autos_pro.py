"""
Servicio profesional de búsqueda web para información de autos.
Obtiene datos en tiempo real de múltiples fuentes.
"""

import os
import re
import json
import requests
from typing import Optional, List, Dict, Any
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

from infrastructure.logging.structured_logging import api_logger

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class FuenteDatos:
    """Representa una fuente de datos de precios de autos."""
    
    def __init__(self, nombre: str, url: str, tipo: str):
        self.nombre = nombre
        self.url = url
        self.tipo = tipo  # "web", "api", "scraper"


class ServicioBusquedaAutos:
    """
    Servicio profesional para buscar información de autos en tiempo real.
    Usa múltiples fuentes de datos.
    """
    
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY", "")
        self._init_fuentes()
    
    def _init_fuentes(self):
        """Inicializa las fuentes de datos."""
        self.fuentes = [
            FuenteDatos("Toyota México", "https://www.toyota.mx", "oficial"),
            FuenteDatos("Honda México", "https://www.honda.mx", "oficial"),
            FuenteDatos("Nissan México", "https://www.nissan.mx", "oficial"),
            FuenteDatos("Ford México", "https://www.ford.mx", "oficial"),
            FuenteDatos("Chevrolet México", "https://www.chevrolet.mx", "oficial"),
            FuenteDatos("Kia México", "https://www.kia.com/mx", "oficial"),
            FuenteDatos("Hyundai México", "https://www.hyundai.com.mx", "oficial"),
            FuenteDatos("Mazda México", "https://www.mazda.mx", "oficial"),
            FuenteDatos("VW México", "https://www.vw.com.mx", "oficial"),
            FuenteDatos("MercadoLibre Autos", "https://autos.mercadolibre.com.mx", "marketplace"),
            FuenteDatos("Autocosmos", "https://www.autocosmos.com.mx", "marketplace"),
            FuenteDatos("Kavak", "https://www.kavak.com/mx", "used"),
            FuenteDatos("Carrosycamionetas", "https://www.carrosycamionetas.com", "used"),
        ]
    
    def buscar_auto(
        self, 
        marca: str, 
        modelo: str, 
        anio: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Busca información de un auto específico.
        
        Args:
            marca: Marca del auto (ej: Toyota)
            modelo: Modelo del auto (ej: Corolla)
            anio: Año del auto (opcional)
        
        Returns:
            Dict con información completa del auto
        """
        year = anio or "2024"
        
        # Buscar precios oficiales
        precios_oficiales = self._buscar_precios_oficiales(marca, modelo, year)
        
        # Buscar precios de usados
        precios_usados = self._buscar_precios_usados(marca, modelo, year)
        
        # Buscar especificaciones
        especificaciones = self._buscar_especificaciones(marca, modelo, year)
        
        return {
            "busqueda": {
                "marca": marca,
                "modelo": modelo,
                "anio": year,
                "timestamp": self._obtener_timestamp()
            },
            "precios_oficiales": precios_oficiales,
            "precios_usados": precios_usados,
            "especificaciones": especificaciones,
            "fuentes": self._obtener_fuentes_consultadas()
        }
    
    def _buscar_precios_oficiales(self, marca: str, modelo: str, year: str) -> List[Dict]:
        """Busca precios oficiales del auto."""
        if not self.serpapi_key:
            return self._buscar_precios_fallback(marca, modelo, year)
        
        consultas = [
            f"{marca} {modelo} {year} precio lista Mexico sitio:oficial",
            f"{marca} {modelo} {year} precio Mexico 2024",
        ]
        
        resultados = []
        for consulta in consultas:
            results = self._buscar_serpapi(consulta)
            resultados.extend(results)
        
        return self._procesar_precios(resultados, "oficial")
    
    def _buscar_precios_usados(self, marca: str, modelo: str, year: str) -> List[Dict]:
        """Busca precios de autos usados."""
        if not self.serpapi_key:
            return []
        
        consultas = [
            f"{marca} {modelo} {year} usado precio Mexico",
            f"{marca} {modelo} seminuevo precio Mexico",
        ]
        
        resultados = []
        for consulta in consultas:
            results = self._buscar_serpapi(consulta)
            resultados.extend(results)
        
        return self._procesar_precios(resultados, "usado")
    
    def _buscar_especificaciones(self, marca: str, modelo: str, year: str) -> Dict:
        """Busca especificaciones del auto."""
        if not self.serpapi_key:
            return {}
        
        consulta = f"{marca} {modelo} {year} especificaciones motor hp Mexico"
        resultados = self._buscar_serpapi(consulta)
        
        specs = {
            "motor": "",
            "potencia": "",
            "consumo": "",
            "transmision": "",
            "combustible": ""
        }
        
        for r in resultados:
            texto = r.get("descripcion", "").lower()
            texto_titulo = r.get("titulo", "").lower()
            
            # Buscar motor
            if "motor" in texto or "motor" in texto_titulo:
                match = re.search(r'(\d+\.?\d*)\s*(?:L|ltros?|cc)', texto, re.IGNORECASE)
                if match:
                    specs["motor"] = match.group(1) + "L"
            
            # Buscar horsepower
            if "hp" in texto or "caballos" in texto:
                match = re.search(r'(\d+)\s*(?:hp|caballos?|cv)', texto, re.IGNORECASE)
                if match:
                    specs["potencia"] = match.group(1) + " hp"
            
            # Buscar consumo
            if "consumo" in texto or "km/l" in texto:
                match = re.search(r'(\d+\.?\d*)\s*(?:km/?l|mpg)', texto, re.IGNORECASE)
                if match:
                    specs["consumo"] = match.group(1) + " km/L"
        
        return specs
    
    def _buscar_serpapi(self, consulta: str) -> List[Dict]:
        """Realiza búsqueda usando SerpAPI."""
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
        except Exception as e:
            api_logger.warning("SerpAPI falló", consulta=consulta, error=str(e))
        
        return []
    
    def _buscar_precios_fallback(self, marca: str, modelo: str, year: str) -> List[Dict]:
        """Fallback cuando no hay API key."""
        return [
            {
                "precio": "Consultar dealership",
                "version": "Precio de lista",
                "fuente": f"Visita www.{marca.lower()}.mx para precios oficiales",
                "tipo": "oficial"
            }
        ]
    
    def _procesar_precios(self, resultados: List[Dict], tipo: str) -> List[Dict]:
        """Procesa y extrae precios de los resultados."""
        precios = []
        
        for r in resultados:
            texto = r.get("descripcion", "") + " " + r.get("titulo", "")
            
            # Buscar precios en diferentes formatos
            patrones_precio = [
                r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:MXN|mn|m\.n\.)',
                r'desde\s*\$\s*(\d{1,3}(?:,\d{3})*)',
                r'(\d{1,3}(?:,\d{3})*)\s*MXN',
            ]
            
            for patron in patrones_precio:
                match = re.search(patron, texto, re.IGNORECASE)
                if match:
                    precio_str = match.group(1).replace(",", "")
                    try:
                        precio = float(precio_str)
                        if 100000 < precio < 5000000:  # Rango razonable en MXN
                            precios.append({
                                "precio": f"${precio:,.0f} MXN",
                                "version": self._extraer_version(texto),
                                "fuente": r.get("fuente", ""),
                                "url": r.get("url", ""),
                                "tipo": tipo
                            })
                    except:
                        pass
        
        # Eliminar duplicados y limitar
        seen = set()
        unique_precios = []
        for p in precios:
            key = p["precio"]
            if key not in seen:
                seen.add(key)
                unique_precios.append(p)
        
        return unique_precios[:5]
    
    def _extraer_version(self, texto: str) -> str:
        """Extrae la versión del auto del texto."""
        versiones = ["base", "le", "xle", "se", "sport", "touring", "limited", "premium"]
        texto_lower = texto.lower()
        
        for v in versiones:
            if v in texto_lower:
                return v.upper()
        
        return "General"
    
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
            "volkswagen": "Volkswagen México",
            "mercadolibre": "MercadoLibre",
            "autocosmos": "Autocosmos",
            "kavak": "Kavak",
            "carrosycamionetas": "Carros y Camionetas",
        }
        
        url_lower = url.lower()
        for patron, nombre in fuentes.items():
            if patron in url_lower:
                return nombre
        
        # Extraer dominio
        if "/" in url:
            dominio = url.split("/")[2]
            return dominio.replace("www.", "").split(".")[0].title()
        
        return "Desconocido"
    
    def _obtener_timestamp(self) -> str:
        """Obtiene el timestamp actual."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _obtener_fuentes_consultadas(self) -> List[str]:
        """Retorna lista de fuentes disponibles."""
        return [f.nombre for f in self.fuentes]
    
    def formatear_resultado(self, resultado: Dict) -> str:
        """Formatea el resultado para mostrar al usuario."""
        if not resultado:
            return "No se encontró información."
        
        busqueda = resultado.get("busqueda", {})
        marca = busqueda.get("marca", "").title()
        modelo = busqueda.get("modelo", "").title()
        anio = busqueda.get("anio", "")
        
        output = f"🚗 **{marca} {modelo} {anio}**\n\n"
        
        # Precios oficiales
        precios_ofic = resultado.get("precios_oficiales", [])
        if precios_ofic:
            output += "💰 **Precios Nuevos:**\n"
            for p in precios_ofic[:3]:
                output += f"• {p.get('version', 'General')}: {p.get('precio', 'N/A')}\n"
                output += f"  📍 {p.get('fuente', 'N/A')}\n"
            output += "\n"
        
        # Precios usados
        precios_usad = resultado.get("precios_usados", [])
        if precios_usad:
            output += "🔧 **Precios Usados:**\n"
            for p in precios_usad[:3]:
                output += f"• Desde: {p.get('precio', 'N/A')}\n"
                output += f"  📍 {p.get('fuente', 'N/A')}\n"
            output += "\n"
        
        # Especificaciones
        specs = resultado.get("especificaciones", {})
        if specs and any(specs.values()):
            output += "⚙️ **Especificaciones:**\n"
            if specs.get("motor"):
                output += f"• Motor: {specs['motor']}\n"
            if specs.get("potencia"):
                output += f"• Potencia: {specs['potencia']}\n"
            if specs.get("consumo"):
                output += f"• Consumo: {specs['consumo']}\n"
        
        output += f"\n⏰ *Última actualización: {busqueda.get('timestamp', 'N/A')}*"
        
        return output


# Instancia global
_servicio_buscar: Optional[ServicioBusquedaAutos] = None


def get_servicio_autos() -> ServicioBusquedaAutos:
    """Obtiene el servicio de búsqueda de autos."""
    global _servicio_buscar
    if _servicio_buscar is None:
        _servicio_buscar = ServicioBusquedaAutos()
    return _servicio_buscar
