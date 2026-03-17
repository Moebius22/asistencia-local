import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
import time

# 1. Configuración de la página
st.set_page_config(page_title="Asistencia Pehuajó", page_icon="📍", layout="wide")

st.title("📍 Registro de Asistencia - Pehuajó")

# --- LISTA DE PERSONAS ---
asistentes_frecuentes = [
    "Cervigno, Amalia", "Cervigno, Rocio", "Corbalan, Roma", "Corbalan, Ana Laura", 
    "Villar, Clara", "Galeano, Lorenzo", "Corbalan, Andrea", "Atun, Matias", 
    "Atun, Adela", "Corbalan, Carlos", "Corbalan, Jorge", "Mendieta, Gladis", 
    "Corbalan, Mariano", "Corbalan, Miriam", "Corbalan, Sandra", "Cervigno, Ernesto", 
    "Cervigno, Rosana", "Guaimas, Ana", "Galiani, Agustin", "Gazotti, Luciana", 
    "Paulina", "Pablo", "Gazotti, Victor", "Galvan, Norma", "Gazotti, Thiago", 
    "Jorgelina", "Griego, Soledad", "Guzzo, Francisco", "Tobio, Carla", 
    "Guzzo, Luca", "Guzzo, Sara", "Guzzo, Antonia", "Nanton, Patricia", 
    "Gazotti, Magali", "Martinez, Gladis", "Peñaloza, Nicolas", "Peralta, Marta", 
    "Peralta, Federico", "Pugnaloni, Dolores", "Rodriguez, Jorge", "Corbalan, Ruth", 
    "Rodriguez, Martin", "Cornero, Natalia", "Rodriguez, Franco", "Sangregorio, Nestor", 
    "Rodriguez, Barbara", "Sangregorio, Regina", "Sangregorio, Bautista", 
    "Sangregorio, Simon", "Corbalan, Cosby", "Villalba, Dario", "Maria, Jose", 
    "Villalba, Santiago", "Villalba, Tomas"
]

# 2. Conexión y Limpieza
try:
    url_hoja = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_actual = conn.read(spreadsheet=url_hoja, ttl=10)
    df_actual = df_actual.loc[:, ~df_actual.columns.str.contains('^Unnamed')].dropna(how='all')
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

fecha_hoy = date.today().strftime("%d/%m/%Y")
ya_registrados = []
if not df_actual.empty:
    df_actual["Fecha"] = df_actual["Fecha"].astype(str)
    ya_registrados = df_actual[df_actual["Fecha"] == fecha_hoy]["Nombre y Apellido"].unique().tolist()

# --- SECCIÓN 1: REGISTRO ---
st.subheader("Seleccione para registrar ingreso:")
busqueda = st.text_input("🔍 Buscar nombre:", placeholder="Escriba aquí...")
lista_filtrada = sorted([n for n in asistentes_frecuentes if busqueda.lower() in n.lower()])

cols = st.columns(4)
for i, nombre_persona in enumerate(lista_filtrada):
    with cols[i % 4]:
        esta_registrado = nombre_persona in ya_registrados
        label = f"✅ {nombre_persona.split(',')[0]}" if esta_registrado else nombre_persona
        if st.button(label, key=f"btn_{i}_{nombre_persona}", use_container_width=True, disabled=esta_registrado):
            df_reciente = conn.read(spreadsheet=url_hoja, ttl=0)
            df_reciente = df_reciente.loc[:, ~df_reciente.columns.str.contains('^Unnamed')].dropna(how='all')
            nuevo_registro = pd.DataFrame({"Nombre y Apellido": [nombre_persona], "Fecha": [fecha_hoy]})
            df_final = pd.concat([df_reciente, nuevo_registro], ignore_index=True)
            conn.update(spreadsheet=url_hoja, data=df_final)
            st.rerun()

st.markdown("---")

# --- SECCIÓN 2: REPORTE HTML AMENO ---
st.subheader("📊 Reporte de Asistencia")

# Función para generar el HTML con estilo
def generar_html_lindo(df):
    estilo_css = """
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .titulo { color: #2E4053; text-align: center; margin-bottom: 20px; }
        table { border-collapse: collapse; width: 100%; margin-top: 10px; border: 1px solid #ddd; }
        th { background-color: #F2F4F4; color: #1B2631; padding: 12px; text-align: left; border-bottom: 2px solid #AED6F1; }
        td { padding: 10px; border-bottom: 1px solid #E5E8E8; color: #566573; }
        tr:nth-child(even) { background-color: #FBFCFC; }
        tr:hover { background-color: #EBF5FB; }
    </style>
    """
    html_tabla = df.to_html(index=False, classes='table')
    html_final = f"""
    <html>
    <head>{estilo_css}</head>
    <body>
        <h2 class="titulo">Asistencia Comunidad Pehuajó</h2>
        <p style="text-align: center;">Reporte generado el: {fecha_hoy}</p>
        {html_tabla}
    </body>
    </html>
    """
    return html_final

col_del, col_rep = st.columns(2)

with col_del:
    if st.button("🗑️ Eliminar último registro", type="primary", use_container_width=True):
        if not df_actual.empty:
            conn.update(spreadsheet=url_hoja, data=df_actual.iloc[:-1])
            st.rerun()

with col_rep:
    if not df_actual.empty:
        html_data = generar_html_lindo(df_actual)
        st.download_button(
            label="📄 Descargar Reporte Lindo (HTML)",
            data=html_data,
            file_name=f"Reporte_Pehuajo_{fecha_hoy}.html",
            mime="text/html",
            use_container_width=True
        )

# Vista previa rápida
if st.checkbox("Ver tabla rápida"):
    st.dataframe(df_actual.tail(10), use_container_width=True)
