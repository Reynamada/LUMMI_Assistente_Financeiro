# 🛠️ Plataformas, APIs e Bibliotecas do LUMMI
> Resumo detalhado de cada tecnologia usada, seu papel e por que foi escolhida.

---

## 🎯 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│  USUÁRIO  →  Streamlit (UI)  →  Lógica (app.py / skills.py)    │
│                    ↓                    ↓                        │
│              PostgreSQL/Neon      OpenRouter (IA)               │
│                                         ↓                        │
│              BrasilAPI ← Fallback → BCB/SGS → PTAX              │
│              AwesomeAPI (câmbio)                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ CAMADA DE INTERFACE

### 1. Streamlit
| | |
|---|---|
| **Site** | [streamlit.io](https://streamlit.io) |
| **Tipo** | Framework web Python |
| **Custo** | Gratuito (open source) |
| **Deploy** | Streamlit Community Cloud (gratuito) |

**Por que foi escolhido:**
- Permite construir uma aplicação web completa **100% em Python**, sem HTML/CSS/JavaScript
- Ideal para dashboards financeiros com gráficos, métricas e chat em uma única interface
- `@st.cache_data` permite cachear chamadas de API automaticamente — chave para a performance
- `st.session_state` mantém o estado do chat e dados do usuário entre interações sem banco adicional
- Deploy gratuito e integrado com GitHub (qualquer push publica a nova versão automaticamente)

**Usado em:** `src/app.py`, `src/skills.py`

---

## 🧠 CAMADA DE INTELIGÊNCIA ARTIFICIAL

### 2. OpenRouter
| | |
|---|---|
| **Site** | [openrouter.ai](https://openrouter.ai) |
| **Tipo** | Gateway de modelos LLM (API unificada) |
| **Autenticação** | Bearer Token (armazenado em secrets) |
| **Protocolo** | Compatível com API OpenAI (`/chat/completions`) |
| **Custo** | Pago por token (modelos gratuitos disponíveis) |

**Por que foi escolhido:**
- Funciona como um **"roteador de IA"**: permite acessar dezenas de modelos (OpenAI, Anthropic, Google, Meta, NVIDIA) com **uma única chave de API e um único endpoint**
- Se um modelo estiver indisponível ou com rate-limit, o sistema tenta o próximo automaticamente (**fallback de modelos**)
- Permite trocar o modelo sem mudar o código — apenas muda a string do nome
- Controle de custo: é possível usar modelos gratuitos (`:free`) em desenvolvimento e modelos pagos em produção

**Modelos em uso:**
| Modelo | Papel |
|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | Modelo primário (padrão) |
| Fallbacks configurados em `app.py` | Acionados automaticamente em caso de erro 429 ou timeout |

**Usado em:** `src/config.py`, `src/app.py`

---

## 🗄️ CAMADA DE PERSISTÊNCIA

### 3. PostgreSQL (via Neon.tech)
| | |
|---|---|
| **Site** | [neon.tech](https://neon.tech) |
| **Tipo** | Banco de dados relacional serverless |
| **Custo** | Gratuito (plano Free: 0.5 GB) |
| **Protocolo** | `postgresql://` via psycopg2 |

**Por que foi escolhido:**
- Armazena todas as transações financeiras, perfil do usuário, metas, dívidas e tipos de transação de forma **persistente e estruturada**
- Neon é um PostgreSQL **serverless** — escala automaticamente e não precisa de servidor dedicado
- Integra diretamente com Streamlit Cloud via `st.secrets` (sem expor credenciais no código)
- Suporte a múltiplos acessos simultâneos sem corrupção de dados (ACID compliant)

**Tabelas principais:**
| Tabela | Conteúdo |
|---|---|
| `Transacao` | Todas as receitas e despesas com data, valor, categoria |
| `Perfil` | Dados do usuário: nome, renda, perfil de investidor, metas |
| `Meta` | Metas financeiras com valor objetivo e progresso |
| `TipoTransacao` | Categorias dinâmicas (CRUD pelo usuário) |

**Usado em:** `src/database.py`, `src/agente.py`

### 4. SQLAlchemy
| | |
|---|---|
| **Tipo** | ORM (Object-Relational Mapper) Python |
| **Custo** | Gratuito (open source) |

**Por que foi escolhido:**
- **Abstrai o banco de dados**: o código Python trabalha com objetos, não com SQL bruto — mais seguro (evita SQL Injection) e mais legível
- **Migrations idempotentes**: cria ou atualiza tabelas sem quebrar um banco que já existe
- Permite trocar o banco de dados (de PostgreSQL para SQLite, por exemplo) mudando apenas a string de conexão

**Usado em:** `src/database.py`, `src/agente.py`

---

## 📡 CAMADA DE DADOS DE MERCADO

> Estratégia de **resiliência em 3 camadas** — sem ponto único de falha.

### 5. BrasilAPI — Fonte Primária de Taxas
| | |
|---|---|
| **Site** | [brasilapi.com.br](https://brasilapi.com.br) |
| **Endpoint** | `GET /api/taxas/v1` |
| **Tipo** | API open source brasileira |
| **Autenticação** | Nenhuma |
| **Custo** | Gratuito |
| **Cache LUMMI** | `@st.cache_data(ttl=3600)` — 1 hora |

**Por que foi escolhido:**
- **1 única requisição HTTP** retorna SELIC, CDI e IPCA — mais eficiente que fazer chamadas separadas
- Tem **CDN global** com cache próprio — resposta em ~200ms contra 2-5s do BCB direto
- Open source, mantido pela comunidade brasileira, confiável e sem rate-limit agressivo
- Agrega dados do BCB oficialmente, então os dados têm a mesma fonte de verdade

**Dados retornados:**
```json
[
  { "nome": "SELIC",  "valor": 14.5  },
  { "nome": "CDI",    "valor": 14.4  },
  { "nome": "IPCA",   "valor": 4.39  }
]
```

### 6. BCB / SGS (Banco Central do Brasil) — Fallback de Taxas + Câmbio PTAX
| | |
|---|---|
| **Site** | [api.bcb.gov.br](https://api.bcb.gov.br) |
| **Endpoint** | `GET /dados/serie/bcdata.sgs.{código}/dados/ultimos/{N}` |
| **Tipo** | API oficial do governo brasileiro |
| **Autenticação** | Nenhuma (pública) |
| **Custo** | Gratuito |
| **Cache LUMMI** | `@st.cache_data(ttl=3600)` — 1 hora |

**Por que foi escolhido:**
- É a **fonte oficial** dos dados financeiros do Brasil — os dados do BCB são os mais autoritativos
- Acionado automaticamente quando a BrasilAPI falha (rate-limit, CDN issue)
- Usado para série específica da poupança (código `196`) e TR (código `226`) para calcular o rendimento real
- Para câmbio, fornece USD PTAX (série `10813`) e EUR PTAX (série `21619`) como terceira camada de fallback

**Códigos SGS usados:**
| Código | Indicador | Periodicidade |
|---|---|---|
| `432` | Taxa SELIC Meta (a.a.) | Mensal |
| `196` | Rendimento Poupança (a.m.) | Mensal |
| `226` | Taxa Referencial — TR (a.m.) | Mensal |
| `433` | IPCA (a.m.) | Mensal |
| `189` | IGP-M (a.m.) | Mensal |
| `10813` | Dólar PTAX (USD/BRL) | Diário |
| `21619` | Euro PTAX (EUR/BRL) | Diário |

> [!IMPORTANT]
> O LUMMI usa `/ultimos/{N}` — busca apenas os N registros necessários, **nunca** o endpoint `/dados` sem filtro (que baixaria décadas de histórico completo).

### 7. AwesomeAPI — Câmbio em Tempo Real (Primário)
| | |
|---|---|
| **Site** | [economia.awesomeapi.com.br](https://economia.awesomeapi.com.br) |
| **Endpoint** | `GET /last/USD-BRL,EUR-BRL` |
| **Tipo** | API de câmbio gratuita |
| **Autenticação** | Nenhuma |
| **Custo** | Gratuito |
| **Cache LUMMI** | `@st.cache_data(ttl=1800)` — 30 minutos |

**Por que foi escolhido:**
- Retorna cotação do dólar e euro em **tempo real** (dados do mercado, não PTAX de fechamento)
- **Zero burocracia**: sem cadastro, sem chave de API, sem limite de plano
- Inclui `pctChange` (variação % do dia) — informação que o BCB PTAX não fornece de forma fácil
- Cache de 30min (menor que as taxas de 1h) porque câmbio muda mais frequentemente

**Dados retornados:**
```json
{
  "USDBRL": { "bid": "5.78", "pctChange": "-0.32", "create_date": "2026-06-07 17:00:00" },
  "EURBRL": { "bid": "6.41", "pctChange": "+0.12", "create_date": "2026-06-07 17:00:00" }
}
```

---

## 📄 CAMADA DE EXPORTAÇÃO

### 8. ReportLab
| | |
|---|---|
| **Tipo** | Biblioteca Python para geração de PDF |
| **Custo** | Gratuito (open source) |

**Por que foi escolhido:**
- Gera PDFs **100% programaticamente** em Python, sem dependência de browsers ou ferramentas externas
- Suporta layout complexo: tabelas, cores, logotipo, cabeçalhos, rodapés — o relatório do LUMMI é um PDF profissional formatado em A4
- Compatível com Streamlit Cloud (sem necessidade de instalar software externo)
- O PDF é gerado **em memória** (bytes) e disponibilizado como download direto, sem salvar arquivo no servidor

**Usado em:** `src/skills.py` — função `gerar_relatorio_pdf()`

---

## ⚙️ BIBLIOTECAS DE SUPORTE

### 9. Pandas
**Papel:** Processamento e manipulação de dados financeiros

- Converte os dados das APIs de mercado (JSON → DataFrame) para manipulação
- Calcula saldos, filtros por mês, agrupamentos por categoria
- Base de todos os gráficos e tabelas exibidas no dashboard

### 10. NumPy
**Papel:** Cálculos numéricos de alta performance

- Suporte interno ao Pandas para operações vetorizadas
- Usado implicitamente em conversões de tipos e cálculos de percentual

### 11. Requests
**Papel:** Chamadas HTTP para todas as APIs externas

- Faz todas as requisições à BrasilAPI, BCB e AwesomeAPI
- Configurado com `timeout` em todos os pontos para evitar travamentos
- Exceções específicas (`RequestException`) tratadas em cada chamada

### 12. psycopg2-binary
**Papel:** Driver de conexão Python ↔ PostgreSQL

- Camada de baixo nível usada pelo SQLAlchemy para se comunicar com o banco PostgreSQL/Neon
- `-binary` = versão pré-compilada, sem dependências de sistema (ideal para cloud)

---

## 🔐 GERENCIAMENTO DE SEGREDOS

### 13. Streamlit Secrets (`.streamlit/secrets.toml`)
**Papel:** Armazenamento seguro de credenciais

| Variável | O que armazena |
|---|---|
| `DATABASE_URL` | String de conexão PostgreSQL (Neon) |
| `OPENROUTER_API_KEY` | Chave Bearer para a API de IA |
| `APP_USER` | Login de acesso ao LUMMI |
| `APP_PWD` | Senha de acesso ao LUMMI |

- Em desenvolvimento local: lido do arquivo `.streamlit/secrets.toml` (não versionado no git)
- Em produção (Streamlit Cloud): configurado via painel web da plataforma, **nunca exposto no código**

---

## 📊 Resumo Comparativo

| Tecnologia | Tipo | Custo | Autenticação | Papel no LUMMI |
|---|---|---|---|---|
| **Streamlit** | Framework UI | Gratuito | — | Interface web + Deploy |
| **OpenRouter** | Gateway LLM | Pago/Free | Bearer Token | Inteligência Artificial |
| **PostgreSQL/Neon** | Banco de dados | Gratuito | URL + senha | Persistência de dados |
| **SQLAlchemy** | ORM Python | Gratuito | — | Abstração do banco |
| **BrasilAPI** | API de mercado | Gratuito | Nenhuma | Taxas (primário) |
| **BCB/SGS** | API governamental | Gratuito | Nenhuma | Taxas (fallback) + Histórico |
| **AwesomeAPI** | API de câmbio | Gratuito | Nenhuma | USD/EUR (primário) |
| **ReportLab** | Geração PDF | Gratuito | — | Relatórios exportáveis |
| **Pandas** | Análise de dados | Gratuito | — | Processamento financeiro |
| **Requests** | HTTP client | Gratuito | — | Comunicação com APIs |

> [!NOTE]
> Das 10 tecnologias principais, **9 são completamente gratuitas**. O único custo real é o uso do OpenRouter — e mesmo esse oferece modelos gratuitos (`:free`) para desenvolvimento e demonstração.

---

## 🔄 Fluxo Completo de uma Pergunta sobre Taxas

```
Usuário digita: "Quanto rende a poupança hoje?"
         ↓
app.py detecta keyword "poupança" no texto
         ↓
Chama consultar_indicadores_economicos_br() [skills.py]
         ↓
  ┌─ _buscar_taxas_brasilapi() ─ BrasilAPI ─ ✅ retorna SELIC 14.5%
  │         [se falhar]
  └─ _buscar_taxas_bcb() ─ BCB/SGS série 432 ─ retorna SELIC
              ↓
  _calcular_rendimento_poupanca(14.5, tr=0.0) = 0.5% a.m.
         ↓
Dados injetados no System Prompt do OpenRouter
         ↓
IA responde: "A poupança rende 0.5% a.m. + TR. Com SELIC em 14.5%..."
         ↓
Usuário vê resposta baseada em dados reais ✅
```
