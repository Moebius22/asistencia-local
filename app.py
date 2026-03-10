import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Asistencia Pehuajó", layout="centered", page_icon="📋")

# Estilos CSS mejorados
st.markdown("""
    <style>
    .reporte-tabla { border-collapse: collapse; width: 100%; border: 2px solid black; }
    .reporte-tabla th, .reporte-tabla td { border: 1px solid black !important; padding: 8px; text-align: left; color: black; }
    .stButton>button { border-radius: 5px; height: 2.5em; font-size: 14px; }
    /* Estilo para el cuadro de total */
    .total-box { border: 2px solid black; padding: 10px; margin-top: 10px; font-weight: bold; font-size: 18px; text-align: center; background-color: #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("📋 Control de Asistencia")

# --- LISTA DE PERSONAS ---
if 'lista_personas' not in st.session_state:
    # Lista original
    nombres = [
        "Guaimas, Ana", "Cervigno, Ernesto", "Cervigno, Rosana", "Corbalan, Sandra", 
        "Corbalan, Ana Laura", "Villar, Clara", "Galeano, Lorenzo", "Corbalan, Jorge", 
        "Corbalan, Carlos", "Mendieta, Gladis", "Rodriguez, Jorge", "Corbalan, Ruth", 
        "Rodriguez, Martin", "Rodriguez, Franco", "Cornero, Natalia", "Sangregorio, Nestor", 
        "Rodriguez, Barbara", "Sangregorio, Regina", "Sangregorio, Bautista", "Sangregorio, Simon", 
        "Gazotti, Victor Enrique", "Galvan, Norma", "Gazotti, Thiago", "Gazotti, Hugo", 
        "Gazotti, Magali", "Gazotti, Luciana", "Paulina", "Pablo", "Guzzo, Francisco", 
        "Tobio, Carla", "Guzzo, Luca", "Guzzo, Sara", "Guzzo, Antonia", "Manton, Patricia", 
        "Corbalan, Andrea", "Atun, Adela", "Cervigno, Rocio", "Corbalan, Roma", "Griego, Soledad", 
        "Galiani, Agustin", "Villalba, Dario", "Maria, Jose", "Villalba, Tomas", 
        "Villalba, Santiago", "Corbalan, Mariano", "Corbalan, Miriam", "Jorgelina", 
        "Peñaloza, Nicolas", "Pugnaloni, Dolores", "Cervigno, Amalia"
    ]
    # Ordenamos alfabéticamente por Apellido (ya que están escritos como 'Apellido, Nombre')
    st.session_state.lista_personas = sorted(list(set(nombres)))

if 'asistencias' not in st.session_state:
    st.session_state.asistencias = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

# --- LÓGICA DE REGISTRO ---
fecha_hoy = date.today().strftime("%d/%m/%Y")

st.subheader(f"Registro del día: {fecha_hoy}")

# Filtramos quiénes ya están presentes hoy para cambiar el estado de los botones
presentes_hoy = st.session_state.asistencias[st.session_state.asistencias['Fecha'] == fecha_hoy]['Nombre y Apellido'].tolist()

cols = st.columns(3) # Botones más pequeños usando 3 columnas en lugar de 2
for i, persona in enumerate(st.session_state.lista_personas):
    col = cols[i % 3]
    
    # Si la persona ya está presente, el botón se deshabilita y cambia de color (simulado)
    if persona in presentes_hoy:
        col.button(f"✔️ {persona}", key=f"btn_{i}", disabled=True, use_container_width=True)
    else:
        if col.button(persona, key=f"btn_{i}", use_container_width=True):
            nueva_fila = pd.DataFrame({"Nombre y Apellido": [persona], "Fecha": [fecha_hoy]})
            st.session_state.asistencias = pd.concat([st.session_state.asistencias, nueva_fila], ignore_index=True)
            st.rerun() # Recarga la app para que el botón se ponga gris inmediatamente

# --- BOTÓN DE ATRÁS (DESHACER ÚLTIMO CLIC) ---
if not st.session_state.asistencias.empty:
    st.divider()
    if st.button("⬅️ Deshacer último registro (Borrar error)", type="secondary"):
        st.session_state.asistencias = st.session_state.asistencias[:-1]
        st.rerun()

st.divider()

# --- REPORTE ---
st.header("📊 Reporte de Asistencia")
fecha_reporte = st.date_input("Fecha del reporte", value=date.today())
fecha_rep_str = fecha_reporte.strftime("%d/%m/%Y")

reporte_dia = st.session_state.asistencias[st.session_state.asistencias['Fecha'] == fecha_rep_str]

if not reporte_dia.empty:
    df_final = reporte_dia[['Nombre y Apellido']].reset_index(drop=True)
    df_final.index = df_final.index + 1
    df_final.index.name = "N°"
    df_final = df_final.reset_index()

    tabla_html = df_final.to_html(index=False, classes='reporte-tabla', border=1)
    total = len(df_final)
    total_html = f'<div class="total-box">TOTAL ASISTENTES: {total}</div>'

    st.write(tabla_html + total_html, unsafe_allow_html=True)
    
    reporte_completo_html = f"<html><body><h2>Reporte {fecha_rep_str}</h2>{tabla_html}{total_html}</body></html>"
    st.download_button("📥 Descargar Reporte HTML", data=reporte_completo_html, file_name=f"asistencia_{fecha_rep_str}.html", mime="text/html")
else:
    st.info("No hay registros para esta fecha.")
