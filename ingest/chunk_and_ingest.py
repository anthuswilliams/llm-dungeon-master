import poppler
import requests

from utils.elastic import elastic_request


def create_embedding_mapping(index):
    return elastic_request(url=index,
                           method=requests.put,
                           data={
                               "mappings": {
                                   "dynamic": True,
                                   "properties": {
                                       "content-embedding": {
                                           "properties": {
                                               "predicted_value": {
                                                   "type": "dense_vector",
                                                   "index": True,
                                                   "dims": 1536,
                                                   "similarity": "cosine"
                                               }
                                           }
                                       }
                                   }
                               }
                           })


def stringify(thing):
    return " ".join(thing)


def chunk_file(path_to_file):
    doc = poppler.load_from_file(path_to_file)

    chapter_heading = []
    section_heading = []
    current_doc = []
    docs = {}
    last_font_size = 0

    for p in range(doc.pages):
        page = doc.create_page(p)
        for b in page.text_list(page.TextListOption.text_list_include_font):
            font_size = b.get_font_size()

            if font_size < last_font_size:
                if b.text != ",":
                    current_doc.append("\n--------\n")

            if font_size < 20:
                if font_size > last_font_size:
                    current_doc.append("\n")
                current_doc.append(b.text)

            if font_size > last_font_size:
                if font_size > 20:
                    # end of section
                    docs[f"{stringify(chapter_heading)}{(' - ' + stringify(section_heading)) if section_heading else ''}"] = f"{stringify(chapter_heading)}\n\n{stringify(section_heading)}\n{stringify(current_doc)}"
                    current_doc = []
                    section_heading = []
                    if font_size > 30:
                        # end of chapter
                        chapter_heading = []

            if font_size > 30 and font_size < 35:
                chapter_heading.append(b.text)

            if font_size > 20 and font_size < 30:
                section_heading.append(b.text)

            last_font_size = font_size
    return docs


def ingest(doc, title, index):
    print(title, doc)
    cleaned_title = title.replace("?", "")
    rslt = elastic_request(method=requests.put,
                           url=f"{index}/_doc/{cleaned_title}?pipeline=clean_and_embed",
                           data={"content": doc})
    return rslt


if __name__ == "__main__":

    FILENAME = "/data/Tasha’s Cauldron of Everything.pdf"
    INDEX = "tashas-cauldron-of-everything"
    docs = chunk_file(FILENAME)
    for title, item in docs.items():
        if title:
            try:
                rslt = ingest(item, title, INDEX)
                rslt.raise_for_status()
            except Exception as e:
                print("Error: ", e)
                print(rslt.json())
                raise
