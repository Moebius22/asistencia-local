import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="Asistencia Pehuajó", layout="centered")

# --- CONEXIÓN DEFINITIVA ---
try:
    # 1. Obtener la info del diccionario service_account_info de los secretos
    info = st.secrets["connections"]["gsheets"]["service_account_info"]
    url_hoja = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # 2. Reparar la llave privada (esto es lo que causaba el error de formato)
    info["private_key"] = info["private_key"].replace("\\n", "\n")
    
    # 3. Conectar pasando el diccionario LIMPIO
    conn = st.connection("gsheets", type=GSheetsConnection, service_account_info=info)
    
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- LÓGICA DE LA APP ---
st.title("Control de Asistencia")

nombres = sorted(["Atun, Adela", "Cervigno, Amalia", "Cervigno, Ernesto", "Cervigno, Rocio", "Cervigno, Rosana", "Corbalan, Ana Laura", "Corbalan, Andrea", "Corbalan, Carlos", "Corbalan, Jorge", "Corbalan, Mariano", "Corbalan, Miriam", "Corbalan, Roma", "Corbalan, Ruth", "Corbalan, Sandra", "Cornero, Natalia", "Galeano, Lorenzo", "Galiani, Agustin", "Galvan, Norma", "Gazotti, Hugo", "Gazotti, Luciana", "Gazotti, Magali", "Gazotti, Thiago", "Gazotti, Victor Enrique", "Griego, Soledad", "Guaimas, Ana", "Guzzo, Antonia", "Guzzo, Francisco", "Guzzo, Luca", "Guzzo, Sara", "Jorgelina", "Manton, Patricia", "Maria, Jose", "Mendieta, Gladis", "Pablo", "Paulina", "Peralta, Marta", "Peñaloza, Nicolas", "Pugnaloni, Dolores", "Rodriguez, Barbara", "Rodriguez, Franco", "Rodriguez, Jorge", "Rodriguez, Martin", "Sangregorio, Bautista", "Sangregorio, Nestor", "Sangregorio, Regina", "Sangregorio, Simon", "Tobio, Carla", "Villalba, Dario", "Villalba, Santiago", "Villalba, Tomas", "Villar, Clara"])

try:
    df = conn.read(spreadsheet=url_hoja, ttl=0)
except:
    df = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

fecha_hoy = date.today().strftime("%d/%m/%Y")
st.write(f"📅 Fecha: {fecha_hoy}")

# Filtro de presentes hoy
presentes = []
if not df.empty:
    presentes = df[df['Fecha'] == fecha_hoy]['Nombre y Apellido'].tolist()

cols = st.columns(3)
for i, persona in enumerate(nombres):
    col = cols[i % 3]
    if persona in presentes:
        col.button(f"✔️ {persona}", key=f"p_{i}", disabled=True, use_container_width=True)
    else:
        if col.button(persona, key=f"b_{i}", use_container_width=True):
            nueva_fila = pd.DataFrame({"Nombre y Apellido": [persona], "Fecha": [fecha_hoy]})
            updated_df = pd.concat([df, nueva_fila], ignore_index=True)
            conn.update(spreadsheet=url_hoja, data=updated_df)
            st.rerun()
