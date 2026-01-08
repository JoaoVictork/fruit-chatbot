import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from google import genai

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY não encontrada. "
        "Verifique se o arquivo backend/.env existe e contém GEMINI_API_KEY=SUASENHA."
    )

GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "models/gemini-1.5-flash")
logger.info("Usando modelo do Gemini (config): %s", GEMINI_MODEL_NAME)

client = genai.Client(api_key=GEMINI_API_KEY)

