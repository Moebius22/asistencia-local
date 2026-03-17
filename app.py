import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# 1. Configuración de la página
st.set_page_config(page_title="Asistencia Pehuajó", page_icon="📍")

st.title("📍 Registro de Asistencia - Pehuajó")

# --- LISTA DE PERSONAS (Editalos aquí) ---
asistentes_frecuentes = [
    "Cervigno, Amalia", "Cervigno, Rocio", "Corbalan, Roma", "Corbalan, Ana Laura", "Villar, Clara", "Galeano, Lorenzo", "Corbalan, Andrea", "Atun, Matias", "Atun, Adela", "Corbalan, Carlos", "Corbalan, Jorge", "Mendieta, Gladis", "Corbalan, Mariano", Corbalan, Miriam", "Corbalan, Sandra", "Cervigno, Ernesto", "Cervigno, Rosana", "Guaimas, Ana", "Galiani, Agustin", "Gazotti, Luciana", "Paulina", "Pablo", "Gazotti, Victor", "Galvan, Norma", "Gazotti, Thiago", "Gazotti, Victor", "Jorgelina", "Griego, Soledad", "Guzzo, Francisco", "Tobio, Carla", "Guzzo, Luca", "Guzzo, Sara", "Guzzo, Antonia", "Nanton, Patricia", "Gazotti, Magali", "Martinez, Gladis", "Peñaloza, Nicolas", "Peralta, Marta", "Peralta, Federico", "Pugnaloni, Dolores", "Rodriguez, Jorge", "Corbalan, Ruth", "Rodriguez, Martin", "Cornero, Natalia", "Rodriguez, Franco", "Sangregorio, Nestor", "Rodriguez, Barbara", "Sangregorio, Regina", "Sangregorio, Bautista", "Sangregorio, Simon", "Corbalan, Cosby", "Villalba, Dario", "Maria, Jose", "Villalba, Santiago", "Villalba, Tomas"
]

# 2. Conexión con Google Sheets
try:
    url_hoja = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Error: Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- SECCIÓN 1: REGISTRO CON BOTONES ---
st.subheader("Seleccione para registrar ingreso:")
cols = st.columns(3)

for i, nombre_persona in enumerate(asistentes_frecuentes):
    with cols[i % 3]:
        if st.button(nombre_persona, use_container_width=True):
            try:
                fecha_hoy = date.today().strftime("%d/%m/%Y")
                df_existente = conn.read(spreadsheet=url_hoja)
                nuevo_registro = pd.DataFrame({"Nombre y Apellido": [nombre_persona], "Fecha": [fecha_hoy]})
                df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
                conn.update(spreadsheet=url_hoja, data=df_final)
                st.success(f"✅ {nombre_persona} registrado")
                st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")

# --- SECCIÓN 2: REGISTRO MANUAL ---
with st.expander("➕ Registrar nombre manualmente"):
    nombre_manual = st.text_input("Escriba el nombre completo:")
    if st.button("Guardar Registro Manual"):
        if nombre_manual:
            fecha_hoy = date.today().strftime("%d/%m/%Y")
            df_existente = conn.read(spreadsheet=url_hoja)
            nuevo_registro = pd.DataFrame({"Nombre y Apellido": [nombre_manual], "Fecha": [fecha_hoy]})
            df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
            conn.update(spreadsheet=url_hoja, data=df_final)
            st.success(f"✅ {nombre_manual} registrado")
        else:
            st.warning("Escriba un nombre.")

st.markdown("---")

# --- SECCIÓN 3: REPORTES Y DESCARGAS ---
st.subheader("📊 Administración y Reportes")

try:
    # Leemos los datos una sola vez para esta sección
    df_reporte = conn.read(spreadsheet=url_hoja)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Botón para descargar el reporte en CSV
        csv = df_reporte.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte Completo (CSV)",
            data=csv,
            file_name=f"asistencia_pehuajo_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col2:
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            st.rerun()

    # Visualización previa
    if st.checkbox("Ver registros recientes"):
        st.dataframe(df_reporte.tail(15), use_container_width=True)

except Exception as e:
    st.info("Aún no hay datos suficientes para generar reportes.")
