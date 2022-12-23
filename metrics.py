import sys
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from tqdm import tqdm
from elastic_index import ElasticIndex


K = 20


def connect_to_elastic():
    es = Elasticsearch("http://127.0.0.1:9200")
    if not es.ping():
        sys.exit(es.info())

    return es


def parse_xml_files(queries_file_path, relevant_file_path):
    relevance = {}
    queries = {}

    with open(queries_file_path, encoding="cp1251", errors="ignore") as qfile, open(
        relevant_file_path, encoding="cp1251", errors="ignore"
    ) as rfile:
        qsoup = BeautifulSoup(qfile, "xml")
        rsoup = BeautifulSoup(rfile, "xml")

        ids = set()
        for document in rsoup.find_all("document"):
            task_id = document.parent["id"]
            ids.add(task_id)

            doc_id = document["id"]
            doc_rel = document["relevance"]

            if task_id in relevance:
                relevance[task_id][doc_id] = doc_rel
            else:
                relevance[task_id] = {doc_id: doc_rel}

        for task in qsoup.find_all("task", id=list(ids)):
            task_id = task["id"]
            queries[task_id] = task.querytext.string

    return queries, relevance


def count_relevant(search_result, relevance: dict):
    hits = search_result["hits"]["hits"]
    relevant = 0
    for hint in hits:
        source = hint["_source"]
        hint_id = source["id"]

        if relevance.get(hint_id) == "vital":
            relevant += 1

    return relevant


def query_metrics(index: ElasticIndex, qtext, query, relevance: dict):
    query_relevant = count_relevant(query, relevance)
    total_relevant = len([rel for rel in relevance.values() if rel == "vital"])

    pm = query_relevant / K
    rm = query_relevant / total_relevant if total_relevant != 0 else 0.0

    rpm_search_result = index.search_content(
        qtext, total_relevant, index.index == "pagerank"
    )
    rpm_relevant = count_relevant(rpm_search_result, relevance)
    rpm = rpm_relevant / total_relevant if total_relevant != 0 else 0.0

    return [pm, rm, rpm]


def index_metrics(index: ElasticIndex, queries, relevance):
    metrics = {}
    for qid, qtext in tqdm(queries.items(), desc=index.index):
        result = index.search_content(qtext, K, index.index == "pagerank")
        qmetrics = query_metrics(index, qtext, result, relevance[qid])
        metrics[qid] = qmetrics

    map = sum([metric[0] for metric in metrics.values()]) / len(metrics)

    return map, metrics


def main():
    es = connect_to_elastic()
    queries, relevance = parse_xml_files("web2008_adhoc.xml", "relevant_table_2009.xml")

    original_index = ElasticIndex(es, "original")
    stemmed_index = ElasticIndex(es, "stemmed")
    pagerank_index = ElasticIndex(es, "pagerank")
    indexes = [original_index, stemmed_index, pagerank_index]

    for index in indexes:
        map, metrics = index_metrics(index, queries, relevance)
        with open(f"{index.index}_metrics.txt", "w+", encoding="utf-8") as file:
            file.write(f"MAP@20: {map:.3f}\n")
            for qid, qmetric in metrics.items():
                pm = qmetric[0]
                rm = qmetric[1]
                rpm = qmetric[2]

                file.write(
                    f"{qid}, P@20: {pm:.3f}, R@20: {rm:.3f}, R-percision@20: {rpm:.3f}\n"
                )


if __name__ == "__main__":
    main()
