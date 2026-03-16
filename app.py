import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="Asistencia Pehuajó", layout="centered")

# --- FORZAR CUENTA DE SERVICIO ---
try:
    # 1. Traemos los datos de los secrets
    conf = st.secrets["connections"]["gsheets"]
    
    # 2. Construimos el diccionario que la librería exige para habilitar CRUD
    # Es VITAL que los nombres de las llaves sean estos exactamente
    creds = {
        "project_id": conf["project_id"],
        "client_email": conf["client_email"],
        "private_key": conf["private_key"].replace("\\n", "\n"),
        "type": "service_account",
    }
    
    # 3. Creamos la conexión pasando las credenciales explícitamente
    conn = st.connection(
        "gsheets", 
        type=GSheetsConnection, 
        service_account_info=creds # Esto le dice: "No soy público, soy una cuenta de servicio"
    )
    url_hoja = conf["spreadsheet"]

except Exception as e:
    st.error(f"Error de autenticación: {e}")
    st.stop()

st.title("Control de Asistencia Comunidad Pehuajó")

# --- LISTA DE NOMBRES ---
nombres = sorted(["Atun, Adela", "Cervigno, Amalia", "Cervigno, Ernesto", "Cervigno, Rocio", "Cervigno, Rosana", "Corbalan, Ana Laura", "Corbalan, Andrea", "Corbalan, Carlos", "Corbalan, Jorge", "Corbalan, Mariano", "Corbalan, Miriam", "Corbalan, Roma", "Corbalan, Ruth", "Corbalan, Sandra", "Cornero, Natalia", "Galeano, Lorenzo", "Galiani, Agustin", "Galvan, Norma", "Gazotti, Hugo", "Gazotti, Luciana", "Gazotti, Magali", "Gazotti, Thiago", "Gazotti, Victor Enrique", "Griego, Soledad", "Guaimas, Ana", "Guzzo, Antonia", "Guzzo, Francisco", "Guzzo, Luca", "Guzzo, Sara", "Jorgelina", "Manton, Patricia", "Maria, Jose", "Mendieta, Gladis", "Pablo", "Paulina", "Peralta, Marta", "Peñaloza, Nicolas", "Pugnaloni, Dolores", "Rodriguez, Barbara", "Rodriguez, Franco", "Rodriguez, Jorge", "Rodriguez, Martin", "Sangregorio, Bautista", "Sangregorio, Nestor", "Sangregorio, Regina", "Sangregorio, Simon", "Tobio, Carla", "Villalba, Dario", "Villalba, Santiago", "Villalba, Tomas", "Villar, Clara"])

# --- LÓGICA DE DATOS (REEMPLAZA ESTA PARTE) ---
try:
    df = conn.read(spreadsheet=url_hoja, ttl=0)
    
    # Si la planilla existe pero está vacía o no tiene columnas, las creamos
    if df is None or df.empty or 'Nombre y Apellido' not in df.columns:
        df = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])
except Exception as e:
    # Si hay un error total en la lectura, empezamos con un DataFrame limpio
    df = pd.DataFrame(columns=["Nombre y Apellido", "Fecha"])

fecha_hoy = date.today().strftime("%d/%m/%Y")
st.write(f"📅 **Hoy:** {fecha_hoy}")

# Filtrar presentes (ahora con verificación de columna)
presentes = []
if not df.empty and 'Nombre y Apellido' in df.columns and 'Fecha' in df.columns:
    df['Fecha'] = df['Fecha'].astype(str)
    presentes = df[df['Fecha'] == fecha_hoy]['Nombre y Apellido'].tolist()
    
# --- BOTONES ---
cols = st.columns(3)
for i, nombre in enumerate(nombres):
    col = cols[i % 3]
    if nombre in presentes:
        col.button(f"✔️ {nombre}", key=f"b_{i}", disabled=True, use_container_width=True)
    else:
       if col.button(nombre, key=f"b_{i}", use_container_width=True):
            nueva_fila = pd.DataFrame({"Nombre y Apellido": [nombre], "Fecha": [fecha_hoy]})
            updated_df = pd.concat([df, nueva_fila], ignore_index=True)
            
            # --- CAMBIO AQUÍ: Usamos create en lugar de update para forzar la escritura ---
            try:
                conn.create(spreadsheet=url_hoja, data=updated_df)
                st.success(f"✅ {nombre} registrado")
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo guardar: {e}")
