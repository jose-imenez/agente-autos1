"""
Base de conocimientos de autos para RAG.
Contiene información de marcas, modelos, precios y especificaciones.
"""

from typing import List, Dict, Any


class BaseConocimientosAutos:
    """Base de conocimientos sobre autos."""
    
    def __init__(self):
        self.documentos = self._cargar_conocimiento()
    
    def _cargar_conocimiento(self) -> List[Dict[str, Any]]:
        """Carga la base de conocimientos."""
        return [
            # Toyota
            {
                "id": "toyota_corolla_2024",
                "marca": "Toyota",
                "modelo": "Corolla",
                "anio": "2024",
                "tipo": "sedan",
                "contenido": """
Toyota Corolla 2024 es un sedán compacto japonés. 
Precio nuevo desde $419,900 MXN (versión base) hasta $455,700 MXN (versión LE).
Motor 2.0L 168 hp, transmisión CVT, consumo combinado 6.8 L/100km.
Tres versiones: Base, LE y XSE. 
Garantía 5 años o 150,000 km.
Mejor auto compacto en reliability.
                """.strip(),
                "fuente": "Toyota México"
            },
            {
                "id": "toyota_corolla_2025",
                "marca": "Toyota",
                "modelo": "Corolla",
                "anio": "2025",
                "tipo": "sedan",
                "contenido": """
Toyota Corolla 2025 es la versión más reciente del sedán compacto.
Precio estimado desde $429,000 MXN.
Motor híbrido disponible desde $485,000 MXN.
Samecnologias: Toyota Safety Sense 3.0, pantalla de 10.5 pulgadas.
                """.strip(),
                "fuente": "Toyota México"
            },
            {
                "id": "toyota_rav4_2024",
                "marca": "Toyota",
                "modelo": "RAV4",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Toyota RAV4 2024 es un SUV compacto japonés.
Precio desde $544,000 MXN (versión base).
Motor 2.5L 203 hp, disponible en gasolina e híbrido.
Versión híbrida desde $625,900 MXN.
Espacio para 5 pasajeros, cajuela 580 litros.
                """.strip(),
                "fuente": "Toyota México"
            },
            {
                "id": "toyota_hilux_2024",
                "marca": "Toyota",
                "modelo": "Hilux",
                "anio": "2024",
                "tipo": "pickup",
                "contenido": """
Toyota Hilux 2024 es una pickup mediana robusta.
Precio desde $589,000 MXN.
Motor 2.8L turbodiésel 177 hp o 2.7L gasolina 164 hp.
Tracción 4x4 opcional, capacidad de carga 1,000 kg.
                """.strip(),
                "fuente": "Toyota México"
            },
            
            # Honda
            {
                "id": "honda_civic_2024",
                "marca": "Honda",
                "modelo": "Civic",
                "anio": "2024",
                "tipo": "sedan",
                "contenido": """
Honda Civic 2024 es un sedán compacto deportivo.
Precio desde $429,000 MXN (versión LX) hasta $499,000 MXN (versión Touring).
Motor 2.0L 158 hp o 1.5L turbo 180 hp.
Transmisión CVT o manual de 6 velocidades.
Sistema de seguridad Honda Sensing incluido.
                """.strip(),
                "fuente": "Honda México"
            },
            {
                "id": "honda_cr_v_2024",
                "marca": "Honda",
                "modelo": "CR-V",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Honda CR-V 2024 es un SUV compacto premium.
Precio desde $589,000 MXN.
Motor 1.5L turbo 190 hp, tracción integral opcional.
Interior con materiales de alta calidad, pantalla de 9 pulgadas.
                """.strip(),
                "fuente": "Honda México"
            },
            {
                "id": "honda_accord_2024",
                "marca": "Honda",
                "modelo": "Accord",
                "anio": "2024",
                "tipo": "sedan",
                "contenido": """
Honda Accord 2024 es un sedán mediano premium.
Precio desde $599,000 MXN.
Motor 1.5L turbo 192 hp o 2.0L turbo 252 hp (Sport).
Sistema híbrido disponible.
                """.strip(),
                "fuente": "Honda México"
            },
            
            # Nissan
            {
                "id": "nissan_sentra_2024",
                "marca": "Nissan",
                "modelo": "Sentra",
                "anio": "2024",
                "tipo": "sedan",
                "contenido": """
Nissan Sentra 2024 es un sedán compacto.
Precio desde $339,900 MXN.
Motor 2.0L 145 hp, transmisión CVT.
Diseño V-Motion, tecnología ProPILOT.
                """.strip(),
                "fuente": "Nissan México"
            },
            {
                "id": "nissan_kicks_2024",
                "marca": "Nissan",
                "modelo": "Kicks",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Nissan Kicks 2024 es un subcompact SUV.
Precio desde $369,900 MXN.
Motor 1.6L 118 hp, tracción integral opcional.
Sistema de audio Bose, cámara de 360 grados.
                """.strip(),
                "fuente": "Nissan México"
            },
            {
                "id": "nissan_frontier_2024",
                "marca": "Nissan",
                "modelo": "Frontier",
                "anio": "2024",
                "tipo": "pickup",
                "contenido": """
Nissan Frontier 2024 es una pickup mediana.
Precio desde $519,900 MXN.
Motor 2.5L 188 hp o 2.3L turbodiésel 190 hp.
Cajuela de carga con área utilitaria.
                """.strip(),
                "fuente": "Nissan México"
            },
            
            # Ford
            {
                "id": "ford_mustang_2024",
                "marca": "Ford",
                "modelo": "Mustang",
                "anio": "2024",
                "tipo": "deportivo",
                "contenido": """
Ford Mustang 2024 es un muscle car icónico.
Precio desde $799,000 MXN (EcoBoost) hasta $1,199,000 MXN (GT).
Motor 2.3L EcoBoost 310 hp o 5.0L V8 450 hp.
Transmisión manual de 6 velocidades o automática de 10 velocidades.
                """.strip(),
                "fuente": "Ford México"
            },
            {
                "id": "ford_escape_2024",
                "marca": "Ford",
                "modelo": "Escape",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Ford Escape 2024 es un SUV compacto.
Precio desde $459,900 MXN.
Motor 1.5L turbo 180 hp o 2.0L turbo 250 hp.
Versión híbrida y plug-in híbrida disponibles.
                """.strip(),
                "fuente": "Ford México"
            },
            {
                "id": "ford_broncobytes_2024",
                "marca": "Ford",
                "modelo": "Bronco",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Ford Bronco 2024 es un SUV off-road.
Precio desde $699,000 MXN (2 puertas) hasta $899,000 MXN (4 puertas).
Motor 2.7L V6 twin-turbo 330 hp.
Tracción 4x4 con modo Trail Control.
                """.strip(),
                "fuente": "Ford México"
            },
            
            # Chevrolet
            {
                "id": "chevrolet_spark_2024",
                "marca": "Chevrolet",
                "modelo": "Spark",
                "anio": "2024",
                "tipo": "hatchback",
                "contenido": """
Chevrolet Spark 2024 es un auto subcompacto.
Precio desde $239,900 MXN.
Motor 1.4L 98 hp, transmisión manual o automática.
5 puertas, ideal para ciudad.
                """.strip(),
                "fuente": "Chevrolet México"
            },
            {
                "id": "chevrolet_equinox_2024",
                "marca": "Chevrolet",
                "modelo": "Equinox",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Chevrolet Equinox 2024 es un SUV compacto.
Precio desde $489,900 MXN.
Motor 1.5L turbo 170 hp, tracción integral opcional.
Sistema de infoentretenimiento con pantalla de 10 pulgadas.
                """.strip(),
                "fuente": "Chevrolet México"
            },
            {
                "id": "chevrolet_trax_2024",
                "marca": "Chevrolet",
                "modelo": "Trax",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Chevrolet Trax 2024 es un subcompact SUV.
Precio desde $329,900 MXN.
Motor 1.4L turbo 138 hp.
Diseño agresivo, pantalla de 8 pulgadas.
                """.strip(),
                "fuente": "Chevrolet México"
            },
            
            # Kia
            {
                "id": "kia_forte_2024",
                "marca": "Kia",
                "modelo": "Forte",
                "anio": "2024",
                "tipo": "sedan",
                "contenido": """
Kia Forte 2024 es un sedán compacto.
Precio desde $329,900 MXN.
Motor 2.0L 147 hp, transmisión CVT.
5 años de garantía, diseño deportivo.
                """.strip(),
                "fuente": "Kia México"
            },
            {
                "id": "kia_sportage_2024",
                "marca": "Kia",
                "modelo": "Sportage",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Kia Sportage 2024 es un SUV compacto.
Precio desde $449,900 MXN.
Motor 2.0L 155 hp o 1.6L turbo 177 hp.
Diseño distintivo, interior espaciosoo.
                """.strip(),
                "fuente": "Kia México"
            },
            {
                "id": "kia_sorento_2024",
                "marca": "Kia",
                "modelo": "Sorento",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Kia Sorento 2024 es un SUV mediano.
Precio desde $599,900 MXN.
Motor 2.5L 191 hp o 2.2L turbodiésel 199 hp.
7 asientos, opciones híbridas.
                """.strip(),
                "fuente": "Kia México"
            },
            
            # Hyundai
            {
                "id": "hyundai_creta_2024",
                "marca": "Hyundai",
                "modelo": "Creta",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Hyundai Creta 2024 es un subcompact SUV.
Precio desde $379,900 MXN.
Motor 2.0L 157 hp, transmisión automática de 6 velocidades.
Diseño robusto, equipamiento completo.
                """.strip(),
                "fuente": "Hyundai México"
            },
            {
                "id": "hyundai_tucson_2024",
                "marca": "Hyundai",
                "modelo": "Tucson",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Hyundai Tucson 2024 es un SUV compacto.
Precio desde $489,900 MXN.
Motor 2.0L 155 hp o 1.6L turbo 177 hp.
Diseño paramétrico, interior digital.
                """.strip(),
                "fuente": "Hyundai México"
            },
            {
                "id": "hyundai_santa_fe_2024",
                "marca": "Hyundai",
                "modelo": "Santa Fe",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Hyundai Santa Fe 2024 es un SUV mediano.
Precio desde $599,900 MXN.
Motor 2.5L 191 hp o 2.2L turbodiésel 199 hp.
7 asientos, versión híbrida disponible.
                """.strip(),
                "fuente": "Hyundai México"
            },
            
            # Mazda
            {
                "id": "mazda3_2024",
                "marca": "Mazda",
                "modelo": "Mazda3",
                "anio": "2024",
                "tipo": "hatchback",
                "contenido": """
Mazda3 2024 es un hatchback compacto premium.
Precio desde $389,900 MXN.
Motor 2.0L 153 hp o 2.5L 191 hp.
Diseño Kodo, interior de materiales premium.
                """.strip(),
                "fuente": "Mazda México"
            },
            {
                "id": "mazda_cx5_2024",
                "marca": "Mazda",
                "modelo": "CX-5",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Mazda CX-5 2024 es un SUV compacto premium.
Precio desde $489,900 MXN.
Motor 2.0L 155 hp o 2.5L 191 hp.
Tracción integral opcional, interior de lujo.
                """.strip(),
                "fuente": "Mazda México"
            },
            {
                "id": "mazda_cx9_2024",
                "marca": "Mazda",
                "modelo": "CX-9",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Mazda CX-9 2024 es un SUV grande.
Precio desde $699,900 MXN.
Motor 2.5L turbo 250 hp.
7 asientos, tracción integral.
                """.strip(),
                "fuente": "Mazda México"
            },
            
            # Volkswagen
            {
                "id": "vw_jetta_2024",
                "marca": "Volkswagen",
                "modelo": "Jetta",
                "anio": "2024",
                "tipo": "sedan",
                "contenido": """
Volkswagen Jetta 2024 es un sedán compacto alemán.
Precio desde $349,900 MXN.
Motor 1.4L turbo 150 hp o 2.0L turbo 230 hp (GLI).
Calidad alemana, garantía 5 años.
                """.strip(),
                "fuente": "Volkswagen México"
            },
            {
                "id": "vw_tiguan_2024",
                "marca": "Volkswagen",
                "modelo": "Tiguan",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Volkswagen Tiguan 2024 es un SUV compacto.
Precio desde $469,900 MXN.
Motor 2.0L turbo 174 hp o 220 hp (R-Line).
Tracción integral 4Motion opcional.
                """.strip(),
                "fuente": "Volkswagen México"
            },
            {
                "id": "vw_teramont_2024",
                "marca": "Volkswagen",
                "modelo": "Teramont",
                "anio": "2024",
                "tipo": "suv",
                "contenido": """
Volkswagen Teramont 2024 es un SUV grande.
Precio desde $699,900 MXN.
Motor 2.0L turbo 280 hp o 3.6L V6 280 hp.
7 asientos, tracción integral.
                """.strip(),
                "fuente": "Volkswagen México"
            },
            
            # Información general
            {
                "id": "info_comparar_autos",
                "marca": "general",
                "modelo": "comparar",
                "anio": "general",
                "tipo": "guia",
                "contenido": """
Para comparar autos considera:
1. Precio inicial y costo total de propiedad
2. Consumo de combustible
3. Costo de mantenimiento
4. Valor de reventa
5. Equipamiento de seguridad
6. Espacio interior y cajuela
7. Rendimiento y potencia
8. Garantía del fabricante
                """.strip(),
                "fuente": "Guía general"
            },
            {
                "id": "info_comprar_usado",
                "marca": "general",
                "modelo": "usado",
                "anio": "general",
                "tipo": "guia",
                "contenido": """
Consejos para comprar auto usado:
1. Revisa el historial del vehículo (carfax)
2. Inspecciona físicamente: suspensión, motor, transmisión
3. Verifica que todos los documentos estén al día
4. Prueba de manejo obligatoria
5. Consulta el valor en guías como Kelly Blue Book
6. Negocia basado en defectos encontrados
7. Preferible comprar a particulares que dealers
                """.strip(),
                "fuente": "Guía general"
            },
            {
                "id": "info_financiamiento",
                "marca": "general",
                "modelo": "financiamiento",
                "anio": "general",
                "tipo": "guia",
                "contenido": """
Opciones de financiamiento para autos:
1. Crédito con banco: tasas fijas, usually 9-15% anual
2. Crédito con financiera de marca: promociones 0% interés
3. Arrendamiento (leasing): mensualidades menores
4. Comprar de contado: mejor precio, sin intereses

Compara tasas en múltiples instituciones antes de decidir.
                """.strip(),
                "fuente": "Guía general"
            }
        ]
    
    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Retorna todos los documentos."""
        return self.documentos
    
    def buscar_por_marca(self, marca: str) -> List[Dict[str, Any]]:
        """Busca autos por marca."""
        return [d for d in self.documentos if d.get("marca", "").lower() == marca.lower()]
    
    def buscar_por_modelo(self, modelo: str) -> List[Dict[str, Any]]:
        """Busca autos por modelo."""
        return [d for d in self.documentos if modelo.lower() in d.get("modelo", "").lower()]


# Instancia global
_base_conocimientos: BaseConocimientosAutos = None


def get_base_conocimientos() -> BaseConocimientosAutos:
    """Obtiene la base de conocimientos."""
    global _base_conocimientos
    if _base_conocimientos is None:
        _base_conocimientos = BaseConocimientosAutos()
    return _base_conocimientos
