import sys
import settings
import mappings
import parsing
import warnings
import itertools
import numpy as np
import scipy

import xml.etree.ElementTree as ET
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from glob import glob
from elastic_index import ElasticIndex
from tqdm import tqdm
from bs4 import XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning
import networkx as nx


def connect_to_elastic():
    es = Elasticsearch("http://127.0.0.1:9200")
    if not es.ping():
        sys.exit(es.info())

    return es


def index_document(es_index: ElasticIndex, bulk_data, path: str):
    with tqdm(desc=f"{path}/{es_index.index}") as pbar:
        successes = 0
        total = 0
        for ok, _ in es_index.streaming_bulk(bulk_data):
            pbar.update()
            successes += ok
            total += 1
        pbar.write(f"Finished indexing into {es_index.index}: {successes}/{total}")


def streaming_pagerank_bulk(hints, graph: nx.DiGraph):
    pageranks = nx.pagerank(graph)
    for hint in hints:
        source = hint["_source"]
        del source["hrefs"]

        url = source["url"]
        source["pagerank"] = pageranks[url]

        yield source


if __name__ == "__main__":
    warnings.filterwarnings(
        action="ignore", category=XMLParsedAsHTMLWarning, module="bs4"
    )
    warnings.filterwarnings(
        action="ignore", category=MarkupResemblesLocatorWarning, module="bs4"
    )

    es = connect_to_elastic()
    original_index = ElasticIndex(es, "original")
    original_index.create_index(mappings.ORIGINAL_MAPPING, settings.ORIGINAL_SETTINGS)

    stemmed_index = ElasticIndex(es, "stemmed")
    stemmed_index.create_index(mappings.STEMMED_MAPPING, settings.STEMMED_SETTINGS)

    paths = glob("data/*xml")
    for path in paths:
        original, stemmed = itertools.tee(parsing.parse_document(path))
        index_document(original_index, original, path)
        index_document(stemmed_index, stemmed, path)

    graph = nx.DiGraph()
    hints = list(
        scan(es, index=original_index.index, query={"query": {"match_all": {}}})
    )
    for hint in hints:
        source = hint["_source"]
        url = source["url"]

        if url not in graph:
            graph.add_node(url)

        hrefs = [(url, href) for href in source["hrefs"] if href not in graph]
        graph.add_edges_from(hrefs)

    nx.write_gexf(graph, "graph.gexf")

    pagerank_index = ElasticIndex(es, "pagerank")
    pagerank_index.create_index(mappings.PAGERANK_MAPPING, settings.PAGERANK_SETTINGS)
    index_document(pagerank_index, streaming_pagerank_bulk(hints, graph), "None")
