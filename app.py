import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, datetime
import time
import os
import base64

# 1. Configuración de la página
st.set_page_config(page_title="INA Pehuajó", page_icon="⛪", layout="wide")

# --- FUNCIÓN PARA CARGAR IMAGEN EN BASE64 ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# --- MOSTRAR LOGO EN LA APP ---
if os.path.exists("logo.png"):
    col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
    with col_l2:
        st.image("logo.png", width=150)

st.markdown("<h1 style='text-align: center;'>📍 Registro de Asistencia</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Iglesia Nueva Apostólica - Comunidad Pehuajó</h3>", unsafe_allow_html=True)
st.markdown("---")

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
    "Villalba, Santiago", "Villalba, Tomas", "Bequi", "Candela", "Scalora", "France", "Ravlich", "Jankulick", "Gantus", "Sojak", "Legal Cristian"
]

# 2. Conexión y Manejo de Datos Vacíos
try:
    url_hoja = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_actual = conn.read(spreadsheet=url_hoja, ttl=5)
    
    # Si el DF está vacío o no tiene columnas, creamos uno base
    if df_actual is None or df_actual.empty:
        df_actual = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])
    else:
        # Limpieza normal
        df_actual = df_actual.loc[:, ~df_actual.columns.str.contains('^Unnamed')].dropna(how='all')
except Exception as e:
    st.error("Error de conexión. Revisa los permisos del Excel.")
    st.stop()

# --- SECCIÓN DE FECHA ---
col_fecha, _ = st.columns([1, 2])
with col_fecha:
    fecha_seleccionada = st.date_input("📅 Fecha de asistencia:", date.today())
    fecha_str = fecha_seleccionada.strftime("%d/%m/%Y")

# Inicializar variables de filtrado para evitar el NameError
ya_registrados = []
total_dia = 0
df_filtrado = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

if not df_actual.empty and "Fecha" in df_actual.columns:
    df_actual["Fecha"] = df_actual["Fecha"].astype(str)
    df_filtrado = df_actual[df_actual["Fecha"] == fecha_str]
    ya_registrados = df_filtrado["Nombre y Apellido"].unique().tolist()
    total_dia = len(df_filtrado)

# --- SECCIÓN 1: REGISTRO ---
st.subheader(f"Registrar para el día {fecha_str} (Total: {total_dia})")
busqueda = st.text_input("🔍 Buscar nombre:", placeholder="Escriba aquí...")
lista_filtrada = sorted([n for n in asistentes_frecuentes if busqueda.lower() in n.lower()])

cols = st.columns(4)
for i, nombre_persona in enumerate(lista_filtrada):
    with cols[i % 4]:
        esta_registrado = nombre_persona in ya_registrados
        label = f"✅ {nombre_persona.split(',')[0]}" if esta_registrado else nombre_persona
        
        if st.button(label, key=f"btn_{i}_{nombre_persona}", use_container_width=True, disabled=esta_registrado):
            try:
                # Leer lo más reciente
                df_reciente = conn.read(spreadsheet=url_hoja, ttl=0)
                if df_reciente is None or df_reciente.empty:
                    df_reciente = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])
                else:
                    df_reciente = df_reciente.loc[:, ~df_reciente.columns.str.contains('^Unnamed')].dropna(how='all')
                
                nuevo_registro = pd.DataFrame({"Nombre y Apellido": [nombre_persona], "Fecha": [fecha_str]})
                df_final = pd.concat([df_reciente, nuevo_registro], ignore_index=True)
                conn.update(spreadsheet=url_hoja, data=df_final)
                st.rerun()
            except:
                st.error("Error al guardar. Reintente.")

st.markdown("---")

# --- SECCIÓN 2: REPORTE ---
def generar_html_lindo(df, total, fecha_tit):
    logo_base64 = get_base64_image("logo.png")
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="100">' if logo_base64 else ""
    estilo_css = "<style>body{font-family:sans-serif;text-align:center;}.header-container{border-bottom:3px solid #3498DB;margin-bottom:20px;}table{width:100%;border-collapse:collapse;text-align:left;}th{background:#34495E;color:white;padding:12px;}td{padding:10px;border-bottom:1px solid #ddd;}</style>"
    html_tabla = df.to_html(index=False) if not df.empty else "<p>No hay registros para esta fecha.</p>"
    return f"<html><head>{estilo_css}</head><body><div class='header-container'>{logo_html}<h2>Iglesia Nueva Apostólica - Comunidad Pehuajó</h2><p>Fecha: {fecha_tit}</p><div>Total: {total}</div></div>{html_tabla}</body></html>"

col_del, col_rep = st.columns(2)
with col_del:
    if st.button("🗑️ Eliminar último registro", type="primary", use_container_width=True):
        if not df_actual.empty:
            conn.update(spreadsheet=url_hoja, data=df_actual.iloc[:-1])
            st.rerun()

with col_rep:
    if not df_filtrado.empty:
        html_data = generar_html_lindo(df_filtrado, total_dia, fecha_str)
        st.download_button(f"📄 Descargar Reporte de {fecha_str}", data=html_data, file_name=f"Asistencia_INA_{fecha_str}.html", mime="text/html", use_container_width=True)

with st.expander(f"👁️ Previsualización del día {fecha_str}"):
    st.table(df_filtrado)
