# Base de Conhecimento

## Dados Utilizados


| Arquivo | Formato | Para que serve no Lummi |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores, ou seja, dar continuidade ao atendimento de forma mais eficiente.  |
| `perfil_investidor.json` | JSON | Personalizar as explicaçoes sobre as duvidas e necessidades de aprendizado do client. |
| `produtos_financeiros.json` | JSON | Conhecer os produtos disponiveis para que eles possan ser ensinados ao cliente |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente e usar essas informaçoes de forma didatica |
| `material_educativo.json` | JSON | Material para uso educativo, para ensinar ao cliente conceitos basicos sobre finanças |

> [!TIP]

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

[Seguindo a mesma estrutura e atributos, adicione outros produtos: FII - Fundo Imobiliário, Fundo DI (Depósito Interfinanceiro), Tesouro IPCA+(Índice de Preços ao Consumidor Amplo), Poupança, Debêntures Incentivadas, Fundo de Previdência Conservador, Conta Remunerada, Caixinha Digital.
Coloquei por separado os produtos: LCI e LCA, já que eles tem significado diferentes. Adicione a cada um dos produtos um atributo: Descrição.

Atualizei o perfil de investidor com dados autênticos, preenchendo cada atributo devidamente para refletir um cenário real.
No archivo de transações, modifiquei alguns valores e descrição de despesas e adicione escola e banco, com seus respectivos atributos preenchidos.
Adicione o arquivo material_educativo.json, que contem conhecimento confiavel sobre finanças, estructurado de forma educativa para o cliente. 
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
