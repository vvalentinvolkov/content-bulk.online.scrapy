import logging


def get_random_oids(collection, sample_size):
    pipeline = [{"$project": {'_id': 1}}, {"$sample": {"size": sample_size}}]
    return [s['_id'] for s in collection.aggregate(pipeline)]


def get_random_documents(DocCls, sample_size):
    doc_collection = DocCls._get_collection()
    random_oids = get_random_oids(doc_collection, sample_size)
    return DocCls.objects(id__in=random_oids)


def check_documents(DocCls, sample_size):
    for doc in get_random_documents(DocCls, sample_size):
        # general validation (types and values)
        doc.validate()

        # load all subfields,
        # this may trigger additional queries if you have ReferenceFields
        # so it may be slow
        for field in doc._fields:
            try:
                getattr(doc, field)
            except Exception:
                logging.warning(f"Could not load field {field} in Document {doc.id}")
                raise
            else:
                return True
