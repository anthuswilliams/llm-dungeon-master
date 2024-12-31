import json
import os
import requests


ELASTIC_HOST = "https://192.168.1.153:9200"


def elastic_request(data=None, method=None, url=None, headers=None):
    if not method:
        method = requests.get
    if not headers:
        headers = {"Content-Type": "application/json"}
    if data and headers["Content-Type"] == "application/json":
        data = json.dumps(data)

    return method(f"{ELASTIC_HOST}/{url}",
                  headers={
                      "Accept": "application/json",
                      "Authorization": f"ApiKey {os.getenv('ELASTIC_API_KEY')}",
                      **headers
                  },
                  verify=False,
                  data=data)
