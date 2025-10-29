from fastapi import HTTPException
from pydantic import BaseModel
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class ContactForm(BaseModel):
    name: str
    email: str
    message: str


def send_email(name: str, email: str, message: str) -> bool:
    print("\n📧 Iniciando envío de email:")
    try:
        # Obtener configuración
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = os.getenv("SMTP_PORT")
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        receiver_email = os.getenv("RECEIVER_EMAIL", sender_email)

        # Validar configuración
        if not smtp_server:
            raise ValueError("SMTP_SERVER no está configurado")
        if not smtp_port:
            raise ValueError("SMTP_PORT no está configurado")
        if not sender_email:
            raise ValueError("SENDER_EMAIL no está configurado")
        if not sender_password:
            raise ValueError("SENDER_PASSWORD no está configurado")
        if not receiver_email:
            raise ValueError("RECEIVER_EMAIL no está configurado")

        print("├─ Configuración SMTP:")
        print(f"│  ├─ Servidor: {smtp_server}")
        print(f"│  ├─ Puerto: {smtp_port}")
        print(f"│  ├─ Remitente: {sender_email}")
        print(f"│  └─ Destinatario: {receiver_email}")

        # Preparar mensaje
        msg = MIMEMultipart()
        msg["Subject"] = f"📧 Nuevo mensaje de {name}"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        html_content = f"""
        <h2>Nuevo mensaje desde tu portfolio</h2>
        <p><strong>Nombre:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Mensaje:</strong></p>
        <p>{message}</p>
        """

        msg.attach(MIMEText(html_content, "html"))
        print("├─ Mensaje preparado correctamente")

        # Enviar email
        print("├─ Conectando al servidor SMTP...")
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            print("├─ Iniciando TLS...")
            server.starttls()
            print("├─ Autenticando...")
            server.login(sender_email, sender_password)
            print("├─ Enviando mensaje...")
            server.send_message(msg)

        print("└─ ✅ Email enviado correctamente")
        return True

    except ValueError as e:
        print(f"└─ ❌ Error de configuración: {str(e)}")
        raise
    except smtplib.SMTPAuthenticationError:
        print("└─ ❌ Error de autenticación SMTP: credenciales incorrectas")
        raise ValueError("Error de autenticación: verifica SENDER_EMAIL y SENDER_PASSWORD")
    except Exception as e:
        print(f"└─ ❌ Error enviando email: {str(e)}")
        print(f"   └─ Tipo: {type(e).__name__}")
        raise


async def contact_form(contact: ContactForm):
    try:
        if len(contact.name.strip()) < 2:
            raise HTTPException(status_code=400, detail="El nombre debe tener al menos 2 caracteres")

        if len(contact.message.strip()) < 10:
            raise HTTPException(status_code=400, detail="El mensaje debe tener al menos 10 caracteres")

        email_sent = send_email(contact.name, contact.email, contact.message)

        if email_sent:
            return {"success": True, "message": "✅ Mensaje enviado correctamente. Te contactaré pronto."}
        else:
            raise HTTPException(status_code=500, detail="Error al enviar el mensaje. Por favor, intenta nuevamente.")

    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 Error en lógica de contacto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, intenta más tarde.")
