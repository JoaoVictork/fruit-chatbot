from fastapi import APIRouter, HTTPException

from app.db.connection import get_db_connection
from app.services.fruit_service import responder_pergunta
from schemas import ChatRequest, ChatResponse, FruitResponse

router = APIRouter()


@router.get(
    "/fruits/{fruit_name}",
    response_model=FruitResponse,
    summary="Obter informações de uma fruta",
    description=(
        "Retorna o nome, preço e estoque de uma fruta cadastrada no banco de dados. "
        "A busca não é sensível a maiúsculas/minúsculas."
    ),
)
def get_fruit_info(fruit_name: str) -> FruitResponse:
    """Busca uma fruta pelo nome no banco de dados.

    - **fruit_name**: nome da fruta (ex.: `Banana`, `Maçã`, `abacaxi`).
    - **Resposta**: objeto contendo `name`, `price` e `stock`.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, price, stock FROM fruits WHERE LOWER(name) = LOWER(?)",
        (fruit_name,),
    )

    fruit = cursor.fetchone()
    conn.close()

    if not fruit:
        raise HTTPException(status_code=404, detail="Fruta não encontrada")

    return {
        "name": fruit["name"],
        "price": fruit["price"],
        "stock": fruit["stock"],
    }


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Fazer uma pergunta ao chatbot de frutas",
    description=(
        "Recebe uma pergunta em linguagem natural sobre frutas (preço ou estoque) "
        "e retorna uma resposta em texto, baseada nas informações do banco de dados. "
        "A interpretação da pergunta é feita com o modelo Gemini, com fallback heurístico."
    ),
)
def chat(request: ChatRequest) -> ChatResponse:
    """Chatbot de frutas.

    Envie uma pergunta em português mencionando uma fruta e o tipo de informação desejada.

    Exemplos de perguntas:
    - `Quanto custa a banana?`
    - `Temos morango em estoque?`
    - `A gente ainda tem manga disponível?`
    """
    answer = responder_pergunta(request.pergunta)
    return ChatResponse(answer=answer)
