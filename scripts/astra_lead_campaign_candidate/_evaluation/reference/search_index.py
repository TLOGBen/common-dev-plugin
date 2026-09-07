def build_index(catalog):
    terms, regions = {}, {}
    for row in catalog["items"]:
        for tag in row["tags"]:
            terms.setdefault(tag, set()).add(row["id"])
        regions.setdefault(row["region"], set()).add(row["id"])
    return {"schema_version": 3, "release_id": catalog["release_id"],
            "terms": {key: sorted(ids) for key, ids in terms.items()},
            "regions": {key: sorted(ids) for key, ids in regions.items()}}
