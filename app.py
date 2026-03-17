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
    # Leer datos una vez al inicio para verificar estados
    df_actual = conn.read(spreadsheet=url_hoja).dropna(how='all')
except Exception as e:
    st.error("Error de conexión: Revisa los Secrets.")
    st.stop()

# --- SECCIÓN 1: REGISTRO CON BOTONES ---
st.subheader("Seleccione para registrar ingreso:")
busqueda = st.text_input("🔍 Buscar nombre en la lista:", placeholder="Filtrar por apellido o nombre...")

lista_filtrada = [n for n in asistentes_frecuentes if busqueda.lower() in n.lower()]
fecha_hoy = date.today().strftime("%d/%m/%Y")

# Verificar quiénes ya se registraron hoy
ya_registrados = df_actual[df_actual["Fecha"] == fecha_hoy]["Nombre y Apellido"].tolist()

cols = st.columns(4)
for i, nombre_persona in enumerate(lista_filtrada):
    with cols[i % 4]:
        # Si ya está registrado hoy, el botón se deshabilita y cambia el texto
        esta_registrado = nombre_persona in ya_registrados
        label = f"✅ {nombre_persona}" if esta_registrado else nombre_persona
        
        if st.button(label, key=f"btn_{i}", use_container_width=True, disabled=esta_registrado):
            try:
                nuevo_registro = pd.DataFrame({"Nombre y Apellido": [nombre_persona], "Fecha": [fecha_hoy]})
                df_final = pd.concat([df_actual, nuevo_registro], ignore_index=True)
                conn.update(spreadsheet=url_hoja, data=df_final)
                st.success(f"Registrado: {nombre_persona}")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# --- SECCIÓN 2: ADMINISTRACIÓN Y ELIMINAR ---
st.subheader("📊 Gestión de Registros")

col_info, col_del = st.columns([2, 1])

with col_info:
    if st.checkbox("Ver lista completa de hoy"):
        st.dataframe(df_actual[df_actual["Fecha"] == fecha_hoy], use_container_width=True)

with col_del:
    st.warning("🗑️ Zona de Corrección")
    if st.button("Eliminar ÚLTIMO registro", type="secondary", use_container_width=True):
        if not df_actual.empty:
            # Quitamos la última fila
            df_corregido = df_actual.iloc[:-1]
            conn.update(spreadsheet=url_ho_ja, data=df_corregido)
            st.success("Último registro eliminado correctamente.")
            st.rerun()
        else:
            st.info("No hay registros para eliminar.")

# --- SECCIÓN 3: REPORTE ---
csv = df_actual.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar Reporte Completo (CSV)",
    data=csv,
    file_name=f"asistencia_{date.today()}.csv",
    mime="text/csv",
    use_container_width=False
)
