from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from typing import Any


class ElasticIndex:
    def __init__(self, es: Elasticsearch, index: str):
        self.__es = es
        self.index = index

    def create_index(
        self, mappings: dict[str, Any], settings: dict[str, Any], force=True
    ):
        exists = self.__es.indices.exists(index=self.index)

        if exists and not force:
            return

        if exists and force:
            self.__es.indices.delete(index=self.index)

        return self.__es.indices.create(
            index=self.index, mappings=mappings, settings=settings
        )

    def streaming_bulk(self, actions):
        return streaming_bulk(self.__es, index=self.index, actions=actions)

    def __query(text: str):
        return {"match": {"content": {"query": text}}}

    def __pagerank_query(text: str):
        return {
            "bool": {
                "must": {"match": {"content": {"query": text}}},
                "should": {
                    "rank_feature": {"field": "pagerank", "saturation": {"pivot": 10}}
                },
            }
        }

    def search_content(self, text: str, size: int, pagerank=False):
        query = (
            ElasticIndex.__query(text)
            if not pagerank
            else ElasticIndex.__pagerank_query(text)
        )
        return self.__es.search(index=self.index, query=query, size=size, from_=0)
