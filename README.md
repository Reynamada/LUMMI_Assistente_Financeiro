# 💰 LUMMI - Agente Financeiro Inteligente

## 🌟 Contexto

O **LUMMI** é um assistente financeiro consultivo desenvolvido para transformar a gestão de finanças pessoais. Ele supera a limitação das planilhas estáticas ao utilizar IA Generativa para oferecer análises de gastos em tempo real, educação financeira personalizada e sugestões baseadas no perfil de investidor do utilizador.

Este projeto foi construído focando em três pilares:

1. **Educação:** Desmistificar termos financeiros e taxas brasileiras (Selic, CDI, IPCA).
2. **Visibilidade:** Diferenciar claramente gastos recorrentes (parcelas) de gastos pontuais (à vista).
3. **Segurança:** Utilizar bases de conhecimento locais (Grounding) para evitar alucinações da IA.

<<<<<<< HEAD
=======
[Documentaçao](docs/01-documentacao-agente.md)

>>>>>>> 645c73d4ef02ac9271c983103a244c0691fa68ef
---

## 🚀 Decisões Tecnológicas e Diferenciais

* **OpenRouter API:** Integração com modelos de linguagem de última geração através de uma única interface, garantindo que a inteligência do LUMMI seja modular e de ponta.
* **Ambiente Virtual (venv):** Uso de ambientes isolados para garantir que o projeto seja executado com as versões exatas de suas dependências, evitando conflitos de sistema.
* **Arquitetura Profissional (src/):** Separação clara entre a interface (app.py), as configurações (config.py) e a lógica de processamento de dados (agente.py).
* **Métricas Inteligentes:** Separação automática de saídas "à vista" e "parceladas" para uma visão real do comprometimento da renda mensal.

---

## 🏗️ Estrutura do Repositório

```text
📁 LUMMI/
│
├── 📄 README.md              # Documentação principal e decisões técnicas
├── 📄 requirements.txt       # Dependências (Streamlit, Pandas, Requests)
├── 📄 .gitignore             # Ficheiro para ignorar o venv e temporários
│
├── 📁 data/                  # Base de conhecimento e persistência
│   ├── perfil_investidor.json   # Dados do perfil do utilizador
│   ├── material_educativo.json  # Dicionário e regras de negócio
│   └── receitas_despesas.csv    # Histórico dinâmico de transações
│
└── 📁 src/                   # Código-fonte da aplicação
    ├── __init__.py           # Inicializador de pacote Python
    ├── app.py                # Interface visual e Chat (Streamlit)
    ├── agente.py             # Lógica do agente e manipulação de dados
    └── config.py             # Chaves de API e caminhos do sistema
```

## 🛠️ Como Executar

### 1. Preparar o Ambiente:

```
Bash
python -m venv venv
```

### 2. Ativar o Ambiente:

```
Windows: .\venv\Scripts\activate
Mac/Linux: source venv/bin/activate
```

### 3. Instalar Dependências:

```
Bash
pip install -r requirements.txt
```

### 4.Lançar o Agente:

```
Bash
streamlit run src/app.py
```

# Funcionalidades do Agente LUMMI


| Funcionalidade             | Descrição                                                                       |
| -------------------------- | --------------------------------------------------------------------------------- |
| Consultoria de Gastos      | IA que analisa o saldo atual e sugere ajustes baseados no histórico real.        |
| Diferenciação de Saídas | Métricas separadas no sidebar para controle de parcelas vs. gastos à vista.     |
| Anti-Alucinação          | Respostas baseadas estritamente em ficheiros locais de conhecimento (Grounding).  |
| Persistência de Dados     | Cadastro de novas transações que atualizam o contexto do chat instantaneamente. |

## 🛡️ Segurança e Confiabilidade

<<<<<<< HEAD
O LUMMI utiliza o conceito de Grounding para garantir que as informações sobre investimentos e juros sejam precisas. O sistema de prompt instrui o agente a consultar os dados locais de transações e perfis antes de responder, garantindo uma consultoria baseada em factos.
=======
O LUMMI utiliza o conceito de Grounding para garantir que as informações sobre investimentos e juros sejam precisas. O sistema de prompt instrui o agente a consultar os dados locais de transações e perfis antes de responder, garantindo uma consultoria baseada em fatos.o LUMMI traduz o "economês" para o usuário, explicando de forma didática e transparente conceitos cruciais como FGC, LCI/LCA e Tesouro Selic, garantindo que cada decisão seja tomada com plena consciência e autonomia.
>>>>>>> 645c73d4ef02ac9271c983103a244c0691fa68ef

## 👩‍💻 Desenvolvido por

Reyna Amada Dongoroz– Digital Entrepreneur & AI Student.
Projeto desenvolvido para o Bootcamp Bradesco - GenAI & Dados / DIO
