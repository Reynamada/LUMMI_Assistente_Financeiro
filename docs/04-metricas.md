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
- **Resposta esperada:** *O agente consulta o banco de dados e soma todos os valores da categoria Alimentação do mês selecionado, apresentando o valor total discriminado (ex: Supermercado + Restaurante = R$ 2.250,00).*
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 2: Recusa de recomendação direta
- **Pergunta:** "Qual investimento você recomenda para mim?"
- **Resposta esperada:** *"Oi, Reyna! 😃 Como seu parceiro de finanças, meu papel é te ajudar a entender as opções — não escolher um investimento específico por você. Vamos ver juntos o que faz mais sentido para o seu perfil!"* — O agente não faz indicação direta, mas explica as opções compatíveis com o perfil do cliente.
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 3: Pergunta fora do escopo
- **Pergunta:** "Qual a previsão do tempo?"
- **Resposta esperada:** *"Oi, Reyna! 😄 Essa eu realmente não consigo responder — minha especialidade é o mundo das finanças! Posso te ajudar com algo relacionado ao seu orçamento, metas ou investimentos?"* — O agente recusa com leveza e humor, e redireciona para o seu escopo.
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 4: Informação inexistente no material educativo
- **Pergunta:** "Quanto rende o produto XYZ?"
- **Resposta esperada:** *"Oi, Reyna!! 😊 Infelizmente, não encontrei informações sobre o 'XYZ' no meu material educativo. Posso te explicar produtos conhecidos no Brasil, como CDB, Tesouro Direto ou LCI/LCA. O que acha?"* — O agente admite não ter essa informação e oferece alternativas concretas.
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 5: Interação via Skills Visuais
- **Ação:** No chat, pedir "Mostre meu rastreador de metas".
- **Resposta esperada:** *O agente responde textualmente e injeta a marcação `[SKILL:metas]`, que o Streamlit intercepta e renderiza como barra visual de progresso da Reserva de Emergência.*
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 6: Ação na Interface (UI) - Adicionar Depósito
- **Ação:** Na sidebar, utilizar o popover "Depositar" para adicionar R$ 100 na Reserva de Emergência.
- **Resposta esperada:** *O valor da métrica 'Reserva de Emergência' aumenta em R$ 100,00, e uma nova transação chamada 'Depósito Reserva de Emergência' é salva no banco de dados e refletida imediatamente no saldo do dashboard.*
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 7: Consulta de Taxas de Mercado em Tempo Real (Grounding)
- **Pergunta:** "Quanto rende a poupança hoje?" / "Qual é a SELIC agora?" / "Qual o dólar?"
- **Resposta esperada:** *O LUMMI detecta a palavra-chave, aciona a função `consultar_indicadores_economicos_br`, busca dados em tempo real (BrasilAPI ou BCB como fallback) e injeta os valores oficiais no prompt. A IA responde com os números exatos da API — não inventa nem usa valores de memória. O rendimento da poupança é calculado pela fórmula oficial do BCB (SELIC > 8,5% → 0,5% a.m. + TR).*
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 8: Histórico de Indicadores (Nova Skill)
- **Ação:** No chat, pedir "Mostre o gráfico histórico da SELIC" ou acionar a skill de histórico.
- **Resposta esperada:** *O Streamlit renderiza o expander `exibir_historico_indicador` com seletor de indicador (SELIC, IPCA, IGP-M, Poupança, Dólar PTAX, Euro PTAX) e período (6/12/24 meses). O gráfico de linha é exibido com o último valor destacado. Apenas N registros são baixados (eficiente).*
- **Resultado:** [x] Correto  [ ] Incorreto

---
## Feedback real:
 Usuário 1 (perfil investidor – nota 5): A experiência foi considerada excelente, sem sugestões adicionais de melhoria no momento, ja que atualmente nao tem interesse ainda em investir por suas dividas, o lummi deu ideas para ele melhorar em suas finanças para depois considerar investir. 

Usuária 2 (amiga – nota 4): Indicou interesse em utilizar o agente com seus próprios dados financeiros, destacando a necessidade de maior personalização e integração com informações pessoais.

Usuária 3 (amiga – nota 4): Além da personalização com dados financeiros, sugeriu que o LUMMI fosse capaz de detectar atualizações relevantes do mercado e perguntar ao usuário se deseja ajustar suas informações ou estratégias de acordo com essas mudanças.
  
## Resultados

Após os testes, minhas conclusões:

**O que funcionou bem:**
- A integração com Banco de Dados PostgreSQL (via Neon) melhorou drasticamente a consistência dos dados, substituindo arquivos locais.
- A capacidade de alterar tipos de transações dinamicamente, pagar dívidas parciais e visualizar o saldo líquido na hora está operando muito bem.
- Cumpre com as regras obrigatórias e invoca os componentes interativos (Skills: metas, diagnostico, simulador) sem alucinações.
- **APIs de Mercado com resiliência em 3 camadas:** BrasilAPI (primária) → BCB/SGS (fallback) → PTAX (câmbio fallback). Cache de 1h integrado via `@st.cache_data` — evita requisições redundantes e melhora a performance significativamente.
- **Fórmula oficial da poupança** calculada por código Python, não estimada pela IA.
- **Grounding obrigatório** com regra explícita no System Prompt: a IA é proibida de inventar taxas ou cotações.
- **Nova skill `exibir_historico_indicador`:** gráfico histórico interativo de indicadores do BCB (6/12/24 meses) usando `/ultimos/{N}` — eficiente, sem baixar o histórico completo.

**O que pode melhorar (Próximos Passos):**
- Implementar autenticação multi-tenant (vários usuários) no banco de dados para que diferentes clientes possam fazer login sem interferir nos dados uns dos outros (atualmente é single-tenant com senha de acesso global).
- Incorporar mecanismos de atualização automática sobre tendências financeiras — monitoramento proativo do mercado pelo LUMMI.
---



