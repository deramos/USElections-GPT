import logging
import asyncio
from util.chat_util import LLMUtil
from fastapi import APIRouter, WebSocket
from fastapi import Request, HTTPException, Path
from fastapi.responses import StreamingResponse
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
    global rag_llm
    rag_llm = LLMUtil.init_llm()


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


@router.post('/{session_id}')
async def http_chat(
        request: Request,
        session_id: str = Path(..., description='The session ID')
):
    data = await request.json()
    message = data.get("message")

    if not message:
        return HTTPException(status_code=400, detail='No input message received.')

    chat_response = rag_llm.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}})

    chat_answer = ' '.join(chat_response['answer'].split('\n\n'))

    async def stream_response():
        for word in chat_answer.split():
            yield f"data: {word}\n\n"
            await asyncio.sleep(0.05)
        yield "data: [END]\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")
