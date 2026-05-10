import json
import os
import uuid
from threading import Lock

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

_lock = Lock()


def _collection_path(name: str) -> str:
    return os.path.join(DATA_DIR, f"{name}.json")


def _load_collection(name: str) -> list:
    path = _collection_path(name)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_collection(name: str, data: list):
    path = _collection_path(name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def _oid() -> str:
    return str(uuid.uuid4())


def _match(item: dict, query: dict) -> bool:
    for k, v in query.items():
        iv = item.get(k)
        if str(iv) != str(v) and iv != v:
            return False
    return True


class JsonCollection:
    def __init__(self, name: str):
        self.name = name

    def _data(self) -> list:
        return _load_collection(self.name)

    def _write(self, data: list):
        with _lock:
            _save_collection(self.name, data)

    async def find_one(self, query: dict) -> dict | None:
        data = self._data()
        for item in data:
            if _match(item, query):
                return dict(item)
        return None

    def find(self, query: dict = None) -> "JsonCursor":
        data = self._data()
        if query:
            filtered = [dict(item) for item in data if _match(item, query)]
        else:
            filtered = [dict(item) for item in data]
        return JsonCursor(filtered)

    async def insert_one(self, doc: dict) -> "InsertResult":
        if "_id" not in doc:
            doc["_id"] = _oid()
        data = self._data()
        data.append(doc)
        self._write(data)
        return InsertResult(doc["_id"])

    async def update_one(self, query: dict, update: dict):
        data = self._data()
        set_fields = update.get("$set", {})
        count = 0
        for item in data:
            if _match(item, query):
                item.update(set_fields)
                count = 1
                break
        self._write(data)
        return UpdateResult(count)

    async def delete_one(self, query: dict):
        data = self._data()
        new_data = []
        deleted = 0
        for item in data:
            if _match(item, query) and deleted == 0:
                deleted = 1
            else:
                new_data.append(item)
        self._write(new_data)
        return DeleteResult(deleted)

    async def delete_many(self, query: dict):
        data = self._data()
        new_data = [item for item in data if not _match(item, query)]
        deleted = len(data) - len(new_data)
        self._write(new_data)
        return DeleteResult(deleted)


class InsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class UpdateResult:
    def __init__(self, matched_count):
        self.matched_count = matched_count


class DeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class JsonCursor:
    def __init__(self, items: list):
        self._items = list(items)
        self._sort_key = None
        self._sort_reverse = False
        self._limit_n = None

    def sort(self, key, direction=1):
        self._sort_key = key
        self._sort_reverse = direction == -1
        return self

    def limit(self, n):
        self._limit_n = n
        return self

    async def to_list(self, length=None):
        items = self._items
        if self._sort_key:
            items = sorted(items, key=lambda x: x.get(self._sort_key, ""), reverse=self._sort_reverse)
        if self._limit_n:
            items = items[:self._limit_n]
        if length:
            items = items[:length]
        return items

    def __aiter__(self):
        self._iter_index = 0
        if self._sort_key:
            self._items = sorted(self._items, key=lambda x: x.get(self._sort_key, ""), reverse=self._sort_reverse)
        if self._limit_n:
            self._items = self._items[:self._limit_n]
        return self

    async def __anext__(self):
        if self._iter_index >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._iter_index]
        self._iter_index += 1
        return item


def get_collection(name: str) -> JsonCollection:
    return JsonCollection(name)
