"""Utilidades específicas para Linux basadas en NetworkManager (nmcli).

Este módulo proporciona funciones para listar perfiles Wi‑Fi y obtener
sus contraseñas (PSK) almacenadas mediante `nmcli`.
"""

import subprocess
import shutil


def get_profiles():
    """Devuelve la lista de conexiones Wi‑Fi conocidas por NetworkManager.

    Requisitos:
        - El binario `nmcli` debe estar disponible en el sistema.

    Retorna:
        Lista de nombres de conexión (SSIDs guardados) gestionados por NM.
    """
    if shutil.which('nmcli') is None:
        return []
    # Se listan todas las conexiones y se filtran las de tipo Wi‑Fi.
    result = subprocess.run(
        ['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return []
    profiles = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split(':', 1)
        if len(parts) != 2:
            continue
        name, ctype = parts[0].strip(), parts[1].strip()
        # `TYPE` puede mostrarse como 'wifi' o '802-11-wireless' según versión.
        if ctype in ('wifi', '802-11-wireless') and name:
            profiles.append(name)
    return profiles


def get_password(profile_name: str) -> str:
    """Obtiene la clave PSK de una conexión gestionada por NM.

    Parámetros:
        profile_name: Nombre de la conexión tal como aparece en `nmcli`.

    Retorna:
        La contraseña si está disponible; un mensaje estándar en caso contrario.
    """
    if shutil.which('nmcli') is None:
        return "No disponible (nmcli no encontrado)"
    # Se consulta el campo '802-11-wireless-security.psk' de la conexión.
    result = subprocess.run(
        ['nmcli', '-s', '-g', '802-11-wireless-security.psk', 'connection', 'show', profile_name],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return "No disponible"
    password = result.stdout.strip()
    if password:
        return password
    return "Sin contrasena o WPS"


def get_interfaces() -> str:
    """Devuelve el estado de dispositivos gestionados por NetworkManager."""
    if shutil.which('nmcli') is None:
        return ''
    r = subprocess.run(['nmcli', 'device', 'status'], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ''


def get_drivers() -> str:
    """Devuelve información relevante de dispositivos Wi‑Fi (driver/HWADDR).

    Estrategia: listar dispositivos y para cada interfaz Wi‑Fi consultar
    campos específicos, ya que algunas versiones no muestran GENERAL.DRIVER
    al pedir múltiples dispositivos en bloque.
    """
    if shutil.which('nmcli') is None:
        return ''
    # 1) Listar dispositivos y tipos
    devs = subprocess.run(['nmcli', '-t', '-f', 'DEVICE,TYPE', 'device', 'status'],
                          capture_output=True, text=True)
    if devs.returncode != 0:
        return ''
    lines = []
    for line in devs.stdout.splitlines():
        if not line.strip() or ':' not in line:
            continue
        dev, dtype = line.split(':', 1)
        dev, dtype = dev.strip(), dtype.strip()
        if dtype not in ('wifi', '802-11-wireless') or not dev:
            continue
        # 2) Consultar driver y MAC por interfaz
        drv = subprocess.run(['nmcli', '-g', 'GENERAL.DRIVER', 'device', 'show', dev],
                             capture_output=True, text=True)
        mac = subprocess.run(['nmcli', '-g', 'GENERAL.HWADDR', 'device', 'show', dev],
                             capture_output=True, text=True)
        drv_val = drv.stdout.strip() if drv.returncode == 0 else ''
        mac_val = mac.stdout.strip() if mac.returncode == 0 else ''
        lines.append(f"DEVICE={dev}\tDRIVER={drv_val or 'N/A'}\tHWADDR={mac_val or 'N/A'}")
    return "\n".join(lines)


def get_ipconfig_all() -> str:
    """Equivalente aproximado de ipconfig /all en Linux (salida de `ip address`)."""
    if shutil.which('ip') is None:
        return ''
    r = subprocess.run(['ip', 'address'], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ''


def get_mac_addresses() -> str:
    """Listado abreviado de interfaces y MAC usando `ip -br link`."""
    if shutil.which('ip') is None:
        return ''
    r = subprocess.run(['ip', '-br', 'link'], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ''


def export_profiles() -> str:
    """Exporta la definición de conexiones conocidas (sin escribir archivos).

    No existe un comando de exportación directo como en Windows. Se obtiene
    la configuración detallada de cada conexión mediante `nmcli connection show`.
    """
    if shutil.which('nmcli') is None:
        return ''
    # Listar nombres de conexiones wifi y concatenar su detalle.
    names_proc = subprocess.run(['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show'],
                                capture_output=True, text=True)
    if names_proc.returncode != 0:
        return ''
    out = []
    for line in names_proc.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split(':', 1)
        if len(parts) != 2:
            continue
        name, ctype = parts[0].strip(), parts[1].strip()
        if ctype in ('wifi', '802-11-wireless'):
            det = subprocess.run(['nmcli', '-s', 'connection', 'show', name], capture_output=True, text=True)
            if det.returncode == 0:
                out.append(f"[nmcli connection show {name}]\n{det.stdout.strip()}\n")
    return "\n".join(out)

