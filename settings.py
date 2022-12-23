ORIGINAL_SETTINGS = {"number_of_shards": 1, "number_of_replicas": 0}


STEMMED_SETTINGS = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
        "filter": {
            "russian_stop": {"type": "stop", "stopwords": "_russian_"},
            "russian_stemmer": {"type": "snowball", "language": "russian"},
        },
        "analyzer": {
            "rebuilt_russian": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "russian_stop", "russian_stemmer"],
            }
        },
    },
}


PAGERANK_SETTINGS = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
        "filter": {
            "russian_stop": {"type": "stop", "stopwords": "_russian_"},
            "russian_stemmer": {"type": "snowball", "language": "russian"},
        },
        "analyzer": {
            "rebuilt_russian": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "russian_stop", "russian_stemmer"],
            }
        },
    },
}
