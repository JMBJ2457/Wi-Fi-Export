"""
ANALIZADOR DE PERFILES WI-FI - v1.0
Analiza perfiles de redes Wi‑Fi y permite enviar un informe por correo electrónico.
USO AUTORIZADO: Herramienta con fines educativos. Úsela únicamente en equipos propios o con autorización expresa del titular.
"""

import os
import platform
import sys
from wifi_analyzer import platform_windows as win_mod
from wifi_analyzer import platform_linux as lin_mod
from wifi_analyzer import report as report_mod
from wifi_analyzer import email_utils


class WiFiAnalyzer:
    def __init__(self):
        self.profiles_data = {}
        
    def collect_optional_info(self):
        """Recolecta información adicional opcional (solo Windows)."""
        try:
            sysname = platform.system()
            extra = {}
            if sysname == 'Windows':
                extra['interfaces'] = win_mod.get_interfaces()
                extra['drivers'] = win_mod.get_drivers()
                extra['ipconfig'] = win_mod.get_ipconfig_all()
                extra['getmac'] = win_mod.get_mac_addresses()
                # Exportar perfiles a un directorio local (Windows)
                export_dir = os.path.join(os.getcwd(), 'wifi_exports')
                os.makedirs(export_dir, exist_ok=True)
                extra['exports'] = win_mod.export_profiles(export_dir)
            else:
                # Equivalentes en Linux
                extra['interfaces'] = lin_mod.get_interfaces()
                extra['drivers'] = lin_mod.get_drivers()
                extra['ipconfig'] = lin_mod.get_ipconfig_all()
                extra['getmac'] = lin_mod.get_mac_addresses()
                extra['exports'] = lin_mod.export_profiles()
            return extra
        except Exception:
            return {}

    def get_optional_section(self, section: str) -> tuple[str, str]:
        """Obtiene una única sección opcional por nombre y su título.

        Secciones válidas: 'interfaces', 'drivers', 'ipconfig', 'getmac', 'exports'.

        Retorna: (titulo, contenido). Si no hay contenido, devuelve cadena vacía.
        """
        sysname = platform.system()
        title = ""
        content = ""
        try:
            if sysname == 'Windows':
                if section == 'interfaces':
                    title = "[netsh wlan show interfaces]"
                    content = win_mod.get_interfaces()
                elif section == 'drivers':
                    title = "[netsh wlan show drivers]"
                    content = win_mod.get_drivers()
                elif section == 'ipconfig':
                    title = "[ipconfig /all]"
                    content = win_mod.get_ipconfig_all()
                elif section == 'getmac':
                    title = "[getmac]"
                    content = win_mod.get_mac_addresses()
                elif section == 'exports':
                    title = "[netsh wlan export profile]"
                    export_dir = os.path.join(os.getcwd(), 'wifi_exports')
                    os.makedirs(export_dir, exist_ok=True)
                    content = win_mod.export_profiles(export_dir)
            else:
                if section == 'interfaces':
                    title = "[nmcli device status]"
                    content = lin_mod.get_interfaces()
                elif section == 'drivers':
                    title = "[nmcli -t -f DEVICE,TYPE,GENERAL.DRIVER,GENERAL.HWADDR device show]"
                    content = lin_mod.get_drivers()
                elif section == 'ipconfig':
                    title = "[ip address]"
                    content = lin_mod.get_ipconfig_all()
                elif section == 'getmac':
                    title = "[ip -br link]"
                    content = lin_mod.get_mac_addresses()
                elif section == 'exports':
                    title = "[nmcli connection show <NAME>]"
                    content = lin_mod.export_profiles()
        except Exception:
            content = ""
        return title, (content or "")

    def get_wifi_profiles(self):
        """Obtiene la lista de perfiles Wi-Fi guardados en el sistema"""
        try:
            print("[INFO] Obteniendo perfiles Wi-Fi...")
            system_name = platform.system()
            if system_name == 'Windows':
                profiles = win_mod.get_profiles()
            else:
                profiles = lin_mod.get_profiles()

            print(f"[OK] Encontrados {len(profiles)} perfiles Wi-Fi")
            return profiles
            
        except Exception as e:
            print(f"[ERROR] Error obteniendo perfiles: {str(e)}")
            return []
    
    def get_wifi_password(self, profile_name):
        """Extrae la contrasena de un perfil Wi-Fi especifico"""
        try:
            print(f"[INFO] Extrayendo contrasena para: {profile_name}")
            system_name = platform.system()
            if system_name == 'Windows':
                return win_mod.get_password(profile_name)
            else:
                return lin_mod.get_password(profile_name)
                
        except Exception as e:
            print(f"[ERROR] Error extrayendo contrasena para {profile_name}: {str(e)}")
            return "Error al obtener"
    
    def analyze_wifi_profiles(self):
        """Funcion principal que orquesta el analisis completo"""
        print("[INFO] Iniciando analisis de perfiles Wi-Fi...")
        
        # Obtener perfiles
        profiles = self.get_wifi_profiles()
        
        if not profiles:
            print("[ERROR] No se encontraron perfiles Wi-Fi")
            return False
        
        # Extraer contrasenas para cada perfil
        for profile in profiles:
            password = self.get_wifi_password(profile)
            self.profiles_data[profile] = password
        
        print("[OK] Analisis completado")
        return True
    
    def format_results(self, include_extra: bool = False):
        """Formatea los resultados para el correo electronico"""
        extra = self.collect_optional_info() if include_extra else None
        return report_mod.format_results(self.profiles_data, extra)
    
    def send_email(self, smtp_server, smtp_port, email_user, email_password, 
                   recipient_email, subject="Reporte Analisis Wi-Fi", include_extra: bool = False):
        """Envia el reporte por correo electronico usando SMTP"""
        try:
            print("[INFO] Preparando envio de correo...")
            message_body = self.format_results(include_extra=include_extra)
            print(f"[INFO] Conectando a servidor SMTP: {smtp_server}:{smtp_port}")
            ok = email_utils.send_email(smtp_server, smtp_port, email_user, email_password,
                                        recipient_email, subject, message_body)
            if ok:
                print("[OK] Correo enviado exitosamente")
                return True
            print("[ERROR] Error enviando correo")
            return False
        except Exception as e:
            print(f"[ERROR] Error enviando correo: {str(e)}")
            return False
    
    def show_results(self, include_extra: bool = False):
        """Muestra los resultados en pantalla"""
        print("\n" + self.format_results(include_extra=include_extra))
    
    def save_to_file(self, filename="wifi_results.txt", include_extra: bool = False):
        """Guarda los resultados en un archivo"""
        try:
            results = self.format_results(include_extra=include_extra)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(results)
            print(f"[OK] Resultados guardados en: {filename}")
            return True
        except Exception as e:
            print(f"[ERROR] Error guardando archivo: {str(e)}")
            return False


