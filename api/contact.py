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
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        receiver_email = os.getenv("RECEIVER_EMAIL", sender_email)

        if not sender_email or not sender_password:
            print("❌ Faltan credenciales de email")
            return False

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

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("✅ Email enviado correctamente")
        return True

    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False


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
