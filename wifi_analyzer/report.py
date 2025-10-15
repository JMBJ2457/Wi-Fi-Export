"""Generación de reportes de análisis Wi‑Fi.

Este módulo contiene utilidades para componer el reporte en texto plano
con los perfiles detectados y metadatos del sistema.
"""

import os
import platform
from datetime import datetime


def format_results(profiles_data: dict, extra: dict | None = None) -> str:
    """Construye el reporte en texto plano a partir de los resultados.

    Parámetros:
        profiles_data: Mapeo {perfil: contraseña} obtenido del análisis.
        extra: Secciones adicionales opcionales en forma de dict con claves
               como 'interfaces', 'drivers', 'ipconfig', 'getmac', 'exports', etc.

    Retorna:
        Cadena con el reporte formateado en texto plano.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    system_name = platform.system()
    if system_name == 'Windows':
        computer = os.environ.get('COMPUTERNAME', 'Desconocido')
        user = os.environ.get('USERNAME', 'Desconocido')
    else:
        computer = os.uname().nodename if hasattr(os, 'uname') else os.environ.get('HOSTNAME', 'Desconocido')
        user = os.environ.get('USER', 'Desconocido')

    # Cabecera del reporte con metadatos de ejecución.
    message = f"""
REPORTE DE ANALISIS WI-FI
Fecha y hora: {timestamp}
Equipo: {computer}
Usuario: {user}

{'='*50}
PERFILES WI-FI Y CONTRASENAS ENCONTRADAS
{'='*50}

"""

    if profiles_data:
        # Cálculo de anchos de columna para una tabla alineada.
        headers = ("Perfil", "Contrasena")
        # Ordenar perfiles alfabéticamente para una lectura consistente
        sorted_items = sorted(profiles_data.items(), key=lambda kv: str(kv[0]).lower())
        name_width = max(len(headers[0]), max(len(str(p)) for p, _ in sorted_items))
        pass_width = max(len(headers[1]), max(len(str(pw)) for _, pw in sorted_items))

        border = "+" + "-" * (name_width + 2) + "+" + "-" * (pass_width + 2) + "+\n"
        header_row = f"| {headers[0]:<{name_width}} | {headers[1]:<{pass_width}} |\n"

        message += border
        message += header_row
        message += border

        for profile, password in sorted_items:
            message += f"| {profile:<{name_width}} | {password:<{pass_width}} |\n"

        message += border
    else:
        message += "No se encontraron perfiles con contrasenas.\n"

    # Secciones adicionales opcionales (si se proporcionan).
    if extra:
        message += f"\n{'='*50}\n"
        message += f"INFORMACIÓN ADICIONAL DEL SISTEMA ({system_name})\n"
        message += f"{'='*50}\n\n"

        if system_name == 'Windows':
            if extra.get('interfaces'):
                message += "[netsh wlan show interfaces]\n"
                message += extra['interfaces'].rstrip() + "\n\n"

            if extra.get('drivers'):
                message += "[netsh wlan show drivers]\n"
                message += extra['drivers'].rstrip() + "\n\n"

            if extra.get('ipconfig'):
                message += "[ipconfig /all]\n"
                message += extra['ipconfig'].rstrip() + "\n\n"

            if extra.get('getmac'):
                message += "[getmac]\n"
                message += extra['getmac'].rstrip() + "\n\n"

            if extra.get('exports'):
                message += "[netsh wlan export profile]\n"
                message += extra['exports'].rstrip() + "\n\n"
        else:
            if extra.get('interfaces'):
                message += "[nmcli device status]\n"
                message += extra['interfaces'].rstrip() + "\n\n"

            if extra.get('drivers'):
                message += "[nmcli -t -f DEVICE,TYPE,GENERAL.DRIVER,GENERAL.HWADDR device show]\n"
                message += extra['drivers'].rstrip() + "\n\n"

            if extra.get('ipconfig'):
                message += "[ip address]\n"
                message += extra['ipconfig'].rstrip() + "\n\n"

            if extra.get('getmac'):
                message += "[ip -br link]\n"
                message += extra['getmac'].rstrip() + "\n\n"

            if extra.get('exports'):
                message += "[nmcli connection show <NAME>]\n"
                message += extra['exports'].rstrip() + "\n\n"

    # Aviso legal y delimitadores finales.
    message += f"\n{'='*50}\n"
    message += "USO AUTORIZADO: Este informe se proporciona únicamente con propósitos educativos y de aprendizaje.\n"
    message += "Empléelo solo en dispositivos de su propiedad o con permiso previo y explícito del titular.\n"
    message += f"{'='*50}\n"

    return message

