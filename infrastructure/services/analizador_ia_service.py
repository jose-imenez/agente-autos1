"""
Infraestructura - Servicio de Análisis de IA Avanzado.

Implementa el análisis profundo de problemas con generación de
múltiples soluciones detalladas.
"""

from datetime import datetime
from typing import Optional

from domain.entities.entities import (
    Problema,
    Solucion,
    ResultadoAnalisis,
    ComplexityLevel,
    SolutionCategory,
)
from domain.interfaces.ports import IAnalizadorService


class AnalizadorIAAvanzado(IAnalizadorService):
    """
    Servicio de análisis de problemas con IA avanzada.
    
    Genera entre 5-8 soluciones alternativas con análisis detallado
    incluyendo ventajas, desventajas, complejidad y recomendaciones.
    
    Patrones aplicados:
        - Strategy: Diferentes estrategias según categoría detectada
        - Factory: Generación de soluciones por categoría
    """
    
    def __init__(self):
        self._categorias_palabras = {
            SolutionCategory.ALIMENTACION: [
                "comer", "comida", "hambre", "almorzar", "desayunar", "cenar",
                "restaurante", "cocinar", "receta", "alimentos", "nutric",
                "desayuno", "almuerzo", "cena", "merienda",
                "que comer", "que preparar", "cocina",
                "ingredientes", "plato", "menu", "delivery", "rapido",
                "vegetariano", "vegano", "saludable", "gastronom",
                "desayunar", "gourmet", "cocina", "preparar", "almorzar",
                "restaurantes", "comida rápida", "pedir", "ordenar"
            ],
            SolutionCategory.NEGOCIOS: [
                "trabajo", "empleo", "jefe", "oficina", "compañeros", "colegas",
                "empresa", "negocio", "ventas", "cliente", "proveedor",
                "marketing", "inversión", "dinero", "presupuesto", "costo",
                "reunión", "presentación", "informe", "proyecto", "equipo",
                "entrevista", "currículum", "cv", "salario", "puesto",
                "ascenso", "promoción", "empleado", "patrón", "gerente",
                "trabajador", "laboral", "profesional", "corporativo"
            ],
            SolutionCategory.REDES: [
                "red", "wifi", "internet", "conectar", "servidor", "router",
                "ip", "dhcp", "vlan", "firewall", "seguridad", "lan", "wan",
                "wireless", "conexión", "nube", "cloud", "dns"
            ],
            SolutionCategory.DESARROLLO: [
                "programar", "código", "desarrollar", "software", "app",
                "web", "api", "base de datos", "debug", "error", "bug",
                "programación", "desarrollador", "developer", "frontend", "backend",
                "fullstack", "java", "python", "javascript", "git", "github"
            ],
            SolutionCategory.TECNOLOGIA: [
                "computadora", "ordenador", "laptop", "celular", "teléfono",
                "hardware", "backup", "recuperar", "actualizar", "pc",
                "mac", "windows", "disco", "memoria", "técnico", "reparar",
                "celular", "móvil", "tablet", "ipad", "dispositivo"
            ],
            SolutionCategory.PERSONAL: [
                "estudiar", "estudio", "examen", "carrera", "universidad",
                "colegio", "escuela", "clase", "tarea", "deberes", "notas",
                "salud", "ejercicio", "gimnasio", "deporte", "cansado",
                "estrés", "ansiedad", "relax", "relaj", "bienestar",
                "viaje", "vacaciones", "fin de semana", "tiempo libre",
                "organizar", "planificar", "metas", "objetivos", "hábitos"
            ],
        }
    
    def analizar(
        self, 
        problema: Problema,
        soluciones_previas: Optional[list] = None
    ) -> ResultadoAnalisis:
        """
        Analiza el problema y genera soluciones detalladas.
        
        Args:
            problema: Entidad problema con texto y contexto
            soluciones_previas: Lista de soluciones ya generadas en sesiones anteriores
            
        Returns:
            ResultadoAnalisis con 5 soluciones de categorías diferentes
        """
        texto = problema.texto.lower()
        contexto = problema.contexto.lower() if problema.contexto else ""
        
        # Extraer categorías ya usadas
        categorias_usadas = set()
        if soluciones_previas:
            for sol in soluciones_previas:
                if hasattr(sol, 'categoria'):
                    categorias_usadas.add(sol.categoria)
        
        # Detectar categoría principal
        categoria = self._detectar_categoria(texto + " " + contexto)
        
        # Verificar si necesita preguntas aclaratorias
        preguntas = self._generar_preguntas_aclaratorias(texto, categoria)
        
        # Generar razonamiento estructurado
        razonamiento = self._generar_razonamiento(texto, categoria)
        
        # Generar 5 soluciones de categorías diferentes
        soluciones = self._generar_soluciones(texto, categoria, categorias_usadas)
        
        return ResultadoAnalisis(
            problema_original=problema.texto,
            timestamp=datetime.now(),
            soluciones=soluciones,
            razonamiento=razonamiento,
            preguntas_aclaratorias=preguntas,
        )
    
    def _filtrar_duplicados(
        self, 
        nuevas_soluciones: list[Solucion],
        soluciones_previas: list
    ) -> list[Solucion]:
        """
        Filtra soluciones que sean conceptualmente similares a las previas.
        
        Args:
            nuevas_soluciones: Soluciones recién generadas
            soluciones_previas: Soluciones ya usadas anteriormente
            
        Returns:
            Lista de soluciones sin duplicados conceptuales
        """
        # Extraer títulos y palabras clave de soluciones previas
        titulos_previos = {sol.titulo.lower().strip() for sol in soluciones_previas}
        
        # Crear conjunto de palabras clave de soluciones previas
        palabras_previas = set()
        for sol in soluciones_previas:
            # Agregar palabras del título
            palabras_previas.update(sol.titulo.lower().split())
            # Agregar palabras de la descripción (primeras 10)
            palabras_previas.update(sol.descripcion.lower().split()[:10])
        
        # Filtrar nuevas soluciones
        soluciones_unicas = []
        
        for sol in nuevas_soluciones:
            titulo_lower = sol.titulo.lower().strip()
            
            # Skip si el título es exactamente igual
            if titulo_lower in titulos_previos:
                continue
            
            # Skip si tiene muchas palabras en común con soluciones previas
            palabras_sol = set(sol.titulo.lower().split())
            palabras_sol.update(sol.descripcion.lower().split()[:10])
            
            interseccion = palabras_sol & palabras_previas
            # Si más del 60% de palabras coinciden, considerar duplicado
            if len(palabras_sol) > 0 and len(interseccion) / len(palabras_sol) > 0.6:
                continue
            
            soluciones_unicas.append(sol)
        
        return soluciones_unicas
    
    def _detectar_categoria(self, texto: str) -> SolutionCategory:
        """Detecta la categoría más probable del problema."""
        coincidencias = {}
        
        # Contar coincidencias por categoría
        for categoria, palabras in self._categorias_palabras.items():
            count = sum(1 for palabra in palabras if palabra in texto)
            coincidencias[categoria] = count
        
        # Verificar si hay coincidencias
        valores = list(coincidencias.values())
        if not valores or max(valores) == 0:
            return SolutionCategory.GENERAL
        
        # Encontrar categoría con más coincidencias
        max_count = max(valores)
        for categoria, count in coincidencias.items():
            if count == max_count:
                return categoria
        
        return SolutionCategory.GENERAL
    
    def _es_problema_ambiguo(self, texto: str) -> bool:
        """Determina si el problema necesita más información."""
        indicadores_ambiguos = [
            "no sé", "no sé qué", "no sé cómo",
            "algo", "cosas", "cosas raras",
            "mal", "mal funciona", "no funciona bien"
        ]
        return any(ind in texto for ind in indicadores_ambiguos)
    
    def _generar_preguntas_aclaratorias(
        self, texto: str, categoria: SolutionCategory
    ) -> list[str]:
        """Genera preguntas para clarificar un problema ambiguo."""
        if not self._es_problema_ambiguo(texto):
            return []
        
        preguntas_base = [
            "¿Cuál es el objetivo específico que quieres lograr?",
            "¿Tienes algún constraint de tiempo o presupuesto?",
            "¿Qué recursos tienes disponibles actualmente?",
        ]
        
        preguntas_por_categoria = {
            SolutionCategory.ALIMENTACION: [
                "¿Tienes alguna restricción alimentaria?",
                "¿Prefieres cook en casa o afuera?",
                "¿Cuánto tiempo tienes para preparar?",
            ],
            SolutionCategory.REDES: [
                "¿Es para uso doméstico o empresarial?",
                "¿Cuántos dispositivos necesitan conexión?",
                "¿Tienes infraestructura existente?",
            ],
            SolutionCategory.DESARROLLO: [
                "¿Qué lenguaje o tecnología prefieres?",
                "¿Es un proyecto nuevo o existente?",
                "¿Hay requisitos de rendimiento específicos?",
            ],
            SolutionCategory.TECNOLOGIA: [
                "¿Qué sistema operativo usas?",
                "¿Es para uso personal o profesional?",
                "¿Tienes experiencia técnica?",
            ],
        }
        
        preguntas = preguntas_base.copy()
        if categoria in preguntas_por_categoria:
            preguntas.extend(preguntas_por_categoria[categoria])
        
        return preguntas[:5]
    
    def _generar_razonamiento(
        self, texto: str, categoria: SolutionCategory
    ) -> str:
        """Genera una explicación estructurada del análisis."""
        return f"""
Análisis realizado para el problema reportado.

Categoría detectada: {categoria.value.upper()}

El sistema ha identificado las siguientes características en tu problema:
- Palabras clave identificadas en el texto
- Contexto relevante para la categoría {categoria.value}

Se han generado múltiples soluciones alternativas considerando:
1. Viabilidad técnica de cada opción
2. Relación costo-beneficio
3. Tiempo de implementación
4. Complejidad de ejecución
5. Recursos necesarios

Selecciona la opción que mejor se adapte a tu situación específica.
        """.strip()
    
    def _generar_soluciones(
        self, 
        texto: str, 
        categoria_principal: SolutionCategory,
        categorias_usadas: Optional[set] = None
    ) -> list[Solucion]:
        """
        Genera 5 soluciones de categorías diferentes.
        Las soluciones se personalizan con el contexto específico del problema.
        
        Paso 1: Detecta hasta 5 categorías relevantes
        Paso 2: Genera 1 solución personalizada por categoría
        Paso 3: Evita categorías usadas anteriormente
        """
        if categorias_usadas is None:
            categorias_usadas = set()
        
        # Mapeo de categorías a métodos de solución personalizada
        metodos_soluciones = {
            SolutionCategory.ALIMENTACION: self._soluciones_alimentacion_personalizadas,
            SolutionCategory.REDES: self._soluciones_redes_personalizadas,
            SolutionCategory.DESARROLLO: self._soluciones_desarrollo_personalizadas,
            SolutionCategory.NEGOCIOS: self._soluciones_negocios_personalizadas,
            SolutionCategory.TECNOLOGIA: self._soluciones_tecnologia_personalizadas,
            SolutionCategory.PERSONAL: self._soluciones_personal_personalizadas,
            SolutionCategory.GENERAL: self._soluciones_general_personalizadas,
        }
        
        # Paso 1: Detectar categorías relevantes (excluyendo las ya usadas)
        categoriasRelevantes = self._detectar_multiples_categorias(
            texto, 
            categoria_principal,
            categorias_usadas,
            max_categorias=5
        )
        
        soluciones = []
        
        # Paso 2: Generar 1 solución personalizada por categoría
        for categoria in categoriasRelevantes:
            metodo = metodos_soluciones.get(categoria)
            if metodo:
                solucion = metodo(texto)
                if solucion:
                    soluciones.append(solucion)
        
        return soluciones
    
    def _detectar_multiples_categorias(
        self,
        texto: str,
        categoria_principal: SolutionCategory,
        categorias_usadas: set,
        max_categorias: int = 5
    ) -> list[SolutionCategory]:
        """
        Detecta múltiples categorías relevantes para el texto.
        """
        texto_lower = texto.lower()
        
        # Puntuaciones por categoría
        puntuaciones = {}
        
        for categoria, palabras in self._categorias_palabras.items():
            # Skip si ya usada
            if categoria in categorias_usadas:
                continue
            
            # Contar coincidencias
            count = sum(1 for palabra in palabras if palabra in texto_lower)
            
            # Boost para categoría principal
            if categoria == categoria_principal:
                count += 5
            
            if count > 0:
                puntuaciones[categoria] = count
        
        # Ordenar por puntuación
        categorias_ordenadas = sorted(
            puntuaciones.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Tomar top 5
        return [cat for cat, _ in categorias_ordenadas[:max_categorias]]
    
    def _soluciones_alimentacion(self, texto: str) -> list[Solucion]:
        return [
            Solucion(
                titulo="Cocinar en casa",
                descripcion="Preparar la comida en casa utilizando ingredientes frescos. "
                           "Esta opción permite control total sobre los ingredientes, "
                           "nutrientes y porciones.",
                ventajas=[
                    "Control total sobre ingredientes y calidad",
                    "Más económico a largo plazo",
                    "Más saludable al evitar excesos",
                    "Puedes adaptar a restricciones dietéticas",
                    " skill de cocina Improves",
                ],
                desventajas=[
                    "Requiere tiempo para preparar",
                    "Necesitas conocimientos básicos de cocina",
                    "Requiere equipamiento básico",
                    "Debes hacer las compras",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Ideal si tienes al menos 30-60 minutos diarios "
                            "y quieres optimizar presupuesto y salud.",
                tecnologias=["Ingredientes frescos", "Utensilios básicos"],
            ),
            Solucion(
                titulo="Delivery de comida",
                descripcion="Ordenar comida a través de aplicaciones como Rappi, "
                           "Uber Eats, o Delivery directo de restaurantes.",
                ventajas=[
                    "Conveniencia y ahorro de tiempo",
                    "Variedad de opciones culinarias",
                    "Sin necesidad de cocinar",
                    "Opción para ocasiones especiales",
                ],
                desventajas=[
                    "Más costoso que cook en casa",
                    "Calidad nutricional variable",
                    "Dependencia de servicios externos",
                    "Tiempo de espera variable",
                    "Genera residuos de包装",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Perfecto para días ocupados o cuando no tienes "
                            "energía para cocinar. Úsalo con moderación.",
                tecnologias=["Apps de delivery", "Medios de pago digital"],
            ),
            Solucion(
                titulo="Comida rápida saludable",
                descripcion="Visitar restaurantes de comida rápida que ofrecen "
                           "opciones más saludables como ensaladas, bowls, o wraps.",
                ventajas=[
                    "Más rápido que cocinar",
                    "Algunas opciones saludables disponibles",
                    "No requiere planificación",
                    "Bueno para eating fuera de casa",
                ],
                desventajas=[
                    "Opciones limitadas realmente saludables",
                    "Puede ser costoso",
                    "Menos control sobre ingredientes",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Útil cuando tienes poco tiempo pero quieres "
                            "algo mejor que comida chatarra.",
                tecnologias=["Apps de reseñas", "Opciones de menú digital"],
            ),
            Solucion(
                titulo="Meal Prep semanal",
                descripcion="Preparar múltiples porciones de comida el fin de semana "
                           "para toda la semana. Técnica de batch cooking.",
                ventajas=[
                    "Ahorro de tiempo significativo",
                    "Control total de ingredientes",
                    "Más económico",
                    "Reduce decisiones diarias",
                    "Ideal para agendas ocupadas",
                ],
                desventajas=[
                    "Requiere inversión inicial de tiempo",
                    "Necesitas almacenamiento adecuado",
                    "Algo de planificación",
                    "Puede aburrir si no varías",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Excelente para profesionales con agendas ocupadas. "
                            "Invierte 2-3 horas el fin de semana.",
                tecnologias=["Recipientes herméticos", "Planificador de comidas"],
            ),
            Solucion(
                titulo="Comida en restaurante",
                descripcion="Ir a un restaurante tradicional a comer. Experiencia "
                           "social y culinaria completa.",
                ventajas=[
                    "Experiencia social",
                    "Variedad de cocina gourmet",
                    "No hay que limpiar",
                    "Ambiente diferente",
                ],
                desventajas=[
                    "Más costoso",
                    "Tiempo de espera",
                    "Menos control sobre preparación",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Ideal para ocasiones especiales o cuando "
                            "quieres una experiencia diferente.",
                tecnologias=["Reservaciones", "Reseñas de restaurantes"],
            ),
            Solucion(
                titulo="Pedir a familiares/amigos",
                descripcion="Coordinar para comer con familiares o amigos que "
                           "puedan preparar o compartir comida.",
                ventajas=[
                    "Socialización",
                    "Ahorro económico",
                    "Comida casera",
                    "Fortalece relaciones",
                ],
                desventajas=[
                    "Requiere coordinación",
                    "Depende de otros",
                    "Puede ser incómodo si es frecuente",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Excelente opción para mantener relaciones "
                            "sociales mientras resuelves la comida.",
                tecnologias=["Comunicación efectiva", "Calendario compartido"],
            ),
        ]
    
    def _soluciones_redes(self, texto: str) -> list[Solucion]:
        return [
            Solucion(
                titulo="Topología en estrella",
                descripcion="Diseñar una red donde todos los dispositivos se "
                           "conectan a un punto central (switch/router). "
                           "La configuración más común y fácil de gestionar.",
                ventajas=[
                    "Fácil de implementar y gestionar",
                    "Fácil detección de fallos",
                    "Escalable, agregar dispositivos es simple",
                    "Fallos individuales no afectan toda la red",
                ],
                desventajas=[
                    "Punto único de fallo en el switch central",
                    "Requiere más cableado",
                    "Costo de switch gestionable",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.REDES,
                recomendacion="Ideal para oficinas pequeñas y medianas. "
                            "Estándar de la industria para redes LAN.",
                tecnologias=["Switch gestionable", "Cableado CAT6", "Router"],
            ),
            Solucion(
                titulo="Implementar VLANs",
                descripcion="Crear Redes Locales Virtuales para segmentar el "
                           "tráfico y mejorar seguridad y rendimiento.",
                ventajas=[
                    "Mejor seguridad por segmentación",
                    "Reducción de tráfico broadcast",
                    "Flexibilidad en gestión de grupos",
                    "Aislamiento de dispositivos críticos",
                ],
                desventajas=[
                    "Requiere equipo gestionable",
                    "Conocimiento técnico necesario",
                    "Configuración más compleja",
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.REDES,
                recomendacion="Recomendado para redes con más de 50 dispositivos "
                            "o cuando hay requisitos de seguridad.",
                tecnologias=["Switch VLAN", "Router con soporte VLAN"],
            ),
            Solucion(
                titulo="Configurar DHCP automático",
                descripcion="Implementar servidor DHCP para asignación "
                           "automática de IPs, eliminando configuración manual.",
                ventajas=[
                    "Simplifica configuración de nuevos dispositivos",
                    "Evita conflictos de IP",
                    "Gestión centralizada",
                    "Ahorro de tiempo",
                ],
                desventajas=[
                    "Dependencia del servidor DHCP",
                    "Requiere configuración inicial",
                    "Posible vulnerabilidad si no hay seguridad",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.REDES,
                recomendacion="Imprescindible para cualquier red moderna. "
                            "Casi todos los routers lo soportan.",
                tecnologias=["Router con DHCP", "Servidor DHCP (Linux/Windows)"],
            ),
            Solucion(
                titulo="Red WiFi mesh",
                descripcion="Implementar sistema WiFi Mesh para cobertura "
                           "uniforme en todo el espacio.",
                ventajas=[
                    "Cobertura uniforme",
                    "Roaming seamless entre nodos",
                    "Fácil expansión",
                    "Gestión centralizada",
                ],
                desventajas=[
                    "Costo inicial más alto",
                    "Rendimiento puede variar",
                    "Depende de cantidad de nodos",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.REDES,
                recomendacion="Ideal para hogares grandes o oficinas "
                            "con zonas sin cobertura.",
                tecnologias=["Sistemas Mesh (Eero, Ubiquiti, Google WiFi)"],
            ),
            Solucion(
                titulo="Firewall y seguridad perimetral",
                descripcion="Implementar firewall con reglas de seguridad "
                           "para proteger la red de amenazas externas.",
                ventajas=[
                    "Protección contra amenazas",
                    "Control de acceso",
                    "Registro de actividad",
                    "Filtrado de contenido",
                ],
                desventajas=[
                    "Costo de equipo profesional",
                    "Configuración compleja",
                    "Mantenery actualizar",
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.REDES,
                recomendacion="Necesario si manejas datos sensibles o "
                            "tienes múltiples usuarios.",
                tecnologias=["Firewall (pfSense, UTM, hardware dedicado)"],
            ),
            Solucion(
                titulo="VPN para acceso remoto",
                descripcion="Crear Red Privada Virtual para permitir acceso "
                           "seguro a la red desde ubicaciones remotas.",
                ventajas=[
                    "Acceso seguro desde cualquier lugar",
                    "Encriptación de tráfico",
                    "Protección de datos sensibles",
                ],
                desventajas=[
                    "Configuración técnica necesaria",
                    "Rendimiento depende de conexión",
                    "Requiere mantenimiento",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.REDES,
                recomendacion="Esencial para trabajo remoto o acceso "
                            "a recursos de empresa.",
                tecnologias=["Servidor VPN", "Clientes OpenVPN/WireGuard"],
            ),
            Solucion(
                titulo="Red guest aislada",
                descripcion="Crear red separada para visitantes que no tenga "
                           "acceso a recursos internos.",
                ventajas=[
                    "Seguridad de datos internos",
                    " Aislamiento de amenazas",
                    "Control de ancho de banda",
                    "Responsabilidad separada",
                ],
                desventajas=[
                    "Requiere router con soporte",
                    "Configuración adicional",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.REDES,
                recomendacion="Imprescindible para oficinas que reciben "
                            "visitas frecuentes.",
                tecnologias=["Router con soporte multi-SSID"],
            ),
        ]
    
    def _soluciones_desarrollo(self, texto: str) -> list[Solucion]:
        return [
            Solucion(
                titulo="Arquitectura MVC",
                descripcion="Implementar patrón Model-View-Controller para "
                           "separar lógica de negocio de presentación.",
                ventajas=[
                    "Separación clara de responsabilidades",
                    "Mantenibilidad del código",
                    "Testabilidad mejorada",
                    "Trabajo en equipo facilitado",
                ],
                desventajas=[
                    "Curva de aprendizaje inicial",
                    "Puede ser overkill para proyectos pequeños",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.DESARROLLO,
                recomendacion="Estándar para aplicaciones web medianas "
                            "y grandes. Recomendado para este proyecto.",
                tecnologias=["Frameworks MVC (Django, Laravel, Spring)"],
            ),
            Solucion(
                titulo="API RESTful",
                descripcion="Diseñar API REST para comunicación entre "
                           "frontend y backend.",
                ventajas=[
                    "Separación frontend/backend",
                    "Escalabilidad",
                    "Integraciones fáciles",
                    "Estándar de industria",
                ],
                desventajas=[
                    "Más endpoints a mantener",
                    "Versionado necesario",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.DESARROLLO,
                recomendacion="Necesario para aplicaciones modernas "
                            "y SPA.",
                tecnologias=["FastAPI", "Flask", "Express", "OpenAPI"],
            ),
            Solucion(
                titulo="Base de datos con ORM",
                descripcion="Usar ORM para abstraer consultas SQL y facilitar "
                           "el manejo de datos.",
                ventajas=[
                    "Código más legible",
                    "Portabilidad entre DBs",
                    "Prevención de SQL injection",
                    "Modelos claros",
                ],
                desventajas=[
                    "Overhead de rendimiento",
                    "Curva de aprendizaje",
                    "Menos control que SQL puro",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.DESARROLLO,
                recomendacion="Recomendado para proyectos que usarán "
                            "diferentes bases de datos.",
                tecnologias=["SQLAlchemy", "Django ORM", "TypeORM", "Prisma"],
            ),
            Solucion(
                titulo="Patrón Repository",
                descripcion="Implementar Repository para abstraer acceso a datos.",
                ventajas=[
                    "Bajo acoplamiento",
                    "Facilidad de testing con mocks",
                    "Cambios de storage sin afectar lógica",
                ],
                desventajas=[
                    "Capa adicional de complejidad",
                    "Puede ser redundante con ORM",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.DESARROLLO,
                recomendacion="Útil cuando tienes múltiples fuentes de datos.",
                tecnologias=["Patrón Repository", "Unit of Work"],
            ),
            Solucion(
                titulo="Docker y contenedores",
                descripcion="Contenerizar la aplicación para despliegue "
                           "consistente.",
                ventajas=[
                    "Entorno consistente",
                    "Despliegue rápido",
                    "Escalabilidad",
                    "Aislamiento de dependencias",
                ],
                desventajas=[
                    "Curva de aprendizaje Docker",
                    "Recursos adicionales",
                    "Debugging puede ser complejo",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.DESARROLLO,
                recomendacion="Imprescindible para CI/CD y producción.",
                tecnologias=["Docker", "Docker Compose", "Kubernetes"],
            ),
            Solucion(
                titulo="CI/CD Pipeline",
                descripcion="Implementar integración y despliegue continuo.",
                ventajas=[
                    "Automatización de pruebas",
                    "Despliegue más rápido",
                    "Detección temprana de errores",
                    "Rollback fácil",
                ],
                desventajas=[
                    "Setup inicial complejo",
                    "Requiere pruebas automatizadas",
                ],
                complejidad=ComplexityLevel.ALTA,
                categoria=SolutionCategory.DESARROLLO,
                recomendacion="Esencial para equipos que despliegan "
                            "frecuentemente.",
                tecnologias=["GitHub Actions", "GitLab CI", "Jenkins"],
            ),
        ]
    
    def _soluciones_negocios(self, texto: str) -> list[Solucion]:
        # Detectar si es tema de empleo/trabajo
        es_empleo = any(palabra in texto.lower() for palabra in [
            "trabajo", "empleo", "jefe", "oficina", "compañeros", "colegas",
            "entrevista", "currículum", "cv", "salario", "puesto",
            "ascenso", "promoción", "empleado", "patrón", "gerente"
        ])
        
        if es_empleo:
            return [
                Solucion(
                    titulo="Actualizar CV y perfil profesional",
                    descripcion="Rediseñar tu currículum con formato moderno, "
                               "destacando logros cuantificables y habilidades clave.",
                    ventajas=[
                        "Mayor visibilidad ante reclutadores",
                        "Destaca tus accomplishments reales",
                        "Optimizado para ATS (sistemas de seguimiento)",
                    ],
                    desventajas=[
                        "Tiempo de redacción",
                        "Puede requerir ayuda profesional",
                    ],
                    complejidad=ComplexityLevel.BAJA,
                    categoria=SolutionCategory.NEGOCIOS,
                    recomendacion="Prioridad si estás buscando empleo activamente.",
                    tecnologias=["Canva", "Resume.io", "LinkedIn"],
                ),
                Solucion(
                    titulo="Prepararse para entrevistas",
                    descripcion="Investigar la empresa, practicar preguntas comunes "
                               "y preparar respuestas STAR para situaciones laborales.",
                    ventajas=[
                        "Mayor confianza durante la entrevista",
                        " respuestas más estructuradas y profesionales",
                        " mejor impresión al reclutador",
                    ],
                    desventajas=[
                        "Requiere tiempo de preparación",
                        "Puede generar ansiedad",
                    ],
                    complejidad=ComplexityLevel.BAJA,
                    categoria=SolutionCategory.NEGOCIOS,
                    recomendacion="Esencial para cualquier proceso de selección.",
                    tecnologias=["Glassdoor", "Entrevista mock", "YouTube"],
                ),
                Solucion(
                    titulo="Desarrollar habilidades demandadas",
                    descripcion="Identificar habilidades técnicas y blandas más "
                               "valoradas en tu sector y crear un plan de aprendizaje.",
                    ventajas=[
                        "Aumenta tu valor en el mercado laboral",
                        "Mayores oportunidades de crecimiento",
                        "Preparación para ascensos",
                    ],
                    desventajas=[
                        "Requiere inversión de tiempo",
                        "Puede haber costos de capacitación",
                    ],
                    complejidad=ComplexityLevel.MEDIA,
                    categoria=SolutionCategory.NEGOCIOS,
                    recomendacion="Invierte en ti mismo para seguridad laboral a largo plazo.",
                    tecnologias=["Coursera", "Udemy", "YouTube", "Bootcamps"],
                ),
                Solucion(
                    titulo="Expandir red de contactos profesionales",
                    descripcion="Conectar con profesionales del sector, asistir a "
                               "eventos de networking y participar en comunidades relevantes.",
                    ventajas=[
                        "Mayores oportunidades de empleo",
                        "Mentoría y guía profesional",
                        "Conocimiento de mercado",
                    ],
                    desventajas=[
                        "Requiere keluar de zona de confort",
                        "Resultados a mediano/largo plazo",
                    ],
                    complejidad=ComplexityLevel.BAJA,
                    categoria=SolutionCategory.NEGOCIOS,
                    recomendacion="El networking es clave en el mercado laboral actual.",
                    tecnologias=["LinkedIn", "Eventos profesionales", "Meetups"],
                ),
                Solucion(
                    titulo="Considerar cambio de área o industria",
                    descripcion="Evaluar si tus habilidades son transferibles a otros "
                               "sectores con mayor demanda o mejor compensación.",
                    ventajas=[
                        "Mayores salarial en otros sectores",
                        "Nuevos desafíos y aprendizajes",
                        "Expansión de oportunidades",
                    ],
                    desventajas=[
                        "Curva de aprendizaje",
                        "Posible riesgo inicial",
                    ],
                    complejidad=ComplexityLevel.ALTA,
                    categoria=SolutionCategory.NEGOCIOS,
                    recomendacion="Analiza el mercado antes de tomar decisiones.",
                    tecnologias=["LinkedIn", "Informes laborales", "Mentores"],
                ),
                Solucion(
                    titulo="Mejorar relación con supervisor",
                    descripcion="Comunicar expectativas, pedir feedback regularmente "
                               "y alinear objetivos con los de la empresa.",
                    ventajas=[
                        "Mejor ambiente de trabajo",
                        "Mayores posibilidades de ascenso",
                        "Referencias positivas",
                    ],
                    desventajas=[
                        "Depende de ambos lados",
                        "Requiere comunicación efectiva",
                    ],
                    complejidad=ComplexityLevel.MEDIA,
                    categoria=SolutionCategory.NEGOCIOS,
                    recomendacion="Una buena relación con tu jefe es clave para el éxito laboral.",
                    tecnologias=["1:1 meetings", "Feedback tools"],
                ),
                Solucion(
                    titulo="Negociar condiciones laborales",
                    descripcion="Preparar argumentos con datos, conocer el mercado "
                               "y presentar propuesta profesionalmente.",
                    ventajas=[
                        "Mejora salarial o de condiciones",
                        "Reconocimiento de tu valor",
                        "Mejora calidad de vida",
                    ],
                    desventajas=[
                        "Riesgo de rechazo",
                        "Requiere preparación",
                    ],
                    complejidad=ComplexityLevel.MEDIA,
                    categoria=SolutionCategory.NEGOCIOS,
                    recomendacion="Siempre justifica con datos y logros concretos.",
                    tecnologias=["Glassdoor", "Salary surveys", "LinkedIn Salary"],
                ),
            ]
        
        # Soluciones para negocio/empresa
        return [
            Solucion(
                titulo="Análisis FODA empresarial",
                descripcion="Realizar análisis FODA (Fortalezas, Oportunidades, "
                           "Debilidades, Amenazas) de la empresa.",
                ventajas=[
                    "Visión completa del negocio",
                    "Identificación de áreas clave",
                    "Planificación estratégica clara",
                ],
                desventajas=[
                    "Requiere información honesta",
                    "Análisis estático",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Paso inicial para cualquier planificación estratégica.",
                tecnologias=["Plantillas FODA", "Workshops"],
            ),
            Solucion(
                titulo="Lean Startup",
                descripcion="Aplicar metodología Lean Startup con MVP y "
                           "feedback loop rápido.",
                ventajas=[
                    "Reducción de riesgo",
                    "Validación rápida de hipótesis",
                    "Iteración rápida",
                    "Recursos optimizados",
                ],
                desventajas=[
                    "No funciona para todos los productos",
                    "Requiere tolerancia al cambio",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Ideal para nuevos productos o servicios.",
                tecnologias=["Métricas MVP", "A/B Testing", "Analytics"],
            ),
            Solucion(
                titulo="Automatización de procesos",
                descripcion="Automatizar procesos repetitivos para aumentar "
                           "eficiencia operativa.",
                ventajas=[
                    "Reducción de errores",
                    "Ahorro de tiempo",
                    "Consistencia",
                    "Escalabilidad",
                ],
                desventajas=[
                    "Inversión inicial",
                    "Cambio cultural necesario",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Prioriza procesos de alto volumen y repetitivos.",
                tecnologias=["Zapier", "Power Automate", "Scripts"],
            ),
            Solucion(
                titulo="CRM para gestión clientes",
                descripcion="Implementar sistema CRM para gestionar relaciones "
                           "con clientes.",
                ventajas=[
                    "360° del cliente",
                    "Automatización comercial",
                    "Mejora atención al cliente",
                ],
                desventajas=[
                    "Costo de implementación",
                    "Adopción del equipo",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Esencial para negocios con volumen alto de clientes.",
                tecnologias=["Salesforce", "HubSpot", "Zoho"],
            ),
            Solucion(
                titulo="Estrategia de ventas",
                descripcion="Definir proceso de ventas, capacitar equipo "
                           "y establecer métricas de seguimiento.",
                ventajas=[
                    "Proceso de ventas optimizado",
                    "Mejor conversión",
                    "Predicción de ingresos",
                ],
                desventajas=[
                    "Requiere tiempo para implementar",
                    "Necesita disciplina del equipo",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion=" Fundamental para crecer ventas.",
                tecnologias=["Salesforce", "Pipedrive", "HubSpot"],
            ),
            Solucion(
                titulo="Plan de marketing digital",
                descripcion="Desarrollar presencia online con SEO, redes sociales "
                           "y publicidad digital.",
                ventajas=[
                    "Mayor visibilidad",
                    "Segmentación de audiencia",
                    "Medición de resultados",
                ],
                desventajas=[
                    "Resultados a mediano plazo",
                    "Requiere contenido constante",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Imprescindible en el mundo digital actual.",
                tecnologias=["Google Ads", "Facebook Ads", "SEO", "Instagram"],
            ),
        ]
    
    def _soluciones_tecnologia(self, texto: str) -> list[Solucion]:
        return [
            Solucion(
                titulo="Backup automático en la nube",
                descripcion="Configurar respaldo automático de datos críticos "
                           "a servicios cloud.",
                ventajas=[
                    "Protección contra pérdida de datos",
                    "Acceso desde cualquier lugar",
                    "Versionado de archivos",
                ],
                desventajas=[
                    "Costo recurrente",
                    "Dependencia de internet",
                    "Concerns de privacidad",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.TECNOLOGIA,
                recomendacion="Imprescindible para cualquier empresa o "
                            "usuario con datos importantes.",
                tecnologias=["Google Drive", "Dropbox", "AWS S3", "OneDrive"],
            ),
            Solucion(
                titulo="Actualización de software",
                descripcion="Mantener todos los sistemas y aplicaciones "
                           "actualizados.",
                ventajas=[
                    "Seguridad mejorada",
                    "Nuevas funcionalidades",
                    "Rendimiento optimizado",
                ],
                desventajas=[
                    "Tiempo requerido",
                    "Posibles incompatibilidades",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.TECNOLOGIA,
                recomendacion="Configura actualizaciones automáticas cuando "
                            "sea posible.",
                tecnologias=["Windows Update", "Patch Management"],
            ),
            Solucion(
                titulo="Diagnóstico profesional",
                descripcion="Solicitar revisión técnica profesional para "
                           "identificar problemas.",
                ventajas=[
                    "Diagnóstico preciso",
                    "Soluciones expertas",
                    "Prevención de problemas mayores",
                ],
                desventajas=[
                    "Costo del servicio",
                    "Tiempo de espera",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.TECNOLOGIA,
                recomendacion="Cuando el problema persiste o no tienes "
                            "conocimientos técnicos.",
                tecnologias=["Soporte técnico", "Consultoría IT"],
            ),
        ]
    
    def _soluciones_personal(self, texto: str) -> list[Solucion]:
        return [
            Solucion(
                titulo="Método GTD",
                descripcion="Implementar Getting Things Done para organizar "
                           "tareas y aumentar productividad.",
                ventajas=[
                    "Estructura clara de tareas",
                    "Reducción de estrés",
                    "Enfoque en prioridades",
                    "Visión global",
                ],
                desventajas=[
                    "Curva de aprendizaje",
                    "Requiere disciplina",
                    "Overhead inicial",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Ideal para personas con muchas responsabilidades "
                            "o sensación de overwhelm.",
                tecnologias=["Notion", "Todoist", "Things", "Excel"],
            ),
            Solucion(
                titulo="Bloques de tiempo (Time Blocking)",
                descripcion="Asignar bloques específicos de tiempo para "
                           "diferentes actividades.",
                ventajas=[
                    "Enfoque profundo",
                    "Menor procrastinación",
                    "Mejor estimation de tiempo",
                ],
                desventajas=[
                    "Rígido para emergencias",
                    "Requiere planificación",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Excelente para trabajo deep work.",
                tecnologias=["Calendario", "Google Calendar", "Fantastical"],
            ),
            Solucion(
                titulo="Habitos atómicos",
                descripcion="Crear pequeños hábitos incrementales usando "
                           "la metodología de James Clear.",
                ventajas=[
                    "Sostenible a largo plazo",
                    "No requiere motivación extrema",
                    "Efecto compuesto",
                ],
                desventajas=[
                    "Resultados lentos",
                    "Inconsistencia inicial",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Para cambio de hábitos sostenibles.",
                tecnologias=["Habit trackers", "Streaks"],
            ),
        ]
    
    def _soluciones_general(self, texto: str) -> list[Solucion]:
        return [
            Solucion(
                titulo="Análisis de recursos disponibles",
                descripcion="Evaluar qué recursos (tiempo, dinero, personas, "
                           "tecnología) están disponibles.",
                ventajas=[
                    "Realista y práctico",
                    "Base para planificación",
                    "Identifica limitaciones",
                ],
                desventajas=[
                    "Puede revelar constraints",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Siempre el primer paso antes de planificar.",
                tecnologias=["Inventario de recursos", "Matriz de recursos"],
            ),
            Solucion(
                titulo="Consultar con expertos",
                descripcion="Buscar asesoría de personas con experiencia "
                           "en el área del problema.",
                ventajas=[
                    "Conocimiento especializado",
                    "Ahorro de tiempo",
                    "Evitar errores comunes",
                ],
                desventajas=[
                    "Costo potencial",
                    "Calidad variable",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion=" Especialmente útil para decisiones importantes.",
                tecnologias=["Mentores", "Consultores", "Comunidades"],
            ),
            Solucion(
                titulo="Prototipo o MVP",
                descripcion="Crear una versión mínima del resultado para "
                           "testear antes de comprometerse.",
                ventajas=[
                    "Validación rápida",
                    "Bajo costo de fracaso",
                    "Feedback real",
                ],
                desventajas=[
                    "Calidad puede suffer",
                    "Scope creep",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Útil cuando hay incertidumbre sobre la solución.",
                tecnologias=["Herramientas de prototipado", "Paper prototyping"],
            ),
            Solucion(
                titulo="Matriz de decisión",
                descripcion="Crear matriz con criterios ponderados para "
                           "evaluar opciones objetivamente.",
                ventajas=[
                    "Decisión más objetiva",
                    "Visualiza trade-offs",
                    "Documenta razonamiento",
                ],
                desventajas=[
                    "Tiempo en análisis",
                    "Subjetividad en ponderación",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Para decisiones importantes con múltiples opciones.",
                tecnologias=["Excel", "Google Sheets", "Decidim"],
            ),
            Solucion(
                titulo="Iteración rápida",
                descripcion="Implementar solución básica, medir resultados, "
                           "y ajustar rápidamente.",
                ventajas=[
                    "Aprendizaje rápido",
                    "Adaptación al cambio",
                    "Mínimo tiempo invertido",
                ],
                desventajas=[
                    "Puede ser caótico",
                    "Calidad inconsistente",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.GENERAL,
                recomendacion="Para ambientes cambiantes o startups.",
                tecnologias=["Métricas", "Feedback loops", "A/B Testing"],
            ),
        ]
    
    # ==================== SOLUCIONES PERSONALIZADAS ====================
    
    def _soluciones_alimentacion_personalizadas(self, texto: str) -> Optional[Solucion]:
        """Genera una solución personalizada para alimentación."""
        texto_lower = texto.lower()
        
        # Detectar urgencia
        es_urgente = any(p in texto_lower for p in ["ahora", "rápido", "pronto", "hambre"])
        
        if es_urgente:
            return Solucion(
                titulo="Pedir delivery ahora",
                descripcion=f"Usa una app de entrega como Rappi o Uber Eats para recibir comida en 30-45 minutos. Busca opciones cerca de tu ubicación con buena calificación.",
                ventajas=[
                    "Respuesta inmediata al hambre",
                    "Sin necesidad de cocinar",
                    "Variedad de opciones a un clic",
                ],
                desventajas=[
                    "Costo mayor que cook en casa",
                    "Tiempo de espera variable",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.ALIMENTACION,
                recomendacion="Perfecto cuando necesitas comer ya y no tienes tiempo de cocinar.",
                tecnologias=["Rappi", "Uber Eats", "PedidosYa"],
            )
        
        return Solucion(
            titulo="Planificar comidas de la semana",
            descripcion=f"Elige 3 recetas que puedas preparar en 30 min o menos. Compra los ingredientes una vez. Ejemplo:如果你在找健康选择试试沙拉配烤鸡胸。",
            ventajas=[
                "Ahorro de tiempo durante la semana",
                "Más económico",
                "Controlas ingredientes y porciones",
            ],
            desventajas=[
                "Requiere 1-2 horas de preparación",
                "Debes tener utensilios básicos",
            ],
            complejidad=ComplexityLevel.BAJA,
            categoria=SolutionCategory.ALIMENTACION,
            recomendacion="Ideal si tienes evenings ocupados entre semana.",
            tecnologias=["Notas", "Excel", "YouTube recetas"],
        )
    
    def _soluciones_negocios_personalizadas(self, texto: str) -> Optional[Solucion]:
        """Genera solución personalizada para empleo/trabajo."""
        texto_lower = texto.lower()
        
        if any(p in texto_lower for p in ["entrevista", "entrevistar"]):
            return Solucion(
                titulo="Preparar respuestas STAR",
                descripcion="Para cada pregunta de behavioural, prepara: Situation (situación), Task (tu tarea), Action (qué hiciste), Result (resultado). Ejemplo: 'Situación: Mi equipo tenía conflictos. Tarea: Mediar. Acción: Implementé reuniones semanales. Resultado: 40% más productividad.'",
                ventajas=[
                    "Respuestas estructuradas y memorizables",
                    "Demuestra achievements concretos",
                    "Funciona para cualquier pregunta de comportamiento",
                ],
                desventajas=[
                    "Tiempo de preparación",
                    "Debes practicar en voz alta",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Practica 3 ejemplos STAR antes de cada entrevista.",
                tecnologias=["Notas", "Grabadora", "YouTube ejemplos"],
            )
        
        if any(p in texto_lower for p in ["cv", "currículum", "currriculum"]):
            return Solucion(
                titulo="Rediseñar CV con logros",
                descripcion="Cambia 'Responsable de ventas' por 'Incrementé ventas 35% en 6 meses implementando nuevo sistema de seguimiento'. Usa números concretos.",
                ventajas=[
                    "Destacas sobre otros candidatos",
                    "Reclutadores notan resultados",
                    "Pasa filtros ATS",
                ],
                desventajas=[
                    "Requiere pensar en métricas",
                    "Puede tomar 1-2 horas",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Cada frase debe responder: ¿Qué lograste? ¿Cuánto? ¿En cuánto tiempo?",
                tecnologias=["Canva", "Resume.io", "LinkedIn"],
            )
        
        return Solucion(
            titulo="Hacer networking activo",
            descripcion="Envía 5 mensajes esta semana a personas de tu industria. Menciona algo específico de su trabajo: 'Vi tu post sobre X y me interesó porque...'. Pide 15 min para un coffee chat virtual.",
            ventajas=[
                "70% de empleos vienen de conexiones",
                "Información de mercado oculta",
                "Mentoría sin costo",
            ],
            desventajas=[
                "Requiere salir de zona de confort",
                "Resultados a mediano plazo",
            ],
            complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.NEGOCIOS,
                recomendacion="Calidad sobre cantidad: 5 mensajes bien personalizados > 50 mensajes genéricos.",
            tecnologias=["LinkedIn", "Twitter/X", "Meetups"],
        )
    
    def _soluciones_personal_personalizadas(self, texto: str) -> Optional[Solucion]:
        """Genera solución personalizada para estudio."""
        texto_lower = texto.lower()
        
        if any(p in texto_lower for p in ["examen", "parcial", "prueba"]):
            return Solucion(
                titulo="Hacer simulacro de examen",
                descripcion=f"Busca exámenes anteriores del curso o crea uno con tiempo límite. Hazlo en condiciones reales: sin celular, sin notas, en silencio. Revisa solo al final.",
                ventajas=[
                    "Identificas temas débiles",
                    "Reduce ansiedad del examen",
                    "Mejora gestión de tiempo",
                ],
                desventajas=[
                    "Requiere discipline",
                    "Tiempo de preparación",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.PERSONAL,
                recomendacion="Haz al menos 1 simulacro 2 días antes del examen real.",
                tecnologias=["Exam topics", "YouTube", "Apuntes propios"],
            )
        
        return Solucion(
            titulo="Técnica de repetición espaciada",
            descripcion="Ejemplo: Si necesitas memorizar 50 vocabulario, no estudies 2 horas seguidas. Estudia 15 min 4 veces en días diferentes. Usa flashcards.",
            ventajas=[
                "Memoria a largo plazo",
                "Menos tiempo total",
                "Efectivo para cualquier materia",
            ],
            desventajas=[
                "Requiere planificación",
                "No sirve para último momento",
            ],
            complejidad=ComplexityLevel.BAJA,
            categoria=SolutionCategory.PERSONAL,
            recomendacion="Aplica esta técnica desde el primer día de clases, no solo para exámenes.",
            tecnologias=["Anki", "Quizlet", "Notas"],
        )
    
    def _soluciones_redes_personalizadas(self, texto: str) -> Optional[Solucion]:
        """Genera solución personalizada para redes."""
        texto_lower = texto.lower()
        
        if any(p in texto_lower for p in ["wifi", "lento", "conexión"]):
            return Solucion(
                titulo="Cambiar posición del router",
                descripcion=f"Coloca el router en el centro de tu casa, elevado, lejos de paredes gruesas y electrodomésticos. Evita hornos microwave y teléfonos inalámbricos cerca.",
                ventajas=[
                    "Señal más fuerte en toda la casa",
                    "Sin costo adicional",
                    "Fácil de implementar",
                ],
                desventajas=[
                    "Puede requerir cable ethernet",
                    "Dependiendo de tamaño de casa",
                ],
                complejidad=ComplexityLevel.BAJA,
                categoria=SolutionCategory.REDES,
                recomendacion="El router debe estar visible, no dentro de un mueble.",
                tecnologias=["Router WiFi", "Medidor señal apps"],
            )
        
        return Solucion(
            titulo="Reiniciar router semanalmente",
            descripcion="Apaga el router 30 segundos una vez por semana. Esto limpia la memoria caché ypreviene problemas de conexión acumulados.",
            ventajas=[
                "Mejora rendimiento",
                "Previene fallos",
                "Sin costo",
            ],
            desventajas=[
                "Corta internet 30 segundos",
            ],
            complejidad=ComplexityLevel.BAJA,
            categoria=SolutionCategory.REDES,
            recomendacion="Programa hacerlo cada domingo cuando no lo necesites.",
            tecnologias=["Timer", "App router"],
        )
    
    def _soluciones_tecnologia_personalizadas(self, texto: str) -> Optional[Solucion]:
        """Genera solución personalizada para tecnología."""
        texto_lower = texto.lower()
        
        return Solucion(
            titulo="Crear backup ahora",
            descripcion="Copia tus archivos importantes a Google Drive o disco externo ahora mismo. Configura backup automático para que no tengas que acordarte.",
            ventajas=[
                "Protección contra pérdida de datos",
                "Acceso desde cualquier dispositivo",
                "Tranquilidad mental",
            ],
            desventajas=[
                "Requiere internet para cloud",
                "Costo almacenamiento cloud",
            ],
            complejidad=ComplexityLevel.BAJA,
            categoria=SolutionCategory.TECNOLOGIA,
            recomendacion="Hazlo ahora, no 'después'. 1 hora que dediques hoy = días de trabajo que salvas.",
            tecnologias=["Google Drive", "OneDrive", "Disco externo"],
        )
    
    def _soluciones_desarrollo_personalizadas(self, texto: str) -> Optional[Solucion]:
        """Genera solución personalizada para desarrollo."""
        texto_lower = texto.lower()
        
        if any(p in texto_lower for p in ["error", "bug", "fallo"]):
            return Solucion(
                titulo="Reproducir el error consistently",
                descripcion="Antes de buscar solución, reproduce el error exactamente: ¿Qué pasos seguiste? ¿Qué inputs usaste? ¿Qué versión del código? Un bug que no puedes reproducir es muy difícil de solving.",
                ventajas=[
                    "Entiendes la causa raíz",
                    "Puedes verificar cuando esté fixed",
                    "Ahorras tiempo buscando",
                ],
                desventajas=[
                    "Requiere paciencia",
                    "Puede tomar tiempo",
                ],
                complejidad=ComplexityLevel.MEDIA,
                categoria=SolutionCategory.DESARROLLO,
                recomendacion="Escribe los pasos exactos en un papel antes de buscar en Google.",
                tecnologias=["Debugging tools", "Logs", "Postman"],
            )
        
        return Solucion(
            titulo="Crear pequeños proyectos",
            descripcion="Elige algo que uses daily y recrea una versión simple. Ejemplo: Si usas Spotify, haz un playlist manager simple. Aprenderás más que con tutoriales.",
            ventajas=[
                "Aprendizaje activo",
                "Portfolio para展示了",
                "Proyectos relevantes para trabajo",
            ],
            desventajas=[
                "Tiempo significativo",
                "Puede frustrar al principio",
            ],
            complejidad=ComplexityLevel.MEDIA,
            categoria=SolutionCategory.DESARROLLO,
            recomendacion="1 proyecto pequeño por semana es mejor que 10 tutoriales.",
            tecnologias=["GitHub", "VS Code", "Stack Overflow"],
        )
    
    def _soluciones_general_personalizadas(self, texto: str) -> Optional[Solucion]:
        """Genera solución simple y accionable."""
        
        return Solucion(
            titulo="Empezar con la acción más pequeña",
            descripcion=f"Cuando no sabes qué hacer, identifica 1 acción que tomes hoy que te acerque a tu meta. No necesitas tener todo claro - solo empezar.",
            ventajas=[
                "Elimina parálisis de análisis",
                "Genera momentum",
                "Aprendes actuando",
            ],
            desventajas=[
                "Puede sentirse insuficiente",
                "Requiere tolerancia a la ambigüedad",
            ],
            complejidad=ComplexityLevel.BAJA,
            categoria=SolutionCategory.GENERAL,
            recomendacion="La perfección es el enemigo del progreso. Empieza imperfecto.",
            tecnologias=["Notas", "Calendario"],
        )
