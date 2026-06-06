# Base de Conhecimento

## Dados Utilizados


| Fonte | Formato | Para que serve no Lummi |
|---------|---------|---------------------|
| Banco de Dados (Tabela `Perfil`) | PostgreSQL / JSON | Personalizar as explicações sobre as dúvidas e necessidades de aprendizado do cliente. Armazena metas, renda e dados pessoais. |
| Banco de Dados (Tabela `Transacao`) | PostgreSQL | Analisar padrão de gastos e receitas do cliente, calcular saldo, rastrear pagamentos mensais e usar essas informações de forma didática. (O arquivo CSV local serve apenas para migração inicial). |
| `material_educativo.json` | JSON | Material para uso educativo, para ensinar ao cliente conceitos básicos sobre finanças, produtos. |

> [!TIP]
> O arquivo `material_educativo.json` é a única fonte de conhecimento **local e estática**. Todo o restante (perfil do usuário, transações e histórico do chat) vive no banco de dados PostgreSQL (Neon) e é consultado dinamicamente a cada interação.

---

## Adaptações nos Dados

```
- O perfil do investidor e o histórico de transações foram migrados para um **Banco de Dados Relacional (PostgreSQL no Neon)** via SQLAlchemy, garantindo maior integridade, segurança e controle dinâmico (edição, deleção e inserção em tempo real).
- A base de conhecimento em JSON (`material_educativo.json`) foi mantida por ser altamente estruturada e eficiente para injetar conceitos e alertas como grounding no modelo de IA (incluindo FII, Tesouro IPCA+, LCI/LCA, Debêntures e criptomoedas).
- Adicionado sistema de persistência para o Histórico do Chat (`ChatHistory`) no banco de dados, o que permite aos usuários rever atendimentos de dias anteriores sem sobrecarregar a memória de contexto do agente no dia atual.
``` 

---

## Estratégia de Integração

### Como os dados são carregados?

Tem duas possibilidades:
## 1.Injeção direta no prompt
Copiar e colar os dados (Ctrl + C / Ctrl + V) diretamente no contexto da conversa.
Útil para testes rápidos ou quando os dados são pequenos.

## 2. Carregamento via código 
Utilizar scripts em Python para ler arquivos estruturados (JSON, CSV).
Essa abordagem é mais robusta, pois permite manipulação, análise e atualização dinâmica dos dados.


```python
import json
import pandas as pd
from config import CAMINHO_EDU
from database import get_session, Perfil, Transacao

#====== CARREGAR DADOS =============
def carregar_dados_base():
    perfil = {
        "nome": "Usuário", "profissao": "Não informada", "renda_mensal": 0.0, 
        "perfil_investidor": "Conservador", "reserva_emergencia_atual": 0.0, "metas": []
    }
    try:
        db = get_session()
        perfil_db = db.query(Perfil).first()
        if perfil_db and perfil_db.dados_json:
            perfil = json.loads(perfil_db.dados_json)
        db.close()
    except Exception as e:
        pass

    try:
        with open(CAMINHO_EDU, 'r', encoding='utf-8') as f:
            edu = json.load(f)
    except Exception as e:
        edu = {"conteudo": {"investimentos": {"termos": []}, "alertas_educacionais": []}}
        
    return perfil, edu

def carregar_transacoes():
    try:
        db = get_session()
        transacoes = db.query(Transacao).all()
        db.close()
        
        dados = [{
            'id': t.id, 'data': t.data, 'descricao': t.descricao,
            'categoria': t.categoria, 'valor': t.valor, 'tipo': t.tipo,
            'data_vencimento': t.data_vencimento, 'dia_vencimento': t.dia_vencimento
        } for t in transacoes]
        
        df = pd.DataFrame(dados)
        if not df.empty:
            df['data'] = pd.to_datetime(df['data'])
            return df
    except Exception as e:
        pass
    return pd.DataFrame(columns=['id', 'data', 'descricao', 'categoria', 'valor', 'tipo', 'data_vencimento', 'dia_vencimento'])


### 3. Exibição das Metas (Bloco de Metas)
O assistente exibe o progresso das metas financeiras (incluindo a Reserva de Emergência) de forma interativa através do componente definido na skill `exibir_rastreador_metas` em `src/skills.py`:

```python
def exibir_rastreador_metas(perfil):
    with st.expander("🎯 Rastreador de Metas", expanded=True):
        metas = perfil.get('metas', [])
        reserva_atual = perfil.get('reserva_emergencia_atual', 0.0)
        
        if metas:
            for m in metas:
                nome_meta = m.get('meta', 'Meta')
                valor_nec = m.get('valor_necessario', 1.0)
                
                if "reserva" in nome_meta.lower():
                    progresso = min(reserva_atual / valor_nec, 1.0)
                    st.write(f"🛡️ **{nome_meta}**")
                    st.write(f"R$ {reserva_atual:.2f} / R$ {valor_nec:.2f}")
                else:
                    patrimonio = perfil.get('patrimonio_total', 0.0)
                    progresso = min(patrimonio / valor_nec, 1.0)
                    st.write(f"🎯 **{nome_meta}**")
                    st.write(f"R$ {patrimonio:.2f} / R$ {valor_nec:.2f}")
                    
                st.progress(progresso)
                st.caption(f"Prazo: {m.get('prazo', 'N/A')}")
                st.markdown("---")
        else:
            st.info("Nenhuma meta definida no seu perfil.")
