import json
import pandas as pd
import os
from config import CAMINHO_PERFIL, CAMINHO_EDU, CAMINHO_CSV, DATA_DIR

def carregar_dados_base():
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
        with open(CAMINHO_PERFIL, 'r', encoding='utf-8') as f:
            perfil = json.load(f)
        with open(CAMINHO_EDU, 'r', encoding='utf-8') as f:
            edu = json.load(f)
        return perfil, edu
    except Exception as e:
        return {
            "nome": "Usuário", "profissao": "Não informada", "renda_mensal": 0.0, 
            "perfil_investidor": "Conservador", "reserva_emergencia_atual": 0.0, "metas": []
        }, {"conteudo": {"investimentos": {"termos": []}, "alertas_educacionais": []}}

def carregar_transacoes():
    if os.path.exists(CAMINHO_CSV):
        df = pd.read_csv(CAMINHO_CSV, encoding='utf-8')
        df['data'] = pd.to_datetime(df['data'], format='mixed', dayfirst=False)
        return df
    return pd.DataFrame(columns=['data', 'descricao', 'categoria', 'valor', 'tipo'])

def salvar_nova_transacao(data, desc, cat, valor, tipo):
    df = carregar_transacoes()
    nova_linha = pd.DataFrame([{
        'data': data, 'descricao': desc, 'categoria': cat, 'valor': valor, 'tipo': tipo
    }])
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(CAMINHO_CSV, index=False, encoding='utf-8')
    return df