"""
Skills Service - Manejo de saludos y despedidas del asistente.
"""

import random
from datetime import datetime
from typing import Optional


class SkillsService:
    """Servicio que maneja las interacciones de bienvenida y despedida."""

    SALUDOS = [
        "Eyyyy, qué onda! 😎 Listo para accion. Cuéntame, qué tienes entre manos?",
        "Wepa! 💪 Bienvenido crack! Aquí estoy para ayudarte a resolver lo que necesites.",
        "Hey! 👋 Qué hubo? Listo para analizar tu situación y buscarle la vuelta.",
        "Holaaa! 🎉 Cuéntame, qué situación tienes? Vamos a resolverla juntos!",
        "Oye! 😏 Adelante, dispara. Estoy aquí para echate la mano con lo que sea.",
        "Buen día! ☀️ Vamos a convertir ese problema en solución. Qué necesitas?",
        "Qué hay! 🚀 Listo para la misión. Dime qué pasa!",
        "Wenas! 🌊 Aqui estoy, fresquito, listo para ayudarte. Qué onda?",
        "Heyyy! 🎯 A la orden! Cuéntame qué necesitas resolver?",
        "Hola! 💡 El universo te trajo hasta aquí. Describe tu problema y encontrémos respuestas.",
        "Eyyyy, bienvenido! 🎮 Vamos a darle duro a esto. Qué tienes?",
        "Wepa! 🔥 Que bueno verte por aquí. Adelante, cuéntame!",
        "Hola! 🙌 Listo para lo que necesites. Qué situación tienes?",
        "Hey! 😎 Qué pasa? Vamos a resolver eso. Adelante!",
        "Buen día! ✨ Aqui tienes tu asistente favorito. Qué necesitas?",
    ]

    DESPEDIDAS = [
        "Chao! 🔥 Exito en lo que hagas. Cuando necesites, aquí estaré! 💪",
        "Ey! 🎯 Mucha suerte con eso! Aqui estaré si necesitas otra vuelta. Exito crack! 💪",
        "Nos vemos! 😎 Que te vaya divino. Cuando quieras, vuelves y le buscamos de nuevo!",
        "Chao! ✌️ Exito en tu camino. Recuerda: siempre hay opciones, solo hay que buscarlas!",
        "Listo! 💡 Ya tienes lo que necesitas. Buena suerte y ojala te vaya increíble! 🎉",
        "Wepa! 🚀 Sesión terminada con clase. Mucha suerte con tu decisión! 💪",
        "Ey! 👋 Gracias por usarme! Buena suerte y ojala te vaya excelente! 🎯",
        "Chao! 🎉 Exito en tu aventura. Aquí estaré si me necesitas de nuevo!",
        "Listo! ✨ Ya tienes opciones para elegir. Buena suerte crack! 🔥",
        "Ey! 💪 Mucho éxito! Vuelve cuando quieras que le buscamos de nuevo! 😎",
    ]

    DESPEDIDAS_SESION = [
        "Chao! 🔥 Sesión terminada con éxito! Gracias por usarme. Buena suerte! 💪",
        "Hasta luego! 😎 Fue un placer ayudarte. Mucha suerte en lo que decidas!",
        "Cerrando sesión! ✨ Gracias por confiar. Buena suerte y éxito! 🎯",
        "Chao! 🎉 Exito en lo que hagas. Cuando necesites, aquí estaré! 💪",
        "Wepa! 🚀 Sesión terminada con clase! Gracias y mucha suerte! 😎",
    ]

    def obtener_saludo(self) -> dict:
        """Retorna un mensaje de saludo aleatorio."""
        return {
            "mensaje": random.choice(self.SALUDOS),
            "tipo": "saludo",
            "timestamp": datetime.now().isoformat(),
        }

    def obtener_despedida(self, sesion_activa: bool = False) -> dict:
        """Retorna un mensaje de despedida aleatorio."""
        if sesion_activa:
            mensaje = random.choice(self.DESPEDIDAS_SESION)
        else:
            mensaje = random.choice(self.DESPEDIDAS)
        
        return {
            "mensaje": mensaje,
            "tipo": "despedida",
            "timestamp": datetime.now().isoformat(),
        }

    def registrar_fin_sesion(self, sesion_id: Optional[str] = None) -> dict:
        """Registra el fin de una sesión y retorna despedida."""
        return self.obtener_despedida(sesion_activa=bool(sesion_id))


skills_service = SkillsService()
