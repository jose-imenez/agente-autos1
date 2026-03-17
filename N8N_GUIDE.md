# Agente de Autos con RAG - Guía para n8n Cloud

## Overview

Este agente busca precios de autos en **tiempo real** usando:
- **SerpAPI** para búsquedas web
- **RAG** para respuestas contextuales
- **Web scraping** de fuentes oficiales

## Endpoints Disponibles

### GET /precio
```
http://tu-servidor:8000/precio?marca=toyota&modelo=corolla&anio=2024
```

### POST /precio
```json
{
  "marca": "toyota",
  "modelo": "corolla",
  "anio": "2024"
}
```

### Respuesta
```json
{
  "status": "success",
  "precios_nuevos": [
    {"precio": "$425,600 MXN", "fuente": "Toyota México", "version": "BASE"}
  ],
  "precios_usados": [
    {"precio": "$312,500 MXN", "fuente": "Kavak"}
  ],
  "especificaciones": {"potencia": "168 hp"}
}
```

## Cómo Desplegar

### Opción 1: Render.com (Gratis)

1. Sube el código a GitHub
2. Ve a https://render.com
3. Crea un "Web Service"
4. Configura:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api_n8n:app --host 0.0.0.0 --port $PORT`
5. Añade variables de entorno:
   - `SERPAPI_KEY` = tu clave de SerpAPI
   - `API_KEY` = tu clave de OpenAI

### Opción 2: Railway

1. Ve a https://railway.app
2. Crea un nuevo proyecto
3. Conecta tu repositorio GitHub
4. Configura las variables de entorno

## Configurar en n8n Cloud

### Paso 1: Obtener URL del servidor
Después de desplegar, tendrás una URL como:
```
https://tu-servidor.onrender.com
```

### Paso 2: Crear Workflow en n8n

```
[Webhook] → [HTTP Request] → [Set] → [Slack/Email]
```

#### Nodo HTTP Request:
- **Method**: GET o POST
- **URL**: `https://tu-servidor.onrender.com/precio`
- **Query Parameters**:
  - marca: {{ $json.marca }}
  - modelo: {{ $json.modelo }}

#### Ejemplo con datos hardcodeados:
- **URL**: `https://tu-servidor.onrender.com/precio?marca=toyota&modelo=corolla`

## Variables de Entorno Requeridas

| Variable | Descripción |
|----------|-------------|
| `SERPAPI_KEY` | Clave de SerpAPI (para búsquedas web) |
| `API_KEY` | Clave de OpenAI (para LLM) |

## Prueba Local

```bash
cd .opencode
python api_n8n.py
```

Luego accede a:
- http://localhost:8000/precio?marca=toyota&modelo=corolla

## Nota Importante

El agente busca **datos reales de internet** cada vez que hace una consulta. No tiene datos locales hardcodeados.
