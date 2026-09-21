"""Load MOCK_DATA.json into MongoDB once, so searches can be served by the database."""

import argparse
import json

from pymongo import ReplaceOne

from people_search import PeopleSearch


def load_records(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list):
        raise ValueError(f"{path} must contain a JSON array of objects")
    return records


def normalize(record: dict) -> dict:
    document = dict(record)
    document["first_name_lower"] = str(record.get("first_name", "")).lower()
    document["last_name_lower"] = str(record.get("last_name", "")).lower()
    return document


def seed(path: str, drop: bool) -> int:
    store = PeopleSearch()
    try:
        if drop:
            store.collection.drop()
        records = load_records(path)
        operations = [
            ReplaceOne({"id": record["id"]}, normalize(record), upsert=True)
            for record in records
        ]
        if operations:
            store.collection.bulk_write(operations, ordered=False)
        store.create_indexes()
        return store.collection.count_documents({})
    finally:
        store.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default="MOCK_DATA.json")
    parser.add_argument("--drop", action="store_true", help="drop the collection first")
    args = parser.parse_args()
    total = seed(args.file, args.drop)
    print(f"Seeded {args.file}; collection now holds {total} documents")


if __name__ == "__main__":
    main()
