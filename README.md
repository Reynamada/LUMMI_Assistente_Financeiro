<div align="center">

<img src="assets/screenshots/LOGOlummi.jpg" alt="LUMMI Logo" width="180" />

# LUMMI — Inteligência Financeira Pessoal com IA

**Assistente financeiro conversacional com IA generativa, análise de dados em tempo real e dashboards inteligentes.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Cloud-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM_Gateway-7C3AED?style=for-the-badge)](https://openrouter.ai/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 🧠 O que é o LUMMI?

**LUMMI** é uma aplicação de **inteligência financeira pessoal** que combina análise de dados financeiros, automação de alertas e um assistente de IA conversacional — tudo em uma única interface web construída com Python e Streamlit.

O projeto foi desenvolvido como parte do laboratório **BIA do Futuro** (DIO — Digital Innovation One) e demonstra a aplicação prática de **LLMs em produção**, integração com **APIs financeiras reais**, persistência em **banco de dados cloud** e design de **produto de software orientado ao usuário final**.

---

## ✨ Funcionalidades Principais

### 💬 Assistente de IA Conversacional (LUMMI)
- Chat em linguagem natural com **contexto financeiro personalizado** do usuário
- Detecção automática de intenção para acionar **skills especializadas**
- Prompt engineering avançado com dados reais de perfil, metas e transações
- Sistema de **fallback de modelos** para garantir alta disponibilidade
- Histórico de atendimento persistido no banco de dados, carregado **diariamente** (não por sessão)

### 📊 Dashboard Financeiro Dinâmico
- Saldo acumulado com cálculo histórico progressivo
- Resumo por tipo e categoria de transação (dinâmico)
- Filtro por mês com métricas de entrada, saída e saldo líquido

### 🎯 Gestão de Metas & Reserva de Emergência (Sidebar)
- **Seletor de Metas Unificado**: Painel integrado na sidebar para acompanhar a Reserva de Emergência e metas personalizadas do usuário.
- **Depósitos em Tempo Real**: Botão "Depositar" que transfere valores do saldo acumulado diretamente para a meta selecionada (com desconto imediato no saldo e registro da transação).
- **Edição & Exclusão Flexíveis**: Permite editar a descrição, o valor objetivo e o prazo final de qualquer meta, além de excluir metas personalizadas (a Reserva de Emergência é protegida contra exclusão).
- **Criação de Novas Metas**: Formulário intuitivo diretamente na barra lateral para registrar novos objetivos de forma instantânea.
- Conquistas com 🎉 banner de comemoração ao atingir 100% do objetivo da meta.

### 📈 Resumo Financeiro Interativo & Ações Rápidas (Sidebar)
- **Dívidas Inteligentes**: Controle de saldos restantes de dívidas cadastrados (ex: Banco, Loja) e exibição de itens pendentes detalhados com status dinâmico (indicação de quitação total).
- **Gastos Recorrentes (`saida mensal`)**: Acompanhamento visual com status **🔴 Pendente** / **🔵 Efetuado**, cálculo de dias restantes para o vencimento ou aviso de atraso e o botão integrado `💳 Pagar` para quitar a fatura com débito automático no saldo do mês selecionado.
- **Edição Dinâmica de Rótulos**: Opção para renomear os rótulos de tipos de transação diretamente no resumo.
- **Alteração Estrutural de Tipos**: Expander dedicado com CRUD completo para adicionar novos tipos (gerando chaves internas automaticamente), editar rótulos ou excluir tipos que não tenham registros vinculados.

### 📥 Exportação de Relatórios Inteligentes (Sidebar)
- 📊 **Planilha Excel**: Geração rápida de arquivos `.xlsx` contendo o extrato completo de transações e o resumo financeiro mensal.
- 📄 **Relatório PDF Profissional (LUMMI)**: Nova funcionalidade na sidebar que utiliza a biblioteca `reportlab` para construir um relatório estruturado em formato A4, contendo:
  - Cabeçalho personalizado com a logomarca da **LUMMI** e metadados do relatório.
  - Tabela consolidada de indicadores e KPIs (Saldo total, saídas, entradas, dívidas e reserva).
  - Resumo de gastos categorizados do mês selecionado.
  - Dados cadastrais do perfil do usuário.
  - Extrato detalhado completo das transações com realce de cor condicional (verde para entradas, vermelho para saídas/despesas comuns e amarelo para dívidas).

### 📅 Alertas de Vencimento
- Skill `exibir_alertas_vencimento` detecta contas vencidas, vencendo hoje e **1 dia antes do vencimento**
- Integra dívidas cadastradas e gastos recorrentes em uma única visão

### 📈 Indicadores de Mercado em Tempo Real
- Consulta à **API oficial do Banco Central do Brasil (SGS/BCB)** com `User-Agent` correto
- Taxas: SELIC, Poupança (a.m.), IPCA e IGP-M sempre atualizadas
- Cotações de câmbio USD e EUR via AwesomeAPI
- Integradas ao contexto do assistente: ao perguntar sobre "poupança" ou "SELIC", o LUMMI busca os dados reais e os usa na resposta

### 🔧 Tipos de Transação Dinâmicos
- CRUD completo de tipos diretamente no banco de dados
- Adição, renomeação e exclusão sem reinicialização da aplicação
- Resumo Financeiro atualizado automaticamente com novos tipos

### 👤 Gestão de Perfil
- Edição de dados cadastrais no sidebar
- Campo `data_nascimento` com **cálculo automático de idade** no momento de salvar
- Metas financeiras com rastreamento e barra de progresso

---

## 🏗️ Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                       Frontend (Streamlit)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │   Sidebar   │  │  Dashboard   │  │    Chat LUMMI IA    │  │
│  │  (Gestão)   │  │  Financeiro  │  │  (Skills + LLMs)   │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬────────────┘  │
└─────────┼────────────────┼───────────────────┼───────────────┘
          │                │                   │
┌─────────▼────────────────▼───────────────────▼───────────────┐
│                      Camada de Lógica                         │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────────────────┐  │
│  │ agente.py│  │  skills.py  │  │       config.py          │  │
│  │ (CRUD +  │  │ (IA Skills  │  │   (Auth + Modelos)       │  │
│  │  Perfil) │  │  + Mercado) │  │                          │  │
│  └────┬─────┘  └──────┬──────┘  └──────────────────────────┘  │
└───────┼───────────────┼──────────────────────────────────────┘
        │               │
┌───────▼───────────────▼──────────────────────────────────────┐
│                   Camada de Dados                             │
│  ┌────────────────────┐       ┌──────────────────────────┐   │
│  │   PostgreSQL Cloud │       │   APIs Externas          │   │
│  │  (SQLAlchemy ORM)  │       │  • BCB/SGS (SELIC/IPCA)  │   │
│  │  • transacoes      │       │  • AwesomeAPI (Câmbio)   │   │
│  │  • perfil          │       │  • OpenRouter (LLMs)     │   │
│  │  • chat_history    │       └──────────────────────────┘   │
│  │  • tipo_transacao  │                                       │
│  └────────────────────┘                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 🤖 Modelos de IA Utilizados

| Modelo | Provedor | Função | Tier |
|---|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b` | NVIDIA | Assistente principal de IA | Gratuito |
| `nvidia/nemotron-3-nano-30b-a3b` | NVIDIA | Fallback de alta disponibilidade | Gratuito |

**Gateway:** [OpenRouter.ai](https://openrouter.ai) — roteamento inteligente com fallback automático entre modelos.

**Técnicas de Prompt Engineering aplicadas:**
- System prompt dinâmico com dados financeiros reais do usuário
- Injeção de contexto situacional (mês selecionado, saldo, metas)
- Detecção de intenção por palavras-chave para acionamento de skills
- Injeção de dados de mercado em tempo real no contexto da resposta
- Rate limit handling com retry e cooldown de 10 segundos

---

## 🗄️ Banco de Dados

**PostgreSQL** (hospedado via Neon.tech / Supabase / Railway — configurável via `secrets.toml`)

### Esquema de Tabelas

| Tabela | Descrição | Colunas Principais |
|---|---|---|
| `transacoes` | Lançamentos financeiros | `id, data, descricao, categoria, valor, tipo, dia_vencimento` |
| `perfil` | Dados cadastrais do usuário (JSON) | `id, dados_json` |
| `chat_history` | Histórico de conversas com a IA | `id, role, content, skill, data_hora` |
| `tipo_transacao` | Tipos dinâmicos de transação | `id, chave, rotulo` |

**Estratégia de migração:** `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` executado em blocos `try/except` individuais por coluna, garantindo idempotência em qualquer estado do banco.

---

## 🔌 APIs e Integrações

| API | Endpoint | Dados | Autenticação |
|---|---|---|---|
| Banco Central Brasil (SGS) | `api.bcb.gov.br` | SELIC, IPCA, Poupança, IGP-M | Pública |
| AwesomeAPI Câmbio | `economia.awesomeapi.com.br` | USD/BRL, EUR/BRL | Pública |
| OpenRouter | `openrouter.ai/api/v1` | LLM Chat Completions | Bearer Token |

---

## 📁 Estrutura do Projeto

```
dio-lab-bia-do-futuro/
├── src/
│   ├── app.py            # Aplicação principal Streamlit (frontend + orquestração)
│   ├── agente.py         # CRUD de transações, perfil e tipos (SQLAlchemy)
│   ├── database.py       # Modelos ORM, init_db(), migrações e session factory
│   ├── skills.py         # Skills da IA: diagnóstico, metas, simulador, alertas, mercado e relatório PDF
│   └── config.py         # Autenticação, caminhos e configurações de modelos
├── data/
│   ├── material_educativo.json   # Conteúdo educativo para o assistente
│   ├── perfil_investidor.json    # Perfil padrão (migrado automaticamente para o DB)
│   └── receitas_despesas.csv     # Dados históricos (migrado automaticamente para o DB)
├── assets/
│   └── screenshots/              # Logo e imagens da aplicação
├── .streamlit/
│   └── secrets.toml              # DATABASE_URL, OPENROUTER_API_KEY, credenciais
├── requirements.txt
└── README.md
```

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.12+
- Conta no [OpenRouter](https://openrouter.ai) (gratuita)
- Banco PostgreSQL (recomendamos [Neon.tech](https://neon.tech) — plano gratuito)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/Reynamada/dio-lab-bia-do-futuro.git
cd dio-lab-bia-do-futuro

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate   # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as credenciais
```

Crie o arquivo `.streamlit/secrets.toml`:

```toml
DATABASE_URL = "postgresql://......."
OPENROUTER_API_KEY = "sk-or-v1-..."
APP_USER = "admin"
APP_PWD = "sua_senha_segura"
```

```bash
# 5. Execute a aplicação
streamlit run src/app.py
```

---

## 🧩 Skills do Assistente LUMMI

| Keyword de Ativação | Skill | Descrição |
|---|---|---|
| `meta`, `objetivo`, `rastreador` | `exibir_rastreador_metas` | Progresso visual das metas financeiras |
| `simulador`, `investir`, `rendimento` | `exibir_simulador_investimentos` | Simulação de investimentos em renda fixa |
| `orçamento`, `diagnóstico`, `gasto` | `exibir_diagnostico_financeiro` | Análise de saúde financeira do mês |
| `motiva`, `inspiração`, `ajuda` | `exibir_motivacao` | Mensagem motivacional personalizada |
| `vencimento`, `fatura`, `pagar` | `exibir_alertas_vencimento` | Alertas de contas próximas do vencimento |
| `selic`, `poupança`, `ipca`, `taxa` | `consultar_indicadores_economicos_br` | Dados reais do Banco Central em tempo real |

---

## 📐 Decisões Técnicas e Padrões

- **ORM com SQLAlchemy:** Abstração total do banco de dados, facilitando troca de provider sem refatoração
- **Migrations idempotentes:** Suporte a bancos em qualquer estado sem quebrar o deploy
- **Session State isolado por data:** Histórico de chat carregado 1x/dia, não por sessão — evita poluição de contexto
- **Tipos dinâmicos no banco:** Lista de categorias de transação gerenciada pelo próprio banco, não por arquivo estático
- **Saldo historicamente correto:** Depósitos na Reserva de Emergência são excluídos dos cálculos de "saídas" para não duplicar o desconto no saldo
- **Prompt contextual:** Cada requisição à IA carrega saldo, histórico do mês, metas e dados de mercado — sem alucinações sobre os dados do usuário

---

## 📊 Métricas do Projeto

| Métrica | Valor |
|---|---|
| Linhas de código (src/) | ~1.800 |
| Arquivos Python | 5 |
| Tabelas no banco | 4 |
| Skills de IA implementadas | 6 |
| APIs externas integradas | 3 |
| Modelos LLM com fallback | 2 |
| Cobertura de tipos de transação | Ilimitada (CRUD dinâmico) |

---

## 🛠️ Stack Tecnológica

```
Backend / Lógica:    Python 3.12 · SQLAlchemy · Pandas · Requests
Frontend:            Streamlit 1.45
Banco de Dados:      PostgreSQL (cloud) via SQLAlchemy ORM
IA / LLMs:           OpenRouter API · NVIDIA Nemotron (120B + 30B)
APIs Financeiras:    Banco Central do Brasil (BCB/SGS) · AwesomeAPI
Autenticação:        Sistema próprio com hash SHA-256
Deploy:              Streamlit Community Cloud / Qualquer server Python
Ambiente:            Python venv · secrets.toml
```

---

## 👩‍💻 Sobre a Autora

Desenvolvido por **Reyna Amada** como projeto de conclusão do laboratório **BIA do Futuro** — DIO (Digital Innovation One).

Este projeto demonstra capacidade em:
- Desenvolvimento de aplicações web completas com Python
- Integração e orquestração de LLMs em produção
- Design de banco de dados relacional com ORM
- Prompt engineering e detecção de intenção
- Integração com APIs financeiras reais
- Experiência do usuário e produto de software

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">

**⭐ Se este projeto foi útil ou inspirador, deixe uma estrela!**

*Construído com 💙 e muita determinação financeira.*

</div>
