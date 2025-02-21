from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    groq_api_key = GROQ_API_KEY,
    model = "mixtral-8x7b-32768",
)

app = FastAPI()

class InputData(BaseModel):
    texto: str
    qtd_pessoas: int

@app.post("/sugestao")
def gerar_sugestao(dados: InputData):
    prompt = f"""
    Baseado no seguinte item: '{dados.texto}', gere sugestões de quantidade necessária para {dados.qtd_pessoas} pessoas.
    Exemplo: Se for café, quantas xícaras ou litros são recomendados?
    """

    resposta = llm([SystemMessage(content="Você é um assistente especializado em planejamento de eventos."),
                    HumanMessage(content=prompt)])
    
    return {"sugestao": resposta.content}

