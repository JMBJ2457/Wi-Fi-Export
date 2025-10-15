# Analizador de Perfiles Wi‑Fi (CLI + GUI)

Bienvenido al repo de un pequeño utilitario que lista perfiles Wi‑Fi guardados, extrae sus contraseñas (cuando es posible) y genera un reporte bonito en texto. Además, puede enviar el informe por correo y trae una GUI sencilla en modo oscuro.

> USO AUTORIZADO: Proyecto con fines educativos. Úsalo solo en equipos propios o con permiso explícito.

---

## ¿Qué hace?

- **Escanea perfiles Wi‑Fi** guardados en el sistema y **obtiene contraseñas**.
- **Genera un reporte** en texto con tabla alineada.
- **Envía el reporte por correo** (SMTP).
- **Extras opcionales** (según SO):
  - Windows: `netsh` (interfaces, drivers, export, etc.)
  - Linux: `nmcli`/`ip` (estado de interfaces, drivers/mac, ip address…)
- **GUI en Tkinter** en tema oscuro.

---

## Requisitos

- Python 3.12+ (probado)
- Windows o Linux
- Para Linux:
  - NetworkManager (`nmcli`) para ver conexiones Wi‑Fi y PSK
  - Paquete `python3-tk` para la GUI: `sudo apt install -y python3-tk`
- Para Windows:
  - `netsh` (nativo) y Python con `tkinter` (instalador oficial de Python lo incluye)

---

## Estructura rápida

- `main.py`: punto de entrada CLI (y abre la GUI si se empaqueta)
- `wifi_analyzer/platform_windows.py`: funciones específicas de Windows (`netsh`)
- `wifi_analyzer/platform_linux.py`: funciones específicas de Linux (`nmcli`, `ip`)
- `wifi_analyzer/report.py`: formatea el reporte (tabla + extras)
- `wifi_analyzer/email_utils.py`: envío de correo SMTP
- `wifi_analyzer/ui.py`: interfaz gráfica (Tkinter)

---

## Uso (CLI)

Desde terminal en el directorio del proyecto:

```bash
python3 main.py
```

Flujo típico:

- El programa analiza perfiles.
- Muestra un menú: ver en pantalla, guardar a archivo, enviar por correo, abrir GUI.
- Puedes elegir incluir **información adicional** (interfaces, drivers, etc.).

Guardar a archivo (ejemplo):

- Elige opción 2, da un nombre o presiona Enter para `wifi_results.txt`.

Enviar correo (ejemplo):

- Opción 3 y completa SMTP/puerto/credenciales/destino.

---

## Uso (GUI)

Tienes dos caminos:

- Abrir desde el **menú CLI** (opción 5).
- O desde Python:

```python
from main import WiFiAnalyzer
from wifi_analyzer.ui import run_gui

run_gui(WiFiAnalyzer())
```

En la GUI encontrarás:

- Botón **Analizar** para generar el reporte.
- **Checkbox** para incluir información adicional.
- **Botones de secciones**: ver solo Interfaces, Drivers, IP, MAC, Export.
- **Guardar** y **Enviar correo** con diálogos sencillos.

---

## Generar ejecutable (build)

### Linux (binario nativo)

1) Crear venv e instalar PyInstaller

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pyinstaller
```

2) Construir

```bash
pyinstaller --onefile --noconsole main.py
# si quieres ver logs en terminal:
# pyinstaller --onefile --console main.py
```

3) Ejecutar

```bash
./dist/main
```

### Windows (.exe)

1) En una máquina Windows:

```bat
py -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install pyinstaller
```

2) Construir `.exe` (GUI por defecto)

```bat
pyinstaller --onefile --noconsole main.py
```

3) Ejecutar

```bat
.dist\main.exe
```

Si alguna vez no detecta Tkinter:

```bat
pyinstaller --onefile --noconsole --hidden-import=tkinter main.py
```

---

## Problemas comunes

- "No module named 'tkinter'":
  - Linux: `sudo apt install -y python3-tk`
  - Windows: usa instalador oficial de Python (incluye Tcl/Tk)

- PEP 668 / entorno gestionado (Ubuntu):
  - Usa un **virtualenv** antes de `pip install`:
  
  ```bash
  sudo apt install -y python3.12-venv
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- En Linux no aparecen extras:
  - Asegúrate de tener `nmcli` (NetworkManager) y `ip` disponibles.

- En Windows, SMTP falla:
  - Gmail requiere App Password con 2FA.

---

## Aviso legal

Este proyecto es **exclusivamente educativo**. No está diseñado para acceder a información de terceros. Úsalo **solo** en equipos propios o con autorización explícita.

---

## Créditos y licenciamiento

- Hecho con Python estándar (`os`, `subprocess`, `re`, `smtplib`, `tkinter`).
- Empaquetado con **PyInstaller**.
- Ajusta y reutiliza a tu gusto respetando el aviso legal.
