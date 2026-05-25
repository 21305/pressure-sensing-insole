import serial
import tkinter as tk
import threading
from io import BytesIO
from PIL import Image, ImageTk
import requests

# ========================= CONFIGURACIÓN =========================
PORT = "COM9"
BAUD = 115200
ser = serial.Serial(PORT, BAUD, timeout=1)

URL_IMAGEN = "https://cdn.supercoloring.com/coloring/2129699/feet-coloring-page-md.png"

ZERO_READING = 680
MAX_READING_50KG = 1029
SCALE_FACTOR = 50.0 / (MAX_READING_50KG - ZERO_READING)

UMBRAL = 20  # valor mínimo para considerar lectura válida
modo_vivo = True  # por defecto se ve en vivo

def lectura_a_kg(lectura):
    peso = (lectura - ZERO_READING) * SCALE_FACTOR
    return round(max(0.0, min(peso, 50.0)), 2)

# ========================= INTERFAZ ==============================
root = tk.Tk()
root.title("Diagnóstico Plantar Inteligente")
root.geometry("700x600")
root.resizable(False, False)
root.configure(bg="#ECECEC")

# ---------------- HEADER ----------------
header = tk.Label(root, text="MAPA DE PRESIÓN PLANTAR",
                  font=("Century Gothic", 18, "bold"),
                  bg="#2C3E50", fg="white", pady=10)
header.pack(fill="x")

# ---------------- CONTENEDOR PRINCIPAL ----------------
main_frame = tk.Frame(root, bg="#ECECEC")
main_frame.pack(fill="both", expand=True)

# --- Columna izquierda: Canvas ---
canvas_frame = tk.Frame(main_frame, bg="#ECECEC")
canvas_frame.pack(side="left", padx=20, pady=10)

canvas = tk.Canvas(canvas_frame, width=320, height=580, bg="white", highlightthickness=0)
canvas.pack()

try:
    response = requests.get(URL_IMAGEN, timeout=5)
    img_data = BytesIO(response.content)
    pie_img = Image.open(img_data).resize((300, 500))
    pie_photo = ImageTk.PhotoImage(pie_img)
    canvas.create_image(160, 250, image=pie_photo)
except Exception as e:
    print("No se pudo descargar la imagen:", e)

def crear_sensor(x, y, r):
    return canvas.create_oval(x-r, y-r, x+r, y+r, fill="", outline="gray", width=2)

sensores = [
    crear_sensor(80, 175, 35),   # S1
    crear_sensor(230, 175, 35),  # S2
    crear_sensor(130, 290, 37),  # S3
    crear_sensor(230, 290, 37),  # S4
    crear_sensor(170, 420, 50)   # S5
]

labels = [
    canvas.create_text(85, 175, text="0%", font=("Century Gothic", 12, "bold")),
    canvas.create_text(235, 175, text="0%", font=("Century Gothic", 12, "bold")),
    canvas.create_text(135, 290, text="0%", font=("Century Gothic", 12, "bold")),
    canvas.create_text(235, 290, text="0%", font=("Century Gothic", 12, "bold")),
    canvas.create_text(175, 420, text="0%", font=("Century Gothic", 12, "bold")),
]

# === Secciones anatómicas ===
canvas.create_text(160, 120, text="ANTEPÍE", font=("Century Gothic", 12, "bold"), fill="#34495E")
canvas.create_text(165, 220, text="MEDIOPIÉ", font=("Century Gothic", 12, "bold"), fill="#34495E")
canvas.create_text(170, 350, text="RETROPIÉ", font=("Century Gothic", 12, "bold"), fill="#34495E")

# === Etiquetas interno/externo ===
canvas.create_text(80, 130, text="INTERNO", font=("Century Gothic", 10, "bold"), fill="#2C3E50")
canvas.create_text(240, 130, text="EXTERNO", font=("Century Gothic", 10, "bold"), fill="#2C3E50")
canvas.create_text(130, 245, text="INTERNO", font=("Century Gothic", 10, "bold"), fill="#2C3E50")
canvas.create_text(240, 245, text="EXTERNO", font=("Century Gothic", 10, "bold"), fill="#2C3E50")

# --- Columna derecha: Diagnóstico + Botón ---
side_panel = tk.Frame(main_frame, bg="#F4F4F4", width=300)
side_panel.pack(side="right", fill="y", padx=10, pady=10)

diag_text = tk.Label(side_panel, text="Presiona 'Capturar pisada' para iniciar diagnóstico.",
                     font=("Century Gothic", 12), bg="#F4F4F4",
                     wraplength=280, justify="left")
diag_text.pack(pady=20)

boton_captura = tk.Button(side_panel, text="Capturar pisada",
                          font=("Century Gothic", 12, "bold"),
                          bg="#3498DB", fg="white",
                          command=lambda: capturar_pisada())
boton_captura.pack(pady=10)

boton_toggle = tk.Button(side_panel, text="Congelar vista",
                         font=("Century Gothic", 12, "bold"),
                         bg="#E67E22", fg="white",
                         command=lambda: toggle_modo())
boton_toggle.pack(pady=10)

