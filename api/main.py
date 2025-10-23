"""
Backend API para portfolio personal - Maneja formulario de contacto y envío de emails
Autor: Brandon Daza
Tecnologías: FastAPI, SMTP, Vercel
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import smtplib
import os
from email.mime.text import MimeText
from email.mime.multipart import MIMEMultipart
import json

# =============================================
# INICIALIZACIÓN DE FASTAPI
# =============================================

app = FastAPI(title="Portfolio Backend", version="1.0.0")

# =============================================
# CONFIGURACIÓN CORS - Permite comunicación con frontend
# =============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Desarrollo local
        "http://127.0.0.1:3000",  # Alternativa local
        "https://porfolio-chop-code-solutions-brando.vercel.app",  # Producción
        # "*",  # ⚠️ REMOVIDO: No usar en producción por seguridad
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
)

# =============================================
# MODELOS DE DATOS PYDANTIC
# =============================================

class ContactForm(BaseModel):
    """Modelo para validar los datos del formulario de contacto"""
    name: str
    email: str
    message: str

# =============================================
# FUNCIONES AUXILIARES
# =============================================

def send_email(name: str, email: str, message: str) -> bool:
    """
    Envía el correo electrónico con la información del formulario de contacto
    
    Args:
        name (str): Nombre de la persona que contacta
        email (str): Email de contacto
        message (str): Mensaje del formulario
        
    Returns:
        bool: True si el email se envió correctamente, False si hubo error
    """
    try:
        # ✅ CORREGIDO: Las contraseñas deben venir de variables de entorno
        # Configuración desde variables de entorno para seguridad
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")  # Servidor SMTP
        smtp_port = int(os.getenv("SMTP_PORT", "587"))  # Puerto SMTP
        sender_email = os.getenv("SENDER_EMAIL")  # Email remitente
        sender_password = os.getenv("SENDER_PASSWORD")  # ✅ Contraseña desde variable de entorno
        receiver_email = os.getenv("RECEIVER_EMAIL", sender_email)  # Email destinatario

        # Validar que existan las credenciales necesarias
        if not sender_email or not sender_password:
            print("❌ Error: Variables de entorno SENDER_EMAIL o SENDER_PASSWORD no configuradas")
            print("💡 Configura las variables en Vercel: Settings -> Environment Variables")
            return False

        # Crear estructura del mensaje MIME
        msg = MIMEMultipart()
        msg["Subject"] = f"📧 Nuevo mensaje de {name} - Portafolio"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        # Contenido HTML del email con estilos
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
                .field {{ margin: 15px 0; }}
                .label {{ font-weight: bold; color: #333; display: block; margin-bottom: 5px; }}
                .message-box {{ background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea; }}
                .footer {{ margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 5px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚀 Nuevo mensaje desde tu Portafolio</h2>
                    <p>Alguien quiere contactarte</p>
                </div>
                <div class="content">
                    <div class="field">
                        <span class="label">👤 Nombre:</span>
                        <span>{name}</span>
                    </div>
                    <div class="field">
                        <span class="label">📧 Email:</span>
                        <span>{email}</span>
                    </div>
                    <div class="field">
                        <span class="label">💬 Mensaje:</span>
                        <div class="message-box">
                            {message}
                        </div>
                    </div>
                </div>
                <div class="footer">
                    <small>📩 Este mensaje fue enviado desde el formulario de contacto de tu portafolio</small>
                </div>
            </div>
        </body>
        </html>
        """

        # Adjuntar contenido HTML al mensaje
        msg.attach(MimeText(html_content, "html"))

        # Enviar email usando SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Seguridad TLS
            server.login(sender_email, sender_password)  # Autenticación
            server.send_message(msg)  # Envío del mensaje

        print("✅ Email enviado correctamente")
        return True

    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False

# =============================================
# ENDPOINTS DE LA API
# =============================================

@app.get("/")
async def root():
    """Endpoint raíz - Verifica que el backend esté funcionando"""
    return {"message": "Backend del portafolio de Brandon Daza funcionando ✅"}

@app.get("/health")
async def health_check():
    """Endpoint de salud - Para monitoreo y verificación del servicio"""
    return {"status": "healthy", "service": "portfolio-backend"}

@app.post("/api/contact")
async def contact_form(contact: ContactForm):
    """
    Endpoint para procesar el formulario de contacto
    
    Args:
        contact (ContactForm): Datos validados del formulario
        
    Returns:
        JSONResponse: Respuesta de éxito o error
    """
    try:
        print(f"📨 Nuevo mensaje de: {contact.name} ({contact.email})")

        # Validaciones de campos
        if len(contact.name.strip()) < 2:
            raise HTTPException(
                status_code=400, 
                detail="El nombre debe tener al menos 2 caracteres"
            )

        if len(contact.message.strip()) < 10:
            raise HTTPException(
                status_code=400, 
                detail="El mensaje debe tener al menos 10 caracteres"
            )

        # Intentar enviar el email
        email_sent = send_email(contact.name, contact.email, contact.message)

        if email_sent:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "✅ Mensaje enviado correctamente. Te contactaré pronto.",
                },
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al enviar el mensaje. Por favor, intenta nuevamente.",
            )

    except HTTPException:
        # Re-lanzar excepciones HTTP específicas
        raise
    except Exception as e:
        # Manejar errores inesperados
        print(f"🔥 Error en el servidor: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor. Por favor, intenta más tarde.",
        )

# =============================================
# HANDLER PARA VERCEL SERVERLESS FUNCTIONS
# =============================================

async def handler(request: Request):
    """
    Handler específico para Vercel Serverless Functions
    
    Args:
        request (Request): Objeto request de Vercel
        
    Returns:
        JSONResponse: Respuesta para el cliente
    """
    try:
        # Obtener método HTTP y path de la URL
        method = request.method
        path = request.url.path
        
        print(f"🔍 Vercel Handler: {method} {path}")
        
        # Enrutamiento manual para Vercel
        if path == "/api/contact" and method == "POST":
            # Procesar formulario de contacto
            body = await request.json()
            contact = ContactForm(**body)
            return await contact_form(contact)
            
        elif path == "/" and method == "GET":
            return JSONResponse(content={"message": "Backend funcionando ✅"})
            
        elif path == "/health" and method == "GET":
            return JSONResponse(content={"status": "healthy", "service": "portfolio-backend"})
            
        else:
            # Endpoint no encontrado
            return JSONResponse(
                status_code=404,
                content={"error": f"Endpoint no encontrado: {method} {path}"}
            )
            
    except Exception as e:
        # Manejo global de errores para Vercel
        print(f"🔥 Error en handler: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error interno: {str(e)}"}
        )

def main(request):
    """
    Función principal alternativa que Vercel puede buscar automáticamente
    
    Args:
        request: Request de Vercel
        
    Returns:
        Response: Respuesta HTTP
    """
    import asyncio
    return asyncio.run(handler(request))