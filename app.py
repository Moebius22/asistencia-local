import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Asistencia Pehuajó", layout="centered", page_icon="📋")

# --- CONEXIÓN QUIRÚRGICA ---
try:
    # 1. Cargamos los secretos
    creds = st.secrets["connections"]["gsheets"].to_dict()
    
    # 2. LIMPIEZA TOTAL: Guardamos la URL y la borramos del diccionario de conexión
    # También borramos 'type' para que no duplique argumentos
    url_hoja = creds.pop("spreadsheet", None)
    creds.pop("type", None)
    
    # 3. Curamos la llave privada
    if "private_key" in creds:
        creds["private_key"] = creds["private_key"].replace("\\n", "\n")
    
    # 4. CONEXIÓN: Ahora 'creds' solo tiene lo que Google necesita para entrar
    conn = st.connection("gsheets", type=GSheetsConnection, **creds)
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- ESTILOS ---
st.markdown("""
    <style>
    .titulo-principal { text-align: center; color: #1E3A8A; }
    .stButton>button { border-radius: 5px; height: 2.8em; font-size: 13px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='titulo-principal'>Control de Asistencia Comunidad Pehuajó</h1>", unsafe_allow_html=True)

# --- LISTA ---
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

fecha_hoy = date.today().strftime("%d/%m/%Y")

# --- LÓGICA DE DATOS ---
try:
    # IMPORTANTE: Le pasamos la URL manualmente aquí
    df_asistencia = conn.read(spreadsheet=url_hoja, ttl=0)
    if df_asistencia is None or df_asistencia.empty:
        df_asistencia = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])
except Exception:
    df_asistencia = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

# Presentes hoy
presentes_hoy = []
if not df_asistencia.empty:
    df_asistencia['Fecha'] = df_asistencia['Fecha'].astype(str)
    presentes_hoy = df_asistencia[df_asistencia['Fecha'] == fecha_hoy]['Nombre y Apellido'].tolist()

st.write(f"📅 **Hoy es:** {fecha_hoy}")

cols = st.columns(3)
for i, persona in enumerate(nombres):
    col = cols[i % 3]
    if persona in presentes_hoy:
        col.button(f"✔️ {persona}", key=f"btn_{i}", disabled=True, use_container_width=True)
    else:
        if col.button(persona, key=f"btn_{i}", use_container_width=True):
            nueva_fila = pd.DataFrame({"Nombre y Apellido": [persona], "Fecha": [fecha_hoy]})
            updated_df = pd.concat([df_asistencia, nueva_fila], ignore_index=True)
            # También pasamos la URL aquí al actualizar
            conn.update(spreadsheet=url_hoja, data=updated_df)
            st.rerun()
