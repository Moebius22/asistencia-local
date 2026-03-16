Para que tu aplicación de asistencia en Pehuajó funcione sin errores de "Variable no definida" o problemas de autenticación, he unificado todo el código.

Este bloque ya incluye las correcciones de la librería datetime, la definición de url_hoja y el manejo robusto de la private_key.

📄 Código Completo (app.py)
Python
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# 1. Configuración de la página
st.set_page_config(page_title="Asistencia Local Pehuajó", layout="centered")

st.title("📍 Sistema de Asistencia")
st.subheader("Registro de Ingreso")

# 2. Conexión con Google Sheets
# Extraemos la URL de los secretos para evitar el error 'url_hoja is not defined'
try:
    url_hoja = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Error al configurar la conexión. Revisa tus Secrets en Streamlit.")
    st.stop()

# 3. Interfaz de usuario
nombre_usuario = st.text_input("Nombre y Apellido del Asistente:")
boton_registrar = st.button("Registrar Asistencia")

# 4. Lógica de guardado
if boton_registrar:
    if nombre_usuario:
        try:
            # Obtener la fecha actual (Corrección del NameError: date)
            fecha_hoy = date.today().strftime("%d/%m/%Y")
            
            # Leer datos existentes para no borrar lo anterior
            df_existente = conn.read(spreadsheet=url_hoja)
            
            # Crear el nuevo registro
            nuevo_dato = pd.DataFrame({
                "Nombre y Apellido": [nombre_usuario],
                "Fecha": [fecha_hoy]
            })
            
            # Concatenar (unir) los datos viejos con el nuevo
            df_actualizado = pd.concat([df_existente, nuevo_dato], ignore_index=True)
            
            # Actualizar la hoja de cálculo
            conn.update(spreadsheet=url_hoja, data=df_actualizado)
            
            st.success(f"✅ ¡Hecho! {nombre_usuario} registrado el {fecha_hoy}")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    else:
        st.warning("Por favor, escribe un nombre antes de registrar.")

# 5. Visualización (Opcional: solo para administradores)
if st.checkbox("Mostrar registros recientes"):
    df_vista = conn.read(spreadsheet=url_hoja)
    st.dataframe(df_vista.tail(10)) # Muestra los últimos 10
