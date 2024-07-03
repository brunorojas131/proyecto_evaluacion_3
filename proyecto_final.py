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

global row_selector
row_selector = None
def haversine(lat1, lon1, lat2, lon2):
    # Función para calcular la distancia entre 2 puntos a partir de la longitud y latitud
    R = 6371.0  # Radio de la Tierra en kilómetros
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distancia = R * c
    return distancia
def ejecutar_query_sqlite(database_name, query, params=None):
    """
    Ejecuta una consulta SQL en una base de datos SQLite.

    Parámetros:
    database_name (str): Nombre del archivo de la base de datos SQLite.
    query (str): Consulta SQL a ejecutar.
    params (tuple): Parámetros para la consulta (opcional).

    Retorna:
    list: Lista con los resultados de la consulta si es un SELECT.
    int: Número de filas afectadas si es un INSERT, UPDATE o DELETE.
    """
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
        else:
            result = cursor.rowcount
            conn.commit()

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        result = None

    finally:
        cursor.close()
        conn.close()

    return result

def agregar_df_a_sqlite(df, database_name, table_name):
    conn = sqlite3.connect(database_name)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

#documentacion=https://github.com/TomSchimansky/TkinterMapView?tab=readme-ov-file#create-path-from-position-list

# Definir la función para convertir UTM a latitud y longitud
def utm_to_latlon(easting, northing, zone):
    utm_proj = pyproj.Proj(proj='utm', zone=zone, ellps='WGS84')
    wgs84_proj = pyproj.Proj(proj='latlong', ellps='WGS84')
    lon, lat = pyproj.transform(utm_proj, wgs84_proj, easting, northing)
    return lat, lon

def combo_event(value):
    if value != "Opción 1":
        global marker_1
        try:
            marker_1.delete()
        except NameError:
            pass
        result = ejecutar_query_sqlite('progra2024_final.db', 'SELECT Latitude, Longitude, Nombre, Apellido FROM coordenadas JOIN personas ON coordenadas.RUT = personas.RUT WHERE personas.RUT = ?', (value,))
        if result:
            nombre_apellido = f"{result[0][2]} {result[0][3]}"
            marker_1 = map_widget.set_marker(result[0][0], result[0][1], text=nombre_apellido)

def combo_event2(value):
    if value != "Opción 2":
        global marker_2
        try:
            marker_2.delete()
        except NameError:
            pass
        result = ejecutar_query_sqlite('progra2024_final.db', 'SELECT Latitude, Longitude, Nombre, Apellido FROM coordenadas JOIN personas ON coordenadas.RUT = personas.RUT WHERE personas.RUT = ?', (value,))
        if result:
            nombre_apellido = f"{result[0][2]} {result[0][3]}"
            marker_2 = map_widget.set_marker(result[0][0], result[0][1], text=nombre_apellido)

def calcular_distancia():
    if optionmenu_1.get() == "Opción 1" or optionmenu_2.get() == "Opción 2":
        CTkMessagebox(title="Error", message="Por favor, seleccione dos RUTs diferentes.")
        return

    global marker_1, marker_2, path_1
    try:
        lat1, lon1 = marker_1.position
        lat2, lon2 = marker_2.position
        distancia = haversine(lat1, lon1, lat2, lon2)
        label_distancia.configure(text=f"Distancia: {distancia:.2f} km")
        
        try:
            path_1.delete()
        except NameError:
            pass
        
        path_1 = map_widget.set_path([marker_1.position, marker_2.position])
    except NameError:
        CTkMessagebox(title="Error", message="Por favor, seleccione dos RUTs diferentes.")

