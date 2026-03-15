"""
Presentation Layer - Controladores MVC.

Contiene los controladores que manejan las vistas y responden a las peticiones.
"""

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


class ProblemaController:
    """
    Controlador para la gestión de problemas.
    
    Maneja la lógica de presentación y coordenación con casos de uso.
    """
    
    def __init__(self):
        self._templates = Jinja2Templates(
            directory="presentation/templates"
        )
    
    def home(self, request: Request) -> HTMLResponse:
        """
        Renderiza la página principal.
        
        Args:
            request: Objeto Request de FastAPI
            
        Returns:
            Respuesta HTML con la plantilla renderizada
        """
        return self._templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "titulo": "Agente IA - Análisis de Problemas",
            }
        )
