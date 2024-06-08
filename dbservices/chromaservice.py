import os
from config import config
from chromadb import HttpClient


class ChromaService:

    _client = None

    @classmethod
    def get_client(cls) -> HttpClient:
        """
        Creates an instance of the Chroma HTTPClient service if it is none, else return the created one.
        :return:
        """
        if not cls._client:
            cls._client = HttpClient(config.CHROMA_DB_URL)
        return cls._client