def guardar_data():
    global datos_globales
    if datos_globales is not None:
        try:
            datos_globales['Latitude'] = None
            datos_globales['Longitude'] = None
            for index, row in datos_globales.iterrows():
                lat, lon = utm_to_latlon(row['Easting'], row['Northing'], row['UTM_Zone'])
                datos_globales.at[index, 'Latitude'] = lat
                datos_globales.at[index, 'Longitude'] = lon

            mostrar_datos(datos_globales)

            tablas = [
                '''CREATE TABLE IF NOT EXISTS personas (
                    RUT TEXT PRIMARY KEY,
                    Nombre TEXT,
                    Apellido TEXT
                )''',
                '''CREATE TABLE IF NOT EXISTS profesiones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE
                )''',
                '''CREATE TABLE IF NOT EXISTS estados_emocionales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE
                )''',
                '''CREATE TABLE IF NOT EXISTS paises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE
                )''',
                '''CREATE TABLE IF NOT EXISTS coordenadas (
                    RUT TEXT PRIMARY KEY,
                    Easting REAL,
                    Northing REAL,
                    UTM_Zone INTEGER,
                    Latitude REAL,
                    Longitude REAL,
                    FOREIGN KEY (RUT) REFERENCES personas (RUT)
                )''',
                '''CREATE TABLE IF NOT EXISTS persona_profesion (
                    RUT TEXT,
                    profesion_id INTEGER,
                    FOREIGN KEY (RUT) REFERENCES personas (RUT),
                    FOREIGN KEY (profesion_id) REFERENCES profesiones (id),
                    PRIMARY KEY (RUT, profesion_id)
                )''',
                '''CREATE TABLE IF NOT EXISTS persona_estado_emocional (
                    RUT TEXT,
                    estado_emocional_id INTEGER,
                    FOREIGN KEY (RUT) REFERENCES personas (RUT),
                    FOREIGN KEY (estado_emocional_id) REFERENCES estados_emocionales (id),
                    PRIMARY KEY (RUT, estado_emocional_id)
                )''',
                '''CREATE TABLE IF NOT EXISTS persona_pais (
                    RUT TEXT,
                    pais_id INTEGER,
                    FOREIGN KEY (RUT) REFERENCES personas (RUT),
                    FOREIGN KEY (pais_id) REFERENCES paises (id),
                    PRIMARY KEY (RUT, pais_id)
                )'''
            ]

            for tabla in tablas:
                ejecutar_query_sqlite('progra2024_final.db', tabla)

            for _, row in datos_globales.iterrows():
                ejecutar_query_sqlite('progra2024_final.db', 
                    'INSERT OR REPLACE INTO personas (RUT, Nombre, Apellido) VALUES (?, ?, ?)',
                    (row['RUT'], row['Nombre'], row['Apellido']))

                ejecutar_query_sqlite('progra2024_final.db',
                    'INSERT OR IGNORE INTO profesiones (nombre) VALUES (?)',
                    (row['Profesion'],))
                profesion_id = ejecutar_query_sqlite('progra2024_final.db',
                    'SELECT id FROM profesiones WHERE nombre = ?',
                    (row['Profesion'],))[0][0]

                ejecutar_query_sqlite('progra2024_final.db',
                    'INSERT OR IGNORE INTO estados_emocionales (nombre) VALUES (?)',
                    (row['Estado_Emocional'],))
                estado_emocional_id = ejecutar_query_sqlite('progra2024_final.db',
                    'SELECT id FROM estados_emocionales WHERE nombre = ?',
                    (row['Estado_Emocional'],))[0][0]

                ejecutar_query_sqlite('progra2024_final.db',
                    'INSERT OR IGNORE INTO paises (nombre) VALUES (?)',
                    (row['Pais'],))
                pais_id = ejecutar_query_sqlite('progra2024_final.db',
                    'SELECT id FROM paises WHERE nombre = ?',
                    (row['Pais'],))[0][0]

                ejecutar_query_sqlite('progra2024_final.db',
                    '''INSERT OR REPLACE INTO coordenadas 
                    (RUT, Easting, Northing, UTM_Zone, Latitude, Longitude)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (row['RUT'], row['Easting'], row['Northing'], row['UTM_Zone'], 
                     row['Latitude'], row['Longitude']))

                ejecutar_query_sqlite('progra2024_final.db',
                    'INSERT OR REPLACE INTO persona_profesion (RUT, profesion_id) VALUES (?, ?)',
                    (row['RUT'], profesion_id))
                ejecutar_query_sqlite('progra2024_final.db',
                    'INSERT OR REPLACE INTO persona_estado_emocional (RUT, estado_emocional_id) VALUES (?, ?)',
                    (row['RUT'], estado_emocional_id))
                ejecutar_query_sqlite('progra2024_final.db',
                    'INSERT OR REPLACE INTO persona_pais (RUT, pais_id) VALUES (?, ?)',
                    (row['RUT'], pais_id))

            CTkMessagebox(title="Éxito", message="Datos guardados correctamente en la base de datos.")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al guardar los datos: {str(e)}")
    else:
        CTkMessagebox(title="Aviso", message="No hay datos para guardar. Por favor, cargue un archivo CSV primero.")

def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
    if archivo:
        try:
            datos = pd.read_csv(archivo)
            
            columnas_mapping = {
                'UTM_Easting': 'Easting',
                'UTM_Northing': 'Northing',
                'UTM_Zone_Number': 'UTM_Zone',
                'RUT': 'RUT',
                'Nombre': 'Nombre',
                'Apellido': 'Apellido',
                'Profesion': 'Profesion',
                'Estado_Emocional': 'Estado_Emocional',
                'Pais': 'Pais',
                'UTM_Zone_Letter': 'UTM_Zone_Letter'
            }
            datos = datos.rename(columns=columnas_mapping)
            
            mostrar_datos(datos)
            
            global datos_globales
            datos_globales = datos
            
            boton_modificar.configure(state="normal")
            boton_eliminar.configure(state="normal")
            boton_guardar.configure(state="normal")
            
            CTkMessagebox(title="Éxito", message="Archivo cargado correctamente.")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al procesar el archivo: {str(e)}")

def leer_archivo_csv(ruta_archivo):
    try:
        datos = pd.read_csv(ruta_archivo)
        mostrar_datos(datos)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")

def mostrar_datos(datos):
    global row_selector
    if not isinstance(datos, pd.DataFrame):
        CTkMessagebox(title="Error", message="Los datos no están en el formato correcto.")
        return
    
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    table = CTkTable(master=scrollable_frame, 
                     values=[datos.columns.tolist()] + datos.values.tolist(),
                     header_color="gray70",
                     hover_color="gray90")
    table.pack(expand=True, fill="both", padx=10, pady=10)

    row_selector = CTkTableRowSelector(table)

def eliminar_dato(datos):
    global row_selector, datos_globales
    indices_to_delete = [int(i) for i in row_selector.selected_rows]
    if indices_to_delete:
        
        indices_to_delete = [i-1 for i in indices_to_delete]
        
        datos.drop(datos.index[indices_to_delete], inplace=True)
        
        datos.reset_index(drop=True, inplace=True)
        
        mostrar_datos(datos)
        
        datos_globales = datos
        
        CTkMessagebox(title="Éxito", message=f"Se han eliminado {len(indices_to_delete)} filas.")
    else:
        CTkMessagebox(title="Aviso", message="No se han seleccionado filas para eliminar.")

def modificar_dato(datos):
    global row_selector
    selected_rows = list(row_selector.selected_rows)
    
    if selected_rows:
        try:
            row_index = int(selected_rows[0]) - 1
        except ValueError:
            print(f"Error: el valor '{selected_rows[0]}' no puede convertirse a entero")
            return
        
        if len(selected_rows) > 1:
            CTkMessagebox(title="Aviso", message="Por favor, seleccione solo una fila para modificar.")
            return
        
        row_data = datos.iloc[row_index]

        edit_window = ctk.CTkToplevel()
        edit_window.title("Modificar Dato")
        edit_window.geometry("400x300")

        entries = {}
        for i, (column, value) in enumerate(row_data.items()):
            ctk.CTkLabel(edit_window, text=column).grid(row=i, column=0, padx=5, pady=5)
            entry = ctk.CTkEntry(edit_window)
            entry.insert(0, str(value))
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[column] = entry

        def save_changes():
            for column, entry in entries.items():
                datos.at[row_index, column] = entry.get()
            edit_window.destroy()
            mostrar_datos(datos)  
            global datos_globales
            datos_globales = datos  
            CTkMessagebox(title="Éxito", message="Dato modificado correctamente")

        ctk.CTkButton(edit_window, text="Guardar Cambios", command=save_changes).grid(row=len(entries), column=0, columnspan=2, pady=10)
    else:
        CTkMessagebox(title="Aviso", message="No se ha seleccionado ninguna fila para modificar.")

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

def actualizar_graficos():
    conn = sqlite3.connect('progra2024_final.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT p.nombre, COUNT(*) as cantidad
        FROM profesiones p
        JOIN persona_profesion pp ON p.id = pp.profesion_id
        GROUP BY p.nombre
        ORDER BY cantidad DESC
        LIMIT 5
    ''')
    datos_profesiones = cursor.fetchall()
    profesiones = [row[0] for row in datos_profesiones]
    cantidades = [row[1] for row in datos_profesiones]

    ax1.clear()
    ax1.bar(profesiones, cantidades)
    ax1.set_xlabel("Profesiones")
    ax1.set_ylabel("Número de profesionales")
    ax1.set_title("Profesiones vs paises")
    ax1.tick_params(axis='x', rotation=45)
    fig1.tight_layout()
    canvas1.draw()

    cursor.execute('''
        SELECT e.nombre, COUNT(*) as cantidad
        FROM estados_emocionales e
        JOIN persona_estado_emocional pe ON e.id = pe.estado_emocional_id
        GROUP BY e.nombre
    ''')
    datos_emocionales = cursor.fetchall()
    estados = [row[0] for row in datos_emocionales]
    cantidades = [row[1] for row in datos_emocionales]

    ax2.clear()
    ax2.pie(cantidades, labels=estados, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    ax2.set_title("Estado emocional vs profesion")
    fig2.tight_layout()
    canvas2.draw()

    cursor.execute('SELECT DISTINCT nombre FROM paises')
    paises = [row[0] for row in cursor.fetchall()]
    combobox_left.configure(values=paises)

    cursor.execute('SELECT DISTINCT nombre FROM estados_emocionales')
    estados_emocionales = [row[0] for row in cursor.fetchall()]
    combobox_right.configure(values=estados_emocionales)

    conn.close()

    combobox_left.configure(command=actualizar_grafico_profesiones_por_pais)
    combobox_right.configure(command=actualizar_grafico_emociones_por_profesion)

def actualizar_grafico_profesiones_por_pais(pais_seleccionado):
    conn = sqlite3.connect('progra2024_final.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT p.nombre, COUNT(*) as cantidad
        FROM profesiones p
        JOIN persona_profesion pp ON p.id = pp.profesion_id
        JOIN persona_pais pais ON pp.RUT = pais.RUT
        JOIN paises pa ON pais.pais_id = pa.id
        WHERE pa.nombre = ?
        GROUP BY p.nombre
        ORDER BY cantidad DESC
        LIMIT 5
    ''', (pais_seleccionado,))
    datos = cursor.fetchall()
    
    profesiones = [row[0] for row in datos]
    cantidades = [row[1] for row in datos]

    ax1.clear()
    ax1.bar(profesiones, cantidades)
    ax1.set_xlabel("Profesiones")
    ax1.set_ylabel("Número de profesionales")
    ax1.set_title(f"Profesiones en {pais_seleccionado}")
    ax1.tick_params(axis='x', rotation=45)
    fig1.tight_layout()
    canvas1.draw()

    conn.close()

def actualizar_grafico_emociones_por_profesion(estado_emocional_seleccionado):
    conn = sqlite3.connect('progra2024_final.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT p.nombre, COUNT(*) as cantidad
        FROM profesiones p
        JOIN persona_profesion pp ON p.id = pp.profesion_id
        JOIN persona_estado_emocional pe ON pp.RUT = pe.RUT
        JOIN estados_emocionales e ON pe.estado_emocional_id = e.id
        WHERE e.nombre = ?
        GROUP BY p.nombre
        ORDER BY cantidad DESC
        LIMIT 5
    ''', (estado_emocional_seleccionado,))
    datos = cursor.fetchall()
    
    profesiones = [row[0] for row in datos]
    cantidades = [row[1] for row in datos]

    ax2.clear()
    ax2.pie(cantidades, labels=profesiones, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    ax2.set_title(f"Distribución de Profesiones para {estado_emocional_seleccionado}")
    fig2.tight_layout()
    canvas2.draw()

    conn.close()

def actualizar_mapa():
    global map_widget
    map_widget.set_position(-33.4569, -70.6483) 
    map_widget.set_zoom(10)
    
    ruts = ejecutar_query_sqlite('progra2024_final.db', 'SELECT RUT FROM personas')
    ruts = [rut[0] for rut in ruts]
    
    optionmenu_1.configure(values=["Opción 1"] + ruts)
    optionmenu_2.configure(values=["Opción 2"] + ruts)
    
    optionmenu_1.set("Opción 1")
    optionmenu_2.set("Opción 2")

def home_button_event():
    select_frame_by_name("home")

def frame_2_button_event():
    select_frame_by_name("frame_2")
    actualizar_graficos()

def frame_3_button_event():
    select_frame_by_name("frame_3")
    actualizar_mapa()

def change_appearance_mode_event(new_appearance_mode):
    ctk.set_appearance_mode(new_appearance_mode)
def mapas(panel):
   
    map_widget = tkintermapview.TkinterMapView(panel,width=800, height=500, corner_radius=0)

    map_widget.pack(fill=ctk.BOTH, expand=True)
    return map_widget

root = ctk.CTk()
root.title("Proyecto Final progra I 2024")
root.geometry("950x450")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "iconos")
logo_image = ctk.CTkImage(Image.open(os.path.join(image_path, "uct.png")), size=(140, 50))
home_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "db.png")),
                          dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
