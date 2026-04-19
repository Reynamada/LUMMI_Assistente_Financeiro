# Código da Aplicação

Esta pasta contém o código do seu agente financeiro.

## Estrutura Sugerida

```
└── 📁 src/                   # Código-fonte da aplicação
    ├── __init__.py           # Inicializador de pacote Python
    ├── app.py                # Interface visual e Chat (Streamlit)
    ├── agente.py             # Lógica do agente e manipulação de dados
    └── config.py             # Chaves de API e caminhos do sistema
```

## requirements.txt

```
 # Dependências isoladas via venv para garantir a integridade do projeto
   streamlit
   pandas
   requests
```

## Como Rodar

### 1. Preparar o Ambiente:
```
Bash
python -m venv venv
```

### 2. Ativar o Ambiente:
```
Windows: .\venv\Scripts\activate
```

### 3. Instalar Dependências:
```
Bash
pip install -r requirements.txt
#No arquivo requerimentos se encontra:
 # Dependências isoladas via venv para garantir a integridade do projeto
   streamlit
   pandas
   requests
```

### 4.Lançar o Agente:
```
Bash
streamlit run src/app.py
```

```
