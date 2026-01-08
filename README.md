# FruitChatbot - Backend

Este é o backend do projeto **FruitChatbot**, um chatbot para consulta de informações sobre uma loja de frutas.

Ele expõe uma API REST usando **FastAPI**, integra-se com o **Gemini** (Google GenAI) para interpretar perguntas em linguagem natural e consulta um banco de dados **SQLite** para retornar preço e estoque de diversas frutas.

---

## Visão Geral da Arquitetura

Estrutura principal do backend:

- `main.py` — Ponto de entrada da aplicação FastAPI.
- `app/` — Código da aplicação backend.
  - `app/api/routes.py` — Rotas HTTP da API (endpoints).
  - `app/services/llm_service.py` — Integração com o LLM Gemini + fallback heurístico.
  - `app/services/fruit_service.py` — Regra de negócio do chatbot (interpretação → banco → resposta).
  - `app/db/connection.py` — Conexão e inicialização do banco de dados SQLite (`fruits.db`).
  - `app/config.py` — Configuração compartilhada (leitura de `.env`, chave do Gemini, criação do client).
- `schemas.py` — Modelos Pydantic usados nos contratos da API.
- `database.py` — Script utilitário para criar/repopular o banco `fruits.db`.
- `.env` — Variáveis de ambiente (por exemplo, `GEMINI_API_KEY`).

Fluxo resumido da rota de chat:

1. O cliente envia uma pergunta em português para `POST /chat`.
2. O serviço `llm_service.interpretar_pergunta` usa o Gemini para extrair:
   - `fruit` — nome da fruta.
   - `info` — tipo de informação desejada (`"preço"` ou `"estoque"`).
   Se o Gemini falhar, uma heurística local tenta inferir esses campos.
3. O serviço `fruit_service.responder_pergunta` consulta o banco SQLite (`fruits`),
   usando `get_db_connection`.
4. A resposta é montada em português, informando o preço ou o estoque da fruta.

---

## Requisitos

- Python 3.10+ (recomendado)
- Ambiente virtual (`venv`) configurado
- Dependências Python (definidas em `requirements.txt` ou instaladas manualmente):
  - `fastapi`
  - `uvicorn`
  - `python-dotenv`
  - `google-genai` (SDK do Gemini)

> Obs.: ajuste os nomes/versões das dependências conforme o arquivo de requisitos do projeto.

---

## Configuração do Ambiente

1. **Crie e ative o ambiente virtual (Windows - PowerShell):**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. **Instale as dependências:**

```powershell
pip install -r requirements.txt
```

3. **Configure o arquivo `.env` na pasta `backend/`:**

Crie um arquivo chamado `.env` dentro da pasta `backend` com, pelo menos:

```env
GEMINI_API_KEY=SEU_TOKEN_AQUI
# Opcional: sobrescrever o modelo padrão
# GEMINI_MODEL_NAME=models/gemini-1.5-flash
```

> A chave do Gemini pode ser obtida no console da Google AI (Gemini API).

4. **(Opcional) Verifique se a chave está sendo carregada corretamente:**

Você pode subir a aplicação e observar os logs, ou usar um script auxiliar se houver.

---

## Inicializando o Banco de Dados

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

---

## Executando a API

Com o ambiente virtual ativo e o banco criado, execute:

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

## Endpoints Principais

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

---

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

---
