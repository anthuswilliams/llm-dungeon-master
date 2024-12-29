import json
import os
import requests


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
