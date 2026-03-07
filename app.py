import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Asistencia Pehuajó", layout="centered", page_icon="📋")

st.markdown("""
    <style>
    /* Estilo para que la tabla ocupe el ancho y se vea limpia */
    .stTable {
        border: 1px solid #e6e9ef;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📋 Control de Asistencia")

# --- LISTA DE PERSONAS ---
if 'lista_personas' not in st.session_state:
    nombres = [
        "Ana Guaimas", "Ernesto Cervigno", "Rosana Cervigno", "Sandra Corbalan", 
        "Ana Laura Corbalan", "Clara Villar", "Lorenzo Galeano", "Jorge Corbalan", 
        "Carlos Corbalan", "Gladis Mendieta", "Jorge Rodriguez", "Ruth Corbalan", 
        "Martin Rodriguez", "Franco Rodriguez", "Natalia Cornero", "Nestor Sangregorio", 
        "Barbara Rodriguez", "Regina Sangregorio", "Bautista Sangregorio", "Simon Sangregorio", 
        "Victor Enrique Gazotti", "Norma Galvan", "Thiago Gazotti", "Hugo Gazotti", 
        "Magali Gazotti", "Luciana Gazotti", "Paulina", "Pablo", "Francisco Guzzo", 
        "Carla Tobio", "Luca Guzzo", "Sara Guzzo", "Antonia Guzzo", "Patricia Manton", 
        "Andrea Corbalan", "Adela Atun", "Rocio Cervigno", "Roma Corbalan", "Soledad Griego", 
        "Agustin Galiani", "Dario Villalba", "Jose Maria", "Tomas Villalba", 
        "Santiago Villalba", "Mariano Corbalan", "Miriam Corbalan", "Jorgelina", 
        "Nicolas Peñaloza", "Dolores Pugnaloni", "Amalia Cervigno"
    ]
    st.session_state.lista_personas = sorted(list(set(nombres)))

# --- BASE DE DATOS TEMPORAL ---
if 'asistencias' not in st.session_state:
    st.session_state.asistencias = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

# --- INTERFAZ DE REGISTRO ---
fecha_hoy = date.today().strftime("%d/%m/%Y")

cols = st.columns(2)
for i, persona in enumerate(st.session_state.lista_personas):
    col = cols[i % 2]
    if col.button(persona, key=f"btn_{i}", use_container_width=True):
        ya_esta = ((st.session_state.asistencias['Nombre y Apellido'] == persona) & 
                   (st.session_state.asistencias['Fecha'] == fecha_hoy)).any()
        
        if not ya_esta:
            nueva_fila = pd.DataFrame({"Nombre y Apellido": [persona], "Fecha": [fecha_hoy]})
            st.session_state.asistencias = pd.concat([st.session_state.asistencias, nueva_fila], ignore_index=True)
            st.toast(f"✅ {persona} registrado")
        else:
            st.warning(f"{persona} ya fue registrado hoy.")

st.divider()

# --- SECCIÓN DE REPORTES ---
st.header("📊 Reporte Detallado")
fecha_reporte = st.date_input("Elegí la fecha para ver el reporte", value=date.today())
fecha_rep_str = fecha_reporte.strftime("%d/%m/%Y")

# Filtrar datos
reporte_dia = st.session_state.asistencias[st.session_state.asistencias['Fecha'] == fecha_rep_str]

if not reporte_dia.empty:
    # 1. Crear la tabla limpia con el contador incluido al final
    df_mostrar = reporte_dia[['Nombre y Apellido']].reset_index(drop=True)
    df_mostrar.index = df_mostrar.index + 1  # Para que enumere 1, 2, 3...
    
    # 2. Aplicar bordes finos mediante Styler (esto le da el look profesional)
    st.write(f"### Lista de Asistentes - {fecha_rep_str}")
    
    # Mostramos la tabla con bordes visibles
    st.dataframe(df_mostrar, use_container_width=True)
    
    # 3. Mostrar Total de asistentes resaltado
    total = len(df_mostrar)
    st.info(f"✨ **Total de personas presentes hoy:** {total}")

    # Botón de descarga
    csv = df_mostrar.to_csv(index=True).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte con Bordes",
        data=csv,
        file_name=f"asistencia_{fecha_rep_str}.csv",
        mime="text/csv",
    )
else:
    st.info(f"No hay registros de asistencia para el día {fecha_rep_str}")
