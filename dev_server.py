# Configuración para desarrollo local
import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

if __name__ == "__main__":
    print("🔧 Iniciando servidor de desarrollo...")
    print("📝 Variables de entorno:")
    print(f"  SMTP_SERVER: {'✅' if os.getenv('SMTP_SERVER') else '❌'}")
    print(f"  SENDER_EMAIL: {'✅' if os.getenv('SENDER_EMAIL') else '❌'}")
    print(f"  SMTP_PORT: {'✅' if os.getenv('SMTP_PORT') else '❌'}")
    
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )