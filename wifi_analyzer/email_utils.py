"""Utilidades de correo electrónico (SMTP).

Este módulo proporciona funciones auxiliares para la composición y
envío de mensajes por SMTP en texto plano.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr

LAST_ERROR = ""

def get_last_error() -> str:
    return LAST_ERROR


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
    global LAST_ERROR

    def _clean(s: str) -> str:
        if s is None:
            return ""
        # Reemplazar NBSP y normalizar espacios
        s = str(s).replace('\u00A0', ' ').replace('\xa0', ' ')
        return ' '.join(s.strip().split())

    def _clean_pwd(s: str) -> str:
        if s is None:
            return ""
        # Eliminar NBSP y TODO tipo de espacio (App Password suele mostrarse con espacios)
        s = str(s).replace('\u00A0', ' ').replace('\xa0', ' ')
        return ''.join(s.split())
    try:
        # Sanitizar entradas (evita NBSP/copypaste invisibles)
        smtp_server = _clean(smtp_server)
        email_user = _clean(email_user)
        email_password = _clean_pwd(email_password)
        recipient_email = _clean(recipient_email)
        subject = _clean(subject)

        # Construcción del mensaje MIME multipart con cuerpo en texto plano.
        msg = MIMEMultipart()
        # Solo la parte de dirección (sin nombre). Si quisieras nombre, usa Header en display name.
        from_addr = parseaddr(email_user)[1]
        to_addr = parseaddr(recipient_email)[1]
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = str(Header(subject, 'utf-8'))

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Establecimiento de sesión SMTP con soporte para SSL (465) o STARTTLS (587).
        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
            server.ehlo()
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
            server.ehlo()
            server.starttls()
            server.ehlo()
        server.login(email_user, email_password)
        # Despacho del mensaje al destinatario indicado.
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()
        LAST_ERROR = ""
        return True
    except Exception as e:
        # Mensaje de diagnóstico para consola/CLI (GUI muestra genérico).
        LAST_ERROR = str(e)
        print(f"[ERROR] SMTP: {e}")
        return False

