# Agno Doc Bot - Estagiário de Suporte

MVP de um agente de suporte nível 1 que utiliza a biblioteca Agno AI para validar requisitos técnicos e consultar documentação de suporte.

## 🎯 Objetivo

Este projeto é um MVP de um "Estagiário de Suporte" que:
- Recebe perguntas via HTTP (FastAPI)
- Utiliza um agente Agno AI para validar requisitos técnicos
- Consulta documentação de suporte e checklists
- Retorna respostas estruturadas em JSON com validações
- Está preparado para integração com n8n (Slack → HTTP → Slack)

## 🏗️ Arquitetura

```
agno-doc-bot/
├── src/
│   ├── app/
│   │   ├── main.py         # API FastAPI principal
│   │   └── deps.py         # Dependências da API
│   ├── agents/
│   │   └── doc_researcher.py # Definição do agente Agno AI
│   ├── core/
│   │   ├── config.py       # Configurações centralizadas
│   │   └── logging.py      # Configuração de logs
│   └── services/
│       ├── retriever_local.py # Retriever de documentos locais
│       └── retriever_web.py   # Retriever de documentos da web
├── docs/
│   └── ...               # Pasta para documentação local
├── .venv/
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Instalação

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Passos de instalação

1. **Clone o projeto:**
```bash
git clone <repository_url>
cd agno-doc-bot
```

2. **Crie um ambiente virtual (recomendado):**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure a API Key do OpenAI:**
```bash
cp .env.example .env
```
Edite o arquivo `.env` e adicione sua API key.

## 🏃‍♂️ Execução

### Desenvolvimento local
```bash
uvicorn src.app.main:app --reload --port 8088 --host 0.0.0.0
```

### Produção
```bash
uvicorn src.app.main:app --host 0.0.0.0 --port 8088
```

A API estará disponível em: `http://localhost:8088`

## 📚 Endpoints da API

### GET /health
Verificação de saúde da API.
```bash
curl http://localhost:8088/health
```

### GET /stats
Estatísticas do índice local.
```bash
curl http://localhost:8088/stats
```

### POST /ask
Endpoint principal para fazer perguntas.

**Request:**
```json
{
    "query": "Como configurar o sistema?"
}
```

**Response:**
```json
{
    "answer": "Para configurar o sistema, siga os passos na documentação...",
    "sources": [
        "https://docs.suaempresa.com/configuracao",
        "https://help.seusistema.com/setup"
    ]
}
```

**Exemplo com curl:**
```bash
curl -X POST http://localhost:8088/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Como configurar o sistema?"}'
```

## 🔧 Configuração

As configurações do projeto são gerenciadas no arquivo `src/core/config.py` e podem ser substituídas por variáveis de ambiente.

### Configurações principais:
- `API_PORT`: Porta da API (padrão: 8088)
- `ALLOWED_DOMAINS`: Lista de domínios permitidos para o `DuckDuckGoTools`.
- `AGENT_INSTRUCTIONS`: Instruções para o agente `doc_researcher`.

Para alterar a porta da API, por exemplo, você pode definir a variável de ambiente `API_PORT`:
```bash
export API_PORT=8089
```

## 🔗 Integração com n8n

Para integrar com n8n, configure um webhook HTTP:

1. **Trigger:** Slack (quando receber mensagem)
2. **HTTP Request:** POST para `http://seu-servidor:8088/ask`
3. **Body:** `{"query": "{{$json.text}}"}`
4. **Response:** Enviar para Slack com `{{$json.answer}}`

## 📝 Logs

Os logs são exibidos no console durante a execução. A configuração de logging pode ser encontrada em `src/core/logging.py`.

## 🐛 Troubleshooting

### Erro de dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Erro de porta em uso
Altere a porta no comando `uvicorn` ou defina a variável de ambiente `API_PORT`.
```bash
uvicorn src.app.main:app --reload --port 8089
```

### Erro de agente
Verifique se a biblioteca Agno está instalada corretamente:
```bash
python -c "import agno; print('Agno instalado com sucesso')"
```
