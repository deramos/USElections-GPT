import logging

from config import config
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logging.basicConfig(level=logging.INFO)


class MongoService:
    client, mongo_db = None, None
    logger = logging.getLogger(__name__)

    @classmethod
    def get_client_and_db(cls):
        """
        Makes instances of the MongDB Client and the Mongo underlying database if the client is None
        :return: A class instance of the Mongo client and the db instance
            cls.client: MongoClient
            cls.mongo_db: Database -> Mongo underlying database
        """
        if cls.client is None:
            cls.client = MongoClient(config.MONGO_URL)
            cls.mongo_db = cls.client.get_database(config.COLLECTION_NAME)
        return cls.client, cls.mongo_db

    @classmethod
    def insert_data(cls, collection_name: str, data: list[dict]) -> bool:
        """
        Inserts data into a mongo collection
        :param collection_name:
        :param data:
        :return: bool -> True if insert is successful
        """
        try:
            _, db = cls.get_client_and_db()
            inserts = db.get_collection(collection_name).insert_many(data)
            cls.logger.info(f"Insert into {collection_name} successful!")
            return inserts.acknowledged
        except PyMongoError as e:
            cls.logger.error(f"Insert failed with error {e}")
            raise e
