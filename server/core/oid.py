import os

USE_MONGO = os.getenv("USE_MONGO", "auto") != "false"


class FlexId:
    def __init__(self, id_str: str):
        self._id = str(id_str)

    def __str__(self):
        return self._id

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self._id)


def oid(id_str: str):
    if USE_MONGO:
        from bson import ObjectId
        try:
            return ObjectId(id_str)
        except Exception:
            return id_str
    return str(id_str)


def to_str(obj) -> str:
    return str(obj)
