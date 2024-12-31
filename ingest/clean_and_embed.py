import requests

from utils.elastic import elastic_request


def create_clean_and_embed_pipeline():
    return elastic_request(
        url="_ingest/pipeline/clean_and_embed",
        method=requests.put,
        data={
            "description": "Ingest document remove links, and generate embeddings",
            "processors": [{
                "gsub": {
                    "field": "content",
                    # remove links from content
                    "pattern": "https?:\/\/[^\s]+\s",
                    "replacement": ""
                },
            }, {
                "gsub": {
                    "field": "content",
                    # remove links at content end (someone better at regex than I could do this in line with above)
                    "pattern": "https?:\/\/[^\s]+$",
                    "replacement": ""
                }
            }, {
                "inference": {
                    "model_id": "open-ai-embeddings",
                    "chunk"
                    "input_output": {
                        "input_field": "content",
                        "output_field": "content-embedding"
                    }
                }
            }]
        })


if __name__ == "__main__":
    try:
        pipeline_endpt = create_clean_and_embed_pipeline()
        pipeline_endpt.raise_for_status()
    except Exception as e:
        print("Error: ", e)
        print(pipeline_endpt.json())
        raise
