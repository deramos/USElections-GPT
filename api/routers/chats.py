from fastapi import APIRouter, WebSocket
from fastapi import Request
from util import utils

router = APIRouter(
    prefix='/chat',
    tags=['chat']
)

@router.on_event('startup')
def init_llm():
    """
    Init Mistral LLM
    :return:
    """
    rag_chain = utils.init_llm()

@router.websocket('/websocket/{client_id}')
async def chat(websocket: WebSocket, client_id: str):
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()
