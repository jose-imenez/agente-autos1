"""
Servicio de integración con APIs de Modelos de Lenguaje (LLM).

Soporta múltiples proveedores: OpenAI, Anthropic, Google, etc.
"""

import os
import json
from typing import Optional, Any
from dataclasses import dataclass

import requests

from infrastructure.logging.structured_logging import api_logger


@dataclass
class LLMResponse:
    """Respuesta del modelo de lenguaje."""
    contenido: str
    modelo: str
    uso_tokens: Optional[dict] = None
    raw_response: Optional[dict] = None


class LLMService:
    """
    Servicio para interactuar con APIs de Modelos de Lenguaje.
    
    Configuración mediante variables de entorno:
    - API_KEY: Clave de API del proveedor
    - LLM_PROVIDER: Proveedor (openai, anthropic, google)
    - MODEL: Modelo a usar
    """
    
    def __init__(self):
        self.api_key = os.getenv("API_KEY", "")
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.model = os.getenv("MODEL", "gpt-4o-mini")
        self._validar_configuracion()
    
    def _validar_configuracion(self) -> None:
        """Valida que la configuración sea correcta."""
        if not self.api_key or self.api_key == "TU_API_KEY":
            api_logger.warning(
                "API Key no configurada",
                provider=self.provider,
               提示="Usando respuestas predefinidas. Configure API_KEY en .env"
            )
        else:
            api_logger.info(
                "LLM Service inicializado",
                provider=self.provider,
                model=self.model
            )
    
    def _obtener_headers(self) -> dict:
        """Obtiene los headers según el proveedor."""
        if self.provider == "openai":
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        elif self.provider == "anthropic":
            return {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
        elif self.provider == "google":
            return {
                "Content-Type": "application/json"
            }
        return {"Authorization": f"Bearer {self.api_key}"}
    
    def _obtener_url(self) -> str:
        """Obtiene la URL del endpoint según el proveedor."""
        if self.provider == "openai":
            return "https://api.openai.com/v1/chat/completions"
        elif self.provider == "anthropic":
            return "https://api.anthropic.com/v1/messages"
        elif self.provider == "google":
            return f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        return "https://api.openai.com/v1/chat/completions"
    
    def _construir_payload(self, mensajes: list[dict], **kwargs) -> dict:
        """Construye el payload según el proveedor."""
        if self.provider == "openai":
            return {
                "model": self.model,
                "messages": mensajes,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000)
            }
        elif self.provider == "anthropic":
            return {
                "model": self.model,
                "messages": mensajes,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000)
            }
        elif self.provider == "google":
            return {
                "contents": [{"parts": [{"text": mensajes[-1]["content"]}]}],
                "generationConfig": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "maxOutputTokens": kwargs.get("max_tokens", 2000)
                }
            }
        return {"model": self.model, "messages": mensajes}
    
    def _extraer_contenido(self, response: dict) -> str:
        """Extrae el contenido de la respuesta según el proveedor."""
        if self.provider == "openai":
            return response.get("choices", [{}])[0].get("message", {}).get("content", "")
        elif self.provider == "anthropic":
            return response.get("content", [{}])[0].get("text", "")
        elif self.provider == "google":
            return response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return str(response)
    
    def _obtener_uso_tokens(self, response: dict) -> Optional[dict]:
        """Extrae el uso de tokens de la respuesta."""
        if self.provider == "openai":
            return response.get("usage")
        elif self.provider == "anthropic":
            return {
                "input_tokens": response.get("usage", {}).get("input_tokens"),
                "output_tokens": response.get("usage", {}).get("output_tokens")
            }
        return None
    
    def generar(
        self, 
        prompt: str, 
        contexto: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Genera una respuesta usando el modelo de lenguaje.
        
        Args:
            prompt: Prompt del usuario
            contexto: Contexto adicional (opcional)
            system_prompt: Prompt del sistema (opcional)
            **kwargs: Parámetros adicionales (temperature, max_tokens, etc.)
        
        Returns:
            LLMResponse con la respuesta del modelo
        """
        # Si no hay API key configurada, usar respuesta predefinida
        if not self.api_key or self.api_key == "TU_API_KEY":
            return self._respuesta_sin_api(prompt, contexto, system_prompt)
        
        # Construir mensajes
        mensajes = []
        
        if system_prompt:
            if self.provider == "anthropic":
                mensajes.append({"role": "system", "content": system_prompt})
            else:
                mensajes.append({"role": "system", "content": system_prompt})
        
        if contexto:
            mensajes.append({
                "role": "system", 
                "content": f"Contexto relevante:\n{contexto}"
            })
        
        mensajes.append({"role": "user", "content": prompt})
        
        try:
            headers = self._obtener_headers()
            url = self._obtener_url()
            payload = self._construir_payload(mensajes, **kwargs)
            
            api_logger.info(
                "Llamando a LLM API",
                provider=self.provider,
                model=self.model,
                url=url
            )
            
            response = requests.post(
                url, 
                headers=headers, 
                json=payload if self.provider != "google" else payload,
                timeout=kwargs.get("timeout", 60)
            )
            
            # Agregar API key a la URL para Google
            if self.provider == "google":
                url_con_key = f"{url}?key={self.api_key}"
                response = requests.post(
                    url_con_key,
                    headers=headers,
                    json=payload,
                    timeout=kwargs.get("timeout", 60)
                )
            
            response.raise_for_status()
            data = response.json()
            
            contenido = self._extraer_contenido(data)
            uso_tokens = self._obtener_uso_tokens(data)
            
            api_logger.info(
                "Respuesta de LLM recibida",
                provider=self.provider,
                model=self.model,
                tokens_usados=uso_tokens.get("total_tokens", "N/A") if uso_tokens else "N/A"
            )
            
            return LLMResponse(
                contenido=contenido,
                modelo=self.model,
                uso_tokens=uso_tokens,
                raw_response=data
            )
            
        except requests.exceptions.RequestException as e:
            api_logger.error("Error en llamada a LLM", error=str(e))
            return self._respuesta_error(prompt, str(e))
        except json.JSONDecodeError as e:
            api_logger.error("Error al decodificar respuesta", error=str(e))
            return self._respuesta_error(prompt, "Error al decodificar respuesta")
    
    def _respuesta_sin_api(
        self, 
        prompt: str, 
        contexto: Optional[str],
        system_prompt: Optional[str]
    ) -> LLMResponse:
        """Respuesta cuando no hay API key configurada."""
        return LLMResponse(
            contenido="⚠️ **API Key no configurada**\n\nPara habilitar respuestas naturales y contextuales:\n\n1. Edita el archivo `.env`\n2. Cambia `API_KEY=TU_API_KEY` por tu clave real\n3. Reinicia el servidor\n\nPuedes obtener tu API key de:\n- OpenAI: https://platform.openai.com/api-keys\n- Anthropic: https://console.anthropic.com/\n- Google AI: https://makersuite.google.com/app/apikey",
            modelo="sin-configurar"
        )
    
    def _respuesta_error(self, prompt: str, error: str) -> LLMResponse:
        """Respuesta en caso de error."""
        return LLMResponse(
            contenido=f"⚠️ **Error al generar respuesta**\n\nError: {error}\n\nPor favor, verifica tu conexión y configuración de API.",
            modelo=self.model
        )
    
    def generar_respuesta_asesor(
        self,
        problema: str,
        analisis_contextual: Optional[dict] = None,
        soluciones: Optional[list] = None
    ) -> str:
        """
        Genera una respuesta de asesor estratégico usando el LLM.
        
        Args:
            problema: El problema del usuario
            analisis_contextual: Análisis contextual realizado
            soluciones: Soluciones generadas previamente
        
        Returns:
            Respuesta natural y contextualizada
        """
        # Construir prompt rico en contexto
        prompt_parts = [
            f"Eres un asesor estratégico crítico y perspicaz.",
            f"\n\n## Problema del usuario",
            f"{problema}"
        ]
        
        if analisis_contextual:
            prompt_parts.append(f"\n\n## Análisis realizado")
            prompt_parts.append(f"- Dominio: {analisis_contextual.get('dominio', 'General')}")
            prompt_parts.append(f"- Objetivo: {analisis_contextual.get('objetivo_real', 'No detectado')}")
            prompt_parts.append(f"- Factor clave: {analisis_contextual.get('factor_clave', 'No detectado')}")
            if analisis_contextual.get('restricciones'):
                prompt_parts.append(f"- Restricciones: {', '.join(analisis_contextual['restricciones'])}")
        
        if soluciones:
            prompt_parts.append(f"\n\n## Soluciones generadas")
            for i, sol in enumerate(soluciones[:5], 1):
                prompt_parts.append(f"\n{i}. **{sol.get('titulo', 'Sin título')}**")
                prompt_parts.append(f"   {sol.get('descripcion', '')[:100]}...")
        
        prompt_parts.append(f"\n\n## Tu tarea")
        prompt_parts.append("""
Responde como un asesor estratégico:
1. No des respuestas genéricas o superficiales
2. Profundiza en el problema real detrás de la pregunta
3. Si algo no está claro, haz preguntas específicas
4. Proporciona análisis estratégico antes de dar soluciones
5. Las recomendaciones deben ser accionables y específicas

Responde en español de manera natural y directa.
""")
        
        prompt = "\n".join(prompt_parts)
        
        response = self.generar(
            prompt=prompt,
            system_prompt="Eres un asesor estratégico experto. Analizas problemas en profundidad, detectas la intención real, y das recomendaciones específicas y accionables. No das respuestas genéricas.",
            temperature=0.7
        )
        
        return response.contenido


# Instancia global del servicio
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Obtiene la instancia global del servicio LLM."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
