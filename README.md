# FruitChatbot

Este repositório contém o projeto **FruitChatbot**, um pequeno sistema de chatbot para uma loja de frutas.

- **Backend**: API em Python com **FastAPI**, integração com **Gemini (Google GenAI)** e banco de dados **SQLite**.
- **Frontend**: interface web simples em **React** (TypeScript) que permite enviar perguntas ao chatbot e exibir as respostas.

O objetivo é permitir que o usuário faça perguntas em linguagem natural sobre **preço** e **estoque** de diversas frutas, e receber respostas baseadas em dados reais do banco.

---

## Estrutura do Projeto

Na raiz do projeto você encontrará:

- `backend/` — código do backend em FastAPI.
- `frontend/` — código do frontend em React.
- `.gitignore` — arquivos e pastas ignorados pelo Git (como `.venv`, `node_modules`, `.env`).
- `README.md` — este arquivo, com visão geral do projeto.

### Backend (`backend/`)

Estrutura principal:

- `main.py` — Ponto de entrada da aplicação FastAPI. Configura logging, CORS e inclui as rotas.
- `app/` — Código da aplicação backend.
  - `app/api/routes.py` — Rotas HTTP da API (endpoints `/fruits` e `/chat`).
  - `app/services/llm_service.py` — Integração com o LLM Gemini + fallback heurístico para interpretar perguntas.
  - `app/services/fruit_service.py` — Regra de negócio do chatbot (interpretação → consulta ao banco → montagem da resposta).
  - `app/db/connection.py` — Conexão e inicialização do banco de dados SQLite (`fruits.db`).
  - `app/config.py` — Configuração compartilhada (leitura de `.env`, chave do Gemini, criação do client Gemini).
- `schemas.py` — Modelos Pydantic usados nos contratos da API.
- `database.py` — Script utilitário para criar/repopular o banco `fruits.db` com frutas de exemplo.
- `.env` — Variáveis de ambiente (por exemplo, `GEMINI_API_KEY`). **Não é versionado**.

Fluxo resumido da rota de chat (`POST /chat`):

1. O cliente envia uma pergunta em português para `/chat` com um JSON do tipo `{ "pergunta": "Quanto custa a banana?" }`.
2. O serviço `llm_service.interpretar_pergunta` usa o Gemini para extrair:
   - `fruit` — nome da fruta.
   - `info` — tipo de informação desejada (`"preço"` ou `"estoque"`).
   Se o Gemini falhar, uma heurística local tenta inferir esses campos a partir do texto.
3. O serviço `fruit_service.responder_pergunta` consulta o banco SQLite (`fruits`) usando `get_db_connection`.
4. A resposta é montada em português, informando o preço ou o estoque da fruta, e devolvida como `ChatResponse`.

### Frontend (`frontend/`)

Estrutura principal:

- `package.json` — dependências e scripts do projeto React.
- `src/` — código-fonte da interface:
  - `src/App.tsx` — componente principal da interface de chat. 
    - Possui um campo de texto para digitar a pergunta.
    - Envia a pergunta via `fetch` para `http://127.0.0.1:8000/chat` (backend).
    - Exibe a resposta em tela ou mensagens de erro.
  - `src/App.css` — estilos básicos da página (layout simples de chat).

A tela mostra um título “FruitChatbot”, um input para escrever a pergunta, um botão **Enviar** e uma área com a resposta ou erro.

---

## Requisitos

### Backend

- Python 3.10+ (recomendado)
- Ambiente virtual (`venv` ou `.venv`)
- Dependências Python (definidas em `requirements.txt` ou instaladas manualmente):
  - `fastapi`
  - `uvicorn`
  - `python-dotenv`
  - `google-genai` (SDK do Gemini)

> Obs.: ajuste os nomes/versões das dependências conforme o arquivo de requisitos do projeto.

### Frontend

- Node.js (versão compatível com Create React App)
- npm (gerenciador de pacotes)

---

## Configuração do Backend

1. **Criar e ativar o ambiente virtual (Windows - PowerShell)**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. **Instalar as dependências**

```powershell
pip install -r requirements.txt
```

3. **Configurar o arquivo `.env` na pasta `backend/`**

Crie um arquivo chamado `.env` dentro da pasta `backend` com, pelo menos:

```env
GEMINI_API_KEY=SEU_TOKEN_AQUI
# Opcional: sobrescrever o modelo padrão
# GEMINI_MODEL_NAME=models/gemini-1.5-flash
```

> A chave do Gemini pode ser obtida no console da Google AI (Gemini API).

4. **Inicializar o banco de dados SQLite**

O banco usado é um arquivo SQLite chamado `fruits.db`, armazenado dentro da pasta `backend/app/`.

Para criar ou recriar o banco, execute:

