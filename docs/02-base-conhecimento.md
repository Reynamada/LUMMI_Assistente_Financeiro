# Base de Conhecimento

## Dados Utilizados

Descreva quais dados da pasta `data/` você utilizou e como:

| Arquivo | Utilização no Agente |
|---------|---------------------|
| `transacoes.json` | [ex: Analisar padrão de gastos do cliente] |
| `perfil_investidor.json` | [ex: Personalizar recomendações] |
| `produtos_financeiros.json` | [ex: Sugerir produtos adequados ao perfil] |

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

[Sua descrição aqui]

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

[ex: Os JSONs são carregados no início da sessão e incluídos no contexto do prompt]

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
