import json
from datetime import datetime


class CustomMongoDecoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, '__str__'):  # This will handle ObjectIds
            return str(obj)

        return super(CustomMongoDecoder, self).default(obj)


def init_llm():
    return None