import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Intentar limpiar la llave antes de que la use la conexión
try:
    if "private_key" in st.secrets["connections"]["gsheets"]:
        # Reemplazamos los saltos de línea literales por los reales si fuera necesario
        raw_key = st.secrets["connections"]["gsheets"]["private_key"]
        clean_key = raw_key.replace("\\n", "\n")
except Exception as e:
    st.error("No se pudieron leer los Secrets correctamente.")

# 2. Establecer la conexión
# Dejamos que Streamlit busque solo los secretos en [connections.gsheets]
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Función para registrar (ejemplo)
def registrar_asistencia(nombre, fecha):
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    # Leer datos actuales
    df = conn.read(spreadsheet=url)
    
    # Crear nueva fila
    nuevo_registro = pd.DataFrame({"Nombre y Apellido": [nombre], "Fecha": [fecha]})
    df_final = pd.concat([df, nuevo_registro], ignore_index=True)
    
    # Actualizar
    conn.update(spreadsheet=url, data=df_final)
    st.success(f"Registro exitoso para {nombre}")
    
# --- LISTA DE NOMBRES ---
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

# Leer datos
try:
    df = conn.read(spreadsheet=url_hoja, ttl=0)
    if df is None or df.empty:
        df = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])
except:
    df = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

fecha_hoy = date.today().strftime("%d/%m/%Y")
st.write(f"📅 **Hoy:** {fecha_hoy}")

# Filtrar presentes
presentes = []
if not df.empty and 'Nombre y Apellido' in df.columns:
    df['Fecha'] = df['Fecha'].astype(str)
    presentes = df[df['Fecha'] == fecha_hoy]['Nombre y Apellido'].tolist()

# Botones con indentación corregida
cols = st.columns(3)
for i, nombre in enumerate(nombres):
    col = cols[i % 3]
    if nombre in presentes:
        col.button(f"✔️ {nombre}", key=f"b_{i}", disabled=True, use_container_width=True)
    else:
        if col.button(nombre, key=f"b_{i}", use_container_width=True):
            nueva_fila = pd.DataFrame({"Nombre y Apellido": [nombre], "Fecha": [fecha_hoy]})
            updated_df = pd.concat([df, nueva_fila], ignore_index=True)
            try:
                # Aquí también, no pasar service_account_info
                conn.update(spreadsheet=url_hoja, data=updated_df)
                st.success(f"¡{nombre} registrado!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
