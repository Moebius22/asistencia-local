import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# 1. Configuración de la página
st.set_page_config(page_title="Asistencia Pehuajó", page_icon="📍", layout="wide")

st.title("📍 Registro de Asistencia - Pehuajó")

# --- LISTA DE PERSONAS ACTUALIZADA ---
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
except Exception as e:
    st.error("Error: Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- SECCIÓN 1: REGISTRO CON BOTONES ---
st.subheader("Seleccione para registrar ingreso:")

# Buscador rápido para no tener que scrollear tanto
busqueda = st.text_input("🔍 Buscar nombre en la lista:", placeholder="Escriba para filtrar...")

# Filtrar lista según búsqueda
lista_filtrada = [n for n in asistentes_frecuentes if busqueda.lower() in n.lower()]

# Mostrar botones en columnas (4 para que entren más en pantalla)
cols = st.columns(4)

for i, nombre_persona in enumerate(lista_filtrada):
    with cols[i % 4]:
        # Usamos el nombre + el índice como KEY para evitar el error DuplicateElementId
        if st.button(nombre_persona, key=f"btn_{i}_{nombre_persona}", use_container_width=True):
            try:
                with st.spinner(f"Registrando..."):
                    fecha_hoy = date.today().strftime("%d/%m/%Y")
                    
                    # Leer datos actuales
                    df_existente = conn.read(spreadsheet=url_hoja).dropna(how='all')
                    
                    # Crear nuevo registro
                    nuevo_registro = pd.DataFrame({
                        "Nombre y Apellido": [nombre_persona], 
                        "Fecha": [fecha_hoy]
                    })
                    
                    # Concatenar y actualizar
                    df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
                    conn.update(spreadsheet=url_hoja, data=df_final)
                    
                    st.success(f"✅ {nombre_persona} registrado")
                    st.balloons()
                    st.rerun() # Evita duplicados al refrescar
            except Exception as e:
                st.error(f"Error al guardar: {e}")

st.markdown("---")

# --- SECCIÓN 2: REGISTRO MANUAL Y REPORTES ---
col_man, col_rep = st.columns(2)

with col_man:
    with st.expander("➕ Registrar alguien fuera de lista"):
        nombre_manual = st.text_input("Nombre completo:", key="input_manual")
        if st.button("Guardar Manual", key="btn_manual"):
            if nombre_manual:
                fecha_hoy = date.today().strftime("%d/%m/%Y")
                df_existente = conn.read(spreadsheet=url_hoja).dropna(how='all')
                nuevo_registro = pd.DataFrame({"Nombre y Apellido": [nombre_manual], "Fecha": [fecha_hoy]})
                df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
                conn.update(spreadsheet=url_hoja, data=df_final)
                st.success(f"✅ {nombre_manual} registrado")
                st.rerun()

with col_rep:
    st.write("📊 **Administración**")
    try:
        df_reporte = conn.read(spreadsheet=url_hoja).dropna(how='all')
        csv = df_reporte.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte (CSV)",
            data=csv,
            file_name=f"asistencia_{date.today()}.csv",
            mime="text/csv",
            key="btn_download",
            use_container_width=True
        )
    except:
        st.info("Sin datos para reporte.")

# --- SECCIÓN 3: TABLA ---
if st.checkbox("Ver últimos 10 registros"):
    try:
        st.table(df_reporte.tail(10))
    except:
        st.write("No hay registros aún.")
