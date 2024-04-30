import logging
from typing import Union
from util import chat_util
from fastapi import Request
from fastapi import APIRouter, WebSocket
from langchain_core.runnables.history import RunnableWithMessageHistory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/chat',
    tags=['chat']
)

rag_llm: RunnableWithMessageHistory


@router.on_event('startup')
def init_llm():
    """
    Init LLM Chatbot
    :return:
    """
    llm_util = chat_util.LLMUtil()
    global rag_llm
    rag_llm = llm_util.init_llm()


@router.websocket('/{session_id}')
async def chat(websocket: WebSocket, session_id: str):
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()
            chat_response = rag_llm.invoke(
                {"input": message},
                config={"configurable": {"session_id": session_id}})
            await websocket.send_text(chat_response['answer'])
    except Exception as e:
        logger.info(f"WebSocket connection closed: {e}")

