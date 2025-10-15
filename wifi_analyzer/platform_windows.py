"""Utilidades específicas para Windows basadas en `netsh`.

Este módulo ofrece funciones para listar perfiles Wi‑Fi, obtener
contraseñas y consultar información adicional de red usando comandos
del sistema disponibles en Windows.
"""

import subprocess
import re


def get_profiles():
    """Devuelve la lista de perfiles Wi‑Fi registrados en Windows.

    Retorna:
        Lista de nombres de perfil (SSID guardados) extraídos de `netsh`.
    """
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'profiles'],
            capture_output=True,
            text=True,
            encoding='cp1252'
        )
        if result.returncode != 0:
            return []

        text_out = result.stdout
        # Compatibilidad bilingüe: español e inglés del sistema.
        pattern_es = r"Perfil de todos los usuarios\s*:\s*(.+)"
        pattern_en = r"All User Profile\s*:\s*(.+)"
        profiles = re.findall(pattern_es, text_out)
        if not profiles:
            profiles = re.findall(pattern_en, text_out)
        return [p.strip() for p in profiles if p.strip()]
    except Exception:
        return []


def get_password(profile_name: str) -> str:
    """Obtiene la contraseña de un perfil Wi‑Fi específico.

    Parámetros:
        profile_name: Nombre del perfil tal como lo reporta `netsh`.

    Retorna:
        La contraseña (Key Content) si está disponible o un mensaje estándar.
    """
    try:
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'profile', profile_name, 'key=clear'],
            capture_output=True,
            text=True,
            encoding='cp1252'
        )
        if result.returncode != 0:
            return "No disponible"

        text_out = result.stdout
        # Compatibilidad bilingüe para la línea con el contenido de la clave.
        pattern_es = r"Contenido de la clave\s*:\s*(.+)"
        pattern_en = r"Key Content\s*:\s*(.+)"
        m = re.search(pattern_es, text_out)
        if not m:
            m = re.search(pattern_en, text_out)
        if m:
            return m.group(1).strip()
        return "Sin contrasena o WPS"
    except Exception:
        return "Error al obtener"


def get_interfaces() -> str:
    """Devuelve información de interfaces Wi‑Fi reportadas por `netsh`."""
    try:
        r = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True, encoding='cp1252')
        return r.stdout if r.returncode == 0 else ''
    except Exception:
        return ''


def get_drivers() -> str:
    """Devuelve información de drivers Wi‑Fi instalados (via `netsh`)."""
    try:
        r = subprocess.run(['netsh', 'wlan', 'show', 'drivers'], capture_output=True, text=True, encoding='cp1252')
        return r.stdout if r.returncode == 0 else ''
    except Exception:
        return ''


def get_ipconfig_all() -> str:
    """Devuelve la salida de `ipconfig /all` completa."""
    try:
        r = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, encoding='cp1252')
        return r.stdout if r.returncode == 0 else ''
    except Exception:
        return ''


def get_mac_addresses() -> str:
    """Devuelve las direcciones MAC mediante el comando `getmac`."""
    try:
        r = subprocess.run(['getmac'], capture_output=True, text=True, encoding='cp1252')
        return r.stdout if r.returncode == 0 else ''
    except Exception:
        return ''


def export_profiles(output_dir: str) -> str:
    """Exporta perfiles Wi‑Fi a XML con claves en claro al directorio indicado."""
    try:
        r = subprocess.run(['netsh', 'wlan', 'export', 'profile', 'key=clear', f'folder={output_dir}'], capture_output=True, text=True, encoding='cp1252')
        return r.stdout if r.returncode == 0 else ''
    except Exception:
        return ''

