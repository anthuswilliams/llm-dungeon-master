import requests
import os
import cbor2
import json

from utils.elastic import elastic_request


def create_inference_endpoint():
    return elastic_request(url="_inference/text_embedding/open-ai-embeddings",
                           method=requests.put,
                           data={
                               "service": "openai",
                               "service_settings": {
                                   "api_key": os.getenv("OPENAI_API_KEY"),
                                   "model_id": "text-embedding-3-small"
                               }
                           })


def create_attach_and_embed_pipeline():
    return elastic_request(
        url="_ingest/pipeline/attach_and_embed",
        method=requests.put,
        data={
            "description": "Ingest PDFs, remove links, and generate generate embeddings",
            "processors": [{
                "attachment": {
                    "field": "data",
                    "indexed_chars": -1,
                    "remove_binary": True
                },
                "gsub": {
                    "field": "attachment.content",
                    # remove links from content
                    "pattern": "https?:\/\/[^\s]+\s",
                    "replacement": ""
                },
                "gsub": {
                    "field": "attachment.content",
                    # remove links at content end (someone better at regex than I could do this in line with above)
                    "pattern": "https?:\/\/[^\s]+$",
                    "replacement": ""
                },
                "inference": {
                    "model_id": "open-ai-embeddings",
                    "input_output": {
                        "input_field": "attachment.content",
                        "output_field": "content-embedding"
                    }
                }
            }]
        })


def create_embed_section_pipeline():
    return elastic_request(
        url="_ingest/pipeline/embed_section",
        method=requests.put,
        data={
            "description": "Generate embeddings",
            "processors": [{
                "inference": {
                    "model_id": "open-ai-embeddings",
                    "input_output": {
                        "input_field": "passage",
                        "output_field": "passage-embedding"
                    }
                }
            }]
        })


def create_pdf_ingest_pipeline():
    return elastic_request(
        url="_ingest/pipeline/pdf_ingest",
        method=requests.put,
        data={
            "description": "Ingest PDFs",
            "processors": [{
                "attachment": {
                    "field": "data",
                    "indexed_chars": -1,
                    "properties": ["content", "title", "date"],
                    "remove_binary": True
                }
            }, {
                "gsub": {
                    "field": "attachment.content",
                    # remove page headers
                    "pattern": "\d{2}/\d{2}/\d{2}, \d{2}:\d{2} [AP]M .+\n\nhttps:\/\/www\.dndbeyond\.com\/.+\n",
                    "replacement": ""
                },
            }, {
                "gsub": {
                    "field": "attachment.content",
                    # remove links
                    "pattern": "https:\/\/www\.dndbeyond\.com\/.+\n",
                    "replacement": ""
                }
            }]
        })


def import_files(dir_path, pipeline):
    failed = []
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if not os.path.isfile(file_path):
            continue
        with open(file_path, 'rb') as file:
            file_content = file.read()
            fname = filename.replace(" ", "-").replace(".pdf", "").lower()
        rslt = elastic_request(method=requests.put,
                               url=f"sources-raw/_doc/{fname}?pipeline={pipeline}",
                               headers={"Content-Type": "application/cbor"},
                               data=cbor2.dumps({"data": file_content}))
        try:
            rslt.raise_for_status()
        except Exception as e:
            print("Error: ", e)
            if rslt.headers.get("content-type") == "application/json":
                print(rslt.json())
            failed.append(filename)

    print("Failed: ", failed)


def create_embedding_mapping():
    return elastic_request(url="sources-chunked",
                           method=requests.put,
                           data={
                               "mappings": {
                                   "dynamic": True,
                                   "properties": {
                                       "passage-embedding": {
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


def process_each_section():
    data = {
        "query": {
            "match_all": {}
        },
        "size": 10000,
        "sort": [
            {"attachment.date": "asc"}
        ]
    }

    r = elastic_request(url="players-handbook/_search?scroll=1m",
                        method=requests.post,
                        data=data).json()
    scroll_id = r["_scroll_id"]
    while len(r["hits"]["hits"]) > 0:
        print(r["hits"]["hits"])
        bulk_submit = [[{"index": {}}, {"passage": passage["text"], "section": hit["_id"]}]
                       for hit in r["hits"]["hits"] for passage in hit["_source"]["passages"]]
        payload = "\n".join([json.dumps(j)
                            for entry in bulk_submit for j in entry])
        # use bulk endpoint to submit each paragraph as a new document
        create = requests.post("https://192.168.1.153:9200/players-handbook-chunked/_bulk?pipeline=embed_section",
                               headers={
                                   "Content-Type": "application/x-ndjson",
                                   "Accept": "application/json",
                                   "Authorization": f"ApiKey {os.getenv('ELASTIC_API_KEY')}"
                               },
                               verify=False,
                               data=f"{payload}\n")
        print(create.json())
        r = elastic_request(url="_search/scroll",
                            data={"scroll": "1m", "scroll_id": scroll_id}).json()


if __name__ == "__main__":
    try:
        inf_endpt = create_inference_endpoint()
        inf_endpt.raise_for_status()
    except Exception as e:
        if inf_endpt.json().get("error", {}).get("type") != "resource_already_exists_exception":
            print("Error: ", e)
            print(inf_endpt.json())
            raise

    for m in [create_attach_and_embed_pipeline, create_pdf_ingest_pipeline, create_embed_section_pipeline]:
        try:
            pipeline_endpt = m()
            pipeline_endpt.raise_for_status()
        except Exception as e:
            print("Error: ", e)
            print(pipeline_endpt.json())
            raise

    import_files(dir_path="/data", pipeline="pdf_ingest")
    # create_embedding_mapping()
    # process_each_section()