```

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
  "nome": "Reyna Amada",
  "idade": 48,
  "profissao": "Engenheiro de informática",
  "renda_mensal": 8000.0,
  "perfil_investidor": "moderado",
  "objetivo_principal": "Construir reserva de emergência",
  "patrimonio_total": 15000.0,
  "reserva_emergencia_atual": 2900.0,
  "aceita_risco": false,
  "metas": [
    {
      "meta": "Completar reserva de emergência",
      "valor_necessario": 15000.0,
      "prazo": "2026-12"
    },
    {
      "meta": "Entrada do apartamento",
      "valor_necessario": 70000.0,
      "prazo": "2027-12"
    }
  ]
}

MATERIAL EDUCATIVO PARA O CLIENTE (data/material_educativo.json):

 {
  "versao": "1.2",
  "projeto": "Agente Lummi - Educação Financeira",
  "data_atualizacao": "2026-04-12",
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
        {
          "sigla": "Selic/CDI",
          "descricao": "Taxas que servem como referência para a renda fixa. A Selic é definida pelo Banco Central e o CDI acompanha de perto."
        },
        {
          "sigla": "IPCA",
          "descricao": "Índice oficial de inflação medido pelo IBGE. Usado para corrigir contratos e investimentos."
        },
        {
          "sigla": "Reserva de Emergência",
          "descricao": "Primeiro passo para quem começa a investir. Deve estar em aplicações seguras e com liquidez diária."
        },
        {
          "sigla": "FGC",
          "descricao": "Fundo Garantidor de Créditos. Protege depósitos e investimentos em bancos até R$ 250 mil por CPF e instituição."
        },
        {
          "sigla": "LCI/LCA",
          "descricao": "Letras de Crédito Imobiliário e do Agronegócio. Isentas de IR para pessoa física e garantidas pelo FGC."
        },
        {
          "sigla": "Tesouro Selic",
          "descricao": "Título público que acompanha a Selic. Ideal para reserva de emergência, com liquidez diária e baixo risco."
        },
        {
          "sigla": "Tesouro IPCA+",
          "descricao": "Título público que paga uma taxa fixa + inflação. Protege o poder de compra no longo prazo."
        },
        {
          "sigla": "CDB",
          "descricao": "Certificado de Depósito Bancário. Você empresta dinheiro ao banco e recebe rendimento atrelado ao CDI."
        },
        {
          "sigla": "Debêntures",
          "descricao": "Títulos emitidos por empresas para captar recursos. Podem render mais, mas têm risco maior que CDBs e Tesouro."
        },
        {
          "sigla": "Fundos de Investimento",
          "descricao": "Aplicações coletivas administradas por gestores. Podem ser de renda fixa, ações ou multimercado."
        },
        {
          "sigla": "Previdência Privada (PGBL/VGBL)",
          "descricao": "Planos de longo prazo voltados para aposentadoria. PGBL e VGBL são modalidades e o risco é definido pelo fundo escolhido."
        },
        {
          "sigla": "Bolsa de Valores (B3)",
          "descricao": "Principal mercado de negociação de ações e derivativos no Brasil. Permite investir em empresas e acompanhar índices como o Ibovespa."
        },
        {
          "sigla": "Fundo de Previdência Conservador",
          "descricao": "Tipo de fundo de investimento usado dentro de um plano de previdência privada (PGBL ou VGBL)."
        }
      ]
    },
    "alertas_educacionais": {
      "titulo": "Alertas Educacionais sobre Investimentos",
      "renda_variavel": {
        "nome": "Renda Variável",
        "o_que_e": "Investimentos cujo valor pode subir ou cair com frequência, conforme o comportamento do mercado.",
        "fatores_oscilacao": [
          "Situação da economia do Brasil e do mundo",
          "Resultados e decisões das empresas",
          "Clima do mercado"
        ],
        "indicado_para": [
          "Objetivos de médio e longo prazo",
          "Pessoas que lidam bem com variações"
        ]
      },
      "criptomoedas": {
        "nome": "Criptomoedas",
        "o_que_sao": "Ativos digitais com alta volatilidade, ou seja, seus preços podem mudar bastante em pouco tempo.",
        "caracteristicas": [
          "Não têm garantia do governo",
          "Não contam com proteção do FGC"
        ],
        "indicado_para": [
          "Pessoas com perfil mais arrojado"
        ]
      }
    },
    "tabela_resumo_previdencia": {
      "titulo": "Resumo: PGBL/VGBL x Fundo Conservador",
      "tabela": [
        {
          "conceito": "Conceito",
          "o_que_e": "O que é",
          "exemplo": "Exemplo"
        },
        {
          "conceito": "Previdência Privada",
          "o_que_e": "Estrutura legal e fiscal para acumular recursos no longo prazo.",
          "exemplo": "Contratar um VGBL."
        },
        {
          "conceito": "Fundo Conservador",
          "o_que_e": "Investimento dentro da Previdência, geralmente com maior peso em renda fixa.",
          "exemplo": "Selecionar renda fixa no VGBL."
        }
      ]
    },
    "perguntas_frequentes": {
      "titulo": "Perguntas frequentes (FAQ)",
      "itens": [
        {
          "pergunta": "Quando PGBL vale mais?",
          "resposta": "Geralmente na declaração completa do IR e contribuição para o INSS, permitindo deduzir até 12% da renda bruta."
        },
        {
          "pergunta": "Quando VGBL é indicado?",
          "resposta": "Na declaração simplificada ou quando já se atingiu o limite de dedução do PGBL."
        },
        {
          "pergunta": "Posso trocar de fundo?",
          "resposta": "Sim, na maioria dos planos é possível realizar a portabilidade interna entre fundos da mesma seguradora."
        }
      ]
    },
    "produtos_comparativo": {
      "cdb": {
        "nome": "CDB",
        "risco": "Baixo",
        "resumo": "Certificado de Depósito Bancário. Empréstimo ao banco com garantia do FGC."
      },
      "tesouro": {
        "nome": "Tesouro Direto",
        "risco": "Mínimo",
        "resumo": "Empréstimo ao Estado. Considerado o mais seguro do país."
      },
      "poupanca": {
        "nome": "Poupança",
        "risco": "Baixo",
        "resumo": "Tradicional e simples, mas com rendimento geralmente inferior a outras rendas fixas."
      },
      "lci_lca": {
        "nome": "LCI/LCA",
        "risco": "Baixo",
        "resumo": "Letras de Crédito isentas de IR para pessoa física e garantidas pelo FGC."
      },
      "debentures": {
        "nome": "Debêntures",
        "risco": "Médio",
        "resumo": "Títulos de dívida de empresas. Não possuem garantia do FGC."
      },
      "fundos_investimento": {
        "nome": "Fundos",
        "risco": "Variável",
        "resumo": "Aplicações coletivas com gestão profissional de terceiros."
      },
      "previdencia_privada": {
        "nome": "Previdência",
        "risco": "Variável",
        "resumo": "Foco em aposentadoria e planejamento sucessório de longo prazo."
      },
      "acoes_b3": {
        "nome": "Ações",
        "risco": "Alto",
        "resumo": "Participação como sócio em empresas listadas na bolsa de valores."
      },
      "fundos_imobiliarios": {
        "nome": "FIIs",
        "risco": "Médio",
        "resumo": "Investimento em ativos imobiliários para recebimento de aluguéis mensais."
      }
    },
    "catalogo_produtos": {
      "titulo": "Catálogo de Produtos Financeiros",
      "produtos": [
        {
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
          "aporte_minimo": 1000.00,
          "indicado_para": "Quem deseja acumular patrimônio para aposentadoria",
          "descricao": "Fundo voltado para aposentadoria, com foco em renda fixa e benefícios fiscais de longo prazo."
        },
        {
          "nome": "Conta Remunerada",
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
        },
        {
          "nome": "Fundo de Ações",
          "categoria": "fundo",
          "risco": "alto",
          "rentabilidade": "Variável:pois depende da valorização ou desvalorização das ações que compõem a carteira do fundo.",
          "aporte_minimo": 100.00,
          "indicado_para": "Perfil arrojado com foco no longo prazo, Pode ter ganhos expressivos no longo prazo, mas também oscilações negativas no curto prazo, não há garantia de rendimento mínimo, diferente dos produtos de renda fixa.",
          "descricao": "Fundo de investimento que aplica principalmente em ações de empresas listadas na bolsa de valores. O investidor participa dos ganhos e perdas do mercado acionário, com potencial de valorização, mas também com maior volatilidade."
        },
        {
          "nome": "Bolsa de Valores (B3)",
          "categoria": "renda_variável",
          "risco": "alto",
          "rentabilidade": "Variável. Depende da valorização das ações, distribuição de dividendos e desempenho do mercado. No longo prazo pode superar a renda fixa, mas com maior volatilidade.",
          "aporte_minimo": "Não há valor mínimo fixo. É possível investir a partir do preço de uma ação ou ETF (geralmente entre R$10 e R$100, dependendo do ativo)",
          "indicado_para": "Investidores com perfil moderado a arrojado, foco no longo prazo e tolerância a oscilações de mercado",
          "descricao": "A B3 é a bolsa de valores oficial do Brasil, onde são negociadas ações, ETFs, fundos imobiliários, BDRs, derivativos e outros ativos de renda variável. O investidor pode se tornar sócio de empresas, participar do crescimento econômico e obter ganhos por valorização e dividendos, assumindo riscos de mercado."
        },
        {
          "nome": "ETF (Exchange Traded Fund)",
          "categoria": "renda_variável",
          "risco": "médio a alto",
          "rentabilidade": "Variável. Acompanha o desempenho de um índice (ex: Ibovespa, S&P 500). Pode refletir ganhos ou perdas do mercado.",
          "aporte_minimo": "Corresponde ao preço de uma cota do ETF, geralmente entre R$10 e R$200",
          "indicado_para": "Quem busca diversificação, baixo custo e exposição ao mercado sem escolher ações individuais",
          "descricao": "Fundo negociado em bolsa que replica índices de mercado. Combina diversificação automática, transparência e liquidez diária, sendo muito utilizado em educação financeira e estratégias de longo prazo."
        },
        {
          "nome": "BDR (Brazilian Depositary Receipt)",
          "categoria": "renda_variável",
          "risco": "alto",
          "rentabilidade": "Variável. Depende da valorização do ativo no exterior e da variação cambial (dólar/real).",
          "aporte_minimo": "A partir do valor de uma unidade de BDR, geralmente entre R$20 e R$200",
          "indicado_para": "Investidores que desejam investir em empresas estrangeiras sem abrir conta no exterior",
          "descricao": "Certificado negociado na B3 que representa ações de empresas estrangeiras como Apple, Microsoft e Amazon, permitindo diversificação internacional com exposição ao câmbio."
        },
        {
          "nome": "Criptomoedas",
          "categoria": "ativos_digitais",
          "risco": "alto",
          "rentabilidade": "Altamente variável. Pode apresentar ganhos elevados ou perdas significativas em curto período.",
          "aporte_minimo": "Muito baixo. É possível investir a partir de R$1, dependendo da corretora",
          "indicado_para": "Perfil arrojado, com alta tolerância ao risco e foco em longo prazo",
          "descricao": "Ativos digitais descentralizados baseados em blockchain, como Bitcoin e Ethereum. Não possuem garantia governamental, apresentam alta volatilidade e são influenciados por fatores tecnológicos, regulatórios e de mercado global."
        }
      ]
    }
  }
}

RECEITAS E DESPESAS DO CLIENTE (exemplo de formato de dados - agora armazenados no banco de dados):
data,descricao,categoria,valor,tipo
2026-04-07 00:00:00.000000,1era quincena,salario,3500.0,entrada
2026-04-07 00:00:00.000000,Aluguel,moradia,1500.0,saida
2026-04-07 00:00:00.000000,Supermercado,alimentacao,1500.0,saida
2026-04-07 00:00:00.000000,Conta de Luz,moradia,660.0,saida
2026-04-07 00:00:00.000000,Escola,Educaçao filhos,1100.0,saida
2026-04-07 00:00:00.000000,Banco, Credito Santander,2400.0,Divida Banco
2026-04-07 00:00:00.000000,cartao loja,Riachuelo,0.0,Divida Loja
2026-04-18 00:00:00.000000,ingreso,renda extra,100.0,entrada
2026-04-29 00:00:00.000000,comida,alimentacao,500.0,saida
2026-04-30 00:00:00.000000,2da quincena 30-04,salario,3500.0,entrada
2026-05-01 00:00:00.000000,comida,alimentacao,500.0,saida
2026-05-01 00:00:00.000000,Robox para investir,lazer,60.0,saida
2026-05-01 00:00:00.000000,planta,alimentacao,15.0,saida
2026-05-01 00:00:00.000000,Robux,lazer,30.0,saida
2026-05-01 00:00:00.000000,lapiz,papeleria,5.0,saida
2026-05-01 00:00:00.000000,borrador,papeleria,10.0,saida
2026-05-01 18:25:01.110501,Pagamento de Divida Loja,Riachuelo,200.0,saida
2026-05-01 19:30:48.409359,Depósito Reserva de Emergência,Reserva de Emergência,500.0,saida

> **Obs:** Este arquivo CSV foi utilizado apenas para a migração inicial dos dados. A fonte da verdade atual é a tabela `Transacao` no PostgreSQL.

HISTORICO DE ATENDIMENTO DO CLIENTE (data/historico_atendimento.csv):
data,canal,tema,resumo,resolvido
2025-09-15,chat,CDB,Cliente perguntou sobre rentabilidade e prazos,sim
2025-09-22,telefone,Problema no app,Erro ao visualizar extrato foi corrigido,sim
2025-10-01,chat,Tesouro Selic,Cliente pediu explicação sobre o funcionamento do Tesouro Direto,sim
2025-10-12,chat,Metas financeiras,Cliente acompanhou o progresso da reserva de emergência,sim
2025-10-25,email,Atualização cadastral,Cliente atualizou e-mail e telefone,sim

```

