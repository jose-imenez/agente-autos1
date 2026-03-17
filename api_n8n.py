# Multi-Agente con RAG y MCP
# El código completo está en multi_agente.py

# Este archivo redirige al multi-agente
# Start Command: uvicorn multi_agente:app --host 0.0.0.0 --port $PORT

from multi_agente import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
