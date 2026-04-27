import os

# ========= CONFIGURAÇÕES OPENROUTER ==============
MODELO = "nvidia/nemotron-3-super-120b-a12b:free"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("A chave OPENROUTER_API_KEY não foi encontrada nas variáveis de ambiente.")


# ========= CAMINHOS DE DADOS ==============
# Ajustado para encontrar a pasta data fora da pasta src
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

CAMINHO_PERFIL = os.path.join(DATA_DIR, 'perfil_investidor.json')
CAMINHO_EDU = os.path.join(DATA_DIR, 'material_educativo.json')
CAMINHO_CSV = os.path.join(DATA_DIR, 'receitas_despesas.csv')