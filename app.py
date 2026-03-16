import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Asistencia Pehuajó", layout="centered", page_icon="📋")

# --- CONEXIÓN QUIRÚRGICA (SOLUCIÓN AL ERROR) ---
try:
    # Traemos todos los secretos
    raw_creds = st.secrets["connections"]["gsheets"].to_dict()
    
    # Extraemos la URL para usarla después (NO en la conexión)
    url_hoja = raw_creds.get("spreadsheet")
    
    # LISTA BLANCA ESTRICTA: Solo estos campos van a la función de conexión
    # Esto elimina 'project_id', 'spreadsheet' y 'type' que causan los errores
    auth_creds = {}
    campos_permitidos = ["client_email", "private_key", "token_uri", "auth_uri"]
    
    for campo in campos_permitidos:
        if campo in raw_creds:
            valor = raw_creds[campo]
            if campo == "private_key":
                # Reparación de saltos de línea
                valor = valor.replace("\\n", "\n")
            auth_creds[campo] = valor

    # CONECTAMOS: Solo con los campos de la lista blanca
    conn = st.connection("gsheets_final", type=GSheetsConnection, **auth_creds)
    
except Exception as e:
    st.error(f"Error crítico de configuración: {e}")
    st.stop()

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .titulo-principal { text-align: center; color: #1E3A8A; font-family: sans-serif; }
    .stButton>button { border-radius: 5px; height: 3em; use-container-width: True; }
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
    # Forzamos el uso de la URL guardada
    df_asistencia = conn.read(spreadsheet=url_hoja, ttl=0)
    if df_asistencia is None or df_asistencia.empty or 'Nombre y Apellido' not in df_asistencia.columns:
        df_asistencia = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])
except Exception:
    df_asistencia = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

fecha_hoy = date.today().strftime("%d/%m/%Y")
st.write(f"📅 **Hoy es:** {fecha_hoy}")

# Marcar presentes
presentes_hoy = []
if not df_asistencia.empty:
    df_asistencia['Fecha'] = df_asistencia['Fecha'].astype(str)
    presentes_hoy = df_asistencia[df_asistencia['Fecha'] == fecha_hoy]['Nombre y Apellido'].tolist()

# --- BOTONES ---
cols = st.columns(3)
for i, persona in enumerate(nombres):
    col = cols[i % 3]
    if persona in presentes_hoy:
        col.button(f"✔️ {persona}", key=f"btn_{i}", disabled=True, use_container_width=True)
    else:
        if col.button(persona, key=f"btn_{i}", use_container_width=True):
            nueva_fila = pd.DataFrame({"Nombre y Apellido": [persona], "Fecha": [fecha_hoy]})
            updated_df = pd.concat([df_asistencia, nueva_fila], ignore_index=True)
            # Guardamos usando la URL
            conn.update(spreadsheet=url_hoja, data=updated_df)
            st.toast(f"✅ Registrado: {persona}")
            st.rerun()
