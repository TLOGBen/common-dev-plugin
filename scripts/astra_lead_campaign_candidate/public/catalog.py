def build_catalog(document):
    items = []
    for row in sorted(document["records"], key=lambda row: row["id"]):
        if row["status"] != "active" or row["channel"] != "standard" or row["slots"] <= 0:
            continue
        items.append({key: row[key] for key in ("id", "name", "region", "slots", "tags")})
    return {"schema_version": 2, "release_id": document["release_id"], "items": items}
