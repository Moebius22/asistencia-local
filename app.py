import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Control de Asistencia", layout="wide")
st.title("📋 Registro de Asistencia Local")

# --- LISTA DE PERSONAS (Pegá tu lista acá) ---
if 'lista_personas' not in st.session_state:
    st.session_state.lista_personas = [
        "Ana Guaimas", "Ernesto Cervigno", "Rosana Cervigno", "Sandra Corbalan", "Ana Laura Corbalan", "Clara Villar", "Lorenzo Galeano", "Jorge Corbalan", "Carlos Corbalan", "Gladis Mendieta", "Jorge Rodriguez", "Ruth Corbalan", "Martin Rodriguez", "Franco Rodriguez", "Natalia Cornero", "Nestor Sangregorio", "Barbara Rodriguez", "Regina Sangregorio", "Bautista Sangregorio", "Simon Sangregorio", Victor Enrique Gazotti", "Norma Galvan", "Thiago Gazotti", "Hugo Gazotti", "Magali Gazotti", "Luciana Gazotti", "Paulina", "Pablo", "Francisco Guzzo", "Carla Tobio", "Luca Guzzo", "Sara Guzzo", "Antonia Guzzo", "Gladis Mendieta", "Patricia Manton", "Andrea Corbalan", "Adela Atun", "Rocio Cervigno", "Roma Corbalan", "Soledad Griego", "Agustin Galiani", "Dario Villalba", "Jose Maria", "Tomas Villalba", "Santiago Villalba", "Mariano Corbalan", "Miriam Corbalan", "Jorgelina", "Nicolas Peñaloza", "Dolores Pugnaloni", "Amalia Cervigno"
    ]

# --- BASE DE DATOS TEMPORAL ---
if 'asistencias' not in st.session_state:
    st.session_state.asistencias = pd.DataFrame(columns=["Nombre", "Fecha", "Hora"])

# --- LÓGICA DE REGISTRO ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Seleccioná los presentes de hoy")
    fecha_hoy = date.today()
    
    # Grid de botones
    for persona in st.session_state.lista_personas:
        if st.button(f"✅ {persona}", key=persona, use_container_width=True):
            nueva_asistencia = pd.DataFrame({
                "Nombre": [persona],
                "Fecha": [fecha_hoy.strftime("%d/%m/%Y")],
                "Hora": [pd.Timestamp.now().strftime("%H:%M:%S")]
            })
            # Evitar duplicados el mismo día
            if not ((st.session_state.asistencias['Nombre'] == persona) & 
                    (st.session_state.asistencias['Fecha'] == fecha_hoy.strftime("%d/%m/%Y"))).any():
                st.session_state.asistencias = pd.concat([st.session_state.asistencias, nueva_asistencia], ignore_index=True)
                st.success(f"Registrado: {persona}")
            else:
                st.warning(f"{persona} ya está en la lista de hoy.")

with col2:
    st.subheader("📊 Reportes")
    fecha_busqueda = st.date_input("Elegí una fecha para el reporte", value=fecha_hoy)
    fecha_str = fecha_busqueda.strftime("%d/%m/%Y")
    
    filtro = st.session_state.asistencias[st.session_state.asistencias['Fecha'] == fecha_str]
    
    st.write(f"Asistentes el {fecha_str}: **{len(filtro)}**")
    st.table(filtro[['Nombre', 'Hora']])
    
    if not filtro.empty:
        csv = filtro.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte (CSV)",
            data=csv,
            file_name=f"asistencia_{fecha_str}.csv",
            mime="text/csv",
        )
