import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Asistencia Pehuajó", layout="centered", page_icon="📋")

# CSS para forzar bordes negros finos en la tabla
st.markdown("""
    <style>
    table {
        border-collapse: collapse;
        width: 100%;
        border: 1px solid black;
    }
    th, td {
        border: 1px solid black !important;
        padding: 8px;
        text-align: left;
        color: black;
    }
    th {
        background-color: #f2f2f2;
    }
    .total-box {
        border: 2px solid black;
        padding: 10px;
        margin-top: 10px;
        font-weight: bold;
        font-size: 18px;
        text-align: center;
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

if 'asistencias' not in st.session_state:
    st.session_state.asistencias = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

# --- REGISTRO ---
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

st.divider()

# --- REPORTE CON BORDES NEGROS ---
st.header("📊 Reporte de Asistencia")
fecha_reporte = st.date_input("Fecha del reporte", value=date.today())
fecha_rep_str = fecha_reporte.strftime("%d/%m/%Y")

reporte_dia = st.session_state.asistencias[st.session_state.asistencias['Fecha'] == fecha_rep_str]

if not reporte_dia.empty:
    # Creamos el DataFrame para mostrar con columnas separadas
    df_final = reporte_dia[['Nombre y Apellido']].reset_index(drop=True)
    df_final.index = df_final.index + 1
    df_final.index.name = "N°"
    df_final = df_final.reset_index() # El índice pasa a ser una columna llamada "N°"

    # Convertimos a HTML para forzar los bordes negros
    st.write(f"### Lista del día {fecha_rep_str}")
    st.write(df_final.to_html(index=False, escape=False), unsafe_allow_html=True)
    
    # Cuadro de total al final
    total = len(df_final)
    st.markdown(f'<div class="total-box">TOTAL ASISTENTES: {total}</div>', unsafe_allow_html=True)
    
    # Botón de descarga
    csv = df_final.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar CSV", data=csv, file_name=f"asistencia_{fecha_rep_str}.csv")
else:
    st.info("No hay registros para esta fecha.")
