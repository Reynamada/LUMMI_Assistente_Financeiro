import os
import json
import hashlib
import streamlit as st

# ========= CONFIGURAÇÕES OPENROUTER ==============
MODELO = "nvidia/nemotron-3-super-120b-a12b:free"

# Busca la clave en las variables de sistema (local) o en Secrets (Streamlit Cloud)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ========= CAMINHOS DE DADOS ==============
# Define la ruta base para encontrar la carpeta /data independientemente de dónde se ejecute
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

CAMINHO_PERFIL = os.path.join(DATA_DIR, 'perfil_investidor.json')
CAMINHO_EDU = os.path.join(DATA_DIR, 'material_educativo.json')
CAMINHO_CSV = os.path.join(DATA_DIR, 'receitas_despesas.csv')

# ========= SISTEMA DE AUTENTICAÇÃO ==============
AUTH_FILE = os.path.normpath(os.path.join(DATA_DIR, "auth.json"))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_credentials():
    user = st.secrets.get("APP_USER", "admin")
    pwd = st.secrets.get("APP_PWD", "admin")
    
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, "r") as f:
                auth_data = json.load(f)
                if "pwd_hash" in auth_data:
                    return user, auth_data["pwd_hash"], True
        except:
            pass
    return user, pwd, False

def verificar_autenticacao():
    user_correct, pwd_correct, is_hashed = get_credentials()

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<br><br><h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.write("Por favor, insira suas credenciais.")
                user_input = st.text_input("Usuário")
                pwd_input = st.text_input("Senha", type="password")
                submit_button = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit_button:
                    if is_hashed:
                        pwd_match = (hash_password(pwd_input) == pwd_correct)
                    else:
                        pwd_match = (pwd_input == pwd_correct)
                    
                    if user_input == user_correct and pwd_match:
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")
        st.stop()
