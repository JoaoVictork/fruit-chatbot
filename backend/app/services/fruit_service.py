from fastapi import HTTPException
import logging

from app.db.connection import get_db_connection
from app.services.llm_service import interpretar_pergunta

logger = logging.getLogger(__name__)


def responder_pergunta(pergunta: str) -> str:
    """Fluxo de domínio do chatbot.

    - Usa o LLM (ou fallback) para interpretar a pergunta.
    - Consulta o banco de dados de frutas.
    - Monta a resposta em português.
    - Levanta HTTPException para casos de erro de domínio.
    """
    dados = interpretar_pergunta(pergunta)
    logger.debug("Interpretação da pergunta: %s", dados)

    fruta = (dados.get("fruit") or "").strip()
    info = (dados.get("info") or "").strip()

    if not fruta or not info:
        raise HTTPException(
            status_code=422,
            detail=(
                "Não consegui entender sua pergunta. "
                "Tente mencionar uma fruta específica e se você quer preço ou estoque."
            ),
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, price, stock FROM fruits WHERE LOWER(name) = LOWER(?)",
        (fruta,),
    )

    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Não encontrei essa fruta no sistema. Verifique o nome e tente novamente.",
        )

    fruta_nome = result["name"]

    if info == "preço":
        return f"O preço da {fruta_nome} é R$ {result['price']}."

    if info == "estoque":
        return f"Temos {result['stock']} unidades de {fruta_nome} em estoque."

    raise HTTPException(
        status_code=422,
        detail=(
            "Tipo de informação solicitado não é suportado. "
            "Use 'preço' ou 'estoque' na sua pergunta."
        ),
    )