# ================== DIAGNÓSTICO POR ZONAS ==================
def obtener_diagnostico_zonas(valores):
    filtrados = [v if v >= UMBRAL else 0 for v in valores]

    antepie = filtrados[0] + filtrados[1]
    mediopie = filtrados[2] + filtrados[3]
    retropie = filtrados[4]

    total = antepie + mediopie + retropie
    if total == 0:
        return ("Sin datos", "No se detectó presión en los sensores.")

    pct_antepie = (antepie / total) * 100
    pct_mediopie = (mediopie / total) * 100
    pct_retropie = (retropie / total) * 100

    if 25 <= pct_antepie <= 40 and 20 <= pct_mediopie <= 30 and 25 <= pct_retropie <= 40:
        return ("Pisada normal", "Distribución equilibrada de cargas en antepié, mediopié y retropié.")

    zona_max = max(pct_antepie, pct_mediopie, pct_retropie)
    if zona_max == pct_antepie:
        if filtrados[0] > filtrados[1]:
            return ("Sobrecarga antepié interno (metatarsalgia medial)",
                    "Revisar apoyo del primer metatarsiano, usar plantilla con descarga en zona medial.")
        else:
            return ("Sobrecarga antepié externo (metatarsalgia lateral)",
                    "Plantilla con soporte externo y redistribución de carga.")
    elif zona_max == pct_mediopie:
        if filtrados[2] > filtrados[3]:
            return ("Colapso del arco (pie plano/pronación)",
                    "Fortalecer musculatura intrínseca, plantilla rígida con soporte de arco.")
        else:
            return ("Arco elevado (pie cavo/supinación)",
                    "Ejercicios de estabilidad, plantilla con amortiguación lateral.")
    else:
        return ("Sobrecarga retropié (talalgia/fascitis plantar)",
                "Uso de almohadilla en talón, estiramiento de fascia y gemelos.")

# =================== VARIABLES DE LECTURA ====================
buffer_lecturas = []
ultima_lectura = [0,0,0,0,0]

# =================== FUNCIONES AUX ===========================
def calcular_porcentajes(valores):
    filtrados = [v if v >= UMBRAL else 0 for v in valores]
    total = sum(filtrados)
    return [0]*5 if total == 0 else [int((v/total)*100) for v in filtrados]

def actualizar_interfaz_con_datos(valores):
    # Actualiza visualmente (porcentajes y colores) sin diagnóstico
    porcentajes = calcular_porcentajes(valores)
    for i, pct in enumerate(porcentajes):
        canvas.itemconfig(labels[i], text=f"S{i+1}: {pct}%")
        color = "#2ECC71" if pct <= 33 else "#F1C40F" if pct <= 66 else "#E74C3C"
        canvas.itemconfig(sensores[i], fill=color)

def actualizar_diag_con_datos(valores):
    # Calcula totales filtrados para peso y diagnóstico
    filtrados = [v if v >= UMBRAL else 0 for v in valores]
    total_filtrado = sum(filtrados)

    d, r = obtener_diagnostico_zonas(valores)
    peso_estimado = lectura_a_kg(total_filtrado)

    diag_text.config(text=(
        f"Diagnóstico: {d}\n"
        f"Recomendación: {r}\n\n"
        f"Lectura usada (filtrada): {total_filtrado}  → Peso estimado: {peso_estimado} kg"
    ))

# =================== LECTURA SERIAL (modo en vivo) ====================
def leer_serial():
    global ultima_lectura, buffer_lecturas
    while True:
        try:
            linea = ser.readline().decode(errors='ignore').strip()
            if not linea:
                continue
            parts = linea.split(",")
            try:
                datos = list(map(int, parts))
            except:
                continue
            if len(datos) == 5:
                buffer_lecturas.append(datos)
                ultima_lectura = datos

                print("Datos recibidos:", datos)
                # Actualización en vivo solo visual (sin diagnóstico)
                if modo_vivo:
                    actualizar_interfaz_con_datos(ultima_lectura)
        except Exception as e:
            print("Error lectura serial:", e)
            continue

# =================== TOGGLE MODO VIVO/CONGELADO ====================
def toggle_modo():
    global modo_vivo
    modo_vivo = not modo_vivo
    if modo_vivo:
        boton_toggle.config(text="Congelar vista")
        # Al volver a vivo, limpia el panel de diagnóstico para evitar confusión
        diag_text.config(text="Vista en vivo activada. Presiona 'Capturar pisada' para diagnóstico.")
    else:
        boton_toggle.config(text="Ver en vivo")
        # En modo congelado puedes capturar diagnóstico con el botón
        diag_text.config(text="Vista congelada. Presiona 'Capturar pisada' para diagnóstico.")

# =================== CAPTURA (diagnóstico bajo demanda) ====================
def capturar_pisada():
    if ultima_lectura == [0,0,0,0,0]:
        diag_text.config(text="No se recibió lectura válida. Intenta de nuevo.")
        return

    # Congela vista en el momento de la captura para que coincida con diagnóstico
    actualizar_interfaz_con_datos(ultima_lectura)
    actualizar_diag_con_datos(ultima_lectura)

# =================== INICIO ====================
threading.Thread(target=leer_serial, daemon=True).start()
root.mainloop()