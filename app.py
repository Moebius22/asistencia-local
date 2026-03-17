import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

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

# 2. Conexión con Google Sheets
try:
    url_hoja = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # LEER DATOS: Forzamos TTL=0 para que siempre traiga lo último y no use memoria vieja
    df_actual = conn.read(spreadsheet=url_hoja, ttl=0).dropna(how='all')
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- LÓGICA DE MARCADO ---
fecha_hoy = date.today().strftime("%d/%m/%Y")

# Filtramos los nombres que ya tienen un registro con la fecha de hoy
if not df_actual.empty:
    # Aseguramos que la columna Fecha sea tratada como texto para comparar bien
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
        
        # Estilo visual: si está registrado, el botón dirá "REGISTRADO" y estará deshabilitado
        label = f"✅ {nombre_persona.split(',')[0]}" if esta_registrado else nombre_persona
        
        if st.button(label, key=f"btn_{i}_{nombre_persona}", use_container_width=True, disabled=esta_registrado):
            try:
                with st.spinner("Guardando..."):
                    # Volvemos a leer justo antes de guardar para evitar pisar datos de otro usuario
                    df_reciente = conn.read(spreadsheet=url_hoja, ttl=0).dropna(how='all')
                    
                    nuevo_registro = pd.DataFrame({
                        "Nombre y Apellido": [nombre_persona], 
                        "Fecha": [fecha_hoy]
                    })
                    
                    # Unimos y nos aseguramos de no dejar filas vacías
                    df_final = pd.concat([df_reciente, nuevo_registro], ignore_index=True)
                    
                    # ACTUALIZAR
                    conn.update(spreadsheet=url_hoja, data=df_final)
                    st.toast(f"¡{nombre_persona} registrado!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

st.markdown("---")

# --- SECCIÓN 2: ELIMINAR Y REPORTES ---
col_del, col_rep = st.columns(2)

with col_del:
    st.subheader("🗑️ Corregir Error")
    if st.button("Eliminar ÚLTIMA fila guardada", type="primary"):
        if not df_actual.empty:
            df_corregido = df_actual.iloc[:-1]
            conn.update(spreadsheet=url_hoja, data=df_corregido)
            st.warning("Se ha eliminado el último registro.")
            st.rerun()

with col_rep:
    st.subheader("📥 Reporte")
    csv = df_actual.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Excel (CSV)", data=csv, file_name=f"asistencia_{fecha_hoy}.csv", mime="text/csv")

if st.checkbox("Ver historial de hoy"):
    st.table(df_actual[df_actual["Fecha"] == fecha_hoy].tail(10))
if st.checkbox("Ver historial de hoy"):
    st.table(df_actual[df_actual["Fecha"] == fecha_hoy].tail(10))
