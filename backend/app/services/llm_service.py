import json
import logging
from typing import Dict

from google.genai import errors as genai_errors

from app.config import client, GEMINI_MODEL_NAME

logger = logging.getLogger(__name__)


def _interpretar_localmente(pergunta: str) -> Dict[str, str]:
    """Heurística simples para extrair fruta e tipo de info da pergunta.

    Usada apenas como fallback quando o Gemini falha.
    """
    pergunta_lower = pergunta.lower()

    mapa_frutas = {
        "banana": "banana",
        "maçã": "maçã",
        "maca": "maçã",
        "manga": "manga",
        "uva": "uva",
        "laranja": "laranja",
        "abacaxi": "abacaxi",
        "morango": "morango",
        "melancia": "melancia",
        "melão": "melão",
        "melao": "melão",
        "limão": "limão",
        "limao": "limão",
        "pêra": "pêra",
        "pera": "pêra",
        "kiwi": "kiwi",
        "mamão": "mamão",
        "mamao": "mamão",
        "coco": "coco",
        "goiaba": "goiaba",
        "pêssego": "pêssego",
        "pessego": "pêssego",
        "ameixa": "ameixa",
        "caqui": "caqui",
        "framboesa": "framboesa",
        "mirtilo": "mirtilo",
    }

    fruta = None
    for chave, normalizado in mapa_frutas.items():
        if chave in pergunta_lower:
            fruta = normalizado
            break

    info = None

    if (
        "preço" in pergunta_lower
        or "preco" in pergunta_lower
        or "custa" in pergunta_lower
        or "valor" in pergunta_lower
        or "quanto ta" in pergunta_lower
        or "quanto tá" in pergunta_lower
        or "quanto e" in pergunta_lower
        or "quanto é" in pergunta_lower
    ):
        info = "preço"

    elif (
        "estoque" in pergunta_lower
        or "quantidade" in pergunta_lower
        or "tem" in pergunta_lower
        or "disponivel" in pergunta_lower
        or "disponível" in pergunta_lower
        or "ainda tem" in pergunta_lower
        or "quantas" in pergunta_lower
        or "temos" in pergunta_lower
        or "restam" in pergunta_lower
    ):
        info = "estoque"

    return {"fruit": fruta or "", "info": info or ""}


def interpretar_pergunta(pergunta: str) -> Dict[str, str]:
    """Usa o Gemini para interpretar a pergunta.

    Em caso de erro na API, cai em um fallback local simples.
    Retorna um dicionário com chaves 'fruit' e 'info';
    se a interpretação falhar, os valores podem ser strings vazias.
    """
    prompt = f"""
        Você é um assistente de uma loja de frutas.
        Interprete a pergunta do usuário e responda **apenas** em JSON
        no formato exato:
        {{"fruit": "nome_da_fruta", "info": "preço" ou "estoque"}}

        Não escreva mais nada além do JSON.

        Pergunta: {pergunta}
        """

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt,
        )
        texto = response.text.strip()
        logger.debug("Resposta bruta do Gemini: %s", texto)

        dados = json.loads(texto)
        fruit = dados.get("fruit")
        info = dados.get("info")
        if not fruit or not info:
            raise ValueError("JSON retornado pelo modelo não contém 'fruit' ou 'info'.")
        return {"fruit": fruit, "info": info}

    except (genai_errors.ClientError, genai_errors.APIError, ValueError, json.JSONDecodeError) as e:
        logger.error("Falha ao interpretar com Gemini: %r", e)
        logger.warning("Usando interpretação local simples como fallback.")
        return _interpretar_localmente(pergunta)

    except Exception as e:
        logger.exception("Erro inesperado ao chamar o Gemini: %r", e)
        return _interpretar_localmente(pergunta)
