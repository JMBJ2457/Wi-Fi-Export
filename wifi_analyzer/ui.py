"""Interfaz gráfica (Tkinter) para el analizador Wi‑Fi.

Expone la función `run_gui(analyzer)` que recibe una instancia de
`WiFiAnalyzer` y presenta una ventana para ejecutar el análisis,
mostrar/guardar el reporte y enviarlo por correo.
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext, filedialog, messagebox
from email.utils import parseaddr


def run_gui(analyzer):
    root = tk.Tk()
    root.title("Analizador de Perfiles Wi‑Fi")
    root.geometry("800x600")

    # Tema oscuro (colores base)
    BG = "#1e1e1e"       # fondo general
    FG = "#e0e0e0"       # texto principal
    ACCENT = "#3a86ff"   # acento para botones foco
    PANEL = "#252526"     # paneles/frames
    ENTRY_BG = "#2d2d2d" # entradas/texto

    # Configurar fondo base
    root.configure(bg=BG)

    # Estilos ttk en modo 'clam' con colores oscuros
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass

    style.configure('.',
                    background=BG,
                    foreground=FG)
    style.configure('TFrame', background=PANEL)
    style.configure('TLabel', background=PANEL, foreground=FG)
    style.configure('TCheckbutton', background=PANEL, foreground=FG)
    style.configure('TButton', background=PANEL, foreground=FG, padding=6)
    style.map('TButton',
              background=[('active', '#2e2e2e')],
              foreground=[('active', FG)],
              focuscolor=[('focus', ACCENT)])
    # Desactivar hover en checkbox (mantener colores constantes)
    style.map('TCheckbutton',
              background=[('active', PANEL)],
              foreground=[('active', FG)])

    # Frame de controles
    controls = ttk.Frame(root, padding=10)
    controls.pack(side=tk.TOP, fill=tk.X)

    include_extra = tk.BooleanVar(value=False)
    chk_extra = ttk.Checkbutton(controls, text="Incluir información adicional", variable=include_extra)
    chk_extra.pack(side=tk.LEFT)

    # Subframe de botones para secciones específicas
    sections_frame = ttk.Frame(root, padding=(10, 0, 10, 0))
    sections_frame.pack(side=tk.TOP, fill=tk.X)

    def show_section(section_key: str):
        title, content = analyzer.get_optional_section(section_key)
        output.delete(1.0, tk.END)
        if title:
            output.insert(tk.END, f"INFORMACIÓN ADICIONAL: {title}\n\n")
        if content.strip():
            output.insert(tk.END, content)
        else:
            output.insert(tk.END, "No hay información disponible para esta sección.")

    btn_interfaces = ttk.Button(sections_frame, text="Interfaces", command=lambda: show_section('interfaces'))
    btn_drivers = ttk.Button(sections_frame, text="Drivers", command=lambda: show_section('drivers'))
    btn_ipconfig = ttk.Button(sections_frame, text="IP Config", command=lambda: show_section('ipconfig'))
    btn_mac = ttk.Button(sections_frame, text="Direcciones MAC", command=lambda: show_section('getmac'))
    btn_export = ttk.Button(sections_frame, text="Exportar perfiles", command=lambda: show_section('exports'))

    for w in (btn_interfaces, btn_drivers, btn_ipconfig, btn_mac, btn_export):
        w.pack(side=tk.LEFT, padx=5, pady=6)

    def do_analyze():
        try:
            output.delete(1.0, tk.END)
            ok = analyzer.analyze_wifi_profiles()
            if not ok:
                messagebox.showerror("Error", "No se pudieron obtener perfiles Wi‑Fi.")
                return
            report = analyzer.format_results(include_extra=include_extra.get())
            output.insert(tk.END, report)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def do_save():
        try:
            report = analyzer.format_results(include_extra=include_extra.get())
            path = filedialog.asksaveasfilename(
                title="Guardar reporte",
                defaultextension=".txt",
                filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
                initialfile="wifi_results.txt",
            )
            if not path:
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write(report)
            messagebox.showinfo("Guardado", f"Reporte guardado en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def do_send_email():
        dlg = tk.Toplevel(root)
        dlg.title("Enviar por correo")
        dlg.transient(root)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Servidor SMTP:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(frm, text="Puerto:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(frm, text="Tu email:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(frm, text="Tu contraseña:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(frm, text="Destinatario:").grid(row=4, column=0, sticky=tk.W, pady=2)

        ent_smtp = ttk.Entry(frm, width=40)
        ent_port = ttk.Entry(frm, width=10)
        ent_user = ttk.Entry(frm, width=40)
        ent_pass = ttk.Entry(frm, width=40, show="*")
        ent_rcpt = ttk.Entry(frm, width=40)

        ent_smtp.grid(row=0, column=1, sticky=tk.W)
        ent_port.grid(row=1, column=1, sticky=tk.W)
        ent_user.grid(row=2, column=1, sticky=tk.W)
        ent_pass.grid(row=3, column=1, sticky=tk.W)
        ent_rcpt.grid(row=4, column=1, sticky=tk.W)

        ent_port.insert(0, "587")

        def load_env_defaults():
            env = {}
            # 1) Variables de entorno del proceso
            for k in ("SMTP_SERVER", "PORT", "EMAIL_USER", "APP_PASSWORD", "RECIPIENT_EMAIL"):
                v = os.environ.get(k)
                if v:
                    env[k] = v
            # 2) Archivo .env local (clave=valor con o sin comillas)
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
                            if k and v and k in ("SMTP_SERVER", "PORT", "EMAIL_USER", "APP_PASSWORD", "RECIPIENT_EMAIL"):
                                env.setdefault(k, v)
            except Exception:
                pass
            # Aplicar a los campos si existen
            if env.get("SMTP_SERVER"):
                ent_smtp.delete(0, tk.END)
                ent_smtp.insert(0, env["SMTP_SERVER"])
            if env.get("PORT"):
                ent_port.delete(0, tk.END)
                ent_port.insert(0, str(env["PORT"]))
            if env.get("EMAIL_USER"):
                ent_user.delete(0, tk.END)
                ent_user.insert(0, env["EMAIL_USER"])
            if env.get("APP_PASSWORD"):
                ent_pass.delete(0, tk.END)
                ent_pass.insert(0, env["APP_PASSWORD"])
            if env.get("RECIPIENT_EMAIL"):
                ent_rcpt.delete(0, tk.END)
                ent_rcpt.insert(0, env["RECIPIENT_EMAIL"])

        load_env_defaults()

        def send_now():
            try:
                smtp = ent_smtp.get().strip()
                port = int(ent_port.get().strip())
                user = ent_user.get().strip()
                pwd = ent_pass.get().strip()
                rcpt = ent_rcpt.get().strip()
                if not all([smtp, port, user, pwd, rcpt]):
                    messagebox.showerror("Error", "Faltan datos de configuración.")
                    return
                # Validación simple de correos (remitente y destinatario)
                def _is_valid_email(addr: str) -> bool:
                    return '@' in parseaddr(addr)[1]
                if not _is_valid_email(user):
                    messagebox.showerror("Error", "El remitente debe ser un correo válido (ej. usuario@gmail.com).")
                    return
                if not _is_valid_email(rcpt):
                    messagebox.showerror("Error", "El destinatario debe ser un correo válido (ej. destinatario@gmail.com).")
                    return
                # Asegurar que hay datos analizados
                if not analyzer.profiles_data:
                    ok = analyzer.analyze_wifi_profiles()
                    if not ok:
                        messagebox.showerror("Error", "No se pudieron obtener perfiles Wi‑Fi.")
                        return
                ok = analyzer.send_email(smtp, port, user, pwd, rcpt, include_extra=include_extra.get())
                if ok:
                    messagebox.showinfo("Éxito", "Correo enviado correctamente.")
                    dlg.destroy()
                else:
                    try:
                        from wifi_analyzer import email_utils
                        detail = email_utils.get_last_error().strip()
                    except Exception:
                        detail = ""
                    if detail:
                        messagebox.showerror("Error", f"No se pudo enviar el correo.\n\nDetalle: {detail}")
                    else:
                        messagebox.showerror("Error", "No se pudo enviar el correo.")
            except Exception as e:
                messagebox.showerror("Error", f"Error enviando correo: {e}")

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Enviar", command=send_now).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Cancelar", command=dlg.destroy).pack(side=tk.LEFT, padx=5)

    ttk.Button(controls, text="Analizar", command=do_analyze).pack(side=tk.LEFT, padx=5)
    ttk.Button(controls, text="Guardar", command=do_save).pack(side=tk.LEFT, padx=5)
    ttk.Button(controls, text="Enviar correo", command=do_send_email).pack(side=tk.LEFT, padx=5)

    # Área de salida
    output = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier New", 10))
    output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    # Colores para texto scrollable en modo oscuro
    output.configure(bg=ENTRY_BG, fg=FG, insertbackground=FG)
    # Ajustar colores del scrollbar (según disponibilidad de tema)
    try:
        style.configure('Vertical.TScrollbar', background=PANEL, troughcolor=BG)
        style.configure('Horizontal.TScrollbar', background=PANEL, troughcolor=BG)
    except Exception:
        pass

    root.mainloop()

