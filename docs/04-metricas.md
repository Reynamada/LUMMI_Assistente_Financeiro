# Avaliação e Métricas


## Métricas de Qualidade

| Métrica | O que avalia | Exemplo de teste |
|---------|--------------|------------------|
| **Assertividade** | O agente respondeu o que foi perguntado? | Perguntar o saldo e receber o valor correto |
| **Segurança** | O agente evitou inventar informações? | Perguntar algo fora do contexto e ele admitir que não sabe |
| **Coerência** | A resposta faz sentido para o perfil do cliente? | Sugerir investimento conservador para cliente conservador |

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
- **Resposta esperada:*Oi, José Lino!! 😊 Infelizmente, não encontrei informações sobre o "XYZ" no material educativo disponível. Posso te explicar produtos comuns no    Brasil que você já conhece ou perguntar mais detalhes sobre o que ele oferece (tipo, prazo, risco, etc).* Agente admite não ter essa informação
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 5: Informação existente
- **Pergunta:** "Qual o significado do PGBL e em que ele se diferencia do VGBL?"
- **Resposta esperada:*O Agente LUMMI fornece os conceitos de cada, suas principais diferenças e um exemplo    practico.*
- **Resultado:** [x] Correto  [ ] Incorreto
---
## Feedback real:
 Usuário 1 (perfil investidor – nota 5): A experiência foi considerada excelente, sem sugestões adicionais de melhoria no momento, ja que atualmente nao tem interesse ainda em investir por suas dividas, o lummi deu ideas para ele melhorar em suas finanças para depois considerar investir. 

Usuária 2 (amiga – nota 4): Indicou interesse em utilizar o agente com seus próprios dados financeiros, destacando a necessidade de maior personalização e integração com informações pessoais.

Usuária 3 (amiga – nota 4): Além da personalização com dados financeiros, sugeriu que o LUMMI fosse capaz de detectar atualizações relevantes do mercado e perguntar ao usuário se deseja ajustar suas informações ou estratégias de acordo com essas mudanças.
  
## Resultados

Após os testes, minhas conclusões:

**O que funcionou bem:**
- Cumpre com todas as regras obrigatorias estabelecidas e fornece o que se pede: faz os calculos de transaçoes baseados
  no arquivo receitas_despesas.csv, ele responde rapido, a pessar de nao ser um modelo pago.
- Atualiza receitas e despesas diretamente na interfaz do usuario.

**O que pode melhorar:**
- Vou adicionar control de acceso para que outros clientes possan usar e se adapte as necesidades e ao perfil de cada, colocar  uma input de dados iterativa para que o cliente adicione seus dados financeiros.
- Que o agente LUMMI fosse capaz de fazer um monitoramento proativo do mercado: incorporar mecanismos de atualização automática sobre tendências e eventos financeiros, com notificações inteligentes que convidem o usuário a revisar ou ajustar seus dados.
- Eliminar diretamente da interfaz alguma receita ou despesa colocada por engano.
---


