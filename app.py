import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
import time

# 1. Configuración de la página
st.set_page_config(page_title="Asistencia Pehuajó", page_icon="📍", layout="wide")

st.title("📍 Registro de Asistencia - Pehuajó")

# --- LISTA DE PERSONAS ---
asistentes_frecuentes = [
    "Cervigno, Amalia", "Cervigno, Rocio", "Corbalan, Roma", "Corbalan, Ana Laura", 
    "Villar, Clara", "Galeano, Lorenzo", "Corbalan, Andrea", "Atun, Matias", 
    "Atun, Adela", "Corbalan, Carlos", "Corbalan, Jorge", "Mendieta, Gladis", 
    "Corbalan, Mariano", "Corbalan, Miriam", "Corbalan, Sandra", "Cervigno, Ernesto", 
    "Cervigno, Rosana", "Guaimas, Ana", "Galiani, Agustin", "Gazotti, Luciana", 
    "Paulina", "Pablo", "Gazotti, Victor", "Galvan, Norma", "Gazotti, Thiago", 
    "Jorgelina", "Griego, Soledad", "Guzzo, Francisco", "Tobio, Carla", 
    "Guzzo, Luca", "Guzzo, Sara", "Guzzo, Antonia", "Nanton, Patricia", 
    "Gazotti, Magali", "Martinez, Gladis", "Peñaloza, Nicolas", "Peralta, Marta", 
    "Peralta, Federico", "Pugnaloni, Dolores", "Rodriguez, Jorge", "Corbalan, Ruth", 
    "Rodriguez, Martin", "Cornero, Natalia", "Rodriguez, Franco", "Sangregorio, Nestor", 
    "Rodriguez, Barbara", "Sangregorio, Regina", "Sangregorio, Bautista", 
    "Sangregorio, Simon", "Corbalan, Cosby", "Villalba, Dario", "Maria, Jose", 
    "Villalba, Santiago", "Villalba, Tomas"
]

# 2. Conexión con Google Sheets (Optimizada para no saturar la cuota)
try:
    url_hoja = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Reducimos la frecuencia de lectura a una cada 10 segundos mínimo
    df_actual = conn.read(spreadsheet=url_hoja, ttl=10).dropna(how='all')
except Exception as e:
    if "429" in str(e):
        st.error("⏳ Google está un poco saturado. Por favor, espera 15 segundos y refresca la página.")
    else:
        st.error(f"Error de conexión: {e}")
    st.stop()

# --- LÓGICA DE MARCADO ---
fecha_hoy = date.today().strftime("%d/%m/%Y")

if not df_actual.empty:
    df_actual["Fecha"] = df_actual["Fecha"].astype(str)
    ya_registrados = df_actual[df_actual["Fecha"] == fecha_hoy]["Nombre y Apellido"].unique().tolist()
else:
    ya_registrados = []

# --- SECCIÓN 1: REGISTRO CON BOTONES ---
st.subheader("Seleccione para registrar ingreso:")
busqueda = st.text_input("🔍 Buscar nombre en la lista:", placeholder="Escriba aquí...")

lista_filtrada = [n for n in asistentes_frecuentes if busqueda.lower() in n.lower()]

cols = st.columns(4)
for i, nombre_persona in enumerate(lista_filtrada):
    with cols[i % 4]:
        esta_registrado = nombre_persona in ya_registrados
        label = f"✅ {nombre_persona.split(',')[0]}" if esta_registrado else nombre_persona
        
        if st.button(label, key=f"btn_{i}_{nombre_persona}", use_container_width=True, disabled=esta_registrado):
            try:
                with st.spinner("Guardando..."):
                    # Al guardar sí necesitamos el dato más fresco posible
                    df_reciente = conn.read(spreadsheet=url_hoja, ttl=0).dropna(how='all')
                    
                    nuevo_registro = pd.DataFrame({
                        "Nombre y Apellido": [nombre_persona], 
                        "Fecha": [fecha_hoy]
                    })
                    
                    df_final = pd.concat([df_reciente, nuevo_registro], ignore_index=True)
                    conn.update(spreadsheet=url_hoja, data=df_final)
                    
                    st.toast(f"¡{nombre_persona} registrado!")
                    # Esperamos un instante antes de reiniciar para que Google procese el cambio
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error("Error al guardar. Posiblemente por exceso de intentos simultáneos. Reintenta en unos segundos.")

st.markdown("---")

# --- SECCIÓN 2: GESTIÓN ---
col_del, col_rep = st.columns(2)

with col_del:
    if st.button("🗑️ Eliminar último registro", type="primary"):
        df_corregido = df_actual.iloc[:-1]
        conn.update(spreadsheet=url_hoja, data=df_corregido)
        st.rerun()

with col_rep:
    csv = df_actual.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar CSV", data=csv, file_name=f"asistencia_{fecha_hoy}.csv")
