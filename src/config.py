import os

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
