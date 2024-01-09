import streamlit as st
from datetime import date
import mysql.connector
from funciones import obtener_familias, obtener_informe, generar_informe_mensual,consultar_vencimientos, top10
import pandas as pd

# Opciones de navegación
paginas = ["Bajas", "Fechas vencimientos", "Stocks"]

# Selector de páginas en la barra lateral
pagina_seleccionada = st.sidebar.selectbox("Elige un reporte", paginas)

############################ Contenido basado en la selección ##############################################

if pagina_seleccionada == "Bajas":
    # Aquí va el código para el contenido de la Página 1
    logo_path = "C:\\Users\\mdasilva\\Desktop\\MySQL BD Stock\\Scripts Python\\Assets\\Hergo-LOGO-02.svg"

    st.image(logo_path, width=150)

    st.title("Consulta de bajas")

    nombres_familias = obtener_familias()

    # Selección de Familia
    familia = st.selectbox("Selecciona la Familia de Productos:", nombres_familias)

    # Selección de Rango de Fechas
    fecha_inicio = st.date_input("Fecha de Inicio", date.today(), format= "DD/MM/YYYY")
    fecha_fin = st.date_input("Fecha de Fin", date.today(), format= "DD/MM/YYYY")

    if st.button("Consultar"):
        resultados = obtener_informe(familia, fecha_inicio, fecha_fin)

        if resultados:
            # Inicializar los acumuladores de totales
            total_cantidad = 0
            total_costo = 0
            total_sku = 0

            # Crear una tabla para mostrar los resultados
            tabla_resultados = []

            for descr,motivo, cantidad, costo, sku in resultados:
                # Acumular los totales
                total_cantidad += cantidad
                total_costo += costo
                total_sku += sku

                # Añadir fila a la tabla de resultados
                tabla_resultados.append({
                    'Motivo': motivo,
                    'Bultos': cantidad,
                    'Nro. SKU' : sku,
                    'Costo': costo
                })

            # Añadir fila de totales
            tabla_resultados.append({
                'Motivo': 'Total',
                'Bultos': total_cantidad,
                'Nro. SKU' : total_sku,
                'Costo': total_costo
            })

            # Mostrar la tabla en Streamlit
            st.table(tabla_resultados)
        else:
            st.write("No se encontraron resultados.")

    ####################################### TOP 10 de roturas #################################################
   
    # Mostrar el TOP 10 en Streamlit
    st.title("TOP 10 de Roturas")
   

    # Obtener la ordenación seleccionada por el usuario
    ordenar_por = st.radio("Ordenar por:", ["Código","Familia", "Proveedor"])

    desde = st.date_input("Desde", date.today(), format= "DD/MM/YYYY")
    hasta = st.date_input("Hasta", date.today(), format= "DD/MM/YYYY")

    if st.button("Ver TOP"):
        df = top10(ordenar_por, desde, hasta)


        st.table(df)


    ####################################### Generar informe mensual #############################################

    st.title("Generación de Informe Mensual")

    fecha_seleccionada = st.date_input("Selecciona una fecha para generar el informe mensual", date.today(), format= "DD/MM/YYYY")

    # Botón para generar el informe

    if st.button("Generar informe mensual"):

        mes_seleccionado = fecha_seleccionada.month
        anio_seleccionado = fecha_seleccionada.year

        # Llamar a la función que genera el informe
        pdf_path = generar_informe_mensual(mes_seleccionado, anio_seleccionado)
       
        # Agrega un botón de descarga personalizado
        with open(pdf_path, "rb") as f:
            st.download_button(
                label='Descargar Informe',
                data=f.read(),
                key='informe_pdf',
                file_name='Informe bajas por Rotura.pdf',
                mime='application/pdf'
            )
    
##############################################################################################################
######################################## VENCIMIENTOS #########################################################
##############################################################################################################
            
elif pagina_seleccionada == "Fechas vencimientos":

     # Crear la aplicación Streamlit
    st.title('Información de Vencimiento de Productos')
    
    df=consultar_vencimientos()

    # Crear una función para aplicar el formato condicional a la columna "dias_restantes"
    def color_dias_restantes(val):
        if val < 15:
            color = 'red'
        elif 15 <= val <= 60:
            color = 'goldenrod'
        else:
            color = 'green'
        return f'color: {color}'

    ubicaciones = ['TODOS'] + list(df['ubicacion'].unique())

    filtro_ubicacion = st.selectbox('Selecciona una ubicación:', ubicaciones)

    if filtro_ubicacion == "TODOS":
        df_filtrado = df
    else:
        df_filtrado = df[df['ubicacion'] == filtro_ubicacion]

    # Aplicar formato condicional a la columna "dias_restantes"
    styled_df = df_filtrado.style.applymap(color_dias_restantes, subset=['dias_restantes'])

    # Mostrar la tabla con formato condicional
    st.dataframe(styled_df)

elif pagina_seleccionada == "Página 3":
    st.write("Contenido de la Página 3")
    # Aquí va el código para el contenido de la Página 3


