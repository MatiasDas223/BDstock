import mysql.connector
import pandas as pd
import glob
import os
import datetime
from datetime import datetime

# Conexión a la base de datos
db = mysql.connector.connect(
    host="192.168.1.66",
    user="root",
    password="admin",
    database="Stock"
)

cursor = db.cursor(buffered=True)

query = "SELECT Fecha from Roturas"
df = pd.read_sql(query, db)
fecha_maxima = df['Fecha'].max()

ruta_base = r"\\layla\\Documentos\\STOCK\\"
ruta_carpetas_base = glob.glob(ruta_base + 'Sto*')
rutas_imagen = []

for ruta in ruta_carpetas_base:
    # Construye la ruta hacia la carpeta "10- ROTURAS"
    ruta_roturas = os.path.join(ruta, '10- ROTURAS')
    
    # Verifica si la carpeta "10- ROTURAS" existe
    if os.path.exists(ruta_roturas):
        # Construye la ruta hacia la carpeta "IMAGEN" dentro de "10- ROTURAS"
        ruta_imagen = os.path.join(ruta_roturas, 'IMAGEN')

        # Verifica si la carpeta "IMAGEN" existe
        if os.path.exists(ruta_imagen):
            rutas_imagen.append(ruta_imagen)

rutas_meses = []

for ruta_imagen in rutas_imagen:
    # Busca todas las subcarpetas dentro de la carpeta "IMAGEN"
    subcarpetas = glob.glob(os.path.join(ruta_imagen, '*/'))

    # Añade las rutas de las subcarpetas a la lista rutas_meses
    rutas_meses.extend(subcarpetas)

rutas_archivos_recientes = []

for ruta_mes in rutas_meses:
    # Lista todos los archivos en la subcarpeta
    archivos = glob.glob(os.path.join(ruta_mes, '*'))

    for archivo in archivos:
        # Obtiene la fecha de modificación del archivo
        fecha_modificacion_datetime = datetime.fromtimestamp(os.path.getmtime(archivo))
        fecha_modificacion = fecha_modificacion_datetime.date()

        # Compara la fecha de modificación con la fecha max
        if fecha_modificacion > fecha_maxima:
            rutas_archivos_recientes.append(archivo)

datos = []
for x in rutas_archivos_recientes:
    y = pd.read_excel(x)
    datos.append(y)

datos = pd.concat(datos)

datos = datos[['fecha', 'articulo', 'cantidad', 'costo', 'nombre']]

datos['fecha'] = datos['fecha'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y').date() if pd.notnull(x) else x)

datos['articulo'] = datos['articulo'].astype(str)

datos.dropna(inplace= True)

# Abre un archivo para registrar los errores
with open("errores_log.txt", "w") as error_log:

    for index, fila in datos.iterrows():
        try:
            # Preparar tu consulta SQL y los valores
            query = "INSERT INTO Roturas (Fecha, Codigo, Cantidad, Costo, Motivo) VALUES (%s, %s, %s, %s, %s)"
            values = (fila['fecha'], fila['articulo'], fila['cantidad'], fila['costo'], fila['nombre'])

            # Ejecutar la consulta
            cursor.execute(query, values)
            db.commit()

        except mysql.connector.IntegrityError as e:
            print(f"Error al insertar la fila {index}: {e}")
            
            # Escribir el error y el código problemático en el archivo de log
            error_log.write(f"Fila {index}, Código: {fila['articulo']}, Error: {e}\n")
            
            # Continuar con la siguiente fila
            continue