import requests

from util import API_URL

base_url = API_URL.replace("ws:", "http:")

# query {
#   sessions {
#     sessionId
#   }
# }

query = """
query {
  sessions {
    trainees {
      user {
        name
      }
      wearable {
        devices {
          type
        }
      }
    }
  }

}
"""



# query = query.replace(" ", "").replace("\n","")
query = query.replace("\n","")
query = query.replace("query", "query=")
# print(query)
# payload = {"query": query}
# r = requests.get(base_url, params=payload)
r = requests.get(base_url + "?" + query)

# print(r.url)
from pprint import pformat
print(pformat(r.json(), indent=2))