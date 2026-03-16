import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Asistencia Pehuajó", layout="centered", page_icon="📋")

# --- CONEXIÓN SEGURA A GOOGLE SHEETS ---
try:
    # Este bloque limpia la llave privada por si hay errores de formato
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        secrets_dict = dict(st.secrets["connections"]["gsheets"])
        secrets_dict["private_key"] = secrets_dict["private_key"].replace("\\n", "\n")
        conn = st.connection("gsheets", type=GSheetsConnection, **secrets_dict)
    else:
        conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# Estilos CSS para que se vea profesional
st.markdown("""
    <style>
    .titulo-principal { text-align: center; color: #1E3A8A; font-family: Arial, sans-serif; }
    .reporte-tabla { border-collapse: collapse; width: 100%; border: 2px solid black; }
    .reporte-tabla th, .reporte-tabla td { border: 1px solid black !important; padding: 8px; text-align: left; color: black; }
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
    df_asistencia = conn.read(ttl=0)
    if df_asistencia is None or df_asistencia.empty or 'Nombre y Apellido' not in df_asistencia.columns:
        df_asistencia = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])
except Exception:
    df_asistencia = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

fecha_hoy = date.today().strftime("%d/%m/%Y")
st.write(f"📅 **Hoy es:** {fecha_hoy}")

# Identificar presentes hoy
presentes_hoy = []
if not df_asistencia.empty:
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
            conn.update(data=updated_df)
            st.toast(f"✅ Guardado: {persona}")
            st.rerun()

# --- REPORTE ---
st.divider()
st.header("📊 Reporte en Tiempo Real")
fecha_reporte = st.date_input("Consultar fecha:", value=date.today())
fecha_rep_str = fecha_reporte.strftime("%d/%m/%Y")

if not df_asistencia.empty:
    reporte_dia = df_asistencia[df_asistencia['Fecha'] == fecha_rep_str]
    if not reporte_dia.empty:
        df_final = reporte_dia[['Nombre y Apellido']].reset_index(drop=True)
        df_final.index = df_final.index + 1
        df_final.index.name = "N°"
        df_final = df_final.reset_index()
        tabla_html = df_final.to_html(index=False, classes='reporte-tabla', border=1)
        st.write(f"{tabla_html}<div class='total-box'>TOTAL ASISTENTES: {len(df_final)}</div>", unsafe_allow_html=True)
    else:
        st.info("No hay registros para esta fecha.")
else:
    st.info("La planilla está lista para recibir el primer registro.")