## Exemplo de Contexto Montado

> Exemplo de como os dados são formatados para o agente.
> Contexto sintetizado da base de conhecimento, otimizado. Ele mantém apenas as
informações mais relevantes, reduzindo tokens sem perder conteúdo essencial:

```
Perfil do Cliente
•	Nome: Reyna Amada, 48 anos, Engenheiro de informática
•	Renda mensal: R$ 8.000,00
•	Perfil investidor: Moderado, não aceita risco
•	Objetivo principal: Construir reserva de emergência
•	Patrimônio total: R$ 15.000,00
•	Reserva atual: R$ 2.900,00
•	Metas:
o	Completar reserva de emergência: R$ 15.000,00 até 12/2026
o	Entrada do apartamento: R$ 70.000,00 até 12/2027

Material Educativo
•	Crédito e Dívidas: Juros compostos (efeito bola de neve), score de crédito, cadastro positivo.
•	Investimentos:
o	Selic/CDI → base da renda fixa
o	IPCA → inflação oficial
o	Reserva de Emergência → liquidez diária
•	Produtos comparativos:
o	CDB → baixo risco, FGC, rende CDI
o	Tesouro Direto → risco mínimo, acessível a partir de R$30
•	Tesouro Selic → baixo risco, liquidez diária, ideal para reserva de emergência
•	Tesouro IPCA+ → protege contra inflação, longo prazo
•	CDB Liquidez Diária → baixo risco, 102% CDI, resgate rápido
•	LCI/LCA → baixo risco, isentos de IR, aporte mínimo R$1.000
•	Fundo DI → baixo risco, acompanha CDI
•	Poupança → liquidez imediata, rendimento inferior
•	Debêntures Incentivadas → médio risco, 12–15% a.a., isentas de IR
•	Fundos multimercado/ações → risco médio/alto, maior potencial de retorno

Receitas e Despesas (último registro)
•	Receita: Salários e Renda Extra R$ 7.100,00
•	Despesas:
o	Moradia: R$ 2.160,00 (aluguel + luz)
o	Alimentação: R$ 2.515,00 (supermercado + refeições + planta)
o	Educação filhos: R$ 1.100,00
o	Dívidas (Banco): R$ 2.400,00 (Crédito Santander)
o	Lazer / Outros: R$ 120,00 (Robux + Papelaria)
o	Depósitos/Pagamentos: R$ 700,00 (Pagamento de Dívida + Depósito Reserva)
•	Saldo líquido aproximado: negativo (-R$ 1.880,00)



```
