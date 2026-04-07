# Base de Conhecimento

## Dados Utilizados

Descreva se usou os arquivos da pasta `data`, por exemplo:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores |
| `perfil_investidor.json` | JSON | Personalizar recomendações |
| `produtos_financeiros.json` | JSON | Sugerir produtos adequados ao perfil |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente |

> [!TIP]

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

[Seguindo a mesma estrutura e atributos, adicione outros produtos: FII - Fundo Imobiliário, Fundo DI (Depósito Interfinanceiro), Tesouro IPCA+(Índice de Preços ao Consumidor Amplo), Poupança, Debêntures Incentivadas, Fundo de Previdência Conservador, Conta Remunerada, Caixinha Digital.
Coloquei por separado os produtos: LCI e LCA, já que tem significado diferentes. Adicione a cada um dos produtos um atributo: Descrição.

Atualizei o perfil de investidor com dados autênticos, preenchendo cada atributo devidamente para refletir um cenário real.
No archivo de transações, modifiquei alguns valores e descrição de despesas e adicione escola e banco, com seus respectivos atributos preenchidos.
]

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

[ex: Os JSON/CSV são carregados no início da sessão e incluídos no contexto do prompt]

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

[Sua descrição aqui]

---

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
