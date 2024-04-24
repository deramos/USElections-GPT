from fastapi import APIRouter, WebSocket
from fastapi import Request

router = APIRouter(
    prefix='/chat',
    tags=['chat']
)


@router.websocket('/ws/{client_id}')
async def chat(websocket: WebSocket, client_id: str):
    request = await Request.json()
