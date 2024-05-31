import http
import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from daos.newsletter import NewsLetterObject
from dbservices.mongoservice import MongoService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/news-letter",
    tags=["News Letter"],
)


@router.post('/subscribe')
async def subscribe(data: NewsLetterObject):
    """
    Subscribes a user to daily newsletter with text to speech (TTS) enabled. The TTS is developed using Seamless
    https://ai.meta.com/research/seamless-communication/
    :return: HTTPStatus_CREATED
    """
    try:
        insert_successful = MongoService.insert_data('newsletter-subscribers',
                                                     data=[jsonable_encoder(data)])

        if insert_successful:
            return JSONResponse(
                content={},
                status_code=http.HTTPStatus.CREATED
            )
    except Exception as e:
        logger.error(f'Error subscribing to newsletter {e}')
        return JSONResponse(
            content={'status': 'fail',
                     'message': 'Error subscribing to newsletter'},
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR
        )

