---
name: obtener_precios
description: "Skill especializada en obtener precios de coches. USO EXCLUSIVO para consultas de precios de vehículos. SIEMPRE busca información actualizada en la web."
---

# Precios de Coches

## IMPORTANTE: Búsqueda Online Obligatoria

**NUNCA uses información hardcodeada. SIEMPRE busca precios reales en la web.**

### Implementación técnica:

1. **Usa el módulo web_client**: `from infrastructure.web_client import get_web_client`
2. **Llama al método**: `web_client.buscar_precios_auto(marca, modelo, anio)`
3. **La API usada es**: `https://serpapi.com/search` (configurable en .env)
4. **Siempre muestra la fuente** de donde obtuviste los datos

### Proceso de búsqueda:

1. **Busca el precio actual** del modelo específico (año, versión)
2. **Busca precios en concessionarios** locales o nacionales
3. **Busca precios de usados** si el usuario quiere esa info
4. **Organiza** la información por secciones claras
5. **Muestra la URL** usada para obtener los datos

### Fuentes a buscar:

- Concesionarias oficiales (Toyota México, Honda México, etc.)
- Sitios de autos (MercadoLibre Autos, Autocosmos, Kavak)
- Kelley Blue Book para precios estimados

### Ejemplo de uso del web_client:

```python
from infrastructure.web_client import get_web_client

web = get_web_client()
resultado = web.buscar_precios_auto("Toyota", "Corolla", "2024")

# Muestra la URL usada:
print(resultado["busqueda"]["url_usada"])  # https://serpapi.com/search
```

### Ejemplo de respuesta esperada:

**Toyota Corolla 2024:**

📡 **Fuente:** https://serpapi.com/search

💰 **Precios Nuevos:**
- BASE: $425,600 MXN (Toyota México)
- LE: $455,700 MXN (Toyota México)

🔧 **Precios Usados:**
- Desde: $312,500 MXN (MercadoLibre)
- Desde: $440,000 MXN (Kavak)

⚙️ **Especificaciones:**
- Motor: 2.0L
- Potencia: 168 hp

**Nota:** Los precios pueden variar. Visita el concesionario para cotización exacta.