chat_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                          dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
add_user_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                              dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

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

frame_2_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Gráficos",
                               fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                               image=chat_image, anchor="w", command=frame_2_button_event)
frame_2_button.grid(row=2, column=0, sticky="ew")

frame_3_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Mapa",
                               fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                               image=add_user_image, anchor="w", command=frame_3_button_event)
frame_3_button.grid(row=3, column=0, sticky="ew")

home_frame = ctk.CTkFrame(root, fg_color="transparent")
home_frame.grid_rowconfigure(1, weight=1)
home_frame.grid_columnconfigure(0, weight=1)

data_panel_superior = ctk.CTkFrame(home_frame, corner_radius=0,)
data_panel_superior.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

data_panel_inferior = ctk.CTkFrame(home_frame, corner_radius=0)
data_panel_inferior.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
data_panel_inferior.grid_rowconfigure(0, weight=1)
data_panel_inferior.grid_columnconfigure(0, weight=1)

home_frame_large_image_label = ctk.CTkLabel(data_panel_superior, text="Ingresa el archivo en formato .csv",font=ctk.CTkFont(size=15, weight="bold"))
home_frame_large_image_label.grid(row=0, column=0, padx=15, pady=15)
home_frame_cargar_datos = ctk.CTkButton(
    data_panel_superior, 
    text="Cargar Archivo", 
    command=seleccionar_archivo,  
    fg_color='green', 
    hover_color='gray'
)
home_frame_cargar_datos.grid(row=0, column=1, padx=15, pady=15)

