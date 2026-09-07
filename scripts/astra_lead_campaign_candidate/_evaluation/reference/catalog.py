def build_catalog(document):
    fields = ("id", "name", "region", "slots", "tags")
    items = [{key: row[key] for key in fields}
             for row in document["records"]
             if row["status"] == "active" and row["channel"] == "standard"]
    return {"schema_version": 3, "release_id": document["release_id"],
            "items": sorted(items, key=lambda row: row["id"])}
