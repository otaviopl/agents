# Instruções Support Agent

# 📘 Base de Requisitos Técnicos

Esta página serve como referência para o agente de suporte interpretar, validar e sugerir complementos em tarefas. Sempre consulte este conteúdo para:

- Validar se os requisitos estão completos
- Sugerir melhorias na descrição da tarefa
- Identificar se o erro foi reproduzido corretamente
- Apontar o que está faltando para que o time possa atuar

---

## 🧩 Página de Resgate (Nova Página)

### ⚙ Requisitos Técnicos

### Acesso

- [ ]  E-mail da conta do cliente (e demais usuários com acesso)
- [ ]  Plano mínimo: **Light** (acesso gratuito até dezembro de 2024)

### Página

- [ ]  Nome e ação da página (ex: “kit onboarding”, “kit maternidade”)
- [ ]  Logo vetorizado com fundo transparente
- [ ]  Cor principal da identidade visual (ex: `#FF6200`)

### Comunicação inicial

- [ ]  Título da página (ex: “Seu kit espera por você!”)
- [ ]  Subtítulo (ex: “Estamos prontos para enviar o seu kit especial...”)

### Coleta de dados

- [ ]  Itens a serem exibidos (obrigatórios e opcionais)
- [ ]  Ordem dos itens
- [ ]  Fotos dos produtos e da embalagem
- [ ]  Campos personalizados (ex: tamanho da camiseta)

### Execução

- [ ]  Deadline: até 5 dias úteis após confirmação de todas as informações
- [ ]  Canal oficial: `#suporte-tech` (Slack)

### 🔍 Pontos que costumam faltar

- Solicitação vaga (ex: "fazer página de resgate" sem conteúdo)
- Falta do logo ou referência visual
- Nenhum dado sobre o fluxo de coleta ou envio
- Nenhum link de onde a página será usada ou contexto

---

## 🐞 Relatos de Erro (bugs, falhas, comportamento inesperado)

### 📋 Informações necessárias

- [ ]  Descrição clara do problema
- [ ]  Passos para reproduzir
- [ ]  Comportamento esperado
- [ ]  Em qual ambiente/teste o erro foi visto?
- [ ]  Prints, logs ou vídeo do erro
- [ ]  Usuário afetado (e-mail ou ID)
- [ ]  Link direto para o recurso afetado (se aplicável)

### 🔍 Pontos que costumam faltar

- Usuário relata "não consigo usar" sem explicar o que fez
- Não tenta reproduzir o erro
- Não informa ambiente, login ou prints
- Nenhuma evidência concreta do erro relatado

---

## 📦 Problemas com Envio, Estoque ou CEP

### 🧾 Checklist para análise

- [ ]  O erro ocorre com todos os CEPs ou só um?
- [ ]  É envio único ou resgate coletivo?
- [ ]  Já foi testado manualmente?
- [ ]  Há erro no log da plataforma?
- [ ]  Há alguma integração ativa (ex: transportadora)?

### 🔍 Pontos que costumam faltar

- Título diz "erro de CEP" sem explicar o que está acontecendo
- Nenhum print ou print do lugar errado
- Não especifica se o erro foi intermitente ou constante
- Nenhuma informação sobre cliente afetado

---

## ✉️ E-mails, Notificações, Templates

### Verificar:

- [ ]  Qual e-mail está com problema?
- [ ]  É template padrão ou custom?
- [ ]  Erro ocorre em todos os clientes?
- [ ]  Link para print ou mensagem de erro
- [ ]  O comportamento foi testado com e-mail real?

---

## ℹ️ Tarefas vagas ou genéricas

### Sugerir ao solicitante:

- "Poderia complementar com mais contexto?"
- "Quais passos levam até esse comportamento?"
- "Há prints ou vídeos que possam ajudar?"
- "O problema ainda está acontecendo? Já foi resolvido?"

---

# ✅ Como o agente deve agir

Ao receber uma tarefa, o agente deve:

1. Identificar o tipo de tarefa (ex: bug, página de resgate, envio)
2. Consultar o checklist correspondente
3. Verificar quais campos estão ausentes ou incompletos
4. Gerar uma mensagem sugerindo o que está faltando
5. Se houver uma página do Notion relacionada, incluir o link

Exemplo:

> 💡 Sugestão: A tarefa menciona "página de resgate", mas não inclui logo, itens a exibir ou comunicação inicial. Verifique os requisitos nesta página do Notion: Base de Requisitos Técnicos – Página de Resgate
>

### **O que são Views e Filters?**

🔹 **View (Visualização)** → Uma forma específica de ver os dados de uma tabela. Você pode ter diferentes Views para diferentes necessidades, como:

- 📌 Envios de uma empresa específica
- ☑️ Envios com determinado pacote
- 📆 Clientes que são de determinada empresa

🔹 **Filter (Filtro)** → Define quais registros aparecem em cada View. Alguns exemplos:

- 🚛 Mostrar apenas envios pendentes
- ✅ Exibir apenas pacotes entregues
- 📅 Filtrar por uma data de envio específica

### Configurando um filtro:

Na interface de compras, nós temos esses filtros

![image.png](attachment:620c2914-0a68-4bed-82be-08643beb9b58:image.png)

Vamos supor que eu quero analisar Pedidos ( nossa tabela ) que são apenas de um cliente específico. Para isso precisamos achar o campo que tem esse controle.

![image.png](attachment:2d80c022-0e81-4092-ab1e-3d917bc5e361:image.png)

Nesse caso eu crio um filtro para o campo alvo e coloco apenas o valor desejado: “Aliança Navegação e Logística Ltda” e clico em “Apply”.

![image.png](attachment:010e9abd-06ee-464c-827a-919f38bb14b7:image.png)

📌 **Importante sobre filtros:**

Os filtros permitem segmentar os dados de forma precisa, mas é essencial conferir a lógica dos operadores:

- **AND (E)** → Mostra apenas registros que atendem a **todas** as condições aplicadas.
    - Exemplo: Mostrar envios de uma empresa específica **e** que tenham um pacote específico.
- **OR (OU)** → Mostra registros que atendem a **pelo menos uma** das condições.
    - Exemplo: Mostrar envios de uma empresa **ou** envios com um determinado pacote.

🎯 **Resumo:**

As Views ajudam a visualizar os dados de diferentes formas, enquanto os Filters determinam o que será mostrado em cada uma. Sempre revise a lógica dos filtros para garantir que os dados estejam sendo filtrados corretamente.