scrollable_frame = ctk.CTkScrollableFrame(master=data_panel_inferior)
scrollable_frame.grid(row=0, column=0,sticky="nsew")

boton_guardar = ctk.CTkButton(data_panel_superior, text="Guardar información", command=guardar_data)
boton_guardar.grid(row=0, column=2, pady=(0, 0), padx=(10, 0))

boton_modificar = ctk.CTkButton(data_panel_superior, text="Modificar dato", command=lambda: modificar_dato(datos_globales))
boton_modificar.grid(row=0, column=3, pady=(0, 0), padx=(10, 0))

boton_eliminar = ctk.CTkButton(data_panel_superior, text="Eliminar dato", command=lambda: eliminar_dato(datos_globales), fg_color='purple', hover_color='red')
boton_eliminar.grid(row=0, column=4, padx=(10, 0))

second_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
second_frame.grid_rowconfigure(1, weight=1)
second_frame.grid_columnconfigure(1, weight=1)

top_frame = ctk.CTkFrame(second_frame)
top_frame.pack(side=ctk.TOP, fill=ctk.X)

bottom_frame = ctk.CTkFrame(second_frame)
bottom_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

left_panel = ctk.CTkFrame(bottom_frame)
left_panel.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

right_panel = ctk.CTkFrame(bottom_frame)
right_panel.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

