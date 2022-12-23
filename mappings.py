ORIGINAL_MAPPING = {
    "properties": {
        "id": {"type": "text"},
        "url": {"type": "text"},
        "content": {"type": "text"},
        "hrefs": {"type": "text"},
    }
}


STEMMED_MAPPING = {
    "properties": {
        "content": {"type": "text", "analyzer": "rebuilt_russian"},
        "id": {"type": "text"},
        "url": {"type": "text"},
        "hrefs": {"type": "text"},
    }
}


PAGERANK_MAPPING = {
    "properties": {
        "content": {"type": "text", "analyzer": "rebuilt_russian"},
        "id": {"type": "text"},
        "url": {"type": "text"},
        "pagerank": {"type": "rank_feature"},
    }
}
