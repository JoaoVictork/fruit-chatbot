from pydantic import BaseModel


class ChatRequest(BaseModel):
    pergunta: str


class ChatResponse(BaseModel):
    answer: str


class FruitResponse(BaseModel):
    name: str
    price: float
    stock: int

