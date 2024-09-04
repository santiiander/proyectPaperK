import smtplib
from email.mime.text import MIMEText

def send_reset_password_email(to_email: str, verification_code: str):
    msg = MIMEText(f"Tu código de verificación para restablecer la contraseña es: {verification_code}")
    msg['Subject'] = 'Recuperación de contraseña'
    msg['From'] = 'santiagoandermatten1@gmail.com'
    msg['To'] = to_email

    # Configuración del servidor SMTP de Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'santiagoandermatten1@gmail.com'  # Reemplaza con tu correo electrónico de Gmail
    smtp_password = 'erns lrvu hwrv fqec'  # Reemplaza con la contraseña de la aplicación o tu contraseña

    # Enviar el correo electrónico
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Inicia la conexión TLS
        server.login(smtp_user, smtp_password)  # Autenticación en el servidor SMTP
        server.sendmail(smtp_user, to_email, msg.as_string())  # Envío del correo electrónico
