def build_index(catalog):
    terms, regions = {}, {}
    for row in catalog["items"]:
        for tag in row["tags"][:1]:
            terms[tag] = [row["id"]]
        regions[row["region"]] = [row["id"]]
    return {"schema_version": 3, "release_id": catalog["release_id"], "terms": terms, "regions": regions}
