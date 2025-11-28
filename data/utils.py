"""
Utilitário para carregar os dados mockados do agente financeiro.
Use este módulo para integrar os dados ao seu agente.
"""

import json
from pathlib import Path

# Caminho base dos dados
DATA_PATH = Path(__file__).parent

def carregar_transacoes():
    """Carrega o histórico de transações do cliente."""
    with open(DATA_PATH / "transacoes.json", "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_perfil():
    """Carrega o perfil do investidor."""
    with open(DATA_PATH / "perfil_investidor.json", "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_produtos():
    """Carrega os produtos financeiros disponíveis."""
    with open(DATA_PATH / "produtos_financeiros.json", "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_todos():
    """Carrega todos os dados de uma vez."""
    return {
        "transacoes": carregar_transacoes(),
        "perfil": carregar_perfil(),
        "produtos": carregar_produtos()
    }

def formatar_contexto_para_prompt(dados=None):
    """
    Formata os dados em texto para incluir no prompt do agente.
    Útil para criar o contexto que será enviado à LLM.
    """
    if dados is None:
        dados = carregar_todos()
    
    perfil = dados["perfil"]
    transacoes = dados["transacoes"]
    
    contexto = f"""
DADOS DO CLIENTE:
- Nome: {perfil["dados_pessoais"]["nome"]}
- Idade: {perfil["dados_pessoais"]["idade"]} anos
- Profissão: {perfil["dados_pessoais"]["profissao"]}
- Renda Mensal: R$ {perfil["dados_pessoais"]["renda_mensal"]:,.2f}

PERFIL DE INVESTIDOR:
- Tipo: {perfil["perfil_investidor"]["tipo"]}
- Tolerância a risco: {perfil["perfil_investidor"]["tolerancia_risco"]}
- Horizonte: {perfil["perfil_investidor"]["horizonte_investimento"]}
- Objetivo: {perfil["perfil_investidor"]["objetivo_principal"]}

SITUAÇÃO FINANCEIRA:
- Patrimônio Total: R$ {perfil["situacao_financeira"]["patrimonio_total"]:,.2f}
- Reserva de Emergência: R$ {perfil["situacao_financeira"]["reserva_emergencia"]:,.2f}
- Saldo em Conta: R$ {transacoes["saldo_atual"]:,.2f}

GASTOS DO MÊS (por categoria):
"""
    for categoria, valor in transacoes["resumo_por_categoria"].items():
        if categoria != "receita":
            contexto += f"- {categoria.title()}: R$ {valor:,.2f}\n"
    
    return contexto


# Exemplo de uso
if __name__ == "__main__":
    print("=== Teste de carregamento dos dados ===\n")
    
    dados = carregar_todos()
    print(f"✓ Transações carregadas: {len(dados['transacoes']['transacoes'])} registros")
    print(f"✓ Perfil carregado: {dados['perfil']['dados_pessoais']['nome']}")
    print(f"✓ Produtos carregados: {len(dados['produtos']['produtos'])} produtos")
    
    print("\n=== Contexto formatado para prompt ===\n")
    print(formatar_contexto_para_prompt(dados))