```powershell
cd backend
.venv\Scripts\python.exe .\database.py
```

Este script:

- Cria a tabela `fruits` (se ainda não existir).
- Limpa todos os registros.
- Insere um conjunto de frutas padrão com:
  - nome (`name`)
  - preço (`price`)
  - estoque (`stock`)

5. **Executar a API com uvicorn**

Sempre que você rodou o backend, usou este comando:

```powershell
cd backend
.venv\Scripts\uvicorn.exe main:app --reload
```

A API ficará disponível em:

- `http://127.0.0.1:8000`

Documentação automática (Swagger):

- `http://127.0.0.1:8000/docs`

Documentação alternativa (ReDoc):

- `http://127.0.0.1:8000/redoc`

---

## Configuração do Frontend

1. **Instalar dependências do frontend**

Na raiz do frontend:

```powershell
cd frontend
npm install
```

2. **Executar o frontend em modo de desenvolvimento**

Sempre que você rodou o frontend, usou este comando:

```powershell
cd frontend
npm start
```

Isso sobe o servidor de desenvolvimento do React, normalmente em:

- `http://localhost:3000`

> Certifique-se de que o backend (FastAPI) esteja rodando em `http://127.0.0.1:8000` ao mesmo tempo, para que o frontend consiga chamar o endpoint `/chat` corretamente.

---

## Endpoints Principais da API

### `GET /fruits/{fruit_name}`

Retorna as informações de uma fruta específica cadastrada no banco.

- **Parâmetros de caminho:**
  - `fruit_name` (string) — nome da fruta (não sensível a maiúsculas/minúsculas).

- **Resposta 200 (OK):**

```json
{
  "name": "Banana",
  "price": 3.5,
  "stock": 120
}
```

- **Resposta 404 (Not Found):**

```json
{
  "detail": "Fruta não encontrada"
}
```

### `POST /chat`

Endpoint principal do chatbot. Recebe uma pergunta em português e retorna uma resposta em texto, baseada nas informações do banco de dados de frutas.

- **Body (JSON):**

```json
{
  "pergunta": "Quanto custa a banana?"
}
```

- **Modelo de request:** `ChatRequest`
  - `pergunta`: `string`

- **Modelo de response:** `ChatResponse`
  - `answer`: `string` — texto em português com a resposta.

- **Resposta 200 (OK) — exemplo:**

```json
{
  "answer": "O preço da Banana é R$ 3.5."
}
```

- **Resposta 404 (Not Found) — fruta não encontrada:**

```json
{
  "detail": "Não encontrei essa fruta no sistema. Verifique o nome e tente novamente."
}
```

- **Resposta 422 (Unprocessable Entity) — pergunta não interpretável:**

```json
{
  "detail": "Não consegui entender sua pergunta. Tente mencionar uma fruta específica e se você quer preço ou estoque."
}
```

- **Resposta 422 (Unprocessable Entity) — tipo de informação não suportado:**

```json
{
  "detail": "Tipo de informação solicitado não é suportado. Use 'preço' ou 'estoque' na sua pergunta."
}
```

---

## Comportamento de Interpretação (Gemini + Heurística)

Ao receber uma pergunta em `/chat`:

1. O backend chama `interpretar_pergunta(pergunta)`, que faz uma requisição ao modelo Gemini
   com um prompt que exige uma resposta em JSON no formato:

   ```json
   {"fruit": "nome_da_fruta", "info": "preço" ou "estoque"}
   ```

2. Se o Gemini retornar um JSON válido com `fruit` e `info`, esses valores são usados.
3. Se houver erro de API, JSON inválido ou campos ausentes, o backend cai em um **fallback local**
   (`_interpretar_localmente`), que tenta inferir:
   - a fruta a partir do texto (por exemplo: banana, maçã/maca, manga, uva, abacaxi, morango, etc.),
   - o tipo de informação (`preço` ou `estoque`) a partir de palavras como "preço", "valor", "custa",
     "estoque", "disponível", "tem", "quantas", etc.

4. Com o par `(fruit, info)` definido, o serviço consulta o banco SQLite e monta uma resposta em português,
   devolvendo sempre um JSON no formato `ChatResponse`.

---

## Tratamento de Erros e Códigos HTTP

A API utiliza códigos HTTP adequados para comunicar o estado da requisição:

- `200 OK` — pergunta entendida e fruta encontrada. Resposta em `answer`.
- `404 Not Found` — a fruta identificada não existe no banco.
- `422 Unprocessable Entity` — a pergunta não pôde ser interpretada (não há fruta ou tipo de informação claros),
  ou o tipo de informação pedido não é suportado.

As mensagens de erro são descritivas e orientam o usuário a reformular a pergunta, quando possível.
