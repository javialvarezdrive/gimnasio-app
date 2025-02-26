import os
import streamlit as st

# Configuración de Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"] if "SUPABASE_URL" in st.secrets else os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets["SUPABASE_KEY"] if "SUPABASE_KEY" in st.secrets else os.getenv("SUPABASE_KEY")

# Configuración de Streamlit
APP_NAME = "Gestión de Gimnasio"
