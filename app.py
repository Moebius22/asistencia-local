¡Esto parece una comedia de enredos! Lo que sucede es que la versión de la librería streamlit-gsheets que tienes instalada es probablemente la más reciente, y ha quitado el soporte para el argumento service_account_info que antes funcionaba.

Vamos a volver a la base, pero con un truco de "limpieza total" que no puede fallar. Vamos a pasarle a la conexión únicamente los campos que Google exige (los del JSON), pero uno por uno, para que la librería no vea nada "extraño" como spreadsheet o project_id y se queje.

🛠️ 1. Código definitivo para app.py
Borrá todo y pegá esto. Es el método más compatible de todos:

Python
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="Asistencia Pehuajó", layout="centered", page_icon="📋")

# --- CONEXIÓN MANUAL PASO A PASO ---
try:
    # 1. Obtenemos el diccionario de los secretos
    # Accedemos a la sección principal
    conf = st.secrets["connections"]["gsheets"]
    
    # 2. Guardamos la URL de la hoja para después
    url_hoja = conf["spreadsheet"]
    
    # 3. Arreglamos la llave privada (reemplazando los \n de texto por reales)
    pk = conf["private_key"].replace("\\n", "\n")
    
    # 4. CONEXIÓN: Pasamos solo los argumentos que gspread acepta oficialmente
    conn = st.connection(
        "gsheets",
        type=GSheetsConnection,
        client_email=conf["client_email"],
        private_key=pk,
        project_id=conf["project_id"]
    )
    
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- ESTILOS ---
st.markdown("""
    <style>
    .titulo-principal { text-align: center; color: #1E3A8A; font-family: sans-serif; }
    .stButton>button { border-radius: 5px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='titulo-principal'>Control de Asistencia Comunidad Pehuajó</h1>", unsafe_allow_html=True)

# --- LISTA DE PERSONAS ---
nombres = sorted([
    "Atun, Adela", "Cervigno, Amalia", "Cervigno, Ernesto", "Cervigno, Rocio", 
    "Cervigno, Rosana", "Corbalan, Ana Laura", "Corbalan, Andrea", "Corbalan, Carlos", 
    "Corbalan, Jorge", "Corbalan, Mariano", "Corbalan, Miriam", "Corbalan, Roma", 
    "Corbalan, Ruth", "Corbalan, Sandra", "Cornero, Natalia", "Galeano, Lorenzo", 
    "Galiani, Agustin", "Galvan, Norma", "Gazotti, Hugo", "Gazotti, Luciana", 
    "Gazotti, Magali", "Gazotti, Thiago", "Gazotti, Victor Enrique", "Griego, Soledad", 
    "Guaimas, Ana", "Guzzo, Antonia", "Guzzo, Francisco", "Guzzo, Luca", "Guzzo, Sara", 
    "Jorgelina", "Manton, Patricia", "Maria, Jose", "Mendieta, Gladis", 
    "Pablo", "Paulina", "Peralta, Marta", "Peñaloza, Nicolas", "Pugnaloni, Dolores", 
    "Rodriguez, Barbara", "Rodriguez, Franco", "Rodriguez, Jorge", "Rodriguez, Martin", 
    "Sangregorio, Bautista", "Sangregorio, Nestor", "Sangregorio, Regina", "Sangregorio, Simon", 
    "Tobio, Carla", "Villalba, Dario", "Villalba, Santiago", "Villalba, Tomas", "Villar, Clara"
])

# --- LECTURA DE DATOS ---
try:
    df_asistencia = conn.read(spreadsheet=url_hoja, ttl=0)
    if df_asistencia is None or df_asistencia.empty:
        df_asistencia = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])
except Exception:
    df_asistencia = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

fecha_hoy = date.today().strftime("%d/%m/%Y")
st.write(f"📅 **Hoy es:** {fecha_hoy}")

# Filtro de presentes
presentes_hoy = []
if not df_asistencia.empty:
    df_asistencia['Fecha'] = df_asistencia['Fecha'].astype(str)
    presentes_hoy = df_asistencia[df_asistencia['Fecha'] == fecha_hoy]['Nombre y Apellido'].tolist()

# --- GRILLA DE BOTONES ---
cols = st.columns(3)
for i, persona in enumerate(nombres):
    col = cols[i % 3]
    if persona in presentes_hoy:
        col.button(f"✔️ {persona}", key=f"btn_{i}", disabled=True, use_container_width=True)
    else:
        if col.button(persona, key=f"btn_{i}", use_container_width=True):
            nueva_fila = pd.DataFrame({"Nombre y Apellido": [persona], "Fecha": [fecha_hoy]})
            updated_df = pd.concat([df_asistencia, nueva_fila], ignore_index=True)
            conn.update(spreadsheet=url_hoja, data=updated_df)
            st.rerun()
