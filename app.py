import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, datetime
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

# 2. Conexión y Limpieza de datos
try:
    url_hoja = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_actual = conn.read(spreadsheet=url_hoja, ttl=5)
    df_actual = df_actual.loc[:, ~df_actual.columns.str.contains('^Unnamed')].dropna(how='all')
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

# --- SECCIÓN DE FECHA ---
col_fecha, col_vacia = st.columns([1, 2])
with col_fecha:
    # Selector de fecha (por defecto hoy)
    fecha_seleccionada = st.date_input("📅 Seleccione la fecha de asistencia:", date.today())
    fecha_str = fecha_seleccionada.strftime("%d/%m/%Y")

# Filtrar datos por la fecha seleccionada
ya_registrados = []
total_dia = 0

if not df_actual.empty:
    if "Fecha" in df_actual.columns:
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
                with st.spinner("Guardando..."):
                    df_reciente = conn.read(spreadsheet=url_hoja, ttl=0)
                    df_reciente = df_reciente.loc[:, ~df_reciente.columns.str.contains('^Unnamed')].dropna(how='all')
                    
                    nuevo_registro = pd.DataFrame({
                        "Nombre y Apellido": [nombre_persona], 
                        "Fecha": [fecha_str] # Usa la fecha elegida en el calendario
                    })
                    
                    df_final = pd.concat([df_reciente, nuevo_registro], ignore_index=True)
                    conn.update(spreadsheet=url_hoja, data=df_final)
                    
                    st.toast(f"¡Registrado para el {fecha_str}!")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error("Error al guardar. Intente nuevamente.")

st.markdown("---")

# --- SECCIÓN 2: REPORTE ---
st.subheader("📊 Reporte de Asistencia")

def generar_html_lindo(df, total, fecha_tit):
    estilo_css = """
    <style>
        body { font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .header-container { text-align: center; border-bottom: 3px solid #3498DB; padding-bottom: 10px; margin-bottom: 20px; }
        .total-box { background-color: #EBF5FB; padding: 10px; border-radius: 5px; font-weight: bold; color: #2E86C1; display: inline-block; margin-top: 10px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th { background-color: #34495E; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #D5DBDB; }
        tr:nth-child(even) { background-color: #F8F9F9; }
    </style>
    """
    html_tabla = df.to_html(index=False)
    return f"""
    <html>
    <head>{estilo_css}</head>
    <body>
        <div class="header-container">
            <h2>Asistencia Comunidad Pehuajó</h2>
            <p>Reporte generado para la fecha: {fecha_tit}</p>
            <div class="total-box">Total en este reporte: {total}</div>
        </div>
        {html_tabla}
    </body>
    </html>
    """

col_del, col_rep = st.columns(2)

with col_del:
    if st.button("🗑️ Eliminar último registro", type="primary", use_container_width=True):
        if not df_actual.empty:
            conn.update(spreadsheet=url_hoja, data=df_actual.iloc[:-1])
            st.rerun()

with col_rep:
    if not df_actual.empty:
        # El reporte descarga lo que estamos viendo en la previsualización (la fecha elegida)
        # Si quieres descargar TODO, cambia df_filtrado por df_actual abajo
        html_data = generar_html_lindo(df_filtrado, total_dia, fecha_str)
        st.download_button(
            label=f"📄 Descargar Reporte de {fecha_str}",
            data=html_data,
            file_name=f"Asistencia_Pehuajo_{fecha_str.replace('/','-')}.html",
            mime="text/html",
            use_container_width=True
        )

with st.expander(f"👁️ Previsualización del día {fecha_str}"):
    st.table(df_filtrado)
