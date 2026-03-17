import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# Configuración de la interfaz
st.set_page_config(page_title="Asistencia Local Pehuajó", page_icon="📍")

st.title("📍 Registro de Asistencia - Pehuajó")
st.write("Ingrese el nombre para registrar la entrada en la base de datos.")

# Conexión principal usando los Secrets
try:
    # Definimos url_hoja directamente desde los secretos para evitar el NameError
    url_hoja = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Error de configuración: Verifica que los Secrets estén bien cargados.")
    st.stop()

# Formulario de entrada
with st.form(key="asistencia_form"):
    nombre = st.text_input("Nombre y Ayellido del Asistente")
    submit_button = st.form_submit_button(label="Registrar")

if submit_button:
    if nombre:
        try:
            # Obtener fecha actual
            fecha_hoy = date.today().strftime("%d/%m/%Y")
            
            # 1. Leer datos actuales
            df_existente = conn.read(spreadsheet=url_hoja)
            
            # 2. Crear nueva fila
            nuevo_registro = pd.DataFrame({
                "Nombre y Apellido": [nombre],
                "Fecha": [fecha_hoy]
            })
            
            # 3. Unir datos
            df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
            
            # 4. Guardar en Google Sheets
            conn.update(spreadsheet=url_hoja, data=df_final)
            
            st.success(f"✅ Registro guardado: {nombre} - {fecha_hoy}")
            st.balloons()
        except Exception as e:
            st.error(f"Hubo un error al guardar: {e}")
    else:
        st.warning("Por favor, ingresa un nombre.")

# Sección para ver la lista (opcional)
if st.checkbox("Ver lista de asistentes"):
    datos = conn.read(spreadsheet=url_hoja)
    st.dataframe(datos)
