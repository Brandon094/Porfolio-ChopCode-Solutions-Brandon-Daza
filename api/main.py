from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import smtplib
import os
from email.mime.text import MimeText
from email.mime.multipart import MIMEMultipart
import json

app = FastAPI(title="Portfolio Backend", version="1.0.0")

# Configurar CORS para permitir tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://porfolio-chop-code-solutions-brando.vercel.app",
        "*",  # Temporal para pruebas
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactForm(BaseModel):
    name: str
    email: str
    message: str

def send_email(name: str, email: str, message: str) -> bool:
    """
    Envía el correo electrónico con la información del formulario
    """
    try:
        # Configuración desde variables de entorno
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        receiver_email = os.getenv("RECEIVER_EMAIL", sender_email)

        if not sender_email or not sender_password:
            print("Error: Configura las variables de entorno de email")
            return False

        # Crear mensaje
        msg = MIMEMultipart()
        msg["Subject"] = f"📧 Nuevo mensaje de {name} - Portafolio"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        # Contenido del email
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

        msg.attach(MimeText(html_content, "html"))

        # Enviar email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("✅ Email enviado correctamente")
        return True

    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "Backend del portafolio de Brandon Daza funcionando ✅"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "portfolio-backend"}

@app.post("/api/contact")
async def contact_form(contact: ContactForm):
    try:
        print(f"📨 Nuevo mensaje de: {contact.name} ({contact.email})")

        # Validaciones
        if len(contact.name.strip()) < 2:
            raise HTTPException(
                status_code=400, detail="El nombre debe tener al menos 2 caracteres"
            )

        if len(contact.message.strip()) < 10:
            raise HTTPException(
                status_code=400, detail="El mensaje debe tener al menos 10 caracteres"
            )

        # Enviar email
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
        raise
    except Exception as e:
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
    Handler para Vercel Serverless Functions
    """
    try:
        # Obtener método y path
        method = request.method
        path = request.url.path
        
        print(f"🔍 Vercel Handler: {method} {path}")
        
        # Manejar rutas específicas
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
            return JSONResponse(
                status_code=404,
                content={"error": f"Endpoint no encontrado: {method} {path}"}
            )
            
    except Exception as e:
        print(f"🔥 Error en handler: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error interno: {str(e)}"}
        )

# Función alternativa que Vercel también puede buscar
def main(request):
    import asyncio
    return asyncio.run(handler(request))