"""Archivo temporal para manejo de errores con FastAPI."""
import sys
import json
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

print("🚀 Iniciando servicio API...")

# Variables globales para diagnóstico
_init_error: Optional[str] = None

# Intentar importar módulos necesarios
try:
    from .contact import ContactForm, contact_form
    print("✅ Módulos importados correctamente")
except ImportError as e:
    _init_error = f"Error importando módulos: {str(e)}\n{traceback.format_exc()}"
    print("❌ " + _init_error)
    # Intentar import relativo como fallback
    try:
        from contact import ContactForm, contact_form
        print("✅ Módulos importados usando import relativo")
        _init_error = None
    except ImportError as e:
        _init_error = f"Error en import alternativo: {str(e)}\n{traceback.format_exc()}"
        print("❌ " + _init_error)

app = FastAPI()

# CORS 
allowed_origin = "*" 
app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
)

def log_error(e: Exception, context: str = "") -> Dict[str, Any]:
    """Genera un mensaje de error detallado para logs."""
    error_detail = {
        "error_type": e.__class__.__name__,
        "error_msg": str(e),
        "context": context,
        "traceback": traceback.format_exc()
    }
    print(f"❌ Error en {context}: {str(e)}\n{error_detail['traceback']}")
    return error_detail

@app.get("/")
async def health_check():
    """Health check con estado de inicialización."""
    if _init_error:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Error de inicialización",
                "detail": _init_error
            }
        )
    return {
        "status": "ok",
        "message": "API funcionando",
        "python_version": sys.version,
        "import_status": "ok"
    }

@app.post("/api/contact")
async def api_contact(contact: ContactForm):
    try:
        if _init_error:
            raise RuntimeError(f"Servicio no inicializado correctamente: {_init_error}")
        print("📧 Procesando solicitud de contacto...")
        result = await contact_form(contact)
        print("✅ Solicitud procesada correctamente")
        return result
    except Exception as e:
        error_detail = log_error(e, "endpoint /api/contact")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error procesando solicitud",
                "detail": str(e),
                "debug_info": error_detail
            }
        )

async def handler(request: Request):
    """Handler principal para Vercel con mejor logging."""
    try:
        print(f"📥 Recibida petición: {request.method} {request.url.path}")
        print(f"Headers: {json.dumps(dict(request.headers))}")
        
        if request.method == "OPTIONS":
            return JSONResponse(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": allowed_origin,
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Max-Age": "86400",
                }
            )

        if request.method != "POST":
            return JSONResponse(
                status_code=405,
                content={"error": "Método no permitido", "allowed_methods": ["POST"]}
            )

        print("🔄 Leyendo body de la petición...")
        body = await request.json()
        print(f"📦 Body recibido: {json.dumps(body)}")
        
        contact = ContactForm(**body)
        print("✅ Datos validados correctamente")
        
        response = await contact_form(contact)
        print("📤 Enviando respuesta...")
        
        return JSONResponse(
            status_code=200,
            content=response,
            headers={"Access-Control-Allow-Origin": allowed_origin}
        )

    except json.JSONDecodeError as e:
        error_detail = log_error(e, "JSON inválido")
        return JSONResponse(
            status_code=400,
            content={"error": "JSON inválido", "detail": str(e)}
        )
    except Exception as e:
        error_detail = log_error(e, f"handler Vercel - {request.method} {request.url.path}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error procesando solicitud",
                "detail": str(e),
                "debug_info": error_detail
            }
        )

def main(request):
    """Punto de entrada para Vercel."""
    try:
        print("\n🔄 Nueva petición recibida en main()")
        import asyncio
        return asyncio.run(handler(request))
    except Exception as e:
        error_detail = log_error(e, "main entry point")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error en el servidor",
                "detail": str(e),
                "debug_info": error_detail
            }
        )