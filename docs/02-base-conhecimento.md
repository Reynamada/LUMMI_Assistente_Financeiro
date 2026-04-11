# Base de Conhecimento

## Dados Utilizados


| Arquivo | Formato | Para que serve no Lummi |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores, ou seja, dar continuidade ao atendimento de forma mais eficiente.  |
| `perfil_investidor.json` | JSON | Personalizar as explicaçoes sobre as duvidas e necessidades de aprendizado do client. |
| `produtos_financeiros.json` | JSON | Conhecer os produtos disponiveis para que eles possan ser ensinados ao cliente |
| `receitas_despesas.csv` | CSV | Analisar padrão de gastos e receitas do cliente e usar essas informaçoes de forma didatica |
| `material_educativo.json` | JSON | Material para uso educativo, para ensinar ao cliente conceitos basicos sobre finanças |

> [!TIP]

---

## Adaptações nos Dados

[
Seguindo a mesma estrutura e atributos, adicione outros produtos: FII - Fundo Imobiliário, Fundo DI (Depósito Interfinanceiro), Tesouro IPCA+(Índice de Preços ao Consumidor Amplo), Poupança, Debêntures Incentivadas, Fundo de Previdência Conservador, Conta Remunerada, Caixinha Digital.
Coloquei por separado os produtos: LCI e LCA, já que eles tem significado diferentes. Adicione a cada um dos produtos um atributo: Descrição.

Atualizei o perfil de investidor com dados autênticos, preenchendo cada atributo devidamente para refletir um cenário real.
No archivo de transações, modifiquei o nome do arquivo para receitas_despesas.csv para ser mais especifico e alguns valores e descrição de despesas e adicione escola e banco, com seus respectivos atributos preenchidos.
Adicione o arquivo material_educativo.json, que contem conhecimento confiavel sobre finanças, estructurado de forma educativa para o cliente. 
]

---

## Estratégia de Integração

### Como os dados são carregados?

Tem duas possibilidades:
## 1.Injeção direta no prompt
Copiar e colar os dados (Ctrl + C / Ctrl + V) diretamente no contexto da conversa.
Útil para testes rápidos ou quando os dados são pequenos.

## 2. Carregamento via código (como no exemplo abaixo)
Utilizar scripts em Python para ler arquivos estruturados (JSON, CSV).
Essa abordagem é mais robusta, pois permite manipulação, análise e atualização dinâmica dos dados.

# Arquivos JSON/CSV são carregados no início da sessão.

```python
import json
import pandas as pd

# -----------------------------
# 1. Carregar perfil e produtos financeiros (JSON)
# -----------------------------
try:
    with open('data/perfil_investidor.json', 'r', encoding='utf-8') as f:
        perfil = json.load(f)

    with open('data/produtos_financeiros.json', 'r', encoding='utf-8') as f:
        produtos = json.load(f)

# -----------------------------
# 2. Carregar histórico_atendimento e receitas_despesas (CSV) com pandas
# -----------------------------
try:
    historico= pd.read_csv(‘data/histórico_atendimento.csv’)
    transacoes = pd.read_csv("data/receitas_despesas.csv")

    print("✅ Transações carregadas:")

```

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?
>
> Os dados não são injetados diretamente no system prompt.
  Eles são carregados via código e consultados dinamicamente conforme a pergunta.
  Isso garante eficiência, evita sobrecarga e permite respostas personalizadas e contextualizadas.

