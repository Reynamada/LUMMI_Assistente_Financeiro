# Avaliação e Métricas

## Como Avaliar seu Agente

A avaliação pode ser feita de duas formas complementares:

1. **Testes estruturados:** Você define perguntas e respostas esperadas;
2. **Feedback real:** Pessoas testam o agente e dão notas.

---

## Métricas de Qualidade

| Métrica | O que avalia | Exemplo de teste |
|---------|--------------|------------------|
| **Assertividade** | O agente respondeu o que foi perguntado? | Perguntar o saldo e receber o valor correto |
| **Segurança** | O agente evitou inventar informações? | Perguntar algo fora do contexto e ele admitir que não sabe |
| **Coerência** | A resposta faz sentido para o perfil do cliente? | Sugerir investimento conservador para cliente conservador |

> [!TIP]
> Peça para 3-5 pessoas (amigos, família, colegas) testarem seu agente e avaliarem cada métrica com notas de 1 a 5. Isso torna suas métricas mais confiáveis! Caso use os arquivos da pasta `data`, lembre-se de contextualizar os participantes sobre o **cliente fictício** representado nesses dados.

---

## Exemplos de Cenários de Teste

Crie testes simples para validar seu agente:

### Teste 1: Consulta de gastos
- **Pergunta:** "Quanto gastei com alimentação?"
- **Resposta esperada:*2250* suma todos os valores da categoria alimentaçao. Valor baseado no `receitas_despesas.csv`
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 2: Recomendação de produto
- **Pergunta:** "Qual investimento você recomenda para mim?"
- **Resposta esperada:*Oi José! 😃 Como seu parceiro de finanças, meu papel é te ajudar a entender as opções, não escolher um investimento específico para você. Vamos fazer assim:* Produto compatível com o perfil do cliente
- **Resultado:** [x ] Correto  [ ] Incorreto

### Teste 3: Pergunta fora do escopo
- **Pergunta:** "Qual a previsão do tempo?"
- **Resposta esperada:** *Oi José! 🙃 Como seu assistente financeiro, não posso recomendar investimentos específicos, mas posso te orientar sobre os princípios básicos!*
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 4: Informação inexistente
- **Pergunta:** "Quanto rende o produto XYZ?"
- **Resposta esperada:*Oi, José! 🙋‍♂️ Com base no material educativo disponível, não há informações sobre um produto chamado "XYZ".* Agente admite não ter essa informação
- **Resultado:** [x] Correto  [ ] Incorreto

---

## Resultados

Após os testes, minhas conclusões:

**O que funcionou bem:**
- Cumpre com todas as regras obrigatorias estabelecidas e fornece o que se pede: faz os calculos de transaçoes baseados
  no arquivo receitas_despesas.csv, ele responde rapido, a pessar de nao ser um modelo pago.

**O que pode melhorar:**
- Vou adicionar control de acceso para que outros clientes possan usar e se adapte as necesidades e ao perfil de cada, colocar
  uma input de dados iterativa para que o cliente adicione seus dados financeiros.

---

## Métricas Avançadas (Opcional)

Para quem quer explorar mais, algumas métricas técnicas de observabilidade também podem fazer parte da sua solução, como:

- Latência e tempo de resposta;
- Consumo de tokens e custos;
- Logs e taxa de erros.

Ferramentas especializadas em LLMs, como [LangWatch](https://langwatch.ai/) e [LangFuse](https://langfuse.com/), são exemplos que podem ajudar nesse monitoramento. Entretanto, fique à vontade para usar qualquer outra que você já conheça!