top_left_panel = ctk.CTkFrame(top_frame)
top_left_panel.pack(side=ctk.LEFT, fill=ctk.X, expand=True)

top_right_panel = ctk.CTkFrame(top_frame)
top_right_panel.pack(side=ctk.RIGHT, fill=ctk.X, expand=True)

label_pais = ctk.CTkLabel(top_left_panel, text="Seleccione país", font=ctk.CTkFont(size=15, weight="bold"))
label_pais.pack(pady=(10, 0), padx=20)

label_estado_emocional = ctk.CTkLabel(top_right_panel, text="Seleccione Estado Emocional", font=ctk.CTkFont(size=15, weight="bold"))
label_estado_emocional.pack(pady=(10, 0), padx=20)

combobox_left = ctk.CTkComboBox(top_left_panel, values=["Opción 1", "Opción 2", "Opción 3"])
combobox_left.pack(pady=20, padx=20)

combobox_right = ctk.CTkComboBox(top_right_panel, values=["Opción 1", "Opción 2", "Opción 3"])
combobox_right.pack(pady=20, padx=20)

fig1, ax1 = plt.subplots()
profesiones = ["Profesion A", "Profesion B", "Profesion C", "Profesion D", "Profesion E"]
paises = ["País 1", "País 2", "País 3", "País 4", "País 5"]
x = np.arange(len(profesiones))
y = np.random.rand(len(profesiones))
ax1.bar(x, y)
ax1.set_xticks(x)
ax1.set_xticklabels(profesiones)
ax1.set_xlabel("Profesiones")
ax1.set_ylabel("Numero de profesionales")
ax1.set_title("Profesiones vs Paises")

