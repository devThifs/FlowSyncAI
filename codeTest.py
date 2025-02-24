from fastapi import FastAPI, Query
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os, json

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="mixtral-8x7b-32768",
)

app = FastAPI()

#mini base de dados dos eventos
eventos = [
    {
        "nome_do_evento": "Palestra de Inteligência Artificial",
        "duracao": "3 horas",
        "horario": "10:00-11:00",
        "lugar": "Auditório",
        "acompanhante": "Clebinho"
    },
    {
        "nome_do_evento": "Reunião de alinhamento de projeto",
        "duracao": "1 hora",
        "horario": "15:00-16:00",
        "lugar": "Sala de reuniões",
        "acompanhante": "Joãozinho"
    },
    {
        "nome_do_evento": "Boschland",
        "duracao": "2 dias",
        "horario": "9:00-18:00",
        "lugar": "Bosch",
        "acompanhante": "Ninguém"
    }
]

class InputData(BaseModel):
    tipo_evento: str
    qtd_pessoas: int

#autocomplete para sugestão de eventos
@app.get("/autocomplete/")
def autocomplete(query: str = Query(..., min_length=1)):
    sugestoes = [evento["nome_do_evento"] for evento in eventos if query.lower() in evento["nome_do_evento"].lower()]
    return {"suggestions": sugestoes}

#obtem detalhes de um evento
@app.get("/evento/")
def get_evento(query: str = Query(..., min_length=1)):
    for evento in eventos:
        if query.lower() in evento["nome_do_evento"].lower():
            return evento
    return {"message": "evento não encontrado. a IA pode gerar uma sugestão."}

#gera sugestão de evento (caso ele não exista) usando a IA
@app.post("/sugestao")
def gerar_sugestao(dados: InputData):
    prompt = f"""
    considere os seguintes eventos já cadastrados:
    {eventos}

    gere sugestões para um evento do tipo '{dados.tipo_evento}' com {dados.qtd_pessoas} participantes.  
    - se for um evento já existente, gere novas variações dentro do mesmo tema (exemplo: "Palestra de Finanças"', "Palestra de Vendas", etc.)
    - se for um evento novo, sugira algo que combine com os eventos já cadastrados.

    retorne a resposta SOMENTE em JSON, com o seguinte formato:

    {{
        "sugestoes": [
            {{
                "nome_do_evento": "...",
                "duracao": "...",
                "horarios_sugeridos": ["...", "..."],
                "lugar": "...",
                "acompanhante": "..."
            }},
            ...
        ]
    }}
    """

    resposta = llm([
        SystemMessage(content="responda APENAS no formato JSON válido."),
        HumanMessage(content=prompt)
    ])

    try:
        return json.loads(resposta.content)  #converte a resposta para JSON
    except json.JSONDecodeError:
        return {"erro": "A IA não retornou um JSON válido. Verifique a formatação."}
