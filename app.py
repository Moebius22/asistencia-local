import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Asistencia Pehuajó", layout="centered", page_icon="📋")

# --- CONEXIÓN QUIRÚRGICA ---
try:
    # 1. Traemos los secretos
    raw_creds = st.secrets["connections"]["gsheets"].to_dict()
    
    # 2. Guardamos la URL
    url_hoja = raw_creds.get("spreadsheet")
    
    # 3. CONSTRUIMOS EL DICCIONARIO DE CUENTA DE SERVICIO
    # Esto es exactamente lo que GSheetsConnection busca por dentro
    service_account_info = {
        "type": "service_account",
        "project_id": raw_creds.get("project_id"),
        "private_key_id": raw_creds.get("private_key_id"),
        "private_key": raw_creds.get("private_key").replace("\\n", "\n") if raw_creds.get("private_key") else None,
        "client_email": raw_creds.get("client_email"),
        "client_id": raw_creds.get("client_id"),
        "auth_uri": raw_creds.get("auth_uri"),
        "token_uri": raw_creds.get("token_uri"),
        "auth_provider_x509_cert_url": raw_creds.get("auth_provider_x509_cert_url"),
        "client_x509_cert_url": raw_creds.get("client_x509_cert_url")
    }
    
    # 4. CONECTAMOS: Pasamos el 'service_account_info' como único argumento
    # Esto evita que 'client_email' o 'project_id' anden sueltos y den error
    conn = st.connection(
        "gsheets", 
        type=GSheetsConnection, 
        service_account_info=service_account_info
    )
    
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- ESTILOS ---
st.markdown("""
    <style>
    .titulo-principal { text-align: center; color: #1E3A8A; }
    .reporte-tabla { border-collapse: collapse; width: 100%; border: 2px solid black; }
    .reporte-tabla th, .reporte-tabla td { border: 1px solid black !important; padding: 8px; color: black; }
    .stButton>button { border-radius: 5px; height: 2.8em; font-size: 13px; margin-bottom: 5px; }
    .total-box { border: 2px solid black; padding: 10px; margin-top: 10px; font-weight: bold; font-size: 18px; text-align: center; background-color: #f0f0f0; color: black; }
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
    if df_asistencia is None or df_asistencia.empty or 'Nombre y Apellido' not in df_asistencia.columns:
        df_asistencia = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])
except Exception:
    df_asistencia = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

fecha_hoy = date.today().strftime("%d/%m/%Y")
st.write(
