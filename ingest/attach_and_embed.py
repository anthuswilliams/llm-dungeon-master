import requests
import json
import os
import base64


ELASTIC_HOST = "https://192.168.1.153:9200"


def elastic_request(data=None, method=None, url=None):
    if method == None:
        method = requests.get
    if data:
        data = json.dumps(data)

    return method(f"{ELASTIC_HOST}/{url}",
                  headers={
                      "Content-Type": "application/json",
                      "Accept": "application/json",
                      "Authorization": f"ApiKey {os.getenv('ELASTIC_API_KEY')}"
                  },
                  verify=False,
                  data=data)


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
                    "pattern": "http?s:\/\/[^\s]+\s",
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


def encode_documents(dir_path):
    encoded_files = []
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as file:
                file_content = file.read()
                encoded_content = base64.b64encode(
                    file_content).decode('utf-8')
                encoded_files.append((filename, encoded_content))

    return encoded_files


def import_files(files):
    for filename, contents in files:
        elastic_request(
            method=requests.put, url=f"players-handbook/_doc/{filename}?pipeline=attach_and_chunk", data={"data": contents})


if __name__ == "__main__":
    try:
        inf_endpt = create_inference_endpoint()
        inf_endpt.raise_for_status()
    except Exception as e:
        if inf_endpt.json().get("error", {}).get("type") != "resource_already_exists_exception":
            print("Error: ", e)
            print(inf_endpt.json())
            raise

    try:
        pipeline_endpt = create_attach_and_embed_pipeline()
        pipeline_endpt.raise_for_status()
    except Exception as e:
        print("Error: ", e)
        print(pipeline_endpt.json())
        raise

    encoded_files = encode_documents(
        dir_path="/data/Player's Handbook 5e (2014)")

    import_files(encoded_files)
