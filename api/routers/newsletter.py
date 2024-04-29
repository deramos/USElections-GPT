import http
import logging
from config import config
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from dbservices.mongoservice import MongoService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/news-letter",
    tags=["News Letter"],
)


@router.post('/subscribe')
async def subscribe(request: Request):
    """
    Subscribes a user to daily newsletter with text to speech (TTS) enabled. The TTS is developed using Seamless
    https://ai.meta.com/research/seamless-communication/
    :return: HTTPStatus_CREATED
    """
    data = await request.json()

    # TODO: Create NewsLetter Object using the parsed JSON. Save the Newsletter object into Mongo using MongoService

    return JSONResponse(
        content={},
        status_code=http.HTTPStatus.CREATED
    )
