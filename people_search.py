"""MongoDB-backed people search used by the Flask `/search` endpoint.

The mock data lives in MongoDB (seeded from MOCK_DATA.json), and every search is
answered by a single indexed query with a projection and a limit, so the full
collection is never pulled into the application.
"""

import os
import re

from pymongo import ASCENDING, MongoClient

DEFAULT_MONGO_URI = "mongodb://localhost:27017/"
DEFAULT_DB_NAME = "mock_people"
DEFAULT_COLLECTION_NAME = "people"

MAX_LIMIT = 100
DEFAULT_LIMIT = 20
MAX_KEYWORD_LENGTH = 128

PROJECTION = {
    "_id": 0,
    "id": 1,
    "first_name": 1,
    "last_name": 1,
    "email": 1,
    "gender": 1,
}


def get_connection_string() -> str:
    return os.getenv("MONGO_URI", DEFAULT_MONGO_URI)


class PeopleSearch:
    """Thin data-access layer over the `people` collection."""

    def __init__(
        self,
        mongo_uri: str | None = None,
        db_name: str = DEFAULT_DB_NAME,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> None:
        self.client = MongoClient(mongo_uri or get_connection_string())
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def create_indexes(self) -> None:
        """Index the normalized name fields so prefix searches use an IXSCAN."""
        self.collection.create_index([("first_name_lower", ASCENDING)])
        self.collection.create_index([("last_name_lower", ASCENDING)])
        self.collection.create_index([("id", ASCENDING)], unique=True)

    @staticmethod
    def build_filter(keyword: str, match: str = "prefix") -> dict:
        """Build an $or filter over the normalized first/last name fields.

        `prefix` anchors the regex at the start of the value, which lets MongoDB
        satisfy the query with an index range scan. `contains` is an unanchored
        substring search, which is a collection scan of the index-covered values.
        """
        pattern = re.escape(keyword.strip().lower())
        if match == "prefix":
            pattern = f"^{pattern}"
        regex = {"$regex": pattern}
        return {"$or": [{"first_name_lower": regex}, {"last_name_lower": regex}]}

    def search(
        self,
        keyword: str,
        limit: int = DEFAULT_LIMIT,
        skip: int = 0,
        match: str = "prefix",
    ) -> list[dict]:
        query = self.build_filter(keyword, match)
        cursor = (
            self.collection.find(query, PROJECTION)
            .sort("id", ASCENDING)
            .skip(skip)
            .limit(limit)
        )
        return list(cursor)

    def count(self, keyword: str, match: str = "prefix") -> int:
        return self.collection.count_documents(self.build_filter(keyword, match))

    def close(self) -> None:
        self.client.close()
