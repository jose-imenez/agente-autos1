---
name: buscar_coche
description: "Skill especializada en buscar coches por marca, modelo, año y características. USO EXCLUSIVO para búsquedas de coches y precios. SIEMPRE busca información actualizada en la web."
---

# Buscar Coche

## IMPORTANTE: Búsqueda Online Obligatoria

**NUNCA uses información hardcodeada. SIEMPRE busca en la web información actualizada.**

### Implementación técnica:

1. **Usa el módulo web_client**: `from infrastructure.web_client import get_web_client`
2. **La API usada es**: `https://serpapi.com/search` (configurable en .env)
3. **Muestra siempre la fuente** de donde obtuviste los datos

### Proceso de búsqueda:

1. **Busca en la web** con el modelo completo (ej: "Toyota Corolla 2024 precio especificaciones")
2. **Extrae información** de fuentes confiables (concesionarias, sitios de autos, etc)
3. **Organiza** por secciones: precio, características, versiones
4. **Cita las fuentes** de donde obtuviste la información
5. **Muestra la URL** usada para obtener los datos

### Ejemplo de uso:

```python
from infrastructure.web_client import get_web_client

web = get_web_client()
resultado = web.buscar_precios_auto("Honda", "Civic", "2024")

# URL usada:
print(resultado["busqueda"]["url_usada"])  # https://serpapi.com/search
```