def main():
    """Funcion principal"""
    print("ANALIZADOR DE PERFILES WI-FI")
    print("SOLO PARA FINES EDUCATIVOS")
    print("="*50)
    
    analyzer = WiFiAnalyzer()

    def load_env_defaults():
        env = {}
        for k in ("SMTP_SERVER", "PORT", "EMAIL_USER", "APP_PASSWORD", "RECIPIENT_EMAIL", "SUBJECT"):
            v = os.environ.get(k)
            if v:
                env[k] = v
        try:
            env_path = os.path.join(os.getcwd(), ".env")
            if os.path.isfile(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#') or '=' not in line:
                            continue
                        k, v = line.split('=', 1)
                        k, v = k.strip(), v.strip().strip('"').strip("'")
                        if k and v and k in ("SMTP_SERVER", "PORT", "EMAIL_USER", "APP_PASSWORD", "RECIPIENT_EMAIL", "SUBJECT"):
                            env.setdefault(k, v)
        except Exception:
            pass
        return env
    
    # Ejecutar analisis
    if analyzer.analyze_wifi_profiles():
        # Mostrar menu de opciones
        print("\n" + "="*50)
        print("OPCIONES DE SALIDA:")
        print("1. Solo ver resultados en pantalla")
        print("2. Guardar resultados en archivo")
        print("3. Enviar reporte por correo")
        print("4. Salir")
        print("5. Abrir interfaz gráfica")
        
        while True:
            try:
                choice = input("\nSelecciona una opcion (1-5): ").strip()
                
                if choice == "1":
                    # Solo mostrar resultados
                    inc = input("\n¿Incluir información adicional opcional? (s/n): ").strip().lower().startswith('s')
                    analyzer.show_results(include_extra=inc)
                    break
                    
                elif choice == "2":
                    # Guardar en archivo
                    inc = input("\n¿Incluir información adicional opcional? (s/n): ").strip().lower().startswith('s')
                    analyzer.show_results(include_extra=inc)
                    filename = input("\nNombre del archivo (Enter para default): ").strip()
                    if not filename:
                        filename = "wifi_results.txt"
                    analyzer.save_to_file(filename, include_extra=inc)
                    break
                    
                elif choice == "3":
                    # Enviar por correo
                    inc = input("\n¿Incluir información adicional opcional? (s/n): ").strip().lower().startswith('s')
                    analyzer.show_results(include_extra=inc)
                    env = load_env_defaults()
                    print("\nCONFIGURACION DE CORREO:")
                    def _prompt(label, default=""):
                        val = input(f"{label}{f' [{default}]' if default else ''}: ").strip()
                        return val or default
                    smtp_server = _prompt("Servidor SMTP (ej: smtp.gmail.com)", env.get("SMTP_SERVER", ""))
                    smtp_port_str = _prompt("Puerto SMTP (ej: 587)", str(env.get("PORT", "")))
                    email_user = _prompt("Tu email", env.get("EMAIL_USER", ""))
                    email_password = _prompt("Tu contrasena", env.get("APP_PASSWORD", ""))
                    recipient = _prompt("Email destinatario", env.get("RECIPIENT_EMAIL", ""))
                    subject = env.get("SUBJECT", "Reporte Analisis Wi-Fi")
                    try:
                        smtp_port = int(smtp_port_str)
                    except Exception:
                        print("[ERROR] Puerto SMTP invalido")
                        break
                    
                    if all([smtp_server, smtp_port, email_user, email_password, recipient]):
                        analyzer.send_email(smtp_server, smtp_port, email_user, 
                                          email_password, recipient, subject, include_extra=inc)
                    else:
                        print("[ERROR] Faltan datos de configuracion")
                    break
                    
                elif choice == "4":
                    print("Saliendo...")
                    break
                
                elif choice == "5":
                    # Abrir GUI (tema oscuro)
                    try:
                        from wifi_analyzer.ui import run_gui
                        run_gui(analyzer)
                    except ModuleNotFoundError as e:
                        if 'tkinter' in str(e).lower():
                            sysname = platform.system()
                            print("[ERROR] Tkinter no está instalado.")
                            if sysname == 'Linux':
                                print("[INFO] Instálalo con tu gestor de paquetes, por ejemplo:")
                                print("       Ubuntu/Debian: sudo apt-get install -y python3-tk")
                                print("       Fedora:        sudo dnf install -y python3-tkinter")
                                print("       Arch:          sudo pacman -S tk")
                            elif sysname == 'Windows':
                                print("[INFO] Usa el instalador oficial de Python (incluye Tcl/Tk) y reconstruye el .exe si aplica.")
                            else:
                                print("[INFO] Verifica la instalación de Tcl/Tk para tu sistema.")
                        else:
                            print(f"[ERROR] No se pudo abrir la interfaz gráfica: {e}")
                    except Exception as e:
                        print(f"[ERROR] No se pudo abrir la interfaz gráfica: {e}")
                    break
                    
                else:
                    print("[ERROR] Opcion invalida. Selecciona 1-5.")
                    
            except KeyboardInterrupt:
                print("\nSaliendo...")
                break
            except ValueError:
                print("[ERROR] Por favor ingresa un numero valido.")
    
    else:
        print("[ERROR] No se pudo completar el analisis")
    
    print("\n[OK] Programa finalizado")
    input("Presiona Enter para salir...")


if __name__ == "__main__":
    import sys
    # Si está empaquetado como ejecutable (PyInstaller), abrir GUI por defecto
    if getattr(sys, 'frozen', False):
        try:
            from wifi_analyzer.ui import run_gui
            run_gui(WiFiAnalyzer())
        except Exception as e:
            # Si la GUI falla, caer al modo CLI
            print(f"[WARN] No se pudo iniciar la GUI: {e}")
            main()
    else:
        main()