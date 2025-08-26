import smtplib
import ssl
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

sender_email = os.getenv("EMAIL_HOST_USER")
password = os.getenv("EMAIL_HOST_PASSWORD")
receiver_email = sender_email # Puedes enviártelo a ti mismo para probar

message = """\
Subject: Test Email from Python

This is a test email sent from a Python script."""

# Crear una conexión segura SSL
context = ssl.create_default_context()

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    print("Correo enviado exitosamente usando SSL (Puerto 465)")
except Exception as e:
    print(f"Error al enviar correo con SSL (Puerto 465): {e}")

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context) # Usar TLS
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    print("Correo enviado exitosamente usando TLS (Puerto 587)")
except Exception as e:
    print(f"Error al enviar correo con TLS (Puerto 587): {e}")