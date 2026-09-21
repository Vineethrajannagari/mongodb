"""Flask API exposing a single `/search` endpoint backed by MongoDB."""

from flask import Flask, jsonify, request

from people_search import DEFAULT_LIMIT, MAX_LIMIT, PeopleSearch

app = Flask(__name__)
store = PeopleSearch()


def parse_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = request.args.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"'{name}' must be an integer") from error
    if value < minimum or value > maximum:
        raise ValueError(f"'{name}' must be between {minimum} and {maximum}")
    return value


@app.get("/search")
def search():
    keyword = (request.args.get("q") or "").strip()
    if not keyword:
        return jsonify({"error": "query parameter 'q' is required"}), 400

    match = request.args.get("match", "prefix")
    if match not in {"prefix", "contains"}:
        return jsonify({"error": "'match' must be 'prefix' or 'contains'"}), 400

    try:
        limit = parse_int("limit", DEFAULT_LIMIT, 1, MAX_LIMIT)
        skip = parse_int("skip", 0, 0, 1_000_000)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    results = store.search(keyword, limit=limit, skip=skip, match=match)
    return jsonify(
        {
            "query": keyword,
            "match": match,
            "limit": limit,
            "skip": skip,
            "count": len(results),
            "total": store.count(keyword, match),
            "results": results,
        }
    )


@app.get("/health")
def health():
    store.client.admin.command("ping")
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
