"""
api/main.py - handler mínimo para Vercel

Este archivo expone un endpoint POST /api/contact (para uso con FastAPI local)
y un `main(request)` que Vercel invoca al mapear rutas a este archivo.
La lógica real de contacto está en `api/contact.py`.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("🚀 Iniciando API de contacto...")
print("📝 Variables de entorno cargadas:", bool(os.getenv("SENDER_EMAIL")))

# Importar la lógica de contacto del módulo local
try:
    # Cuando se importa como paquete (p. ej. en Vercel)
    from .contact import ContactForm, contact_form
    print("✅ Módulos importados correctamente (modo paquete)")
except Exception as e:
    print(f"ℹ️ Fallback a import directo: {e}")
    # Permite ejecutar localmente con 'python api/main.py' si se añade al PYTHONPATH
    try:
        from contact import ContactForm, contact_form
        print("✅ Módulos importados correctamente (modo directo)")
    except Exception as e:
        print(f"❌ Error fatal importando módulos: {e}")
        raise


app = FastAPI()

# CORS básico para pruebas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/contact")
async def api_contact(contact: ContactForm, request: Request):
    try:
        # Log detallado de la petición
        print("\n📨 Nueva petición de contacto")
        print(f"├─ Método: {request.method}")
        print(f"├─ URL: {request.url}")
        print(f"├─ Headers:")
        for header, value in request.headers.items():
            print(f"│  └─ {header}: {value}")
        print(f"├─ Nombre: {contact.name}")
        print(f"├─ Email: {contact.email}")
        print(f"└─ Longitud del mensaje: {len(contact.message)} caracteres")

        result = await contact_form(contact)
        print("✅ Contacto procesado correctamente")
        return result
    except Exception as e:
        print(f"❌ Error en endpoint /api/contact: {str(e)}")
        print(f"└─ Tipo de error: {type(e).__name__}")
        raise


@app.get("/")
async def health_check():
    """Ruta de verificación rápida para saber que el servicio está arriba."""
    env_status = "✅" if os.getenv("SENDER_EMAIL") else "❌"
    return {
        "status": "ok",
        "message": "API de contacto funcionando",
        "env_loaded": env_status
    }


# Handler que Vercel llama. Se encarga de preflight y delega en contact_form para POST.
async def handler(request: Request):
    print(f"📥 Nueva petición: {request.method} {request.url.path}")
    
    # Preflight
    if request.method == "OPTIONS":
        print("👉 Respondiendo a OPTIONS")
        return JSONResponse(status_code=204, content={}, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        })

    if request.method == "POST":
        try:
            print("📦 Leyendo body...")
            body = await request.json()
            print(f"📨 Datos recibidos de: {body.get('name', 'N/A')}")
            
            contact = ContactForm(**body)
            print("✅ Datos validados")
            
            response = await contact_form(contact)
            print("✅ Contacto procesado")
            
            return JSONResponse(
                content=response,
                headers={"Access-Control-Allow-Origin": "*"}
            )
        except Exception as e:
            print(f"❌ Error procesando POST: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e)},
                headers={"Access-Control-Allow-Origin": "*"}
            )

    print("❌ Método no permitido:", request.method)
    return JSONResponse(
        status_code=405,
        content={"message": "Método no permitido."},
        headers={"Access-Control-Allow-Origin": "*"}
    )


def main(request):
    """Punto de entrada para Vercel."""
    print("\n🔄 Nueva petición recibida en main()")
    import asyncio
    return asyncio.run(handler(request))