Uma forma de como os dados serian usados no prompt:
```
DADOS E PERFIL DO CLIENTE (data/perfil_investidor.json):
{
  "nome": "José Lino",
  "idade": 48,
  "profissao": "Engenheiro de informática",
  "renda_mensal": 8000.00,
  "perfil_investidor": "moderado",
  "objetivo_principal": "Construir reserva de emergência",
  "patrimonio_total": 15000.00,
  "reserva_emergencia_atual": 2400.00,
  "aceita_risco": false,
  "metas": [
    {
      "meta": "Completar reserva de emergência",
      "valor_necessario": 15000.00,
      "prazo": "2026-12"
    },
    {
      "meta": "Entrada do apartamento",
      "valor_necessario": 70000.00,
      "prazo": "2027-12"
    }
  ]
}
MATERIAL EDUCATIVO PARA O CLIENTE (data/material_educativo.json):
{
  "versao": "1.1",
  "projeto": "Reyna IA - Educação Financeira",
  "data_atualizacao": "2026-04-08",
  "conteudo": {
    "sistema_credito": {
      "titulo": "Sistema de Crédito e Dívidas",
      "contexto": "O Brasil tem uma das maiores taxas de juros do mundo.",
      "topicos": {
        "juros_compostos": "Explicar o efeito 'bola de neve' no Cartão e Cheque Especial.",
        "score_credito": "Influência do Serasa/Boa Vista nas taxas de juros.",
        "cadastro_positivo": "Histórico de pagamento para facilitar financiamentos."
      }
    },
    "investimentos": {
      "titulo": "Dicionário de Investimentos",
      "termos": [
        {"sigla": "Selic/CDI", "descricao": "Termômetros da economia; regem a Renda Fixa."},
        {"sigla": "IPCA", "descricao": "Inflação oficial; essencial para manter o poder de compra."},
        {"sigla": "Reserva de Emergência", "descricao": "Primeiro passo; foco em Liquidez Diária."}
      ]
    },
    "produtos_comparativo": {
      "cdb": {
        "nome": "Certificado de Depósito Bancário",
        "risco": "Baixo (Garantia FGC)",
        "imposto": "Tabela Regressiva IR",
        "resumo": "Empréstimo para bancos, rende CDI."
      },
      "tesouro": {
        "nome": "Tesouro Direto",
        "risco": "Mínimo (Governo Federal)",
        "acessibilidade": "A partir de R$ 30,00",
        "resumo": "Empréstimo para o Estado, mais seguro do país."
      }
    }
  }
}
PRODUTOS FINANCEIROS (data/produtos_financeiros.json):
[ {
  "nome": "FII - Fundo Imobiliário",
  "categoria": "fundos",
  "risco": "médio",
  "rentabilidade": "Distribuição mensal de dividendos (varia conforme o fundo),entre 7% e 12%a.a.",
  "aporte_minimo": 100.00,
  "indicado_para": "Quem deseja investir em imóveis sem precisar comprar diretamente",
  "descricao": "Fundos que reúnem investidores para aplicar em empreendimentos imobiliários (shoppings, escritórios, galpões logísticos). O investidor recebe rendimentos mensais proporcionais ao lucro dos imóveis, com isenção de IR sobre dividendos para pessoa física."
  },
  {
    "nome": "Tesouro Selic",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "100% da taxa Selic.Taxa Selic vigente: (14,75% a.a. em 2026)",
    "aporte_minimo": 30.00,
    "indicado_para": "Reserva de emergência e iniciantes",
    "descricao": "Título público federal atrelado à Selic, com liquidez diária e segurança garantida pelo Tesouro Nacional."
  },
  {
    "nome": "CDB Liquidez Diária",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "102% do CDI",
    "aporte_minimo": 100.00,
    "indicado_para": "Quem busca rendimento simples e resgate rápido",
    "descricao": "Certificado de Depósito Bancário emitido por bancos, com liquidez diária e cobertura do FGC até R$250 mil."
  },
  {
    "nome": "LCI (Letra de Crédito Imobiliário)",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "90% a 100% do CDI",
    "aporte_minimo": 1000.00,
    "indicado_para": "Quem busca isenção de IR e segurança",
    "descricao": "Título emitido por bancos para financiar o setor imobiliário, com isenção de imposto de renda para pessoa física e exige prazo mínimo de 90 dias."
  },
  {
    "nome": "LCA (Letra de Crédito do Agronegócio)",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "entre 90% e 100% do CDI, variando conforme prazo e emissor.",
    "aporte_minimo": 1000.00,
    "indicado_para": "Quem deseja diversificação e isenção de IR",
    "descricao": "Título emitido para financiar o agronegócio, também isento de imposto de renda para pessoa física e exige prazo mínimo de 90 dias."
  },
  {
    "nome": "Fundo DI (Depósito Interfinanceiro).", 
    "categoria": "fundos",
    "risco": "baixo",
    "rentabilidade": "95% a 105% do CDI (~13,9% a 15,4% ao ano em 2026)",
    "aporte_minimo": 500.00,
    "indicado_para": "Ideal para quem quer deixar o dinheiro aplicado com segurança e disponibilidade.",
    "descricao": "Fundo de investimento que aplica em títulos públicos e privados de baixo risco, acompanhando o CDI."
  },
  {
    "nome": "Tesouro IPCA+(Índice de Preços ao Consumidor Amplo)",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "IPCA + taxa fixa (~5% a 6% a.a. em 2026).",
    "aporte_minimo": 30.00,
    "indicado_para": "Quem quer proteger o dinheiro da inflação",
    "descricao": "Título público que garante rendimento acima da inflação, preservando o poder de compra no longo prazo,+ (mais) → indica que o título paga a variação do IPCA + uma taxa fixa de juros definida no momento da compra.."
  },
  {
    "nome": "Poupança",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "Selic > 8,5% a.a. → Poupança rende 0,5% ao mês + TR (~6,17% a.a.),Selic ≤ 8,5% a.a. → Poupança rende 70% da Selic + TR",
    "aporte_minimo": 0.00,
    "indicado_para": "Quem busca simplicidade e liquidez imediata",
    "descricao": "Aplicação tradicional e acessível, com liquidez imediata, mas rendimento inferior a outros produtos e  isentos de imposto de renda."
  },
  {
    "nome": "Debêntures Incentivadas",
    "categoria": "renda_fixa",
    "risco": "médio",
    "rentabilidade": "12% a 15% a.a. (isento de IR para pessoa física)",
    "aporte_minimo": "R$1.000,00 (emissão direta) ou R$10.000,00 (fundos de debêntures)",
    "indicado_para": "Quem busca retorno maior e isenção de IR",
    "descricao": "Títulos emitidos por empresas para financiar projetos de infraestrutura, com isenção de IR para pessoa física."
  },
  {
    "nome": "Fundo Multimercado Conservador",
    "categoria": "fundos",
    "risco": "médio",
    "rentabilidade": "110% a 120% do CDI (~16% a 17,5% a.a. em 2026)",
    "aporte_minimo": 1000.00,
    "indicado_para": "Quem aceita risco moderado para maior retorno",
    "descricao": "Fundo que mistura renda fixa e outras estratégias, buscando retorno superior ao CDI com risco controlado."
  },
  {
    "nome": "Fundo de Previdência Conservador",
    "categoria": "previdência",
    "risco": "baixo",
    "rentabilidade": "100% a 110% do CDI (~14,6% a 16,1% a.a. em 2026)",
    "aporte_minimo": 1000.00 ,
    "indicado_para": "Quem deseja acumular patrimônio para aposentadoria",
    "descricao": "Fundo voltado para aposentadoria, com foco em renda fixa e benefícios fiscais de longo prazo."
  },
  { "nome": "Conta Remunerada",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "100% do CDI",
    "aporte_minimo": 0.00,
    "indicado_para": "Quem deseja deixar o dinheiro parado na conta rendendo",
    "descricao": "Conta corrente que remunera automaticamente o saldo disponível, sem necessidade de aplicação extra."
  },
  {
    "nome": "Caixinha Digital",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "próximo ao CDI, geralmente entre 95% e 100% do CDI",
    "aporte_minimo": 1.00,
    "indicado_para": "Quem está começando e quer guardar pequenas quantias",
    "descricao": "Funcionalidade oferecida por bancos digitais para guardar valores separados, com rendimento automático."
  }
  {
    "nome": "Fundo de Ações",
    "categoria": "fundo",
    "risco": "alto",
    "rentabilidade": "Variável:pois depende da valorização ou desvalorização das ações que compõem a carteira do fundo.",
    "aporte_minimo": 100.00,
    "indicado_para": "Perfil arrojado com foco no longo prazo, Pode ter ganhos expressivos no longo prazo, mas também oscilações negativas no curto prazo, não há garantia de rendimento mínimo, diferente dos produtos de renda fixa.".
                     
  }
]
RECEITAS E DESPESAS DO CLIENTE (data/receitas_despesas.csv):
data,descricao,categoria,valor,tipo
2026-04-07,Salário,receita,8000.00,entrada
2026-04-07,Aluguel,moradia,1500.00,saida
2026-04-07,Supermercado,alimentacao,2000.00,saida
2026-04-07,HBOmax,lazer,40.90,saida
2026-04-07,PrimeVideo,lazer,40.90,saida
2026-04-07,Farmácia,saude,500.00,saida
2026-04-07,Restaurante,alimentacao,250.00,saida
2026-04-07,Uber,transporte,200.00,saida
2026-04-07,Conta de Luz,moradia,660.00,saida
2026-04-07,Academia,saude,295.00,saida
2026-04-07,Escola,Educaçao filhos,1100.00,saida
2026-04-07,Banco,Compras Parceladas,3000.00,saida mensal

HISTORICO DE ATENDIMENTO DO CLIENTE (data/historico_atendimento.csv):
data,canal,tema,resumo,resolvido
2025-09-15,chat,CDB,Cliente perguntou sobre rentabilidade e prazos,sim
2025-09-22,telefone,Problema no app,Erro ao visualizar extrato foi corrigido,sim
2025-10-01,chat,Tesouro Selic,Cliente pediu explicação sobre o funcionamento do Tesouro Direto,sim
2025-10-12,chat,Metas financeiras,Cliente acompanhou o progresso da reserva de emergência,sim
2025-10-25,email,Atualização cadastral,Cliente atualizou e-mail e telefone,sim

```



## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```
Dados do Cliente:
- Nome: João Silva
- Perfil: Moderado
- Saldo disponível: R$ 5.000

Últimas transações:
- 01/11: Supermercado - R$ 450
- 03/11: Streaming - R$ 55
...
```