canvas1 = FigureCanvasTkAgg(fig1, master=left_panel)
canvas1.draw()
canvas1.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

fig2, ax2 = plt.subplots()
labels = 'A', 'B', 'C', 'D'
sizes = [15, 30, 45, 10]
colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
explode = (0.1, 0, 0, 0) 

ax2.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
ax2.axis('equal')  
ax2.set_title("Estado emocional vs profesion")

canvas2 = FigureCanvasTkAgg(fig2, master=right_panel)
canvas2.draw()
canvas2.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

third_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
third_frame.grid_rowconfigure(0, weight=1)
third_frame.grid_columnconfigure(0, weight=1)
third_frame.grid_rowconfigure(1, weight=3)  

third_frame_top =  ctk.CTkFrame(third_frame, fg_color="gray")
third_frame_top.grid(row=0, column=0,  sticky="nsew", padx=5, pady=5)

third_frame_inf =  ctk.CTkFrame(third_frame, fg_color="lightgreen")
third_frame_inf.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
map_widget=mapas(third_frame_inf)

label_rut1 = ctk.CTkLabel(third_frame_top, text="RUT 1", font=ctk.CTkFont(size=15, weight="bold"))
label_rut1.grid(row=0, column=0, padx=5, pady=5)
optionmenu_1 = ctk.CTkOptionMenu(third_frame_top, dynamic_resizing=True, values=[], command=lambda value: combo_event(value))
optionmenu_1.grid(row=0, column=1, padx=5, pady=(5, 5))
optionmenu_1.set("Opción 1")  

label_rut2 = ctk.CTkLabel(third_frame_top, text="RUT 2", font=ctk.CTkFont(size=15, weight="bold"))
label_rut2.grid(row=1, column=0, padx=5, pady=5)
optionmenu_2 = ctk.CTkOptionMenu(third_frame_top, dynamic_resizing=True, values=[], command=lambda value: combo_event2(value))
optionmenu_2.grid(row=1, column=1, padx=5, pady=(5, 5))
optionmenu_2.set("Opción 2")  

boton_calcular_distancia = ctk.CTkButton(third_frame_top, text="Calcular distancia", command=calcular_distancia)
boton_calcular_distancia.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

label_distancia = ctk.CTkLabel(third_frame_top, text="", font=ctk.CTkFont(size=15, weight="bold"))
label_distancia.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

select_frame_by_name("home")
toplevel_window = None
root.protocol("WM_DELETE_WINDOW", root.quit)
root.mainloop()