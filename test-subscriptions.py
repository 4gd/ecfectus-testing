import asyncio
import json
import uuid
from pprint import pformat

import websockets

from util import API_URL


GQL_CONNECTION_INIT = 'connection_init' # Client -> Server
GQL_CONNECTION_ACK = 'connection_ack' # Server -> Client
GQL_CONNECTION_ERROR = 'connection_error' # Server -> Client
GQL_CONNECTION_KEEP_ALIVE = 'ka' # Server -> Client | NOTE: The keep alive message type does not follow the standard due to connection optimizations
GQL_CONNECTION_TERMINATE = 'connection_terminate' # Client -> Server
GQL_START = 'start' # Client -> Server
GQL_DATA = 'data' # Server -> Client
GQL_ERROR = 'error' # Server -> Client
GQL_COMPLETE = 'complete' # Server -> Client
GQL_STOP = 'stop' # Client -> Server

query = """
  subscription {
    events {
      ... on SoldierPosition {
        trainee {
            user { username }
        }
        x, y
      }
    }
  }
""".replace("\n", "")

register = {
    'id': str(uuid.uuid4()),
    'payload': {
        "query": query
    },
    'type': 'start'
}

async def main():
    async with websockets.connect(API_URL, subprotocols=["graphql-ws"]) as websocket:
        payload = {"type": GQL_CONNECTION_INIT}
        print("Send init message")
        await websocket.send(json.dumps(payload))

        first = True
        while 1:
            resp = await websocket.recv()
            resp = json.loads(resp)
            print("Resp:", resp)
            if resp["type"] == GQL_CONNECTION_ACK:
                print("Connection acknowledged")
                print("Send sub message 1")
                print(pformat(json.dumps(register), indent=2))
                await websocket.send(json.dumps(register))
            elif resp["type"] == GQL_CONNECTION_KEEP_ALIVE:
                print("I want to liiiiiiiiiiiiive")
                if first:
                    # print("Send sub message 1")
                    # print(pformat(json.dumps(register), indent=2))
                    # await websocket.send(json.dumps(register))
                    first = False
            elif resp["type"] == GQL_DATA:
                print("Got data yo")
                print(resp)
            else:
                print("other resp:")
                print(pformat(resp, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
