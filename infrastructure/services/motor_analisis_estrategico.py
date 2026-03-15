"""
Motor de Análisis Estratégico Avanzado.

Analiza el contexto del problema, detecta la intención real,
y genera soluciones personalizadas con justificaciones.
"""

import re
from typing import Optional
from dataclasses import dataclass

from domain.entities.entities import (
    Problema,
    Solucion,
    ResultadoAnalisis,
    ComplexityLevel,
    SolutionCategory,
)
from domain.interfaces.ports import IAnalizadorService
from infrastructure.services.analizador_ia_service import AnalizadorIAAvanzado
from infrastructure.services.busqueda_web_service import get_busqueda_web_service
from infrastructure.services.rag_service import get_rag_service


@dataclass
class AnalisisContextual:
    """Representa el análisis estratégico de un problema."""
    problema_resumido: str
    dominio: str
    objetivo_real: str
    factor_clave: str
    restricciones: list[str]
    oportunidades: list[str]


class MotorAnalisisEstrategico(IAnalizadorService):
    """
    Motor de análisis estratégico que va más allá de categorías.
    
    Proceso:
    1. Analiza el contexto específico
    2. Detecta la intención real del usuario
    3. Identifica factores clave
    4. Genera soluciones justificadas
    """
    
    def __init__(self):
        self._analizador_base = AnalizadorIAAvanzado()
        self._intenciones = self._cargar_intenciones()
    
    def _cargar_intenciones(self) -> dict:
        """Carga el sistema de detección de intenciones."""
        return {
            "opciones_trabajo": {
                "indicadores": [
                    "opciones de trabajo", "trabajos en los que", "qué trabajo",
                    "busco empleo", "empleo", "trabajo", "career", "profesión",
                    "a qué me puedo dedicar", "qué puedo trabajar", "camino profesional",
                    "sector", "industria", "área", "campo profesional"
                ],
                "soluciones": self._generar_soluciones_trabajo,
                "mensaje": "He detectado que buscas opciones laborales o profesionales."
            },
            "problema_sueno": {
                "indicadores": [
                    "no puedo dormir", "problemas para dormir", "insomnio",
                    "no duermo", "dormir mal", "mal sueño", "no descanso",
                    "cansado", "fatigado", "sueño", "dormir", "descansar",
                    "horas de sueño", "regular el sueño"
                ],
                "soluciones": self._generar_soluciones_sueno,
                "mensaje": "He detectado un problema relacionado con el descanso o sueño."
            },
            "consejos_generales": {
                "indicadores": [
                    "consejos", "ayuda", "qué me recomiendas", "sugerencias",
                    "qué hacer", "ideas", "opciones", "alternativas",
                    "qué tal si", "cómo podría", " Ways", "cómo"
                ],
                "soluciones": self._generar_soluciones_consejos,
                "mensaje": "Has solicitado consejos o sugerencias."
            },
            "salud_bienestar": {
                "indicadores": [
                    "salud", "enfermo", "enfermedad", "médico", "doctor",
                    "ejercicio", "gimnasio", "deporte", "bienestar", "cuidado",
                    "dieta", "alimentación", "nutrición", "vitaminas"
                ],
                "soluciones": self._generar_soluciones_salud,
                "mensaje": "Has consultado sobre salud o bienestar."
            },
            "relaciones_sociales": {
                "indicadores": [
                    "amigos", "amistad", "pareja", "relación", "familia",
                    "comunicación", "social", "soledad", "aislado",
                    "conocidos", "red social", "networking"
                ],
                "soluciones": self._generar_soluciones_relaciones,
                "mensaje": "Has consultado sobre relaciones o aspectos sociales."
            },
            "finanzas": {
                "indicadores": [
                    "dinero", "finanzas", "inversión", "ahorrar", "gastar",
                    "presupuesto", "deuda", "ingreso", "salario", "riqueza",
                    "económic", "banco", "crédito", "préstamo"
                ],
                "soluciones": self._generar_soluciones_finanzas,
                "mensaje": "Has consultado sobre finanzas o situación económica."
            },
            "estudio_aprendizaje": {
                "indicadores": [
                    "estudiar", "estudio", "aprender", "carrera", "universidad",
                    "colegio", "escuela", "examen", "tarea", "clase", "curso",
                    "capacitación", "formación", "educación", "skill"
                ],
                "soluciones": self._generar_soluciones_estudio,
                "mensaje": "Has consultado sobre estudio o aprendizaje."
            },
            "desarrollo_personal": {
                "indicadores": [
                    "crecer", "mejorar", "desarrollar", "crecimiento personal",
                    "motivación", "meta", "objetivo", "hábito", "rutina",
                    "productividad", "organizar", "tiempo", "procrastinar",
                    "autodisciplina", "foco", "enfoque"
                ],
                "soluciones": self._generar_desarrollo_personal,
                "mensaje": "Has consultado sobre desarrollo personal o productividad."
            },
            "viajes_vacaciones": {
                "indicadores": [
                    "viaje", "vacaciones", "turismo", "destino", "turistear",
                    "viajar", "escapada", "fin de semana", "hostal", "hotel",
                    "vuelo", "pasaporte", "visa", "turístico"
                ],
                "soluciones": self._generar_soluciones_viajes,
                "mensaje": "Has consultado sobre viajes o vacaciones."
            },
            "entretenimiento": {
                "indicadores": [
                    "entretenimiento", "entretenerse", "aburrimiento", "aburrido", "que hacer",
                    "hobby", "pasatiempo", "actividad", "ocio"
                ],
                "soluciones": self._generar_soluciones_entretenimiento,
                "mensaje": "Has consultado sobre entretenimiento o actividades recreativas."
            },
            "comida_alimentacion": {
                "indicadores": [
                    "comer", "comida", "cocinar", "receta", "restaurante",
                    "desayuno", "almuerzo", "cena", "menú", "ingredientes",
                    "preparar", "cocina", "gastronom", "delivery", "hambre"
                ],
                "soluciones": self._generar_soluciones_alimentacion,
                "mensaje": "Has consultado sobre alimentación o preparación de alimentos."
            },
            "problema_tecnico": {
                "indicadores": [
                    "error", "problema", "no funciona", "falla", "técnico",
                    "computadora", "celular", "internet", "wifi", "software",
                    "hardware", "virus", "pantalla", "celular"
                ],
                "soluciones": self._generar_soluciones_tecnico,
                "mensaje": "Has consultado sobre un problema técnico."
            },
            "autos_vehiculos": {
                "indicadores": [
                    "auto", "carro", "coche", "vehículo", "car", "automóvil",
                    "comprar auto", "vender auto", "mantenimiento", "mecánico",
                    "seguro auto", "licencia", "conducir", "manejar", "carros",
                    "modelo", "marca", "usado", "nuevo", "sedan", "suv", "pickup",
                    "toyota", "honda", "ford", "chevrolet", "nissan", "mazda",
                    "bmw", "mercedes", "audi", "volkswagen", "kia", "hyundai",
                    "camioneta", "deportivo", "electrico", "hibrido", "gasolina",
                    "taller", "refaccion", "llanta", "aceite", "frenos", "bateria",
                    "prestamo", "credito", "cuotas", "seminuevo", "0km", "chocado",
                    "traccion", "4x4", "automatico", "manual", "convertible"
                ],
                "soluciones": self._generar_soluciones_autos,
                "mensaje": "Todo sobre autos! Te ayudo con compras, mantenimiento y mas."
            },
            "musica": {
                "indicadores": [
                    "musica", "song", "cancion", "album", "artista", "banda",
                    "rock", "pop", "reggaeton", "trap", "rap", "hip hop",
                    "jazz", "clasica", "metal", "electronica", "salsa", "bachata",
                    "cumbia", "reggae", "punk", "indie", "alternativo", "urbano",
                    "escuchar", "playlist", "spotify", "apple music", "youtube music",
                    "concierto", "festival", "live", "tour", "gira",
                    "instrumento", "guitarra", "piano", "bateria", "bajo", "violin",
                    "cantante", "voz", "tocar", "componer", "producir", "beat",
                    "bad bunny", "drake", "kendrick", "ferxxo", "karol g", "shawn mendez",
                    "coldplay", " Imagine Dragons", "the weeknd", "bts", "blackpink",
                    "disco", "vinyl", "cd", "streaming", "descargar", "mp3",
                    "genero", "estilo", "tempo", "acorde", "nota", "escala"
                ],
                "soluciones": self._generar_soluciones_musica,
                "mensaje": "Todo sobre musica! Disfruta, aprende o crea."
            },
            "videojuegos": {
                "indicadores": [
                    "videojuego", "juego", "gaming", "playstation", "xbox", "nintendo",
                    "switch", "pc", "steam", "epic", "ps5", "ps4", "xbox series x",
                    "fortnite", "minecraft", "lol", "league of legends", "valorant",
                    "zelda", "mario", "gta", "call of duty", "cod", "fps", "rpg",
                    "jugar", "partida", "online", "multijugador", "esports", "competitivo",
                    "casual", "singleplayer", "coop", "cooperativo", "battle royale",
                    "moba", "shooter", "accion", "aventura", "estrategia", "simulacion",
                    "indie", "aaa", "triple a", "gratis", "free to play", "precio",
                    "logro", "trofeo", "logro", "comunidad", "streamer", "twitch",
                    "nvidia", "amd", "rtx", "rtx 4090", "rtx 3080", "ps4 pro", "ps5 pro",
                    "game pass", "ps plus", "xbox live", "nsO", "ea play", "ubisoft",
                    "mario kart", "animal crossing", "smash", "fifa", "ea fc", "futbol",
                    "halo", "god of war", "spider-man", "last of us", "uncharted",
                    "red dead", "cyberpunk", "elden ring", "zelda totk", "hogwarts"
                ],
                "soluciones": self._generar_soluciones_videojuegos,
                "mensaje": "Gamer! Aqui tienes todo sobre juegos."
            },
            "trabajo_empleo": {
                "indicadores": [
                    "trabajo", "empleo", "empleo", "career", "profesion", "oficio",
                    "buscar trabajo", "ofertas", "vacante", "entrevista", "cv", "curriculum",
                    "salario", "sueldo", "prestaciones", "beneficios", "contrato",
                    "renunciar", "dimitir", "despido", "liquidacion", "finiquito",
                    "jefe", "jefatura", "patron", "empleador", "colaborador",
                    "oficina", "remoto", "hibrido", "presencial", "home office",
                    "freelance", "freelancer", "independiente", "por proyecto",
                    "negocio", "emprender", "emprendedor", "startup", "pyme",
                    "entrevista", "entrevistar", "seleccion", "reclutamiento",
                    "reclutador", "headhunter", "linkedin", "indeed", "computrabajo",
                    "skills", "habilidades", "competencias", "experiencia", "estudios",
                    "carrera", "promocion", "ascenso", "aumento", "negociar",
                    "burnout", "estrés", "feliz", "satisfecho", "ambiente",
                    "coworking", "empleo", "postular", "aplicar", "enviar cv"
                ],
                "soluciones": self._generar_soluciones_trabajo,
                "mensaje": "Hablemos de trabajo y empleo! Te ayudo con tu carrera."
            },
            "comida_alimentacion": {
                "indicadores": [
                    "comida", "comer", "alimentos", "receta", "cocinar", "cocina",
                    "desayuno", "almuerzo", "cena", "merienda", "snack", "antojo",
                    "restaurante", "comida para llevar", "delivery", "servicio a domicilio",
                    "cafe", "restobar", "bar", "comida rapida", "fast food", "chatarra",
                    "saludable", "organico", "natural", "integral", "sin gluten",
                    "vegano", "vegetariano", "carnivoro", "omnivoro", "keto", " Atkins",
                    "dieta", "bajar peso", "subir peso", "musculo", "definicion",
                    "preparar", "ingredientes", "utensilios", "horno", "sarten",
                    "microondas", "air fryer", "cuchillo", "tabla",
                    "tipico", "tradicional", "local", "gourmet", "casero",
                    "rapida", "facil", "complicada", "tiempo", "horas",
                    "pollo", "carne", "pescado", "mariscos", "arroz", "pasta",
                    "frijol", "lenteja", "verdura", "fruta", "ensalada", "sopa",
                    "salsa", "condimento", "especias", "hierbas", "ajo", "cebolla",
                    "pan", "torta", "hamburguesa", "pizza", "tacos", "burrito",
                    "sushi", "ramen", "pad thai", "pasta carbonara", "lasagna",
                    "desayuno americano", "huevos", "tocino", "panque", "waffle"
                ],
                "soluciones": self._generar_soluciones_alimentacion,
                "mensaje": "Hambre! Todo sobre comida aqui."
            },
            "cine_peliculas": {
                "indicadores": [
                    "película", "pelicula", "cine", "movie", "film", "netflix",
                    "hbo", "amazon prime", "disney", "series", "ver", "ESTRENO",
                    "director", "actor", "actriz", "hollywood", "marvel", "dc"
                ],
                "soluciones": self._generar_soluciones_cine,
                "mensaje": "Has consultado sobre cine o películas."
            },
            "deportes": {
                "indicadores": [
                    "fútbol", "futbol", "football", "básquet", "basquet", "basketball",
                    "béisbol", "beisbol", "tennis", "tenis", "golf", "boxeo",
                    "ufc", "mma", "nba", "mlb", "nfl", "europa", "liga",
                    "partido", "equipo", "jugador", "torneo", "copa", "mundial"
                ],
                "soluciones": self._generar_soluciones_deportes,
                "mensaje": "Has consultado sobre deportes."
            },
            "moda_estilo": {
                "indicadores": [
                    "moda", "estilo", "ropa", "vestir", "outfit", "zapatos",
                    "tenis", "camisa", "pants", "jeans", "traje", "formal",
                    "casual", "tendencias", "marca", "nike", "adidas", "zara",
                    "h&m", "tendencia", "look", "vestuario"
                ],
                "soluciones": self._generar_soluciones_moda,
                "mensaje": "Has consultado sobre moda o estilo."
            },
            "ciencias_tecnologia": {
                "indicadores": [
                    "ciencia", "tecnología", "tecnologia", "espacio", "nasa",
                    "inteligencia artificial", "ia", "robot", "espacio",
                    "investigación", "descubrimiento", "física", "química",
                    "biología", "astronomía", "espacio", "satelite", "mars",
                    "innovación", "startup", "tech", "silicon valley"
                ],
                "soluciones": self._generar_soluciones_ciencia,
                "mensaje": "Has consultado sobre ciencia o tecnología."
            }
        }
    
    def _detectar_intencion(self, texto: str) -> tuple[str, float]:
        """Detecta la intención principal del usuario."""
        mejor_intencion = ""
        mejor_puntuacion = 0
        
        texto_lower = texto.lower()
        
        # Marcas de autos conocidas
        marcas_autos = ["toyota", "honda", "ford", "chevrolet", "nissan", "mazda", 
                       "bmw", "mercedes", "audi", "volkswagen", "kia", "hyundai",
                       "subaru", "mitsubishi", "jeep", "lexus", "porsche", "tesla"]
        
        # Priorizar autos si se detecta una marca
        tiene_marca_auto = any(marca in texto_lower for marca in marcas_autos)
        
        for nombre_intencion, datos in self._intenciones.items():
            puntuacion = sum(1 for ind in datos["indicadores"] if ind in texto_lower)
            
            # Boost para autos si hay marca detectada
            if tiene_marca_auto and nombre_intencion == "autos_vehiculos":
                puntuacion += 10
            
            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_intencion = nombre_intencion
        
        if mejor_puntuacion >= 1:
            return mejor_intencion, mejor_puntuacion
        
        return "general", 0
    
    def _generar_soluciones_por_intencion(
        self, 
        texto: str, 
        intencion: str,
        categorias_usadas: set
    ) -> list[Solucion]:
        """Genera soluciones basadas en la intención detectada."""
        
        if intencion in self._intenciones:
            datos_intencion = self._intenciones[intencion]
            metodo_soluciones = datos_intencion["soluciones"]
            
            soluciones_intencion = metodo_soluciones(texto)
            
            # Filtrar soluciones ya usadas
            soluciones_filtradas = []
            titulos_previos = {s.titulo.lower() for s in soluciones_filtradas}
            
            for sol in soluciones_intencion:
                if sol.titulo.lower() not in titulos_previos:
                    if sol.categoria not in categorias_usadas:
                        soluciones_filtradas.append(sol)
                        titulos_previos.add(sol.titulo.lower())
            
            return soluciones_filtradas
        
        return []
    
    def analizar(
        self, 
        problema: Problema,
        soluciones_previas: Optional[list] = None
    ) -> ResultadoAnalisis:
        """Ejecuta el análisis estratégico completo."""
        
        texto = problema.texto.lower()
        texto_original = problema.texto
        
        intencion, puntuacion_intencion = self._detectar_intencion(texto_original)
        
        if puntuacion_intencion >= 1:
            return self._analizar_con_intencion(problema, intencion, soluciones_previas)
        
        es_vaga, razones_vagueza = self._es_entrada_vaga(texto_original, texto)
        problema_real = self._analizar_problema_real(texto_original, texto)
        analisis = self._analisis_contextual(problema.texto, texto)
        categoria = self._analizador_base._detectar_categoria(texto)
        
        categorias_usadas = set()
        if soluciones_previas:
            for sol in soluciones_previas:
                if hasattr(sol, 'categoria'):
                    categorias_usadas.add(sol.categoria)
        
        preguntas_aclaratorias = []
        if es_vaga:
            preguntas_aclaratorias = self._generar_preguntas_aclaratorias(
                texto_original, razones_vagueza, problema_real
            )
        
        soluciones = self._generar_soluciones_estrategicas(
            texto, analisis, categoria, categorias_usadas
        )
        
        from datetime import datetime
        return ResultadoAnalisis(
            problema_original=problema.texto,
            timestamp=datetime.now(),
            soluciones=soluciones,
            razonamiento=self._generar_razonamiento_estrategico(analisis, problema_real, es_vaga),
            preguntas_aclaratorias=preguntas_aclaratorias,
        )
    
    def _analizar_con_intencion(
        self, 
        problema: Problema, 
        intencion: str,
        soluciones_previas: Optional[list] = None
    ) -> ResultadoAnalisis:
        """Analiza el problema usando soluciones específicas para la intención detectada."""
        
        texto_original = problema.texto
        texto = texto_original.lower()
        
        categorias_usadas = set()
        if soluciones_previas:
            for sol in soluciones_previas:
                if hasattr(sol, 'categoria'):
                    categorias_usadas.add(sol.categoria)
        
        soluciones_intencion = self._generar_soluciones_por_intencion(
            texto, intencion, categorias_usadas
        )
        
        if len(soluciones_intencion) >= 3:
            soluciones = soluciones_intencion[:5]
        else:
            analisis = self._analisis_contextual(texto_original, texto)
            categoria = self._analizador_base._detectar_categoria(texto)
            soluciones_estrategicas = self._generar_soluciones_estrategicas(
                texto, analisis, categoria, categorias_usadas
            )
            
            soluciones = soluciones_intencion + soluciones_estrategicas
            soluciones = soluciones[:5]
        
        mensaje_intencion = ""
        if intencion in self._intenciones:
            mensaje_intencion = self._intenciones[intencion]["mensaje"]
        
        from datetime import datetime
        return ResultadoAnalisis(
            problema_original=problema.texto,
            timestamp=datetime.now(),
            soluciones=soluciones,
            razonamiento=f"""
## Análisis de Intención Detectada

**Tu solicitud:** {texto_original}

---

{mensaje_intencion}

He generado opciones específicas para tu situación. Cada solución incluye:
- Una descripción clara
- Ventajas y desventajas  
- Nivel de complejidad
- Recomendación personalizada
- Recursos/ tecnologías útiles

Elige la opción que mejor se adapte a tu contexto y preferencias.
            """.strip(),
            preguntas_aclaratorias=[],
        )

    def _generar_soluciones_trabajo(self, texto: str) -> list[Solucion]:
        """Genera soluciones para opciones de trabajo/empleo."""
        return [
            Solucion(
                titulo="Explorar industrias en crecimiento",
                descripcion="Identifica sectores con alta demanda laboral: tecnología, salud, energías renovables, e-commerce. Investiga qué posiciones están contratando y qué habilidades buscan.",
                ventajas=[
                    "Mayores oportunidades de empleo",
                    "Salarios competitivos",
                    "Estabilidad laboral",
                    "Crecimiento profesional"
                ],
                desventajas=[
                    "Puede requerir recualificación",
                    "Competencia en algunos sectores",
                    "Algunas industrias requieren experiencia"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Investiga al menos 3 industrias que te interesen y sus posiciones más demandadas.",
                tecnologias=["LinkedIn", "Indeed", "Informes de mercado", "Glassdoor"]
            ),
            Solucion(
                titulo="Desarrollar habilidades transversales",
                descripcion="Fortalece habilidades valoradas en cualquier industria: comunicación, pensamiento crítico, resolución de problemas, trabajo en equipo y adaptación al cambio.",
                ventajas=[
                    "Aplicables a múltiples trabajos",
                    "Dificultades de replicar por IA",
                    "Elevan tu valor en cualquier sector",
                    "Facilitan transición de carrera"
                ],
                desventajas=[
                    "Toma tiempo desarrollarlas",
                    "Requiere práctica constante"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
               recomendacion="Elige 2 habilidades y enfócate en desarrollarlas activamente durante los próximos 3 meses.",
                tecnologias=["Coursera", "YouTube", "Libros", "Mentoría"]
            ),
            Solucion(
                titulo="Freelancing y trabajo independiente",
                descripcion="Explora plataformas como Upwork, Fiverr, o Freelancer para ofrecer tus servicios. Comienza con proyectos pequeños para construir reputación.",
                ventajas=[
                    "Flexibilidad de horarios",
                    "Variedad de proyectos",
                    "Potencial de ingresos altos",
                    "Control sobre tu trabajo"
                ],
                desventajas=[
                    "Ingresos variables al inicio",
                    "Necesitas manejar tus propios impuestos",
                    "Competencia global"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Dedica 5 horas semanales a empezar como freelancer mientras mantienes tu empleo actual.",
                tecnologias=["Upwork", "Fiverr", "LinkedIn ProFinder", "Portfolio personal"]
            ),
            Solucion(
                titulo="Trabajo remoto",
                descripcion="Explora oportunidades de trabajo remoto que permiten trabajar desde cualquier ubicación. Muchas empresas ahora ofrecen modalidades híbridas o完全的 remoto.",
                ventajas=[
                    "Ahorro en transporte",
                    "Mayor flexibilidad",
                    "Trabajar desde cualquier lugar",
                    "Mejor balance vida-trabajo"
                ],
                desventajas=[
                    "Requiere autodisciplina",
                    "Posible soledad",
                    "Zonas horarias diferentes"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Busca empresas remoto-first y ajusta tu CV para destacar tu capacidad de trabajo autónomo.",
                tecnologias=["Remote OK", "We Work Remotely", "LinkedIn", "Angel List"]
            ),
            Solucion(
                titulo="Emprendimiento",
                descripcion="Considera crear tu propio negocio o producto. Identifica un problema que puedas resolver y valida tu idea antes de comprometerte completamente.",
                ventajas=[
                    "Control total sobre tu carrera",
                    "Potencial de ingresos ilimitados",
                    "Independencia",
                    "Resolver problemas reales"
                ],
                desventajas=[
                    "Riesgo financiero",
                    "Mucho trabajo inicial",
                    "Incertidumbre",
                    "Responsable de todo"
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Empieza tu proyecto como side hustle mientras tienes ingresos estables.",
                tecnologias=["Lean Startup", "Canvas de Modelo de Negocio", "Stripe", "Marketplaces"]
            ),
        ]
    
    def _generar_soluciones_sueno(self, texto: str) -> list[Solucion]:
        """Genera soluciones para problemas de sueño."""
        return [
            Solucion(
                titulo="Establecer rutina de sueño",
                descripcion="Crea una rutina consistente: misma hora de acostarte y levantarte, incluso en fines de semana. El cuerpo se regula con la consistencia.",
                ventajas=[
                    "Regula tu reloj biológico",
                    "Mejora la calidad del sueño",
                    "Facilita despertar",
                    "Efecto acumulativo positivo"
                ],
                desventajas=[
                    "Difícil cambiar hábitos establecidos",
                    "Resultados no inmediatos"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Elige una hora de despertar realista y manténla 7 días seguidos.",
                tecnologias=["Alarmas", "Aplicaciones de rutina", "Diario de sueño"]
            ),
            Solucion(
                titulo="Optimizar ambiente de dormir",
                descripcion="Tu habitación debe ser oscura, fresca (18-20°C), silenciosa y cómoda. Invierte en sábanas cómodas y elimina fuentes de luz.",
                ventajas=[
                    "Mejora inmediata la calidad",
                    "Sin costo alto",
                    "Fácil de implementar",
                    "Efecto rápido"
                ],
                desventajas=[
                    "Puede requerir inversión",
                    "Depende de tu vivienda"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Prueba con tapones para oídos y antifaz los primeros días.",
                tecnologias=["F遮光窗帘", "Ventilador", "Aire acondicionado", "Tapones"]
            ),
            Solucion(
                titulo="Reducir exposición a pantallas",
                descripcion="Evita pantallas (celular, TV, computadora) al menos 1 hora antes de dormir. La luz azul suprime la producción de melatonina.",
                ventajas=[
                    "Mejora calidad de sueño",
                    "Facilita conciliación",
                    "Beneficia salud ocular",
                    "Reduce ansiedad"
                ],
                desventajas=[
                    "Difícil de implementar",
                    "Requiere nuevo hábito"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Carga tu celular fuera de la habitación.",
                tecnologias=["Filtros de luz azul", "Libros físicos", "Música relajante"]
            ),
            Solucion(
                titulo="Actividad física regular",
                descripcion="El ejercicio mejora la calidad del sueño, pero hazlo al menos 3 horas antes de dormir. El ejercicio intenso cerca de la hora de dormir puede alterar el sueño.",
                ventajas=[
                    "Múltiples beneficios de salud",
                    "Mejora sueño profundo",
                    "Ayuda a manejar estrés",
                    "Efecto a largo plazo"
                ],
                desventajas=[
                    "Requiere consistencia",
                    "No hacer muy tarde"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Camina 30 minutos al día - es suficiente para mejorar tu sueño.",
                tecnologias=["Running", "Yoga", "Gimnasio", "Caminatas"]
            ),
            Solucion(
                titulo="Técnicas de relajación",
                descripcion="Practica respiración profunda, meditación, o relajación muscular progresiva antes de dormir. Esto activa el sistema nervioso parasimpático.",
                ventajas=[
                    "Reduce estrés y ansiedad",
                    "Ayuda a conciliar sueño",
                    "Sin efectos secundarios",
                    "Mejora bienestar general"
                ],
                desventajas=[
                    "Requiere práctica",
                    "Resultados varían"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Prueba la técnica 4-7-8: inhala 4 segundos, mantén 7, exhala 8.",
                tecnologias=["Headspace", "Calm", "YouTube", "Aplicaciones de meditación"]
            ),
        ]
    
    def _generar_soluciones_consejos(self, texto: str) -> list[Solucion]:
        """Genera soluciones generales/consejos."""
        return [
            Solucion(
                titulo="Define tu objetivo específico",
                descripcion="En lugar de una meta vaga, define exactamente qué quieres lograr. 'Quiero perder peso' → 'Quiero perder 5 kg en 3 meses'.",
                ventajas=[
                    "Medible y alcanzable",
                    "Motivación clara",
                    "Puedes celebrar logros"
                ],
                desventajas=[
                    "Requiere honestidad",
                    " Puede parecer limitante"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Escribe tu objetivo en una frase que incluya fecha límite.",
                tecnologias=["Notas", "Objetivos SMART", "Visualización"]
            ),
            Solucion(
                titulo="Comienza con el mínimo viable",
                descripcion="No necesitas tener todo resuelto. Empieza con la acción más pequeña posible y ajusta sobre la marcha.",
                ventajas=[
                    "Elimina parálisis",
                    "Genera momentum",
                    "Aprendes haciendo"
                ],
                desventajas=[
                    "Resultados iniciales pequeños"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Pregúntate: ¿Cuál es la cosa más pequeña que puedo hacer hoy?",
                tecnologias=["Lista de tareas", "Notas"]
            ),
            Solucion(
                titulo="Busca perspectivas externas",
                descripcion="Habla con personas que hayan resuelto algo similar. Una conversación puede ahorrarte meses de esfuerzo.",
                ventajas=[
                    "Perspectiva objetiva",
                    "Ahorra tiempo",
                    "Conexiones valiosas"
                ],
                desventajas=[
                    "Dependes de otros"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Envía 3 mensajes a personas que admiras preguntando por su experiencia.",
                tecnologias=["LinkedIn", "Coffee chat", "Mentoría"]
            ),
            Solucion(
                titulo="Experimenta y itera",
                descripcion="En lugar de buscar la solución perfecta, prueba algo, evalúa resultados, y ajusta. Los mejores resultados vienen de iteración rápida.",
                ventajas=[
                    "Aprendizaje rápido",
                    "Flexibilidad",
                    "Menor riesgo"
                ],
                desventajas=[
                    "Puede parecer ineficiente"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Designa 1 hora semanal para evaluar qué funcionó y qué no.",
                tecnologias=["Diario", "Notas", "Métricas simples"]
            ),
            Solucion(
                titulo="Cuida tu bienestar básico",
                descripcion="A veces los problemas se resuelven atendiendo lo básico: duerme bien, come sanamente, haz ejercicio, y conecta con otros.",
                ventajas=[
                    "Mejora todo",
                    "Fundamento de todo",
                    "Sin costo alto"
                ],
                desventajas=[
                    "Difícil mantener hábito"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Comienza con un hábito básico: duerme 7+ horas o come 3 veces al día.",
                tecnologias=["Rutinas", "Autocuidado"]
            ),
        ]
    
    def _generar_soluciones_salud(self, texto: str) -> list[Solucion]:
        """Genera soluciones para salud y bienestar."""
        return [
            Solucion(
                titulo="Chequeo médico preventivo",
                descripcion="Agenda un chequeo general para evaluar tu estado de salud. Detectar problemas tempranamente mejora significativamente los resultados.",
                ventajas=[
                    "Detección temprana",
                    "Tranquilidad",
                    "Guía personalizada"
                ],
                desventajas=[
                    "Puede encontrar problemas",
                    "Costo si no tienes seguro"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Si no has ido al médico en más de un año, agenda una cita ahora.",
                tecnologias=["Hospitales", "Clínicas", "Seguro médico"]
            ),
            Solucion(
                titulo="Hidratación adecuada",
                descripcion="Bebe al menos 2 litros de agua al día. La deshidratación causa fatiga, dolor de cabeza y afecta tu concentración.",
                ventajas=[
                    "Fácil de implementar",
                    "Mejora energía",
                    "Beneficia piel y salud"
                ],
                desventajas=[
                    "Fácil olvidar"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Lleva una botella de agua contigo y configura recordatorios.",
                tecnologias=["Botella de agua", "Apps de hidratación"]
            ),
            Solucion(
                titulo="Ejercicio moderado",
                descripcion="No necesitas ir al gym. Caminar 30 minutos, subir escaleras, o hacer ejercicios en casa tiene beneficios enormes.",
                ventajas=[
                    "Mejora salud mental",
                    "Más energía",
                    "Duermes mejor"
                ],
                desventajas=[
                    "Requiere tiempo"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Camina 15 minutos mañana y tarde - son 150 minutos semanales.",
                tecnologias=["YouTube workouts", "Running", "Yoga apps"]
            ),
            Solucion(
                titulo="Alimentación equilibrada",
                descripcion="Come variedad de alimentos: proteínas, carbohidratos complejos, grasas saludables, frutas y verduras. Evita ultraprocesados.",
                ventajas=[
                    "Más energía",
                    "Mejor humor",
                    "Prevención enfermedades"
                ],
                desventajas=[
                    "Más caro a veces",
                    "Requiere planificación"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Añade una verdura o fruta a cada comida.",
                tecnologias=["Meal prep", "Recetas saludables", "Nutricionista"]
            ),
            Solucion(
                titulo="Manejo del estrés",
                descripcion="Identifica tus fuentes de estrés y desarrolla estrategias: respiración, meditación, ejercicio, o simplemente decir 'no'.",
                ventajas=[
                    "Mejor salud mental",
                    "Mejora relaciones",
                    "Más productividad"
                ],
                desventajas=[
                    "Requiere autoconocimiento"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Practica 5 minutos de respiración al día y aumenta gradualmente.",
                tecnologias=["Meditación", "Terapias", "Ejercicio", "Diario"]
            ),
        ]
    
    def _generar_soluciones_relaciones(self, texto: str) -> list[Solucion]:
        """Genera soluciones para relaciones sociales."""
        return [
            Solucion(
                titulo="Iniciativa proactiva",
                descripcion="No esperes que otros te busquen. Toma la iniciativa: invita a alguien a tomar café,uni eventos, o envía ese mensaje.",
                ventajas=[
                    "Controlas tu vida social",
                    "Construyes confianza",
                    "Conectas con quien quieres"
                ],
                desventajas=[
                    "Puede dar miedo",
                    "Some pueden rechazar"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Invita a una persona por semana a hacer algo específico.",
                tecnologias=["WhatsApp", "Eventos locales", "Clases"]
            ),
            Solucion(
                titulo="Mejora comunicación",
                descripcion="Practica escucha activa: enfócate en entender antes de responder. Usa 'yo siento' en lugar de 'tú siempre'.",
                ventajas=[
                    "Relaciones más profundas",
                    "Menos conflictos",
                    "Mejor comprensión"
                ],
                desventajas=[
                    "Requiere práctica",
                    "Cambio de hábitos"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="En tu próxima conversación,Deja que la otra persona termine de hablar antes de responder.",
                tecnologias=["Libros de comunicación", "Terapia", "YouTube"]
            ),
            Solucion(
                titulo="Únete a comunidades",
                descripcion="Busca grupos con intereses comunes: deportes, arte, voluntariado, religión, o juegos. Las conexiones se dan naturalmente.",
                ventajas=[
                    "Amistades basadas en intereses",
                    "Actividades estructuradas",
                    "Soporte social"
                ],
                desventajas=[
                    "Requiere tiempo",
                    "Puede ser incómodo al inicio"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Busca 2-3 grupos o eventos que te interesen y asiste esta semana.",
                tecnologias=["Meetup", "Facebook Groups", "Clases locales"]
            ),
            Solucion(
                titulo="Calidad sobre cantidad",
                descripcion="Enfócate en深度 relaciones con pocas personas en lugar de muchas superficiales. 3-5 amigos cercanos es más que suficiente.",
                ventajas=[
                    "Relaciones más significativas",
                    "Mayor apoyo",
                    "Más satisfactorias"
                ],
                desventajas=[
                    "Menor red",
                    "Requiere inversión de tiempo"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Elige 3 personas importantes y comprométete a contactarles regularmente.",
                tecnologias=["Llamadas", "Citas presenciales", "Mensajes"]
            ),
            Solucion(
                titulo="Sé genuino",
                descripcion="Sé tú mismo. Las conexiones reales se basan en autenticidad, no en impresionar o gustar a todos.",
                ventajas=[
                    "Relaciones genuinas",
                    "Menos esfuerzo",
                    "Te aceptan como eres"
                ],
                desventajas=[
                    "Some no te aceptarán"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Comparte algo personal con alguien de confianza esta semana.",
                tecnologias=["Vulnerability", "Honestidad", "Autenticidad"]
            ),
        ]
    
    def _generar_soluciones_finanzas(self, texto: str) -> list[Solucion]:
        """Genera soluciones para finanzas."""
        return [
            Solucion(
                titulo="Presupuesto mensual",
                descripcion="Crea un presupuesto simple: ingresa tus gastos fijos (alquiler, servicios, comida) y establece límites para variables.",
                ventajas=[
                    "Control de gastos",
                    "Ahorro consciente",
                    "Sin sorpresas"
                ],
                desventajas=[
                    "Requiere disciplina",
                    "Al inicio dawork"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Usa la regla 50/30/20: 50% necesidades, 30% deseos, 20% ahorro.",
                tecnologias=["Excel", "Mint", "YNAB", "Apps bancarias"]
            ),
            Solucion(
                titulo="Automata el ahorro",
                descripcion="Configura transferencias automáticas a una cuenta de ahorro el día que cobras. Págate a ti primero.",
                ventajas=[
                    "Ahorras sin pensarlo",
                    "Consistente",
                    "Fuera de vista, fuera de mente"
                ],
                desventajas=[
                    "Menos flexibilidad"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Automatiza transferir 10% de cualquier ingreso inmediatamente.",
                tecnologias=["Banca en línea", "Transferencias automáticas"]
            ),
            Solucion(
                titulo="Reduce gastos innecesarios",
                descripcion="Identifica gastos que puedes eliminar: suscripciones no usadas, comer fuera, compras impulsivas.",
                ventajas=[
                    "Ahorro inmediato",
                    "Sin impacto en calidad de vida",
                    "Fácil de implementar"
                ],
                desventajas=[
                    "Requiere honestidad"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Revisa tus estados de cuenta y marca 3 gastos a eliminar.",
                tecnologias=["Apps de gastos", "Revisión mensual"]
            ),
            Solucion(
                titulo="Diversifica ingresos",
                descripcion="No dependas de una sola fuente. Explora ingresos pasivos: rentals, inversiones, o un side hustle.",
                ventajas=[
                    "Estabilidad financiera",
                    "Crecimiento patrimonial",
                    "Oportunidades"
                ],
                desventajas=[
                    "Requiere inversión inicial",
                    "Toma tiempo"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Dedica 5 horas semanales a desarrollar una fuente de ingreso adicional.",
                tecnologias=["Inversiones", "Freelancing", "Bienes raíces"]
            ),
            Solucion(
                titulo="Invierte para el futuro",
                descripcion="Si tienes ahorros, invierte en índices diversificados para largo plazo. El interés compuesto es poderoso.",
                ventajas=[
                    "Crecimiento del patrimonio",
                    "Derrota inflación",
                    "Preparación jubilación"
                ],
                desventajas=[
                    "Riesgo de mercado",
                    "Requiere conocimiento"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Empieza con poco en fondos indexados de bajo costo.",
                tecnologias=["Fondos indexados", "ETFs", "BRK", "Planner financiero"]
            ),
        ]
    
    def _generar_soluciones_estudio(self, texto: str) -> list[Solucion]:
        """Genera soluciones para estudio y aprendizaje."""
        return [
            Solucion(
                titulo="Aprendizaje activo",
                descripcion="No solo leas o mires videos. Toma notas, enseña a otros, haz ejercicios, o crea proyectos con lo que aprendes.",
                ventajas=[
                    "Retención 10x mayor",
                    "Comprensión profunda",
                    "Aplicación inmediata"
                ],
                desventajas=[
                    "Más effort",
                    "Menos comfortable"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Después de cada sesión de estudio, explica lo aprendido en voz alta.",
                tecnologias=["Feynman technique", "Anki", "Proyectos propios"]
            ),
            Solucion(
                titulo="Establece rutina de estudio",
                descripcion="Crea un horario fijo de estudio. Es más efectivo estudiar 1 hora diaria que 7 horas un solo día.",
                ventajas=[
                    "Há的形成",
                    "Menos agotamiento",
                    "Aprendizaje consistente"
                ],
                desventajas=[
                    "Requiere consistencia"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Elige un hora específica cada día y bloquéala para estudio.",
                tecnologias=["Calendario", "Temporizador", "Notion"]
            ),
            Solucion(
                titulo="Recursos gratuitos de calidad",
                descripcion="YouTube, Coursera, edX, y Khan Academy tienen contenido gratuito excelente. No necesitas pagar para aprender.",
                ventajas=[
                    "Costo cero",
                    "Variedad enorme",
                    "Calidad a menudo mejor que pago"
                ],
                desventajas=[
                    "Overwhelm de opciones",
                    "Sin estructura a veces"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Elige un curso gratuito y comprométete a completarlo.",
                tecnologias=["YouTube", "Coursera", "edX", "Khan Academy"]
            ),
            Solucion(
                titulo="Aprende haciendo",
                descripcion="La mejor manera de aprender es aplicar. Crea un proyecto real: una app, un blog, un negocio pequeño.",
                ventajas=[
                    "Aprendizaje inmersivo",
                    "Portfolio para currículum",
                    "Experiencia práctica"
                ],
                desventajas=[
                    "Difícil al inicio",
                    "Puede ser abrumador"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Elige un proyecto simple y comprométete a terminarlo en 30 días.",
                tecnologias=["GitHub", "Vercel", "WordPress", "Canva"]
            ),
            Solucion(
                titulo="Encuentra un mentor",
                descripcion="Busca a alguien que ya haya recorrido el camino que quieres seguir. Una guía acelera enormemente tu aprendizaje.",
                ventajas=[
                    "Ahorra tiempo y errores",
                    "Feedback personalizado",
                    "Conexiones y oportunidades"
                ],
                desventajas=[
                    "Difícil encontrar",
                    "Requiere iniciativa"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Identifica 3 personas y envíales un mensaje preguntando si pueden ser tu mentor.",
                tecnologias=["LinkedIn", "Eventos", "Comunidades"]
            ),
        ]
    
    def _generar_desarrollo_personal(self, texto: str) -> list[Solucion]:
        """Genera soluciones para desarrollo personal."""
        return [
            Solucion(
                titulo="Establece metas claras",
                descripcion="Define qué quieres lograr con specificity. 'Mejorarme' no es suficiente. 'Leer 12 libros este año' sí lo es.",
                ventajas=[
                    "Direccion clara",
                    "Motivación",
                    "Medible"
                ],
                desventajas=[
                    "Requiere reflexión"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Escribe 3 metas para los próximos 12 meses usando el formato SMART.",
                tecnologias=["Notas", "Vision board", " journaling"]
            ),
            Solucion(
                titulo="Crea hábitos pequeños",
                descripcion="No intentes cambiar todo de golpe. Un hábito pequeño que mantienes vale más que uno grande que abandonas.",
                ventajas=[
                    "Sostenible",
                    "Efecto compuesto",
                    "Motivador"
                ],
                desventajas=[
                    "Resultados lentos"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Elige UN hábito tiny: leer 1 página, hacer 1 flexión. Aumenta gradualmente.",
                tecnologias=["Habit tracker", "Streaks apps"]
            ),
            Solucion(
                titulo="Bloques de tiempo",
                descripcion="Asigna tiempo específico para tareas importantes. No planificas = no happens.",
                ventajas=[
                    "Protege tu tiempo",
                    "Enfoque profundo",
                    "Productividad aumenta"
                ],
                desventajas=[
                    "Rígido al inicio"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Bloquea 2 horas cada mañana para tu tarea más importante.",
                tecnologias=["Google Calendar", "Notion", "Time blocking"]
            ),
            Solucion(
                titulo="Reflexión semanal",
                descripcion="Dedica 30 minutos semanal a reflexionar: qué funcionó, qué no, qué ajustar. Sin reflexión no hay crecimiento.",
                ventajas=[
                    "Mejora continua",
                    "Autoconocimiento",
                    "Ajustes oportunos"
                ],
                desventajas=[
                    "Requiere disciplina"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Elige un momento cada domingo para reflexionar sobre la semana.",
                tecnologias=["Diario", "Notas", "Preguntas de reflexión"]
            ),
            Solucion(
                titulo="Sale de tu zona de confort",
                descripcion="El crecimiento está justo afuera de tu zona de confort. Haz algo que te dé miedo todas las semanas.",
                ventajas=[
                    "Crecimiento acelerado",
                    "Nuevas oportunidades",
                    "Confianza aumenta"
                ],
                desventajas=[
                    "Incomodidad",
                    "Some riesgos"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Haz una lista de 10 cosas que te dan miedo y elige una para hacer esta semana.",
                tecnologias=["Desafíos", " coaching", "Terapia"]
            ),
        ]
    
    def _generar_soluciones_viajes(self, texto: str) -> list[Solucion]:
        """Genera soluciones para viajes y vacaciones."""
        return [
            Solucion(
                titulo="Viajes locales",
                descripcion="Explora tu propia ciudad o región. Hay lugares increíbles cerca de ti que nunca has visitado.",
                ventajas=[
                    "Más barato",
                    "Menos planificación",
                    "Sorpresas locales"
                ],
                desventajas=[
                    "Puede parecer menos 'exótico'"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Investiga 3 destinos a menos de 2 horas de tu casa.",
                tecnologias=["TripAdvisor", "Google Maps", "Blogs de viajes locales"]
            ),
            Solucion(
                titulo="Viajes fuera de temporada",
                descripcion="Viaja en temporada baja para evitar multitudes y ahorrar significativamente en vuelos y hoteles.",
                ventajas=[
                    "Mucho más barato",
                    "Menos turistas",
                    "Experiencia más auténtica"
                ],
                desventajas=[
                    "Some atractivos pueden estar cerrados",
                    "Clima menos predecible"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Investiga cuándo es temporada baja para tu destino soñado.",
                tecnologias=["Skyscanner", "Google Flights", "Blogs de viajes"]
            ),
            Solucion(
                titulo="Alojamiento alternativas",
                descripcion="Usa Airbnb, Booking, o hostels en lugar de hoteles. Es más barato y a menudo más auténtico.",
                ventajas=[
                    "Ahorro significativo",
                    "Experiencia local",
                    "Más espacio"
                ],
                desventajas=[
                    "Menos servicios",
                    "Requiere más gestión"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Compara precios de hotel vs Airbnb para tu próximo destino.",
                tecnologias=["Airbnb", "Booking", "Hostelworld", "Couchsurfing"]
            ),
            Solucion(
                titulo="Viaje flexible",
                descripcion="Sé flexible con fechas y destinos. Los vuelos más baratos están en días y horarios improbables.",
                ventajas=[
                    "Ahorro extremo",
                    "Aventura"
                ],
                desventajas=[
                    "Menos control",
                    "Puede ser agotador"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Usa herramientas de 'explore' en Google Flights para ver precios por mes.",
                tecnologias=["Google Flights", "Skyscanner", "Hopper"]
            ),
            Solucion(
                titulo="Viaje experiencial",
                descripcion="En lugar de ver lugares, vive experiencias: voluntariado, cursos locales, vidas con familias.",
                ventajas=[
                    "Experiencia profunda",
                    "Conexiones humanas",
                    "Memorias únicas"
                ],
                desventajas=[
                    "Más preparación",
                    "Puede ser desafiante"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Busca experiencias locales en Airbnb Experiences o Civitatis.",
                tecnologias=["Airbnb Experiences", "Civitatis", "Workaway", "Helpx"]
            ),
        ]
    
    def _generar_soluciones_entretenimiento(self, texto: str) -> list[Solucion]:
        """Genera soluciones para entretenimiento."""
        return [
            Solucion(
                titulo="Explora nuevos hobbies",
                descripcion="Aprende algo nuevo: instrumento, pintura, cocina, fotografía. Los hobbies enriquecen tu vida y reducen estrés.",
                ventajas=[
                    "Creatividad",
                    "Reducción estrés",
                    "Nuevas habilidades"
                ],
                desventajas=[
                    "Tiempo de aprendizaje"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Elige un hobby que siempre te ha interesado y busca un curso para empezar.",
                tecnologias=["YouTube", "Skillshare", "Clases locales"]
            ),
            Solucion(
                titulo="Lectura variada",
                descripcion="Lee de todo: ficción, no ficción, ciencia, historia. Los libros abren mundos y minds.",
                ventajas=[
                    "Amplía perspectiva",
                    "Conocimiento",
                    "Entretenimiento rico"
                ],
                desventajas=[
                    "Toma tiempo"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Únete a un club de lectura o usa Goodreads para descubrir recomendaciones.",
                tecnologias=["Kindle", "Goodreads", "Audible", "Bibliotecas"]
            ),
            Solucion(
                titulo="Actividad física divertida",
                descripcion="El ejercicio no tiene que ser aburrido: baila, sube montañas, nada, juega deportes.",
                ventajas=[
                    "Salud + diversion",
                    "Socialización",
                    "Menos esfuerzo percibido"
                ],
                desventajas=[
                    "Depende de disponibilidad"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Prueba 3 actividades físicas diferentes hasta encontrar una que te encanta.",
                tecnologias=["Clases", "Deportes", "Naturaleza"]
            ),
            Solucion(
                titulo="Proyectos creativos",
                descripcion="Crea algo: escribe, diseña, programa, construye. La creatividad es profundamente satisfactoria.",
                ventajas=[
                    "Expresión personal",
                    "Logro tangible",
                    "Desarrollo de skills"
                ],
                desventajas=[
                    "Requiere iniciación",
                    "Crítica potencial"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Elige un proyecto pequeño y comprométete a terminarlo en 1 mes.",
                tecnologias=["Canva", "Notion", "GitHub", "Medium"]
            ),
            Solucion(
                titulo="Tiempo sin pantallas",
                descripcion="Desconecta regularmente. Camina, cocina, medita, o simplemente estar sin устройство.",
                ventajas=[
                    "Reducción ansiedad",
                    "Presencia",
                    "Creatividad"
                ],
                desventajas=[
                    "FOMO inicial"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Planifica 1 hora diaria sin teléfono esta semana.",
                tecnologias=["Naturaleza", "Juegos de mesa", "Cocina", "Manualidades"]
            ),
        ]
    
    def _generar_soluciones_alimentacion(self, texto: str) -> list[Solucion]:
        """Genera soluciones para alimentación."""
        return [
            Solucion(
                titulo="Cocina en casa",
                descripcion="Cocinar en casa es más sano, barato y satisfactorio. Empieza con recetas simples.",
                ventajas=[
                    "Más sano",
                    "Más barato",
                    "Control de ingredientes"
                ],
                desventajas=[
                    "Tiempo de preparación",
                    "Requiere habilidades"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Elige 3 recetas simples y aprende a hacerlas bien.",
                tecnologias=["YouTube", "Cookpad", "Libros de cocina"]
            ),
            Solucion(
                titulo="Meal prep",
                descripcion="Prepara comida para toda la semana el fin de semana. Ahorras tiempo y evitas decisiones diarias.",
                ventajas=[
                    "Ahorro de tiempo",
                    "Más sano",
                    "Más barato"
                ],
                desventajas=[
                    "Inversión inicial de tiempo",
                    "Puede aburrir"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Dedica 2 horas el domingo a preparar tu comida de la semana.",
                tecnologias=["Recipientes", "Planificador", "Recetas"]
            ),
            Solucion(
                titulo="Explora cocina local",
                descripcion="Prueba restaurantes locales, mercados de comida, y street food. Es cultural y delicioso.",
                ventajas=[
                    "Experiencia cultural",
                    "Soporte local",
                    "Descubrimiento"
                ],
                desventajas=[
                    "Calidad variable",
                    "Higiene no garantizada"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Busca el mercado local o street food más cercano y pruébalo.",
                tecnologias=["Yelp", "TripAdvisor", "Google Maps"]
            ),
            Solucion(
                titulo="Delivery saludable",
                descripcion="Si pides delivery, elige opciones saludables: ensaladas, bowls, sushi, o opciones de restaurantes的健康.",
                ventajas=[
                    "Conveniente",
                    "Opciones saludables existen",
                    "Variedad"
                ],
                desventajas=[
                    "Más caro",
                    "Menos control"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Guarda 3 opciones saludables en tus apps de delivery.",
                tecnologias=["Rappi", "Uber Eats", "PedidosYa"]
            ),
            Solucion(
                titulo="Comida congelada saludable",
                descripcion="Ten opciones congeladas saludables para días ocupados: verduras, proteínas, platos preparados.",
                ventajas=[
                    "Conveniente",
                    "Menos desperdicio",
                    "Saludable"
                ],
                desventajas=[
                    "Menos fresco",
                    "Algunas opciones procesadas"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Llena tu congelador con opciones saludables para emergencias.",
                tecnologias=["Supermercados", "Mercados"]
            ),
        ]
    
    def _generar_soluciones_tecnico(self, texto: str) -> list[Solucion]:
        """Genera soluciones para problemas técnicos."""
        return [
            Solucion(
                titulo="Reiniciar dispositivo",
                descripcion="El 80% de los problemas técnicos se resuelven reiniciando. Apaga y enciende.",
                ventajas=[
                    "Soluciona muchos problemas",
                    "Rápido",
                    "Sin costo"
                ],
                desventajas=[
                    "No resuelve problemas complejos"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.TECNOLOGIA,
                recomendacion="Antes de hacer cualquier cosa, reinicia tu dispositivo.",
                tecnologias=["Reinicio"]
            ),
            Solucion(
                titulo="Buscar el error",
                descripcion="Copia el mensaje de error y búscalo en Google. Casi siempre alguien más tuvo el mismo problema.",
                ventajas=[
                    "Solución específica",
                    "Gratis",
                    "Inmediato"
                ],
                desventajas=[
                    "Requiere búsqueda",
                    "Soluciones pueden estar desactualizadas"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.TECNOLOGIA,
                recomendacion="Copia el mensaje de error exacto y búscalo entre comillas.",
                tecnologias=["Google", "Stack Overflow", "Foros"]
            ),
            Solucion(
                titulo="Actualizar software",
                descripcion="Mantén tu sistema y aplicaciones actualizados. Las actualizaciones corrigen errores y security.",
                ventajas=[
                    "Seguridad",
                    "Nuevas funciones",
                    "Corrección de errores"
                ],
                desventajas=[
                    "Ocasionalmente rompen cosas",
                    "Toma tiempo"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.TECNOLOGIA,
                recomendacion="Configura actualizaciones automáticas.",
                tecnologias=["Windows Update", "Mac App Store", "Play Store"]
            ),
            Solucion(
                titulo="Hacer backup",
                descripcion="Siempre tienes backup de tus datos importantes. Usa la nube o un disco externo.",
                ventajas=[
                    "Protección de datos",
                    "Paz mental",
                    "Recuperación fácil"
                ],
                desventajas=[
                    "Tiempo inicial",
                    "Costo si usas nube"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.TECNOLOGIA,
                recomendacion="Configura backup automático a la nube hoy.",
                tecnologias=["Google Drive", "Dropbox", "OneDrive", "Time Machine"]
            ),
            Solucion(
                titulo="Buscar ayuda profesional",
                descripcion="Si ya intentaste todo y no funciona, busca ayuda técnica profesional.",
                ventajas=[
                    "Solución garantizada",
                    "Ahorra tiempo",
                    "Experiencia"
                ],
                desventajas=[
                    "Costo",
                    "Dependencia"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.TECNOLOGIA,
                recomendacion="Busca un técnico de confianza o lleva tu dispositivo a una tienda.",
                tecnologias=["Soporte técnico", "Tiendas especializadas"]
            ),
        ]

    def _detectar_info_auto(self, texto: str) -> dict:
        """Detecta información específica del auto en el texto del usuario."""
        texto_lower = texto.lower()
        
        marcas = [
            "toyota", "honda", "ford", "chevrolet", "nissan", "mazda", "bmw",
            "mercedes", "audi", "volkswagen", "kia", "hyundai", "subaru",
            "mitsubishi", "jeep", "ram", "gmc", "dodge", "lexus", "porsche",
            "tesla", "byd", "volvo", "peugeot", "renault", "fiat", "citroen"
        ]
        
        modelos_comunes = [
            "corolla", "civic", "accord", "camry", "mustang", "camaro",
            "altima", "sentra", " Civic", "corolla", "spark", "beat",
            "fiesta", "focus", "ecosport", "escape", "explorer", "edge"
        ]
        
        anios = list(range(2025, 2000, -1))
        anios_str = [str(a) for a in anios]
        
        tipo_busqueda = "general"
        if any(p in texto_lower for p in ["precio", "costo", "cuanto", "vale"]):
            tipo_busqueda = "precio"
        elif any(p in texto_lower for p in ["comparar", "comparacion", "vs", "diferencia"]):
            tipo_busqueda = "comparacion"
        elif any(p in texto_lower for p in ["spec", "caracteristica", "motor", "especificacion"]):
            tipo_busqueda = "especificaciones"
        elif any(p in texto_lower for p in ["usado", "seminuevo", "segunda mano"]):
            tipo_busqueda = "usado"
        
        marca_detectada = None
        for marca in marcas:
            if marca in texto_lower:
                marca_detectada = marca
                break
        
        modelo_detectado = None
        for modelo in modelos_comunes:
            if modelo.lower() in texto_lower:
                modelo_detectado = modelo.lower()
                break
        
        anio_detectado = None
        for anio in anios_str:
            if anio in texto:
                anio_detectado = anio
                break
        
        return {
            "marca": marca_detectada,
            "modelo": modelo_detectado,
            "anio": anio_detectado,
            "tipo_busqueda": tipo_busqueda,
            "tiene_auto": bool(marca_detectada or modelo_detectado)
        }

    def _generar_soluciones_autos(self, texto: str) -> list[Solucion]:
        """Genera soluciones para autos y vehículos."""
        info_auto = self._detectar_info_auto(texto)
        
        if not info_auto["tiene_auto"]:
            return self._generar_soluciones_autos_generales(texto)
        
        # PRIMERO: Buscar en la web (SerpAPI)
        try:
            busqueda_service = get_busqueda_web_service()
            resultados = busqueda_service.buscar_informacion_auto(
                marca=info_auto["marca"] or "",
                modelo=info_auto["modelo"] or "",
                anio=info_auto["anio"],
                tipo_busqueda=info_auto["tipo_busqueda"]
            )
            
            if resultados.get("resultados"):
                return self._crear_soluciones_desde_busqueda(
                    texto, info_auto, resultados
                )
        except Exception as e:
            from infrastructure.logging.structured_logging import app_logger
            app_logger.warning("Búsqueda web falló para autos", error=str(e))
        
        # FALLBACK: Buscar en base de conocimientos local
        try:
            rag_service = get_rag_service()
            contexto_rag = rag_service.buscar_informacion(
                f"{info_auto.get('marca', '')} {info_auto.get('modelo', '')}",
                top_k=3
            )
            
            if contexto_rag:
                return self._crear_soluciones_desde_rag(
                    texto, info_auto, contexto_rag
                )
        except Exception as e:
            from infrastructure.logging.structured_logging import app_logger
            app_logger.warning("RAG falló para autos", error=str(e))
        
        return self._generar_soluciones_autos_generales(texto)
    
    def _crear_soluciones_desde_rag(
        self, 
        texto: str, 
        info_auto: dict, 
        contexto: str
    ) -> list[Solucion]:
        """Crea soluciones basadas en la base de conocimientos RAG."""
        marca = info_auto.get("marca", "").title()
        modelo = info_auto.get("modelo", "").title()
        anio = info_auto.get("anio", "")
        
        auto_nombre = f"{marca} {modelo}" if marca and modelo else "el auto"
        if anio:
            auto_nombre += f" {anio}"
        
        soluciones = []
        
        if info_auto["tipo_busqueda"] == "precio":
            soluciones.append(Solucion(
                titulo=f"💰 Precio de {auto_nombre}",
                descripcion=contexto,
                ventajas=[
                    "Información de la base de conocimientos",
                    "Precios actualizados",
                    "Múltiples versiones disponibles"
                ],
                desventajas=[
                    "Verificar disponibilidad local"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Visita el concesionario para cotización exacta.",
                tecnologias=["Base de conocimientos"]
            ))
        else:
            soluciones.append(Solucion(
                titulo=f"🚗 Información de {auto_nombre}",
                descripcion=contexto,
                ventajas=[
                    "Información verificada",
                    "Especificaciones completas"
                ],
                desventajas=[
                    "Verificar disponibilidad"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Consulta en concesionario para más detalles.",
                tecnologias=["Base de conocimientos"]
            ))
        
        soluciones.append(Solucion(
            titulo="🔍 Búsqueda online",
            descripcion="Para precios actualizados y promociones, busca en línea:",
            ventajas=[
                "Precios de concessionarias",
                "Ofertas del mes"
            ],
            desventajas=[
                "Requiere verificación presencial"
            ],
            complejidad=ComplexityLevel.BAJA,
            categoria=SolutionCategory.NEGOCIOS,
            recomendacion="Busca en sitios de concessionarias oficiales.",
            tecnologias=["Web"]
        ))
        
        return soluciones
    
    def _crear_soluciones_desde_busqueda(
        self, 
        texto: str, 
        info_auto: dict, 
        resultados: dict
    ) -> list[Solucion]:
        """Crea soluciones personalizadas basadas en resultados de búsqueda web."""
        marca = info_auto.get("marca", "").title()
        modelo = info_auto.get("modelo", "").title()
        anio = info_auto.get("anio", "2024")
        
        auto_nombre = f"{marca} {modelo} {anio}" if marca and modelo else "el auto"
        
        descripcion_busqueda = ""
        fuentes = resultados.get("fuentes", [])
        
        for r in resultados.get("resultados", [])[:3]:
            if r.get("descripcion"):
                descripcion_busqueda += f"- {r['descripcion']}\n"
        
        soluciones = []
        
        if info_auto["tipo_busqueda"] == "precio":
            soluciones.append(Solucion(
                titulo=f"💰 Precio de {auto_nombre}",
                descripcion=f"Información de precios encontrada:\n\n{descripcion_busqueda[:500]}",
                ventajas=[
                    "Información actualizada de precios",
                    "Múltiples fuentes consultadas"
                ],
                desventajas=[
                    "Los precios pueden variar por ubicación"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion=f"Visita las fuentes para ver precios actualizados en tu zona.",
                tecnologias=fuentes[:5] if fuentes else ["Búsqueda web"]
            ))
        
        elif info_auto["tipo_busqueda"] == "comparacion":
            soluciones.append(Solucion(
                titulo=f"⚔️ Comparación de {auto_nombre}",
                descripcion=f"Información de comparación encontrada:\n\n{descripcion_busqueda[:500]}",
                ventajas=[
                    "Comparativa de características",
                    "Opiniones de expertos"
                ],
                desventajas=[
                    "Recomendable probar ambos autos"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Agenda pruebas de manejo de ambos autos.",
                tecnologias=fuentes[:5] if fuentes else ["Búsqueda web"]
            ))
        
        else:
            soluciones.append(Solucion(
                titulo=f"🚗 Información de {auto_nombre}",
                descripcion=f"Resultados de búsqueda:\n\n{descripcion_busqueda[:500]}",
                ventajas=[
                    "Información actualizada",
                    "Múltiples fuentes"
                ],
                desventajas=[
                    "Verificar disponibilidad local"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Consulta los enlaces para más detalles.",
                tecnologias=fuentes[:5] if fuentes else ["Búsqueda web"]
            ))
        
        soluciones.append(Solucion(
            titulo="📋 Próximos pasos",
            descripcion="Para tomar una decisión informada:",
            ventajas=[
                "Visitar concesionaria",
                "Solicitar prueba de manejo",
                "Comparar financiamiento"
            ],
            desventajas=[
                "Requiere tiempo"
            ],
            complejidad=ComplexityLevel.MEDIA,
            categoria=SolutionCategory.NEGOCIOS,
            recomendacion="No te apresures, investiga y compara.",
            tecnologias=fuentes[:3] if fuentes else []
        ))
        
        return soluciones
    
    def _generar_soluciones_autos_generales(self, texto: str) -> list[Solucion]:
        """Genera soluciones generales para autos cuando no se detecta uno específico."""
        return [
            Solucion(
                titulo="Comprar auto nuevo vs usado",
                descripcion="Evalúa si te conviene un auto nuevo (garantía, tecnología) o usado (menor depreciación). Investiga el mercado local.",
                ventajas=[
                    "Nuevo: garantia total",
                    "Usado: menor costo inicial",
                    "Mas opciones en tu presupuesto"
                ],
                desventajas=[
                    "Nuevo: depreciacion rapida",
                    "Usado: posibles problemas ocultos"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Haz una lista de tus prioridades: presupuesto, uso, tecnologia.",
                tecnologias=["MercadoLibre", "Autocosmos", " Kelley Blue Book"]
            ),
            Solucion(
                titulo="Mantenimiento preventivo",
                descripcion="Sigue el calendario de mantenimiento: cambio de aceite, filtros, llantas. Previene fallas mayores.",
                ventajas=[
                    "Ahorro a largo plazo",
                    "Mayor vida util",
                    "Mas valor de reventa"
                ],
                desventajas=[
                    "Costo periodicocional",
                    "Requiere tiempo"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Lleva un registro de mantenimiento y no omitas los cambios de aceite.",
                tecnologias=["Manual del propietario", "YouTube tutoriales"]
            ),
            Solucion(
                titulo="Vender tu auto",
                descripcion="Prepara tu auto: limpieza profunda, documentacion al dia, fotos profesionales. Precio competitivo.",
                ventajas=[
                    "Mas dinero por tu auto",
                    "Venta mas rapida"
                ],
                desventajas=[
                    "Tiempo de preparacion",
                    "Negociacion"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Investiga precios de modelos similares en tu zona antes de poner precio.",
                tecnologias=["Facebook Marketplace", "Paginas de autos", "Colegiado"]
            ),
            Solucion(
                titulo="Financiamiento y seguros",
                descripcion="Compara tasas de financiamiento y cotiza varios seguros. El credito puede variar muchisimo entre entidades.",
                ventajas=[
                    "Ahorro significativo",
                    "Opciones flexibles"
                ],
                desventajas=[
                    "Complicado comparar",
                    "Compromiso a largo plazo"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Cotiza al menos 3 entidades diferentes antes de decidir.",
                tecnologias=["Bancos", "Companias de seguros", "Comparadores online"]
            ),
            Solucion(
                titulo="Elegir el auto adecuado",
                descripcion="Define tu uso principal: ciudad, carretera, familia, trabajo. No todos los autos sirven para todo.",
                ventajas=[
                    "satisfaccion a largo plazo",
                    "Ahorro en combustible",
                    "Seguridad apropiada"
                ],
                desventajas=[
                    "Requiere investigacion"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Haz una lista de tus necesidades y priorizalas antes de ver autos.",
                tecnologias=["Reviews", "Videos comparativos", "Foros"]
            ),
            Solucion(
                titulo="Autos electricos e hibridos",
                descripcion="Considera un auto electrico o hibrido. Menor costo de combustible, menos mantenimiento, cero emisiones.",
                ventajas=[
                    "Ahorro en combustible",
                    "Menos mantenimiento",
                    "Cero o bajas emisiones",
                    "Tecnologia de vanguardia"
                ],
                desventajas=[
                    "Costo inicial mas alto",
                    "Carga electrica limitada",
                    "Infraestructura de carga"
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Investiga incentivos fiscales y costos de carga en tu zona.",
                tecnologias=["Tesla", "BYD", "Toyota Hibridos", "Volkswagen ID", "Hyundai Electric"]
            ),
            Solucion(
                titulo="SUVs y crossovers",
                descripcion="Ideales para familias y quien busca espacio. Ofrecen altura, espacio y versatilidad.",
                ventajas=[
                    "Espacio para pasajeros y carga",
                    "Altura de conduccion",
                    "Versatilidad"
                ],
                desventajas=[
                    "Mayor consumo de combustible",
                    "Mas grandes para estacionar"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Busca SUVs con buen rating de seguridad y economia de combustible.",
                tecnologias=["Toyota RAV4", "Honda CR-V", "Mazda CX-5", "Ford Explorer"]
            ),
            Solucion(
                titulo="Pickups y camionetas",
                descripcion="Para trabajo pesado o estilo de vida activo. Capacidad de carga y traccion 4x4.",
                ventajas=[
                    "Capacidad de carga maxima",
                    "Traccion 4x4",
                    "Durabilidad"
                ],
                desventajas=[
                    "Consumo alto de combustible",
                    "Dificiles de estacionar en ciudad"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Evalua si realmente necesitas la capacidad de carga o solo el estilo.",
                tecnologias=["Ford F-150", "Chevrolet Silverado", "Ram 1500", "Toyota Tacoma"]
            ),
            Solucion(
                titulo="Autos deportivos",
                descripcion="Para quienes priorizan rendimiento y emocion. Potencia, velocidad y manejo.",
                ventajas=[
                    "Rendimiento excepcional",
                    "Diseño atractivo",
                    "Experiencia de conduccion"
                ],
                desventajas=[
                    "Costo muy alto",
                    "Combustible costoso",
                    "Seguro elevado"
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Considera usado - los deportivos pierden valor rapido.",
                tecnologias=["Porsche 911", "Chevrolet Corvette", "Ford Mustang", "Dodge Charger"]
            ),
            Solucion(
                titulo="Autos economicos",
                descripcion="Autos compactos con buen rendimiento de combustible. Ideales para ciudad.",
                ventajas=[
                    "Excelente economia de combustible",
                    "Facil de estacionar",
                    "Costo de mantenimiento bajo"
                ],
                desventajas=[
                    "Espacio limitado",
                    "Menos potencia"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Son ideales para primera vez o presupuesto ajustado.",
                tecnologias=["Toyota Corolla", "Honda Civic", "Nissan Sentra", "Hyundai Accent"]
            ),
            Solucion(
                titulo="Conducir seguro",
                descripcion="Tecnicas y habitos para conducir seguro: velocidad, distancias, distracciones.",
                ventajas=[
                    "Evitas accidentes",
                    "Ahorras combustible",
                    "Evitas multas"
                ],
                desventajas=[
                    "Requiere disciplina"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Mantén distancia, no uses telefono y respeta limites de velocidad.",
                tecnologias=["Cursos de manejo", "Dashcam", "Apps de conducir"]
            ),
            Solucion(
                titulo="Tramites y documentacion",
                descripcion="Mantén al dia: licencia, tarjeta de circulacion, verificaciones, seguro.",
                ventajas=[
                    "Evitas multas",
                    "Legalidad total",
                    "Tranquilidad"
                ],
                desventajas=[
                    "Tramites tediosos"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Configura alertas para renewals de licencia y seguro.",
                tecnologias=["Gobierno local", "Portales de tramites", "Apps oficiales"]
            ),
        ]

    def _generar_soluciones_musica(self, texto: str) -> list[Solucion]:
        """Genera soluciones para música."""
        return [
            Solucion(
                titulo="Mejores apps de streaming",
                descripcion="Spotify, Apple Music, YouTube Music, Amazon Music. Cada una tiene pros y contras.",
                ventajas=[
                    "Miles de canciones",
                    "Personalizacion",
                    "Portabilidad"
                ],
                desventajas=[
                    "Suscripcion mensual",
                    "No todas las canciones estan everywhere"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Spotify tiene mejor algoritmo. Apple Music tiene mejor calidad.",
                tecnologias=["Spotify Premium", "Apple Music", "YouTube Music", "Amazon Music"]
            ),
            Solucion(
                titulo="Generos musicales populares",
                descripcion="Reggaeton, trap, pop Latino, urbano lideran. K-pop y anime music en ascenso.",
                ventajas=[
                    "Estas al dia",
                    "Facil encontrar nueva musica",
                    "Playlists actualizadas"
                ],
                desventajas=[
                    "Mucha competencia"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Explora charts de Spotify y Billboard para estar al dia.",
                tecnologias=["Spotify Charts", "Billboard", "Apple Music Charts"]
            ),
            Solucion(
                titulo="Aprender guitarra",
                descripcion="Empieza con guitarra acustica o electrica. YouTube tiene cursos gratuitos para principiantes.",
                ventajas=[
                    "Instrumento versatil",
                    "Portatil",
                    "Comunidad grande"
                ],
                desventajas=[
                    "Dedos duelen al inicio",
                    "Requiere practica diaria"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Compra una guitarra economica y sigue tutoriales de JustinGuitar.",
                tecnologias=["JustinGuitar", "Fender", "Yamaha", "YouTube"]
            ),
            Solucion(
                titulo="Aprender piano",
                descripcion="El piano es ideal para teoria musical. Apps como Simply Piano hacen facil empezar.",
                ventajas=[
                    "Fundamentos musicales",
                    "Teoria facilmente",
                    "Solo o acompanamiento"
                ],
                desventajas=[
                    "Equipo costoso",
                    "Espacio requerido"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Empieza con un piano digital economico o teclado.",
                tecnologias=["Simply Piano", "Yousician", "Casio", "Yamaha P-45"]
            ),
            Solucion(
                titulo="Producir musica",
                descripcion="Crea tus propias canciones con DAWs. Desde basico hasta professional.",
                ventajas=[
                    "Creatividad sin limites",
                    "Potencial de carrera",
                    "Expresion personal"
                ],
                desventajas=[
                    "Curva de aprendizaje pronunciada",
                    "Equipo puede costar"
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Empieza con GarageBand o FL Studio free.",
                tecnologias=["FL Studio", "GarageBand", "Ableton Live", "Logic Pro"]
            ),
            Solucion(
                titulo="Conciertos y festivales",
                descripcion="Vive la musica en vivo: Vive Latino, Coachella, Rock in Rio, Tomorrowland.",
                ventajas=[
                    "Experiencia unica",
                    "Energia de la multitud",
                    "Descubres artistas"
                ],
                desventajas=[
                    "Costo alto",
                    "Mucho calor o frio"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Compra tickets temprano - se agotan rapido y suben de precio.",
                tecnologias=["Ticketmaster", "Eventbrite", "AXS", "Facebook Events"]
            ),
            Solucion(
                titulo="K-Pop",
                descripcion="BTS, BLACKPINK, SEVENTEEN, NEWJEANS, Stray Kids lideran el genero.",
                ventajas=[
                    "Comunidad enorme",
                    "Musica de calidad",
                    "Contenido diverso"
                ],
                desventajas=[
                    "Idolatria excesiva",
                    "Toxicidad en fans"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Explora mas alla de BTS - hay muchas bandas excelentes.",
                tecnologias=["Spotify", "YouTube", "V Live", "Weverse"]
            ),
            Solucion(
                titulo="Urbano Latino",
                descripcion="Bad Bunny, J Balvin, KAROL G, Feid, Myke Towers lideran el reggaeton y trap.",
                ventajas=[
                    "Musica actual",
                    "Energia positiva",
                    "Para escuchar y bailar"
                ],
                desventajas=[
                    "Letras no siempre apropiadas"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Combina viejo y nuevo - escucha clasicos y nuevos exitos.",
                tecnologias=["Spotify", "Apple Music", "YouTube"]
            ),
            Solucion(
                titulo="Rock y metal",
                descripcion="Foo Fighters, Metallica, Linkin Park, Deftones, Ghost. Desde clasico hasta alternativo.",
                ventajas=[
                    "Musica con profundidad",
                    "Letras significativas",
                    "Comunidad fiel"
                ],
                desventajas=[
                    "Genero en declive comercial"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Explora bandas independientes tambien - hay talento enorme.",
                tecnologias=["Spotify", "Bandcamp", "YouTube", "Apple Music"]
            ),
            Solucion(
                titulo="Crear playlist perfecta",
                descripcion="Organiza musica por mood, actividad o momento. Mejora cualquier experiencia.",
                ventajas=[
                    "Personalizacion total",
                    "Facil de usar",
                    "Compartes con amigos"
                ],
                desventajas=[
                    "Tiempo inicial"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Crea playlists para: gym, trabajo, estudio, manejar, relax, fiesta.",
                tecnologias=["Spotify", "Apple Music", "YouTube Music"]
            ),
            Solucion(
                titulo="Vinilos y coleccionismo",
                descripcion="Revive el vinilo. Sonido analogico unico y coleccion valiosa.",
                ventajas=[
                    "Sonido superior",
                    "Arte de portada",
                    "Experiencia tactil"
                ],
                desventajas=[
                    "Costoso",
                    "Requiere equipo"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Empieza con clasicos economicos de segunda mano.",
                tecnologias=["Amazon", "Discogs", "Tiendas de vinilos", "MercadoLibre"]
            ),
        ]

    def _generar_soluciones_videojuegos(self, texto: str) -> list[Solucion]:
        """Genera soluciones para videojuegos."""
        return [
            Solucion(
                titulo="Mejores juegos PS5",
                descripcion="Spider-Man 2, God of War Ragnarok, FF7 Rebirth, Horizon Forbidden West.",
                ventajas=[
                    "Exclusivos increibles",
                    "Graficos next-gen",
                    "Experiencias unicas"
                ],
                desventajas=[
                    "Precio de consola alto",
                    "Exclusivos limitados"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Consigue PS5 Slim si puedes - mejor valor.",
                tecnologias=["PlayStation 5", "PS5 Slim", "DualSense", "PS Plus"]
            ),
            Solucion(
                titulo="Mejores juegos Xbox",
                descripcion="Starfield, Forza Horizon 5, Halo Infinite, Gears of War, Hi-Fi Rush.",
                ventajas=[
                    "Game Pass amazing",
                    "Mejor hardware",
                    "Retrocompatibilidad"
                ],
                desventajas=[
                    "Menos exclusivos"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Game Pass Ultimate vale cada centavo.",
                tecnologias=["Xbox Series X", "Xbox Series S", "Game Pass", "xCloud"]
            ),
            Solucion(
                titulo="Nintendo Switch - Mejores juegos",
                descripcion="Zelda TOTK, Mario Odyssey, Animal Crossing, Smash Bros, Pokemon.",
                ventajas=[
                    "Juegos familiares",
                    "Portatil y TV",
                    "Exclusivos unicos"
                ],
                desventajas=[
                    "Graficos inferiores",
                    "Sin multiplataformas recientes"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Switch OLED tiene la mejor pantalla para jugar portable.",
                tecnologias=["Switch", "Switch OLED", "Switch Lite", "NSO"]
            ),
            Solucion(
                titulo="PC Gaming - Setup completo",
                descripcion="PC gaming ofrece los mejores graficos y mods. Mas caro al inicio, barato a la larga.",
                ventajas=[
                    "Mods y personalizacion",
                    "Mejores graficos",
                    "Juegos mas baratos"
                ],
                desventajas=[
                    "Costo inicial alto",
                    "Actualizaciones constantes"
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Empieza con build economico y mejora gradualmente.",
                tecnologias=["Steam", "Epic Games", "Nvidia RTX", "AMD Ryzen"]
            ),
            Solucion(
                titulo="Mejores juegos gratuitos",
                descripcion="Fortnite, Valorant, Genshin Impact, LoL, Warzone, Apex Legends, Destiny 2.",
                ventajas=[
                    "Costo cero",
                    "Comunidades enormes",
                    "Calidad free-to-play"
                ],
                desventajas=[
                    "Microtransacciones",
                    "Curva de aprendizaje"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Prueba varios hasta encontrar tu juego.",
                tecnologias=["Epic Games", "Steam", "Riot Games", "miHoYo"]
            ),
            Solucion(
                titulo="Juegos cooperativos",
                descripcion="Juega con amigos: It Takes Two, Overcooked, Valheim, Don't Starve.",
                ventajas=[
                    "Diversion social",
                    "Trabajo en equipo",
                    "Memorias compartidas"
                ],
                desventajas=[
                    "Coordinar horarios"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="It Takes Two es obligatorio para parejas o amigos.",
                tecnologias=["Steam", "PlayStation", "Xbox", "Nintendo Switch"]
            ),
            Solucion(
                titulo="RPGs recomendados",
                descripcion="Elden Ring, Baldur's Gate 3, Witcher 3, Final Fantasy, Persona.",
                ventajas=[
                    "Historias profundas",
                    "Muchas horas de juego",
                    "Personalizacion"
                ],
                desventajas=[
                    "Pueden ser muy largos"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Baldur's Gate 3 es el nuevo estandar de RPGs.",
                tecnologias=["Steam", "PlayStation", "Xbox"]
            ),
            Solucion(
                titulo="Juegos indie - Joyas ocultas",
                descripcion="Hollow Knight, Celeste, Hades, Stardew Valley, Dead Cells.",
                ventajas=[
                    "Creatividad sin limites",
                    "Precios razonables",
                    "Experiencias unicas"
                ],
                desventajas=[
                    "Graficos simples"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Stardew Valley y Hades son perfectos para comenzar.",
                tecnologias=["Steam", "Switch", "Humble Bundle"]
            ),
            Solucion(
                titulo="Esports y competencias",
                descripcion="League of Legends, Valorant, CS2, Dota 2. Juega competitivo o solo especta.",
                ventajas=[
                    "Comunidad global",
                    "Carrera profesional",
                    "Espectaculo"
                ],
                desventajas=[
                    "Toxicidad",
                    "Mucho tiempo para mejorar"
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Empieza en ranked solo cuando domines lo basico.",
                tecnologias=["Twitch", "YouTube Gaming", "Discord"]
            ),
            Solucion(
                titulo="Retro gaming - Clasicos",
                descripcion="Revive SNES, N64, PS1, PS2 con emuladores o remakes.",
                ventajas=[
                    "Nostalgia pura",
                    "Juegos iconicos",
                    "Barato o gratis"
                ],
                desventajas=[
                    "Legalidad variable",
                    "Configuracion"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Nintendo Switch Online tiene clasicos de NES, SNES, N64.",
                tecnologias=["RetroArch", "EmuDeck", "NSO", "PS Plus Classics"]
            ),
            Solucion(
                titulo="Game Pass vs PS Plus",
                descripcion="Game Pass tiene mas juegos, PS Plus tiene mejores exclusivos.",
                ventajas=[
                    "Ambos tienen pros",
                    "Variedad de precios",
                    "Juegos nuevos"
                ],
                desventajas=[
                    "Suscripciones se acumulan"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Game Pass Ultimate es la mejor oferta en gaming.",
                tecnologias=["Xbox Game Pass", "PS Plus", "EA Play"]
            ),
            Solucion(
                titulo="Mejores juegos mobiles",
                descripcion="Genshin, Honkai, CODM, Clash Royale, Brawl Stars. Gaming en el telefono.",
                ventajas=[
                    "Juega en cualquier lugar",
                    "Gratis o barato",
                    "Comunidad enorme"
                ],
                desventajas=[
                    "Controles limitados",
                    "Bateria",
                    "Pantalla pequena"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Genshin y Honkai tienen calidad consola en mobile.",
                tecnologias=["iOS", "Android", "App Store", "Play Store"]
            ),
            Solucion(
                titulo="Simuladores de vida",
                descripcion="The Sims 4, Stardew Valley, Animal Crossing, Palia.",
                ventajas=[
                    "Relajante",
                    "Creativo",
                    "Muchas horas"
                ],
                desventajas=[
                    "Puede volverse repetitivo"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Stardew Valley tiene la mejor relacion precio-disfrute.",
                tecnologias=["Steam", "Switch", "iOS", "Android"]
            ),
        ]

    def _generar_soluciones_trabajo(self, texto: str) -> list[Solucion]:
        """Genera soluciones para trabajo y empleo."""
        return [
            Solucion(
                titulo="Buscar trabajo efectivo",
                descripcion="LinkedIn, Indeed, Glassdoor, compuTrabajo. Optimiza tu CV y postula diario.",
                ventajas=[
                    "Muchas ofertas",
                    "Puedes aplicar rapido",
                    "Investigacion de empresas"
                ],
                desventajas=[
                    "Mucha competencia",
                    "Respuestas lentas"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Postula a 5-10 trabajos diarios y personaliza cada CV.",
                tecnologias=["LinkedIn", "Indeed", "Glassdoor", "ZipRecruiter"]
            ),
            Solucion(
                titulo="Crear CV exitoso",
                descripcion="Tu CV debe ser conciso, destacado y relevante. Highlights de logros, no solo tareas.",
                ventajas=[
                    "Mas entrevistas",
                    "Destacas sobre otros",
                    "Profesional"
                ],
                desventajas=[
                    "Tiempo en hacerlo bien"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Usa formato limpio, maximo 1-2 paginas, logros cuantificados.",
                tecnologias=["Canva", "Resume.io", "LinkedIn Profile"]
            ),
            Solucion(
                titulo="Preparar entrevista",
                descripcion="Investiga la empresa, practica respuestas STAR, prepara preguntas.",
                ventajas=[
                    "Mas confianza",
                    "Mejor impresion",
                    "Puedes negociar mejor"
                ],
                desventajas=[
                    "Toma tiempo preparar"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Prepara 3 historias STAR de tus logros antes de cada entrevista.",
                tecnologias=["Glassdoor", "YouTube", "ChatGPT"]
            ),
            Solucion(
                titulo="Negociar salario",
                descripcion="Investiga rangos, conoce tu valor, no aceptes primera oferta por inercia.",
                ventajas=[
                    "Miles mas al ano",
                    "Demuestras valor",
                    "Mejores beneficios"
                ],
                desventajas=[
                    "Puede sonar agresivo"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Siempre negocia - casi siempre hay margen.",
                tecnologias=["Glassdoor", "LinkedIn Salary", "Payscale"]
            ),
            Solucion(
                titulo="Trabajo remoto",
                descripcion="Cada vez mas empresas ofrecen remote. Busca en Remote OK, We Work Remotely.",
                ventajas=[
                    "Ahorras tiempo de traslado",
                    "Horario flexible",
                    "Trabaja desde cualquier lugar"
                ],
                desventajas=[
                    "Requiere autodisciplina",
                    "Pueden pedir overlap de horarios"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Ten espacio de trabajo adecuado y buena conexion a internet.",
                tecnologias=["Remote OK", "We Work Remotely", "LinkedIn", "Angel List"]
            ),
            Solucion(
                titulo="Freelancing",
                descripcion="Trabaja por proyecto: Upwork, Fiverr, Freelancer. Flexibilidad total.",
                ventajas=[
                    "Tu propio jefe",
                    "Horarios flexibles",
                    "Multiples clientes"
                ],
                desventajas=[
                    "Ingresos variables",
                    "Busca clientes constantemente"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Especializate en algo - generalistas ganan menos.",
                tecnologias=["Upwork", "Fiverr", "LinkedIn ProFinder", "Toptal"]
            ),
            Solucion(
                titulo="Emprender",
                descripcion="Crea tu propio negocio. Valida idea, construye MVP, busca clientes.",
                ventajas=[
                    "Potencial ilimitado",
                    "Independencia total",
                    "Creas valor"
                ],
                desventajas=[
                    "Riesgo alto",
                    "Mucho trabajo",
                    "Sin salario fijo"
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Empieza como side hustle antes de dar el salto completo.",
                tecnologias=["Lean Startup", "Canva", "Stripe", "Shopify"]
            ),
            Solucion(
                titulo="Desarrollar habilidades demandadas",
                descripcion="Python, JavaScript, SQL, Cloud, AI/ML. Skills que mejor pagan en 2024.",
                ventajas=[
                    "Alta demanda",
                    "Buenos salarios",
                    "Trabajo remoto facil"
                ],
                desventajas=[
                    "Requiere estudio intensivo"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Elige uno y enfocates - no intentes aprender todo.",
                tecnologias=["freeCodeCamp", "Coursera", "Udemy", "LeetCode"]
            ),
            Solucion(
                titulo="Networking efectivo",
                descripcion="Conecta con profesionales de tu area. LinkedIn, eventos, comunidades.",
                ventajas=[
                    "70% de trabajos vienen de conexiones",
                    "Aprendes del mercado",
                    "Oportunidades ocultas"
                ],
                desventajas=[
                    "Toma tiempo",
                    "Requiere iniciativa"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Envia 10 mensajes de networking semanalmente.",
                tecnologias=["LinkedIn", "Meetup", "Eventos de industria"]
            ),
            Solucion(
                titulo="Cambio de carrera",
                descripcion="Si quieres cambiar de industria, destaca skills transferibles y cursos.",
                ventajas=[
                    "Nueva oportunidad",
                    "Reinicio profesional",
                    "Crecimiento"
                ],
                desventajas=[
                    "Puede haber recorte salarial inicial",
                    "Aprender desde cero"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="No startas from scratch - usa lo que ya sabes.",
                tecnologias=["Coursera", "LinkedIn Learning", "Bootcamps"]
            ),
            Solucion(
                titulo="Manejar entrevista virtual",
                descripcion="Zoom, Teams, Google Meet. Lighting, camara, sonido, conexion.",
                ventajas=[
                    "Puedes aplicar global",
                    "Mas comodidad",
                    "Ahorras tiempo"
                ],
                desventajas=[
                    "Problemas tecnicos",
                    "Menos personal"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Testea todo antes y ten backup de internet.",
                tecnologias=["Zoom", "Microsoft Teams", "Google Meet"]
            ),
            Solucion(
                titulo="Prepararse para ascenso",
                descripcion="Busca visibility, desarrolla liderazgo, asume proyectos visibles.",
                ventajas=[
                    "Mayor salario",
                    "Mas responsabilidad",
                    "Impacto mayor"
                ],
                desventajas=[
                    "Mas trabajo",
                    "Presion"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="No esperes que te reconozcan - hazlo visible.",
                tecnologias=["1:1s", "Feedback regular", "Mentorship"]
            ),
        ]

    def _generar_soluciones_alimentacion(self, texto: str) -> list[Solucion]:
        """Genera soluciones para comida y alimentación."""
        return [
            Solucion(
                titulo="Apps de delivery",
                descripcion="Uber Eats, Rappi, DoorDash, PedidosYa. Comida a tu puerta.",
                ventajas=[
                    "Conveniencia maxima",
                    "Mucha variedad",
                    "Descuentos frecuentes"
                ],
                desventajas=[
                    "Caro con fees",
                    "Propina obligatoria",
                    "Calidad puede variar"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Usa codigos de descuento y ordena directo del restaurant cuando puedas.",
                tecnologias=["Uber Eats", "Rappi", "DoorDash", "PedidosYa"]
            ),
            Solucion(
                titulo="Restaurantes tops - Ocaciones especiales",
                descripcion="Para fechas especiales, busca restaurantes acclaimed. Reserva con anticipacion.",
                ventajas=[
                    "Experiencia unica",
                    "Comida excepcional",
                    "Ambiente perfecto"
                ],
                desventajas=[
                    "Muy caro",
                    "Reservas dificiles"
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Reserva 2-3 semanas antes para fines de semana.",
                tecnologias=["TheFork", "OpenTable", "Resy", "Google"]
            ),
            Solucion(
                titulo="Comida rapida saludable",
                descripcion="Fast food no tiene que ser chatarra. Elige opciones mas saludables.",
                ventajas=[
                    "Rapido y conveniente",
                    "Opciones mejores cada vez",
                    "Mas accesible"
                ],
                desventajas=[
                    "Todavia no es casero"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Elige ensaladas, grilled, sin mayo, agua en lugar de soda.",
                tecnologias=["Chipotle", "Panera", "Shake Shack", "Local healthy spots"]
            ),
            Solucion(
                titulo="Cocinar en casa - Basics",
                descripcion="Aprende recetas basicas: arroz, frijoles, pollo, ensaladas. Ahorras mucho.",
                ventajas=[
                    "Ahorras dinero",
                    "Mas saludable",
                    "Habilidad para toda la vida"
                ],
                desventajas=[
                    "Tiempo de preparacion"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Empieza con una receta facil y dominala antes de avanzar.",
                tecnologias=["YouTube", "Cookpad", "AllRecipes", "TikTok Recipes"]
            ),
            Solucion(
                titulo="Meal prep - Ahorra tiempo",
                descripcion="Prepara comida para toda la semana el domingo. Ahorras tiempo y dinero.",
                ventajas=[
                    "Ahorras horas entre semana",
                    "Come saludable",
                    "Ahorras dinero"
                ],
                desventajas=[
                    "Tiempo el domingo",
                    "Puede aburrir"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Prepara proteina + carbohidratos + verduras en batches.",
                tecnologias=["YouTube", "MealPrepSunday", "Tupperware"]
            ),
            Solucion(
                titulo="Dietas populares",
                descripcion="Keto, Atkins, Paleo, Mediterranea, Vegana. Cada una tiene pros y contras.",
                ventajas=[
                    "Estructura clara",
                    "Resultados comprobados",
                    "Comunidad de apoyo"
                ],
                desventajas=[
                    "Restrictivas",
                    "No funciona para todos"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="La mejor dieta es la que puedes mantener. Prueba 1 mes.",
                tecnologias=["MyFitnessPal", "Cronometer", "Dietitians"]
            ),
            Solucion(
                titulo="Comida tipica local",
                descripcion="Explora la gastronomia local: tacos, arepas, empanadas, pupusas.",
                ventajas=[
                    "Economico",
                    "Autentico",
                    "Cultural"
                ],
                desventajas=[
                    "Puede ser pesado"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Pide recomendaciones locales - los turistas van a lugares diferentes.",
                tecnologias=["Google Maps", "Yelp", "TripAdvisor", "Local blogs"]
            ),
            Solucion(
                titulo="Vegetariano y vegano",
                descripcion="Cada vez mas opciones. Plant-based esta en todos lados.",
                ventajas=[
                    "Mas saludable",
                    "Mejor para el planeta",
                    "Opciones infinitas"
                ],
                desventajas=[
                    "Requiere planeacion",
                    "Suplementos necesarios"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Come colores - asegura variedad de plantas.",
                tecnologias=["HappyCow", "Minimalist Baker", "Forks Over Knives"]
            ),
            Solucion(
                titulo="Cafes y coffee shops",
                descripcion="Para trabajar, dates, o solo relaj. Encuentra tu tercer lugar.",
                ventajas=[
                    "Atmosfera",
                    "Cafe de calidad",
                    "WiFi y espacio"
                ],
                desventajas=[
                    "Puede costar mucho",
                    "Multitud"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Las tarjetas de lealtad se pagan soles - vas a regresar.",
                tecnologias=["Starbucks", "Local roasters", "Blue Bottle", "Stumptown"]
            ),
            Solucion(
                titulo="Desayunos ricos y faciles",
                descripcion="Huevos, avena, smoothies, panqueques, avocado toast. Start your day right.",
                ventajas=[
                    "Energia sostenida",
                    "Facil de preparar",
                    "Delicioso"
                ],
                desventajas=[
                    "Tiempo en la manana"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Prepara overnight oats la noche anterior.",
                tecnologias=["YouTube", "Pinterest", "Breakfast burritos"]
            ),
            Solucion(
                titulo="Smoothies y jugos",
                descripcion="Rapido, nutritivo, delicioso. Combina frutas, verduras, proteina.",
                ventajas=[
                    "Nutrientes concentrados",
                    "Facil de tomar",
                    "Personalizable"
                ],
                desventajas=[
                    "Equipo necesario",
                    "Rapido se oxida"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Añade protein y grasas para que te llenes.",
                tecnologias=["Vitamix", "Ninja", "Simple Green Smoothie"]
            ),
            Solucion(
                titulo="Vinos y espirituosos",
                descripcion="Para ocasiones: vino, cerveza, cocteles. Aprende lo basico.",
                ventajas=[
                    "Experiencia social",
                    "Cultura",
                    "Relax"
                ],
                desventajas=[
                    "Caro",
                    "Salud"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Aprende lo basico - no necesitas ser experto.",
                tecnologias=["Vivino", "Untappd", "Wine Enthusiast"]
            ),
        ]

    def _generar_soluciones_cine(self, texto: str) -> list[Solucion]:
        """Genera soluciones para cine y películas."""
        return [
            Solucion(
                titulo="Plataformas de streaming",
                descripcion="Netflix, HBO Max, Disney+, Prime Video, Apple TV+. Cada una tiene contenido exclusivo.",
                ventajas=[
                    "Miles de peliculas y series",
                    "Ver desde casa",
                    "Variados precios"
                ],
                desventajas=[
                    "Suscripciones se acumulan",
                    "Contenido varia por region"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Usa un mes gratis de cada plataforma para decidir cual te conviene.",
                tecnologias=["Netflix", "HBO Max", "Disney+", "Prime Video"]
            ),
            Solucion(
                titulo="Ver películas en cines",
                descripcion="Aprovecha funciones, estrenos y la experiencia unica del cine.",
                ventajas=[
                    "Experiencia inmersiva",
                    "Estrenos primero",
                    "Sonido e imagen optimos"
                ],
                desventajas=[
                    "Costo entrada",
                    "Viaje necesario"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Busca cines con promociones o descuentos.",
                tecnologias=["Cinepolis", "Cinemark", "AMC", "Fandango"]
            ),
        ]

    def _generar_soluciones_deportes(self, texto: str) -> list[Solucion]:
        """Genera soluciones para deportes."""
        return [
            Solucion(
                titulo="Hacer ejercicio",
                descripcion="Empieza con algo accesible: caminar, correr, entrenar en casa.",
                ventajas=[
                    "Salud fisica y mental",
                    "Energia extra",
                    "Habitos positivos"
                ],
                desventajas=[
                    "Requiere disciplina",
                    "Tiempo"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Empieza con 20 minutos 3 veces por semana.",
                tecnologias=["YouTube", "Apps de ejercicio", "Running", "Gimnasio"]
            ),
        ]

    def _generar_soluciones_moda(self, texto: str) -> list[Solucion]:
        """Genera soluciones para moda y estilo."""
        return [
            Solucion(
                titulo="Armar un guardarropas basico",
                descripcion="Invierte en piezas basicas de calidad: blazer, jeans, camisas.",
                ventajas=[
                    "Versatilidad",
                    "Ahorro a largo plazo",
                    "Siempre tienes que ponerte"
                ],
                desventajas=[
                    "Inversion inicial",
                    "Requiere seleccion"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Prioriza neutros para maxima combinacion.",
                tecnologias=["Zara", "Uniqlo", "H&M", "Nordstrom"]
            ),
        ]

    def _generar_soluciones_ciencia(self, texto: str) -> list[Solucion]:
        """Genera soluciones para ciencia y tecnología."""
        return [
            Solucion(
                titulo="Aprender sobre IA",
                descripcion="Explora el mundo de la inteligencia artificial.",
                ventajas=[
                    "Futuro del trabajo",
                    "Herramientas utiles",
                    "Comprension del mundo"
                ],
                desventajas=[
                    "Cambio rapido",
                    "Mucho ruido"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Prueba ChatGPT para entender el potencial.",
                tecnologias=["ChatGPT", "Coursera", "YouTube"]
            ),
        ]

    def _es_entrada_vaga(self, texto_original: str, texto: str) -> tuple[bool, list[str]]:
        """Detecta si la entrada es vaga y por qué."""
        razones = []
        
        if len(texto_original.split()) < 4:
            razones.append("Muy corta - necesito más contexto")
        
        preguntas_genericas = ["que hacer", "ayuda", "consejo", "no se", "ayudame", "que me recomiendas"]
        if any(p in texto for p in preguntas_genericas) and len(texto_original.split()) < 10:
            razones.append("Pregunta generica sin contexto especifico")
        
        return len(razones) > 0, razones
    
    def _analizar_problema_real(self, texto_original: str, texto: str) -> str:
        """Analiza qué problema REAL está detrás de la pregunta."""
        return texto_original

    def _analisis_contextual(self, texto: str, texto_lower: str) -> AnalisisContextual:
        """Realiza análisis contextual del problema."""
        
        dominio = self._detectar_dominio(texto_lower)
        
        return AnalisisContextual(
            problema_resumido=texto[:100],
            dominio=dominio,
            objetivo_real=texto,
            factor_clave="Analisis requerido",
            restricciones=[],
            oportunidades=["Explorar opciones", "Buscar alternativas"]
        )

    def _detectar_dominio(self, texto: str) -> str:
        """Detecta el dominio principal del problema."""
        
        dominios = {
            "trabajo": ["trabajo", "empleo", "career", "profesion", "salario"],
            "salud": ["salud", "ejercicio", "gimnasio", "enfermo", "medico"],
            "finanzas": ["dinero", "inversion", "ahorro", "deuda", "prestamo"],
            "relaciones": ["amigos", "familia", "pareja", "relacion", "comunicacion"],
            "tecnologia": ["computadora", "celular", "internet", "software", "error"],
            "entretenimiento": ["juego", "musica", "pelicula", "serie", "deporte"],
            "educacion": ["estudiar", "aprender", "curso", "universidad", "examen"]
        }
        
        for dominio, palabras in dominios.items():
            if any(p in texto for p in palabras):
                return dominio
        
        return "general"

    def _generar_soluciones_estrategicas(
        self, 
        texto: str, 
        analisis: AnalisisContextual,
        categoria: SolutionCategory,
        categorias_usadas: set
    ) -> list[Solucion]:
        """Genera soluciones estratégicas generales."""
        
        return [
            Solucion(
                titulo="Define tu objetivo",
                descripcion="Specify exactamente qué quieres lograr. Sin objetivo claro, cualquier camino sirve.",
                ventajas=[
                    "Direccion clara",
                    "Medible",
                    "Motivador"
                ],
                desventajas=[
                    "Requiere reflexion"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Escribe tu objetivo en una frase concreta.",
                tecnologias=["Notas", "Objetivos SMART"]
            ),
            Solucion(
                titulo="Busca perspectivas",
                descripcion="Habla con personas que hayan resuelto algo similar.",
                ventajas=[
                    "Perspectiva objetiva",
                    "Ahorra tiempo",
                    "Conexiones"
                ],
                desventajas=[
                    "Dependes de otros"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Envia mensajes a personas en tu area.",
                tecnologias=["LinkedIn", "Networking"]
            ),
        ]

    def _generar_razonamiento_estrategico(
        self, 
        analisis: AnalisisContextual, 
        problema_real: str,
        es_vaga: bool
    ) -> str:
        """Genera el razonamiento estratégico."""
        
        razonamiento = f"""
## Analisis Estrategico

**Problema:** {problema_real[:200]}

**Dominio:** {analisis.dominio}

"""
        
        if es_vaga:
            razonamiento += """
⚠️ Tu solicitud es bastante general. 
Para darte soluciones más precisas, responde:
- ¿Qué específico quieres lograr?
- ¿Qué has intentado antes?
- ¿Cuál es tu restricción principal (tiempo, dinero, conocimiento)?

"""
        
        return razonamiento.strip()

    def _generar_preguntas_aclaratorias(
        self, 
        texto: str, 
        razones_vagueza: list[str],
        problema_real: str
    ) -> list[str]:
        """Genera preguntas para aclarar el problema."""
        
        preguntas = []
        
        if "Muy corta" in str(razones_vagueza):
            preguntas.append("¿Puedes dar más detalles sobre tu situación?")
        
        if "genérica" in str(razones_vagueza).lower():
            preguntas.append("¿Cuál es el resultado específico que buscas?")
        
        if not preguntas:
            preguntas = [
                "¿Qué has intentado antes?",
                "¿Cuál es tu mayor obstaculo?",
                "¿Tienes alguna limitacion de tiempo o presupuesto?"
            ]
        
        return preguntas

    def _solucion_por_restriccion(self, texto: str, analisis: AnalisisContextual) -> Solucion:
        """Solución que considera las restricciones."""
        
        return Solucion(
            titulo="Comienza con lo que tienes",
            descripcion="No esperes condiciones perfectas. Empieza con lo disponible ahora.",
            ventajas=[
                "Accion inmediata",
                "Sin excusas",
                "Genera momentum"
            ],
            desventajas=[
                "Puede no ser optimo"
            ],
            complejidad=ComplexityLevel.BAJA,
            categoria=SolutionCategory.GENERAL,
            recomendacion="El primer paso es siempre el mas importante.",
            tecnologias=["Notas", "Lista simple"]
        )

    def _solucion_por_objetivo(self, texto: str, analisis: AnalisisContextual) -> Solucion:
        """Solución específica según el objetivo."""
        
        return Solucion(
            titulo="Define tu siguiente accion",
            descripcion="Toda meta se logra con pasos pequenos. Cual es el siguiente paso?",
            ventajas=[
                "Ejecutable",
                "Medible",
                "Sin overwhelm"
            ],
            desventajas=[
                "Requiere focus"
            ],
            complejidad=ComplexityLevel.BAJA,
            categoria=SolutionCategory.GENERAL,
            recomendacion="Que puedes hacer hoy aunque solo sean 15 minutos?",
            tecnologias=["Notas", "Calendar"]
        )

    def _generar_soluciones_videojuegos(self, texto: str) -> list[Solucion]:
        """Genera soluciones para videojuegos."""
        return [
            Solucion(
                titulo="Elegir plataforma",
                descripcion="Decide entre PC, PlayStation, Xbox o Nintendo Switch según tus preferencias y presupuesto.",
                ventajas=[
                    "Cada una tiene exclusivos",
                    "Variedad de precios",
                    "Ecosistemas diferentes"
                ],
                desventajas=[
                    "Costo de entrada",
                    "Exclusivos limitados"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Define qué tipo de juegos te gust mas y elige la mejor plataforma.",
                tecnologias=["Steam", "PlayStation Store", "Nintendo eShop", "Xbox Game Pass"]
            ),
            Solucion(
                titulo="PC Gaming",
                descripcion="Arma o compra una PC para gaming. Puede ser más económico a largo plazo con Game Pass y Steam.",
                ventajas=[
                    "Versatilidad",
                    "Mejores graficos",
                    "Juegos mas baratos"
                ],
                desventajas=[
                    "Costo inicial alto",
                    "Mantenimiento"
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Empieza con un setup básico y mejora gradualmente.",
                tecnologias=["Steam", "Epic Games", "GOG", "Nvidia", "AMD"]
            ),
            Solucion(
                titulo="Gaming social",
                descripcion="Únete a comunidades, juega con amigos online o participa en tournaments.",
                ventajas=[
                    "Diversion social",
                    "Mejora habilidades",
                    "Competencia"
                ],
                desventajas=[
                    "Toxicidad",
                    "Tiempo excesivo"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Busca comunidades positivas y establece limites de tiempo.",
                tecnologias=["Discord", "Twitch", "Reddit", "Steam Community"]
            ),
            Solucion(
                titulo="Juegos gratuitos",
                descripcion="Muchisimos juegos gratuitos de alta calidad: Fortnite, Valorant, LoL, Genshin Impact, Warzone.",
                ventajas=[
                    "Cero costo de entrada",
                    "Calidad profesional",
                    "Comunidades grandes"
                ],
                desventajas=[
                    "Microtransacciones",
                    "Curva de aprendizaje"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Prueba varios gratuitos hasta encontrar uno que te enganche.",
                tecnologias=["Epic Games", "Steam", " Riot Games", "miHoYo"]
            ),
            Solucion(
                titulo="Retro gaming",
                descripcion="Revive clásicos de PS1, N64, SNES o PC antiguo. Emuladores y ports modernos hacen esto facil.",
                ventajas=[
                    "Nostalgia",
                    "Juegos icnicos",
                    "Barato o gratis"
                ],
                desventajas=[
                    "Legalidad variable",
                    "Configuracion"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Busca remakes oficiales o juegos clasicos en Steam/Nintendo eShop.",
                tecnologias=["RetroArch", "Steam", "Nintendo Switch Online", "GOG"]
            ),
        ]

    def _generar_soluciones_cine(self, texto: str) -> list[Solucion]:
        """Genera soluciones para cine y películas."""
        return [
            Solucion(
                titulo="Plataformas de streaming",
                descripcion="Compara Netflix, HBO Max, Disney+, Prime Video, Apple TV+ segun su contenido exclusivo.",
                ventajas=[
                    "Variedad enorme",
                    "Ver desde casa",
                    "Variados precios"
                ],
                desventajas=[
                    "Suscripciones se acumulan",
                    "Contenido varia por region"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Usa un mes gratis de cada plataforma para decidir cual te conviene.",
                tecnologias=["Netflix", "HBO Max", "Disney+", "Prime Video"]
            ),
            Solucion(
                titulo="Ver películas en cines",
                descripcion="Aprovecha funciones, estrenos y la experiencia única del cine. Busca horarios y promociones.",
                ventajas=[
                    "Experiencia inmersiva",
                    "Estrenos primero",
                    "Sonido e imagen optimal"
                ],
                desventajas=[
                    "Costo entrada",
                    "Viaje necesario"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Busca cinemas con promociones como miercoles cine o tarjetas de descuento.",
                tecnologias=["Cinepolis", "Cinemark", "AMC", "Fandango"]
            ),
            Solucion(
                titulo="Generos y recomendaciones",
                descripcion="Explora generos que no conoces. Usa sitios de reseñas para encontrar joyas ocultas.",
                ventajas=[
                    "Nuevas experiencias",
                    "Amplia vision",
                    "Peliculas increibles"
                ],
                desventajas=[
                    "Tiempo invertiry",
                    "Algunas decepciones"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Mira top 100 de IMDb o Letterboxd para descubrimientos.",
                tecnologias=["IMDb", "Letterboxd", "Rotten Tomatoes", "Metacritic"]
            ),
            Solucion(
                titulo="Marathons tematicos",
                descripcion="Organiza viendo marathons de sagas completas: Star Wars, Marvel, Lord of the Rings, etc.",
                ventajas=[
                    "Experiencia completa",
                    "Entretenimiento prolongado",
                    "Preparacion previa"
                ],
                desventajas=[
                    "Mucho tiempo",
                    "Requiere planeacion"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Planea un fin de semana especifico y prepara snacks.",
                tecnologias=["Disney+", "Netflix", "HBO Max"]
            ),
            Solucion(
                titulo="Documentales",
                descripcion="Explora el genero documental para aprender sobre ciencia, historia, naturaleza o temas actuales.",
                ventajas=[
                    "Educativo",
                    "的真实",
                    "Amplia variedad"
                ],
                desventajas=[
                    "Menos action",
                    "Algunos aburren"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Busca documentales altamente valorados en Netflix o YouTube.",
                tecnologias=["Netflix", "YouTube", "Docplay", "National Geographic"]
            ),
        ]

    def _generar_soluciones_deportes(self, texto: str) -> list[Solucion]:
        """Genera soluciones para deportes."""
        return [
            Solucion(
                titulo="Hacer ejercicio",
                descripcion="Empieza con algo accesible: caminar, correr, entrenar en casa. La consistencia es más importante que la intensidad.",
                ventajas=[
                    "Salud fisica y mental",
                    "Energia extra",
                    "Habitos positivos"
                ],
                desventajas=[
                    "Requiere disciplina",
                    "Tiempo"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Empieza con 20 minutos 3 veces por semana. Aumenta gradualmente.",
                tecnologias=["YouTube", "Apps de ejercicio", "Running", "Gimnasio"]
            ),
            Solucion(
                titulo="Ver deportes",
                descripcion="Sigue tus ligas y equipos favoritos. Streaming hace más facil que nunca.",
                ventajas=[
                    "Entretenimiento",
                    "Comunidad",
                    "Aprendizaje"
                ],
                desventajas=[
                    "Costo suscripciones",
                    "Diferencias de horario"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Usa ESPN, Fox Sports o las apps oficiales de las ligas.",
                tecnologias=["ESPN", "Fox Sports", "DAZN", "MLS Live"]
            ),
            Solucion(
                titulo="Apostar responsablemente",
                descripcion="Si te interesa Apostar en deportes, hazlo con mesura. Establece limites claros.",
                ventajas=[
                    "Anade emocion",
                    "Posible ganancias"
                ],
                desventajas=[
                    "Riesgo financiero",
                    "Adiccion"
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Nunca apuestes más de lo que puedas perder. Es solo entretenimiento.",
                tecnologias=["Bet365", "DraftKings", "FanDuel"]
            ),
            Solucion(
                titulo="Practicar un deporte",
                descripcion="Únete a una liga amateur, club o clase de un deporte que te interese.",
                ventajas=[
                    "Ejercicio + social",
                    "Aprendizaje",
                    "Competencia sana"
                ],
                desventajas=[
                    "Compromiso de tiempo",
                    "Equipo/espacio necesario"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Busca grupos locales en Facebook o Meetup de tu deporte favorito.",
                tecnologias=["Facebook Groups", "Meetup", "Clubes locales"]
            ),
            Solucion(
                titulo="Esports",
                descripcion="Explora los deportes electronicos: ver competencias, jugar competitivamente o solo casual.",
                ventajas=[
                    "Accesible desde casa",
                    "Comunidad global",
                    "Carreras profesionales"
                ],
                desventajas=[
                    "Toxicidad",
                    "Tiempo excesivo"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Mira torneos en Twitch o YouTube para entender la escena.",
                tecnologias=["Twitch", "YouTube Gaming", "Discord", "ESL"]
            ),
        ]

    def _generar_soluciones_moda(self, texto: str) -> list[Solucion]:
        """Genera soluciones para moda y estilo."""
        return [
            Solucion(
                titulo="Armar un guardarropas basico",
                descripcion="Invierte en piezas basicas de calidad: blazer, jeans, camisas, zapatos. Combina facilmente.",
                ventajas=[
                    "Versatilidad",
                    "Ahorro a largo plazo",
                    "Siempre tienes que ponerte"
                ],
                desventajas=[
                    "Inversion inicial",
                    "Requiere seleccion"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Prioriza neutros (negro, blanco, azul) para maxima combinacion.",
                tecnologias=["Zara", "Uniqlo", "H&M", "Nordstrom"]
            ),
            Solucion(
                titulo="Estilo personal",
                descripcion="Descubre tu estilo: casual, formal, streetwear, minimalista. Inspirate en otros.",
                ventajas=[
                    "Te sientes bien",
                    "Expresas personalidad",
                    "Facilita compras"
                ],
                desventajas=[
                    "Tiempo de descubrimiento",
                    "Puede costar"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Guarda fotos de outfits que te gusten y busca patrones.",
                tecnologias=["Pinterest", "Instagram", "Lookbook"]
            ),
            Solucion(
                titulo="Ropa sostenible",
                descripcion="Considera ropa de segunda mano, marcas sostenibles o comprar menos pero mejor calidad.",
                ventajas=[
                    "Mejor para el planeta",
                    "Unico",
                    "Ahorro posible"
                ],
                desventajas=[
                    "Mas busqueda",
                    "Calidad variable"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Explora thrift stores o apps de segunda mano de moda.",
                tecnologias=["Depop", "Vinted", "Poshmark", "ThredUp"]
            ),
            Solucion(
                titulo="Accesorios",
                descripcion="Un buen reloj, lentes o joyeria pueden elevar cualquier outfit.",
                ventajas=[
                    "Bajo costo relativo",
                    "Gran impacto",
                    "Personalizacion"
                ],
                desventajas=[
                    "Eleccion abrumadora"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Invierte en 2-3 accesorios de calidad en lugar de muchos baratos.",
                tecnologias=["Amazon", "Joyerias locales", "MercadoLibre"]
            ),
            Solucion(
                titulo="Compras inteligentes",
                descripcion="Espera rebajas, usa cupones, compara precios. Compra con necesidad, no capricho.",
                ventajas=[
                    "Ahorro significativo",
                    "Menos impulse buying",
                    "Mejor calidad"
                ],
                desventajas=[
                    "Requiere paciencia",
                    "Perdidas de tallas"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Haz una lista y espera 48h antes de comprar algo no esencial.",
                tecnologias=["Honey", "Rakuten", "Rebajas", "Black Friday"]
            ),
        ]

    def _generar_soluciones_ciencia(self, texto: str) -> list[Solucion]:
        """Genera soluciones para ciencia y tecnología."""
        return [
            Solucion(
                titulo="Aprender sobre IA",
                descripcion="Explora el mundo de la inteligencia artificial: cursos, herramientas, tendencias.",
                ventajas=[
                    "Futuro del trabajo",
                    "Herramientas utiles",
                    "Comprension del mundo"
                ],
                desventajas=[
                    "Cambio rapido",
                    "Mucho ruido"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Prueba ChatGPT, Midjourney o Copilot para entender el potencial.",
                tecnologias=["ChatGPT", "Coursera", "YouTube", "Fast.ai"]
            ),
            Solucion(
                titulo="Espacio y astronomia",
                descripcion="Explora el universo: telescopios basicos, apps de estrellas, noticias de NASA y SpaceX.",
                ventajas=[
                    "Perspectiva",
                    "Fascinante",
                    "Comunidad activa"
                ],
                desventajas=[
                    "Equipo puede costar",
                    "Contaminacion luminosa"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Descarga una app de astronomia y sal a ver estrellas.",
                tecnologias=["NASA", "SpaceX", "Stellarium", "Star Walk"]
            ),
            Solucion(
                titulo="Tecnologia emergente",
                descripcion="Mantente al dia con blockchain, realidad virtual/aumentada, computacion cuantica.",
                ventajas=[
                    "Ventaja competitiva",
                    "Comprension futura",
                    "Oportunidades"
                ],
                desventajas=[
                    "Complejo",
                    "Mucha especulacion"
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Suscribete a newsletters especializados para mantenerte informado.",
                tecnologias=["Wired", "TechCrunch", "MIT Tech Review", "Ars Technica"]
            ),
            Solucion(
                titulo="Ciencia ciudadana",
                descripcion="Participa en proyectos de investigacion reales:Foldit, Zooniverse, proyectos de clima.",
                ventajas=[
                    "Contribuyes a la ciencia",
                    "Aprendizaje",
                    "Comunidad"
                ],
                desventajas=[
                    "Tiempo requerido"
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Busca proyectos que te interessen en Zooniverse o NASA citizen science.",
                tecnologias=["Zooniverse", "Foldit", "NASA Citizen Science", "eBird"]
            ),
            Solucion(
                titulo="Carreras tech",
                descripcion="Explora opciones en tecnologia: programacion, data science, ciberseguridad, producto.",
                ventajas=[
                    "Alta demanda",
                    "Buenos salarios",
                    "Trabajo remoto"
                ],
                desventajas=[
                    "Requiere estudio",
                    "Competencia"
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Empieza con cursos gratuitos de Python o JavaScript.",
                tecnologias=["freeCodeCamp", "Codecademy", "CS50", "LeetCode"]
            ),
        ]

    def _es_entrada_vaga(self, texto_original: str, texto: str) -> tuple[bool, list[str]]:
        """Detecta si la entrada es vaga y why."""
        razones = []
        
        # Muy corta
        if len(texto_original.split()) < 4:
            razones.append("Muy corta - necesito más contexto")
        
        # Solo contiene preguntas genéricas
        preguntas_genericas = ["qué hacer", "ayuda", "consejo", "no sé", "ayúdame", "qué me recomiendas"]
        if any(p in texto for p in preguntas_genericas) and len(texto_original.split()) < 10:
            razones.append("Pregunta genérica sin contexto específico")
        
        # Sin verbo de acción claro
        verbos_accion = ["hacer", "conseguir", "lograr", "resolver", "empezar", "parar", "mejorar", "crear", "buscar", "aprender"]
        if not any(v in texto for v in verbos_accion):
            razones.append("No hay acción clara - ¿qué quieres lograr?")
        
        # Solo expresses frustración sin problema definido
        frases_frustracion = ["no puedo", "nunca", "siempre", "todo mal", "esto es imposible"]
        if any(f in texto for f in frases_frustracion) and len(texto_original.split()) < 8:
            razones.append("Expresa frustración pero no define el problema")
        
        # Ambiguo - múltiples interpretaciones
        palabras_ambiguas = ["bien", "mejor", "algo", "nada", "todo"]
        if all(p in texto for p in ["no", "sé"]) or (palabras_ambiguas[0] in texto and len(texto_original.split()) < 6):
            razones.append("Entrada ambigua - necesito saber qué específico")
        
        return len(razones) > 0, razones
    
    def _analizar_problema_real(self, texto_original: str, texto: str) -> str:
        """Analiza qué problema REAL está detrás de la pregunta."""
        
        # Detectar si es pregunta simple con problema complejo detrás
        patrones_problema_real = {
            "autodesarrollo sin dirección": {
                "indicadores": ["aprender", "mejorar", "desarrollar", "crecer", "creatividad"],
                "pregunta_profunda": "¿Realmente quieres aprender o escaping de algo más inmediato?"
            },
            "problema de motivación": {
                "indicadores": ["no puedo", "no me sale", "no tengo ganas", "procrastinar"],
                "pregunta_profunda": "¿El problema es que no sabes cómo o que no quieres hacerlo?"
            },
            "parálisis por análisis": {
                "indicadores": ["cuál", "qué", "dónde empiezo", "por dónde", "cómo saber"],
                "pregunta_profunda": "¿Buscas la respuesta perfecta para no actuar?"
            },
            "problema de identidad": {
                "indicadores": ["no sé quién", "qué debería", "no sé qué quiero"],
                "pregunta_profunda": "¿Estás buscando qué hacer o quién ser?"
            },
            "miedo al fracaso": {
                "indicadores": ["y si", "qué pasa si", "tengo miedo", "no me animo"],
                "pregunta_profunda": "¿Qué estás evitando realmente?"
            },
            "sobrecarga de opciones": {
                "indicadores": ["muchas opciones", "no sé cuál", "todo a la vez", "por donde"],
                "pregunta_profunda": "¿El problema es elegir o commitment con algo?"
            },
        }
        
        # Buscar el patrón que más coincide
        for nombre_patron, datos in patrones_problema_real.items():
            if any(ind in texto for ind in datos["indicadores"]):
                return f"[PROBLEMA REAL DETECTADO: {nombre_patron}] {datos['pregunta_profunda']}"
        
        return ""
    
    def _generar_preguntas_aclaratorias(
        self, 
        texto_original: str, 
        razones_vagueza: list[str],
        problema_real: str
    ) -> list[str]:
        """Genera preguntas específicas para profundizar."""
        preguntas = []
        
        # Añadir problema real si se detectó
        if problema_real:
            preguntas.append(problema_real)
        
        # Añadir preguntas específicas según las razones de vaguedad
        for razon in razones_vagueza:
            if "Muy corta" in razon or "genérica" in razon:
                preguntas.append("¿Qué situación específica enfrentas? Describe el contexto.")
                preguntas.append("¿Cuándo started este problema?")
            if "acción clara" in razon:
                preguntas.append("¿Qué resultado específico quieres lograr?")
                preguntas.append("¿Qué has intentado antes?")
            if "frustración" in razon:
                preguntas.append("¿Cuál es la situación concreta que te frustra?")
                preguntas.append("¿Qué pasaría si esta situación se resuelva?")
            if "ambigua" in razon:
                preguntas.append("¿Qué significa 'bien' o 'mejorar' para ti en términos concretos?")
                preguntas.append("¿Cómo sabrías que el problema está resuelto?")
        
        # Dedupe
        return list(dict.fromkeys(preguntas))[:5]
    
    def _analisis_contextual(self, problema_texto: str, texto: str) -> AnalisisContextual:
        """Analiza el contexto específico del problema."""
        
        # Detectar urgencia
        urgencia = any(p in texto for p in ["ahora", "rápido", "pronto", "urgente", "inmediato"])
        
        # Detectar restricciones
        restricciones = []
        if "sin tiempo" in texto or "no tengo tiempo" in texto:
            restricciones.append("Sin tiempo disponible")
        if "sin dinero" in texto or "no tengo plata" in texto:
            restricciones.append("Presupuesto limitado")
        if "solo" in texto or "solo/a" in texto:
            restricciones.append("Solo/a trabajando")
        if "equipo" in texto or "grupo" in texto:
            restricciones.append("Coordinación con otros")
        
        # Detectar oportunidades
        oportunidades = []
        if "tengo" in texto:
            oportunidades.append("Recursos disponibles mencionados")
        
        # Resumir problema
        problema_resumido = self._resumir_problema(problema_texto, texto)
        
        # Detectar objetivo real
        objetivo_real = self._detectar_objetivo(texto)
        
        # Factor clave
        factor_clave = self._detectar_factor_clave(texto)
        
        # Dominio
        dominio = self._detectar_dominio(texto)
        
        return AnalisisContextual(
            problema_resumido=problema_resumido,
            dominio=dominio,
            objetivo_real=objetivo_real,
            factor_clave=factor_clave,
            restricciones=restricciones,
            oportunidades=oportunidades,
        )
    
    def _resumir_problema(self, problema_texto: str, texto: str) -> str:
        """Resume el problema en una línea."""
        
        # Limpiar y resumir
        if len(problema_texto) > 100:
            return problema_texto[:97] + "..."
        return problema_texto
    
    def _detectar_objetivo(self, texto: str) -> str:
        """Detecta el objetivo real del usuario."""
        
        objetivos = {
            "conseguir trabajo": ["conseguir trabajo", "buscar empleo", "nuevo trabajo", "cambiar de trabajo"],
            "avanzar en carrera": ["ascenso", "promoción", "avanzar", "crecer", "progreso"],
            "mejorar habilidades": ["aprender", "mejorar skills", "desarrollar", "capacitarme"],
            "resolver problema inmediato": ["resolver", "solucionar", "arreglar", "qué hago"],
            "tomar decisión": ["qué hago", "no sé qué", "ayuda para decidir", "qué me recomiendan"],
            "gestionar tiempo": ["organizar", "tiempo", "gestionar", "priorizar"],
            "mejorar relaciones": ["relación", "pareja", "familia", "amigos", "comunicación"],
            "cuidar salud": ["salud", "ejercicio", "cansado", "estrés", "bienestar"],
        }
        
        for objetivo, palabras in objetivos.items():
            if any(p in texto for p in palabras):
                return objetivo.replace("_", " ").title()
        
        return "Mejorar situación actual"
    
    def _detectar_factor_clave(self, texto: str) -> str:
        """Identifica el factor clave que influye en la decisión."""
        
        factores = {
            "Tiempo disponible": ["tiempo", "ahora", "rápido", "pronto", "dia", "semana"],
            "Recursos económicos": ["dinero", "plata", "presupuesto", "costo", "caro", "barato"],
            "Conocimiento/Habilidades": ["saber", "conocimiento", "experiencia", "skill", "puedo"],
            "Apoyo social": ["solo", "ayuda", "equipo", "familia", "amigos"],
            "Resultados esperados": ["resultado", "efectivo", "garantizado", "seguro"],
            "Esfuerzo requerido": ["esfuerzo", "trabajo", "dedicar", "complicado"],
        }
        
        for factor, palabras in factores.items():
            if any(p in texto for p in palabras):
                return factor
        
        return "Balance costo-beneficio"
    
    def _detectar_dominio(self, texto: str) -> str:
        """Detecta el dominio principal."""
        
        dominios = {
            "Empleo y Carrera": ["trabajo", "empleo", "jefe", "entrevista", "cv", "salario"],
            "Alimentación": ["comer", "comida", "hambre", "cocinar", "restaurante"],
            "Estudio": ["estudiar", "examen", "carrera", "universidad", "clase"],
            "Tecnología": ["computadora", "celular", "internet", "wifi", "software"],
            "Finanzas": ["dinero", "inversión", "ahorrar", "gastar", "presupuesto"],
            "Salud": ["salud", "ejercicio", "médico", "enfermo", "cansado"],
            "Relaciones": ["pareja", "amigos", "familia", "comunicación"],
            "Productividad": ["organizar", "tiempo", "procrastinar", "enfoque"],
        }
        
        for dominio, palabras in dominios.items():
            if any(p in texto for p in palabras):
                return dominio
        
        return "General"
    
    def _generar_razonamiento_estrategico(
        self, 
        analisis: AnalisisContextual,
        problema_real: str = "",
        es_vaga: bool = False
    ) -> str:
        """Genera un razonamiento estratégico claro."""
        
        problema_real_block = ""
        if problema_real:
            problema_real_block = f"\n\n> ⚠️ **ANÁLISIS PROFUNDO:** {problema_real}\n"
        
        advertencia_vaga = ""
        if es_vaga:
            advertencia_vaga = "\n\n> ⚡ **Tu entrada es vaga.** Las soluciones pueden no ser precisas. Responde las preguntas aclARATORIAS para mejores resultados.\n"
        
        return f"""
## Análisis Estratégico

**Problema:** {analisis.problema_resumido}

**Dominio:** {analisis.dominio}

**Objetivo real:** {analisis.objetivo_real}

**Factor clave:** {analisis.factor_clave}

{"**Restricciones identificadas:** " + ", ".join(analisis.restricciones) if analisis.restricciones else ""}
{"**Oportunidades:** " + ", ".join(analisis.oportunidades) if analisis.oportunidades else ""}
{problema_real_block}
---

### Por qué esto importa

Tu situación tiene características específicas que determinan qué soluciones funcionarán:
- El factor "{analisis.factor_clave}" es lo que más influye en tu decisión
- Buscas: {analisis.objetivo_real}

Las soluciones propuestas a continuación consideran estas variables.{advertencia_vaga}
""".strip()
    
    def _generar_soluciones_estrategicas(
        self, 
        texto: str,
        analisis: AnalisisContextual,
        categoria: SolutionCategory,
        categorias_usadas: set
    ) -> list[Solucion]:
        """Genera soluciones personalizadas basadas en el análisis."""
        
        soluciones = []
        
        # Solución 1: Según urgencia
        if any(p in texto for p in ["ahora", "rápido", "urgente", "pronto"]):
            soluciones.append(self._solucion_inmediata(texto, analisis))
        
        # Solución 2: Según objetivo real
        objetivo_sol = self._solucion_por_objetivo(texto, analisis)
        if objetivo_sol:
            soluciones.append(objetivo_sol)
        
        # Solución 3: Según restricción principal
        if analisis.restricciones:
            restriccion_sol = self._solucion_por_restriccion(texto, analisis)
            if restriccion_sol:
                soluciones.append(restriccion_sol)
        
        # Solución 4: Solución de bajo esfuerzo
        soluciones.append(self._solucion_bajo_esfuerzo(texto, analisis))
        
        # Solución 5: Solución de alto impacto
        soluciones.append(self._solucion_alto_impacto(texto, analisis))
        
        # Filtrar None y asegurar 5 soluciones
        soluciones = [s for s in soluciones if s is not None]
        
        # Si no hay suficientes, agregar soluciones por defecto
        while len(soluciones) < 5:
            soluciones.append(self._solucion_default(texto, analisis, len(soluciones)))
        
        return soluciones[:5]
    
    def _solucion_inmediata(self, texto: str, analisis: AnalisisContextual) -> Solucion:
        """Solución para cuando necesita resultados inmediatos."""
        
        if analisis.dominio == "Alimentación":
            return Solucion(
                titulo="Acción inmediata: Delivery ahora",
                descripcion="En este momento, lo más práctico es ordenar comida a domicilio. Apps como Rappi, Uber Eats o PedidosYa te permiten comer en 30-45 minutos.",
                ventajas=[
                    "Resultado inmediato",
                    "Sin esfuerzo adicional",
                    "Puedes seguir trabajando/mientras esperas",
                ],
                desventajas=[
                    "Costo mayor que cook en casa",
                    "Calidad nutricional variable",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion=f"Para tu caso donde el factor clave es {analisis.factor_clave}, esta es la opción más práctica.",
                tecnologias=["Rappi", "Uber Eats", "PedidosYa"],
            )
        
        if analisis.dominio == "Empleo y Carrera":
            return Solucion(
                titulo="Aplicar a 5 posiciones ahora mismo",
                descripcion="Dedica las próximas 2 horas a aplicar a 5 posiciones que matcheen tu perfil. No busques más - ejecuta.",
                ventajas=[
                    "Acción concreta y medible",
                    "Empieza el proceso hoy",
                    "Momentum psicológico positivo",
                ],
                desventajas=[
                    "Requiere energía mental",
                    "Puede ser frustrante si no hay respuesta inmediata",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion=f"Para urgencia en búsqueda de empleo, el movimiento genera oportunidades.",
                tecnologias=["LinkedIn", "Indeed", "Computrabajo"],
            )
        
        return Solucion(
            titulo="Identificar la acción más pequeña",
            descripcion="En los próximos 30 minutos, haz UNA cosa que te acerque a tu objetivo. No planees más - actúa.",
            ventajas=[
                "Elimina parálisis",
                "Genera momentum",
                "Resultados inmediatos",
            ],
            desventajas=[
                "Solución temporal",
                "No resuelve causa raíz",
            ],
            complejidad=ComplexityLevel.BAJA,
            categoria=SolutionCategory.GENERAL,
            recomendacion="Cuando necesitas urgente results, la acción supera la planificación.",
            tecnologias=["Lista simple", "Notas"],
        )
    
    def _solucion_por_objetivo(self, texto: str, analisis: AnalisisContextual) -> Solucion:
        """Solución específica según el objetivo."""
        
        objetivo = analisis.objetivo_real.lower()
        
        if "trabajo" in objetivo or "empleo" in objetivo:
            return Solucion(
                titulo="Enviar 10 mensajes de networking",
                descripcion="Envía mensajes personalizados a personas de tu sector. No pidas trabajo - pregunta sobre el mercado. Ejemplo: 'Vi que trabajas en X, me interesa saber cómo está el sector para alguien con mi perfil.'",
                ventajas=[
                    "70% de empleos vienen de conexiones",
                    "Información que no está en internet",
                    "Sin competencia masiva",
                ],
                desventajas=[
                    "Respuestas pueden tardar días",
                    "Requiere salir de zona de confort",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="El networking es el accelerator más rápido para conseguir empleo.",
                tecnologias=["LinkedIn InMail", "Twitter DMs"],
            )
        
        if "aprender" in objetivo or "estudiar" in objetivo:
            return Solucion(
                titulo="Aplicar lo que aprendes en 24 horas",
                descripcion="No solo consumes contenido - usarlo inmediatamente. Viste un tutorial de código? Programa algo hoy. Leíste sobre marketing? Aplica una táctica.",
                ventajas=[
                    "Retención 10x mayor",
                    "Portfolio grows",
                    "Aprendes lo que realmente funciona",
                ],
                desventajas=[
                    "Más difícil que solo consumir",
                    "Puede frustrar al principio",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="El aprendizaje real requiere aplicación, no consumo.",
                tecnologias=["GitHub", "Proyectos propios"],
            )
        
        if "decisión" in objetivo:
            return Solucion(
                titulo="Definir criterio único de decisión",
                descripcion="En lugar de analizar todo, define UN criterio que importe: 'Si X > $500, no'. O 'Si no puedo hacerlo en 2 horas, delegar'. Criterios simples = decisiones rápidas.",
                ventajas=[
                    "Decisiones 10x más rápidas",
                    "Menos abrumación",
                    "Consistencia en decisiones",
                ],
                desventajas=[
                    "Puede parecer simplista",
                    "Requiere honestidad",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Las mejores decisiones tienen un 'Sí/No' claro.",
                tecnologias=["Notas", "Matriz simple"],
            )
        
        return Solucion(
            titulo="Define tu siguiente acción",
            descripcion="Independientemente de tu objetivo, el primer paso es definir una acción concreta que puedas tomar hoy.",
            ventajas=[
                "siempre hay algo que hacer",
                "Crea momentum",
                "Reduce overwhelm"
            ],
            desventajas=[
                "Requiere reflexión"
            ],
            complejidad=ComplexityLevel.BAJA,
            categoria=SolutionCategory.GENERAL,
            recomendacion="Pregúntate: ¿Qué es lo mínimo que puedo hacer hoy?",
            tecnologias=["Notas", "Lista simple"]
        )
    
    def _solucion_por_restriccion(self, texto: str, analisis: AnalisisContextual) -> Solucion:
        """Solución que considera las restricciones."""
        
        restriccion = analisis.restricciones[0] if analisis.restricciones else ""
        
        if "tiempo" in restriccion.lower():
            return Solucion(
                titulo="Bloque de tiempo mínimo viable",
                descripcion="Even 15 minutos cuentan. Define: 'Dedicaré 15 minutos hoy a X'. Es tan pequeño que no hay excusa para no hacerlo.",
                ventajas=[
                    "Se hace siempre",
                    "Se siente menos abrumador",
                    "Acumula progreso",
                ],
                desventajas=[
                    "Progreso lento",
                    "Puede frustrar",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="15 minutos diarios > 0 minutos.",
                tecnologias=["Timer", "Calendario"],
            )
        
        if "presupuesto" in restriccion.lower() or "dinero" in restriccion.lower():
            return Solucion(
                titulo="Recursos gratuitos disponibles",
                descripcion="Tienes más opciones gratuitas de las que crees: YouTube para aprender, Reddit para comunidad, LinkedIn gratuito para networking, Open Source para práctica.",
                ventajas=[
                    "Cero inversión",
                    "Calidad a menudo mejor que pago",
                    "Acceso inmediato",
                ],
                desventajas=[
                    "Más ruido que contenido pago",
                    "Requires过滤 skills",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="El recurso más valioso (internet) ya lo tienes. Úsalo estratégicamente.",
                tecnologias=["YouTube", "Reddit", "GitHub", "LinkedIn"],
            )
        
        return Solucion(
            titulo="Trabajar con lo que tienes",
            descripcion=f"Tu restricción de '{restriccion}' es información valiosa. Diseña soluciones DENTRO de esa limitación, no contra ella.",
            ventajas=[
                "Soluciones más realistas",
                "Acción inmediata posible",
                "No esperas condiciones perfectas",
            ],
            desventajas=[
                "Puede parecer compromise",
            ],
            complejidad=ComplexityLevel.BAJA,
            categoria=SolutionCategory.GENERAL,
            recomendacion="Las limitaciones foster creatividad.",
            tecnologias=["Tu mente", "Papel y lápiz"],
        )
    
    def _solucion_bajo_esfuerzo(self, texto: str, analisis: AnalisisContextual) -> Solucion:
        """Solución que requiere mínimo esfuerzo."""
        
        return Solucion(
            titulo="Automatizar o delegar",
            descripcion="¿Qué parte de tu problema puedes automatizar (templates, checklists) o delegar (a alguien más, a una app)?",
            ventajas=[
                "Libera tiempo mental",
                "Escalable",
                "Una vez configurado, corre solo",
            ],
            desventajas=[
                "Setup inicial requiere esfuerzo",
                "No siempre posible",
            ],
            complejidad=ComplexityLevel.MEDIA,
            categoria=SolutionCategory.GENERAL,
            recomendacion=" Trabaja ON your business, not IN it.",
            tecnologias=["Zapier", "Notion", "Asistentes virtuales"],
        )
    
    def _solucion_alto_impacto(self, texto: str, analisis: AnalisisContextual) -> Solucion:
        """Solución de mayor impacto potencial."""
        
        return Solucion(
            titulo="Invertir en tu asset más valioso",
            descripcion="Tu tiempo, red o habilidades. ¿Qué te dá más retorno en las próximas semanas? Invierte ahí el 80% de tu energía.",
            ventajas=[
                "Multiplica resultados",
                "Efecto compuesto",
                "Ventaja competitiva real",
            ],
            desventajas=[
                "Requiere pensar largo plazo",
                "Beneficio no inmediato",
            ],
            complejidad=ComplexityLevel.MEDIA,
            categoria=SolutionCategory.GENERAL,
            recomendacion=" focus on what compounds.",
            tecnologias=["Reflexión diaria", "MVP", "Feedback loops"],
        )
    
    def _solucion_default(self, texto: str, analisis: AnalisisContextual, index: int) -> Solucion:
        """Solución por defecto si no hay suficientes."""
        
        soluciones_default = [
            Solucion(
                titulo="Acción más pequeña posible",
                descripcion="Identifica la acción más pequeña que puedes tomar HOY y hazla. No necesitas tener todo resuelto - solo empezar.",
                ventajas=[
                    "Elimina parálisis",
                    "Genera momentum",
                    "Resultados inmediatos",
                ],
                desventajas=[
                    " Puede parecer insuficiente",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="El progreso genera más progreso.",
                tecnologias=["Notas"],
            ),
            Solucion(
                titulo="Preguntar a alguien con experiencia",
                descripcion="Busca a alguien que haya resuelto un problema similar. Una pregunta específica a la persona correcta vale más que horas de investigación.",
                ventajas=[
                    "Ahorra tiempo",
                    "Información práctica no disponible online",
                    "Construyes relación",
                ],
                desventajas=[
                    "Dependes de disponibilidad ajena",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Las mejores preguntas son específicas y muestran que ya investigaste.",
                tecnologias=["LinkedIn", "Coffee chat"],
            ),
            Solucion(
                titulo="Experimentar en pequeña escala",
                descripcion="Antes de comprometerte, prueba algo pequeño. Un día de prueba, una versión simple, un experimento de 1 hora.",
                ventajas=[
                    "Aprendes rápido",
                    "Bajo riesgo",
                    "Decisiones basadas en datos reales",
                ],
                desventajas=[
                    " Puede haber resistencia inicial",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="El fallo temprano es aprendizaje, no fracaso.",
                tecnologias=["Prototipo", "MVP"],
            ),
        ]
        
        return soluciones_default[index % len(soluciones_default)]
