"""Utilidades de correo electrónico (SMTP).

Este módulo proporciona funciones auxiliares para la composición y
envío de mensajes por SMTP en texto plano.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(smtp_server: str, smtp_port: int, email_user: str, email_password: str,
               recipient_email: str, subject: str, body: str) -> bool:
    """Envía un correo electrónico en formato texto plano mediante SMTP.

    Parámetros:
        smtp_server: Host del servidor SMTP (ej. smtp.gmail.com).
        smtp_port: Puerto del servidor SMTP (ej. 587 para STARTTLS).
        email_user: Dirección de correo remitente (usuario SMTP).
        email_password: Credencial del remitente para autenticación SMTP.
        recipient_email: Dirección de correo destino.
        subject: Asunto del mensaje.
        body: Cuerpo del mensaje en texto plano (UTF-8).

    Retorna:
        True si el mensaje fue enviado correctamente; False en caso contrario.
    """
    try:
        # Construcción del mensaje MIME multipart con cuerpo en texto plano.
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Establecimiento de sesión SMTP con cifrado STARTTLS y autenticación.
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        # Despacho del mensaje al destinatario indicado.
        server.sendmail(email_user, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception:
        # Se retorna False para permitir manejo de error en capas superiores.
        return False

