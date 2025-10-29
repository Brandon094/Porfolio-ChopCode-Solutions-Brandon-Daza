"""
api/main.py - handler mínimo para Vercel

Este archivo expone un endpoint POST /api/contact (para uso con FastAPI local)
y un `main(request)` que Vercel invoca al mapear rutas a este archivo.
La lógica real de contacto está en `api/contact.py`.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Importar la lógica de contacto del módulo local
try:
    # Cuando se importa como paquete (p. ej. en Vercel)
    from .contact import ContactForm, contact_form
except Exception:
    # Permite ejecutar localmente con 'python api/main.py' si se añade al PYTHONPATH
    from contact import ContactForm, contact_form


app = FastAPI()

# CORS básico para pruebas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/contact")
async def api_contact(contact: ContactForm):
    return await contact_form(contact)


@app.get("/")
async def health_check():
    """Ruta de verificación rápida para saber que el servicio está arriba."""
    return {"status": "ok", "message": "API de contacto funcionando"}


# Handler que Vercel llama. Se encarga de preflight y delega en contact_form para POST.
async def handler(request):
    # Preflight
    if request.method == "OPTIONS":
        return JSONResponse(status_code=204, content={}, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        })

    if request.method == "POST":
        try:
            body = await request.json()
            contact = ContactForm(**body)
            response = await contact_form(contact)
            return JSONResponse(content=response, headers={"Access-Control-Allow-Origin": "*"})
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    return JSONResponse(status_code=405, content={"message": "Método no permitido."})


def main(request):
    import asyncio
    return asyncio.run(handler(request))