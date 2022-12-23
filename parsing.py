import base64
import re


from bs4 import BeautifulSoup


def decode(text):
    decoded = base64.b64decode(text)
    return decoded.decode("cp1251")


def parse_content(html, doc_url):
    soup = BeautifulSoup(html, "lxml")

    links = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if (
            href.startswith(doc_url) or href.startswith("#") or href.startswith("?")
        ):  # Игнорируем ссылки на содержимое документа
            continue

        links.add(href)

    for data in soup.find_all(["a", "style", "script"]):
        data.decompose()

    text = soup.get_text(" ", strip=True)
    text = "" if text is None else re.sub("\s+", " ", text)
    text = re.sub("document\.write\(.+?\)", "", text)  # Удаляем остатки скриптов

    return text, list(links)


def parse_document(path: str):
    with open(path, encoding="ascii", errors="ignore") as file:
        soup = BeautifulSoup(file, "xml")

        for document in soup.find_all("document"):
            content = document.content

            html = decode(content.string)
            doc_id = document.docID.string
            doc_url = document.docURL.string
            text, links = parse_content(html, doc_url)

            yield {
                "_source": {
                    "id": doc_id,
                    "url": doc_url,
                    "content": text,
                    "hrefs": links,
                }
            }
