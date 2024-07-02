import math
import customtkinter as ctk
import os
import tkinter
from PIL import Image
from tkinter import filedialog
import pandas as pd
from CTkTable import CTkTable
from CTkTableRowSelector import CTkTableRowSelector
import tkintermapview
import sqlite3
import pyproj
from CTkMessagebox import CTkMessagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

def haversine(lat1, lon1, lat2, lon2):
    #Función para calcular la distancia entre 2 puntos a partir de la longitud
    pass

def ejecutar_query_sqlite(database_name, table_name, columns='*', where_column=None, where_value=None):
    # Código para ejecutar consulta SQL
    pass

def agregar_df_a_sqlite(df, database_name, table_name):
    # Código para agregar DataFrame a SQLite
    pass

def get_country_city(lat, long):
    # Código para obtener país y ciudad a partir de coordenadas
    pass

def utm_to_latlong(easting, northing, zone_number, zone_letter):
    # Código para convertir UTM a lat/long
    pass

def insertar_data(data:list):
    pass

def combo_event2(value):
    # Código para manejar el evento del combobox
    pass

def combo_event(value):
    pass

def center_window(window, width, height):
    root.update_idletasks()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    root_x = root.winfo_x()
    root_y = root.winfo_y()

    x = root_x + (root_width // 2) - (width // 2)
    y = root_y + (root_height // 2) - (height // 2)

    window.geometry(f"{width}x{height}+{x}+{y}")

def setup_toplevel(window):
    window.geometry("400x300")
    window.title("Modificar datos")
    center_window(window, 400, 300)
    window.lift()
    window.focus_force()
    window.grab_set()

    label = ctk.CTkLabel(window, text="ToplevelWindow")
    label.pack(padx=20, pady=20)

def calcular_distancia(RUT1, RUT2):
    pass

def guardar_data(row_selector):
    print(row_selector.get())
    print(row_selector.table.values)

def mostrar_ventana_modificacion(row_selector, datos_globales):
    selected_rows = list(row_selector.selected_rows)
    print(f"Selected rows: {selected_rows}")
    print(f"Type of selected_rows: {type(selected_rows)}")

    if selected_rows:
        try:
            row_index = int(selected_rows[0]) - 1
        except ValueError:
            print(f"Error: el valor '{selected_rows[0]}' no puede convertirse a entero")
            row_index = None
    else:
        row_index = None

    print(f"Row index: {row_index}")

    if row_index is not None:
        ventana_modificacion = tkinter.Toplevel(root)
        ventana_modificacion.geometry("400x300")
        ventana_modificacion.title("Modificar Dato")

        datos = datos_globales[row_index]
        for idx, dato in enumerate(datos):
            etiqueta = tkinter.Label(ventana_modificacion, text=f"Dato {idx+1}: {dato}")
            etiqueta.pack()

def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
    if archivo:
        print(f"Archivo seleccionado: {archivo}")
        mostrar_datos(archivo)

def on_scrollbar_move(*args):
    canvas.yview(*args)
    canvas.bbox("all")

def leer_archivo_csv(ruta_archivo):
    try:
        datos = pd.read_csv(ruta_archivo)
        mostrar_datos(datos)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")

def mostrar_datos(datos):
    boton_imprimir = ctk.CTkButton(
        master=home_frame, text="guardar informacion", command=lambda: guardar_data())
    boton_imprimir.grid(row=2, column=0, pady=(0, 20))
    
    boton_modificar = ctk.CTkButton(
        master=data_panel_superior, text="modificar dato", command=lambda: mostrar_ventana_modificacion(row_selector, datos_globales))
    boton_modificar.grid(row=0, column=2, pady=(0, 0))

    boton_eliminar = ctk.CTkButton(
        master=data_panel_superior, text="Eliminar dato", command=lambda: editar_panel(root), fg_color='purple', hover_color='red')
    boton_eliminar.grid(row=0, column=3, padx=(10, 0))

def select_frame_by_name(name):
    home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
    frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
    frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

    if name == "home":
        home_frame.grid(row=0, column=1, sticky="nsew")
    else:
        home_frame.grid_forget()
    if name == "frame_2":
        second_frame.grid(row=0, column=1, sticky="nsew")
    else:
        second_frame.grid_forget()
    if name == "frame_3":
        third_frame.grid(row=0, column=1, sticky="nsew")
    else:
        third_frame.grid_forget()

def home_button_event():
    select_frame_by_name("home")

def frame_2_button_event():
    select_frame_by_name("frame_2")

def frame_3_button_event():
    select_frame_by_name("frame_3")

def change_appearance_mode_event(new_appearance_mode):
    ctk.set_appearance_mode(new_appearance_mode)

def mapas(panel):
    map_widget = tkintermapview.TkinterMapView(panel, width=800, height=500, corner_radius=0)
    map_widget.pack(fill=ctk.BOTH, expand=True)
    return map_widget

# Crear la ventana principal
root = ctk.CTk()
root.title("Proyecto Final progra I 2024")
root.geometry("950x450")

# Configurar el diseño de la ventana principal
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Establecer la carpeta donde están las imágenes
image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "iconos")
logo_image = ctk.CTkImage(Image.open(os.path.join(image_path, "uct.png")), size=(140, 50))
home_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "db.png")),
                          dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
chat_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                          dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
add_user_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                              dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

# Crear el marco de navegación
navigation_frame = ctk.CTkFrame(root, corner_radius=0)
navigation_frame.grid(row=0, column=0, sticky="nsew")
navigation_frame.grid_rowconfigure(4, weight=1)

navigation_frame_label = ctk.CTkLabel(navigation_frame, text="", image=logo_image,
                                      compound="left", font=ctk.CTkFont(size=15, weight="bold"))
navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

home_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                            image=home_image, anchor="w", command=home_button_event)
home_button.grid(row=1, column=0, sticky="ew")

frame_2_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 2",
                               fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                               image=chat_image, anchor="w", command=frame_2_button_event)
frame_2_button.grid(row=2, column=0, sticky="ew")

frame_3_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 3",
                               fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                               image=add_user_image, anchor="w", command=frame_3_button_event)
frame_3_button.grid(row=3, column=0, sticky="ew")

appearance_mode_menu = ctk.CTkOptionMenu(navigation_frame, values=["Light", "Dark", "System"],
                                         command=change_appearance_mode_event)
appearance_mode_menu.grid(row=5, column=0, padx=20, pady=20, sticky="s")

# Crear los marcos de contenido
home_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
home_frame.grid_columnconfigure(0, weight=1)

second_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
second_frame.grid_columnconfigure(0, weight=1)

third_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
third_frame.grid_columnconfigure(0, weight=1)

# Mostrar la vista inicial
select_frame_by_name("home")

# Crear el marco de datos
data_panel_superior = ctk.CTkFrame(home_frame, corner_radius=10)
data_panel_superior.grid(row=0, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew")

data_panel_inferior = ctk.CTkFrame(home_frame, corner_radius=10)
data_panel_inferior.grid(row=1, column=0, padx=(20, 20), pady=(0, 20), sticky="nsew")

boton_cargar_archivo = ctk.CTkButton(data_panel_superior, text="Cargar archivo", command=seleccionar_archivo)
boton_cargar_archivo.grid(row=0, column=0, pady=(0, 0))

boton_procesar = ctk.CTkButton(data_panel_superior, text="Procesar datos", command=lambda: leer_archivo_csv(archivo))
boton_procesar.grid(row=0, column=1, pady=(0, 0))

# Ejecutar el bucle principal
root.mainloop()
