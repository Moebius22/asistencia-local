import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Asistencia Pehuajó", layout="centered", page_icon="📋")

# Estilos CSS para botones, tablas y títulos
st.markdown("""
    <style>
    .titulo-principal { text-align: center; color: #1E3A8A; font-family: Arial, sans-serif; }
    .reporte-tabla { border-collapse: collapse; width: 100%; border: 2px solid black; }
    .reporte-tabla th, .reporte-tabla td { border: 1px solid black !important; padding: 8px; text-align: left; color: black; }
    .stButton>button { border-radius: 5px; height: 2.8em; font-size: 13px; margin-bottom: 5px; }
    .total-box { border: 2px solid black; padding: 10px; margin-top: 10px; font-weight: bold; font-size: 18px; text-align: center; background-color: #f0f0f0; color: black; }
    </style>
    """, unsafe_allow_html=True)

# TÍTULO SOLICITADO
st.markdown("<h1 class='titulo-principal'>Control de Asistencia Comunidad Pehuajó</h1>", unsafe_allow_html=True)

# --- LISTA DE PERSONAS (Ordenada por Apellido) ---
if 'lista_personas' not in st.session_state:
    nombres = [
        "Atun, Adela", "Cervigno, Amalia", "Cervigno, Ernesto", "Cervigno, Rocio", 
        "Cervigno, Rosana", "Corbalan, Ana Laura", "Corbalan, Andrea", "Corbalan, Carlos", 
        "Corbalan, Jorge", "Corbalan, Mariano", "Corbalan, Miriam", "Corbalan, Roma", 
        "Corbalan, Ruth", "Corbalan, Sandra", "Cornero, Natalia", "Peralta, Marta", "Galeano, Lorenzo", 
        "Galiani, Agustin", "Galvan, Norma", "Gazotti, Hugo", "Gazotti, Luciana", 
        "Gazotti, Magali", "Gazotti, Thiago", "Gazotti, Victor Enrique", "Griego, Soledad", 
        "Guzzo, Antonia", "Guzzo, Francisco", "Guzzo, Luca", "Guzzo, Sara", "Guaimas, Ana",  
        "Jorgelina", "Manton, Patricia", "Maria, Jose", "Mendieta, Gladis", 
        "Pablo", "Paulina", "Peñaloza, Nicolas", "Pugnaloni, Dolores", 
        "Rodriguez, Barbara", "Rodriguez, Franco", "Rodriguez, Jorge", "Rodriguez, Martin", 
        "Sangregorio, Bautista", "Sangregorio, Nestor", "Sangregorio, Regina", "Sangregorio, Simon", 
        "Tobio, Carla", "Villalba, Dario", "Villalba, Santiago", "Villalba, Tomas", "Villar, Clara"
    ]
    st.session_state.lista_personas = sorted(list(set(nombres)))

if 'asistencias' not in st.session_state:
    st.session_state.asistencias = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

# --- LÓGICA DE REGISTRO ---
fecha_hoy = date.today().strftime("%d/%m/%Y")
st.write(f"📅 **Hoy es:** {fecha_hoy}")

# Identificar quiénes ya marcaron presente hoy
presentes_hoy = st.session_state.asistencias[st.session_state.asistencias['Fecha'] == fecha_hoy]['Nombre y Apellido'].tolist()

# Grilla de botones (3 columnas para que sean más pequeños)
cols = st.columns(3)
for i, persona in enumerate(st.session_state.lista_personas):
    col = cols[i % 3]
    
    # Si ya está registrado, el botón aparece "bloqueado" y con tilde
    if persona in presentes_hoy:
        col.button(f"✔️ {persona}", key=f"btn_{i}", disabled=True, use_container_width=True)
    else:
        # Botón normal activo
        if col.button(persona, key=f"btn_{i}", use_container_width=True):
            nueva_fila = pd.DataFrame({"Nombre y Apellido": [persona], "Fecha": [fecha_hoy]})
            st.session_state.asistencias = pd.concat([st.session_state.asistencias, nueva_fila], ignore_index=True)
            st.rerun()

# --- ACCIONES DE CORRECCIÓN ---
if not st.session_state.asistencias.empty:
    st.divider()
    if st.button("⬅️ Deshacer último registro (Borrar error)", type="secondary"):
        st.session_state.asistencias = st.session_state.asistencias[:-1]
        st.rerun()

st.divider()

# --- SECCIÓN DE REPORTE ---
st.header("📊 Reporte Diario")
fecha_reporte = st.date_input("Consultar fecha:", value=date.today())
fecha_rep_str = fecha_reporte.strftime("%d/%m/%Y")

reporte_dia = st.session_state.asistencias[st.session_state.asistencias['Fecha'] == fecha_rep_str]

if not reporte_dia.empty:
    # Preparar tabla con número de orden
    df_final = reporte_dia[['Nombre y Apellido']].reset_index(drop=True)
    df_final.index = df_final.index + 1
    df_final.index.name = "N°"
    df_final = df_final.reset_index()

    # Mostrar tabla con bordes negros
    tabla_html = df_final.to_html(index=False, classes='reporte-tabla', border=1)
    total = len(df_final)
    total_html = f'<div class="total-box">TOTAL ASISTENTES: {total}</div>'

    st.write(tabla_html + total_html, unsafe_allow_html=True)
    
    # Descarga idéntica
    reporte_completo_html = f"""
    <html>
    <head>
        <style>
            .reporte-tabla {{ border-collapse: collapse; width: 100%; border: 2px solid black; }}
            .reporte-tabla th, .reporte-tabla td {{ border: 1px solid black; padding: 8px; text-align: left; }}
            .total-box {{ border: 2px solid black; padding: 10px; margin-top: 10px; font-weight: bold; text-align: center; }}
        </style>
    </head>
    <body>
        <h2>Control de Asistencia Comunidad Pehuajó</h2>
        <p>Fecha del Reporte: {fecha_rep_str}</p>
        {tabla_html}
        {total_html}
    </body>
    </html>
    """
    st.download_button("📥 Descargar Reporte HTML", data=reporte_completo_html, file_name=f"asistencia_{fecha_rep_str}.html", mime="text/html")
else:
    st.info(f"No hay registros de asistencia para el día {fecha_rep_str}.")
