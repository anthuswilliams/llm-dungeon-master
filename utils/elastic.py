import json
import os
import requests


def elastic_request(data=None, method=None, url=None, headers=None):
    if not method:
        method = requests.get
    if not headers:
        headers = {"Content-Type": "application/json"}
    if data and headers["Content-Type"] == "application/json":
        data = json.dumps(data)

    return method(f"{os.getenv('ELASTIC_HOST')}/{url}",
                  headers={
                      "Accept": "application/json",
                      "Authorization": f"ApiKey {os.getenv('K8S_ELASTIC_API_KEY')}",
                      # "Authorization": f"ApiKey {os.getenv('ELASTIC_API_KEY')}",
                      **headers
    },
        verify=False,
        data=data)


def unique_values(index, field):
    return elastic_request(
        url=f"{index}/_search",
        data={"aggs": {f"{field}": {"terms": {"field": field}}}}
    )
