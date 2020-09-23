import threading
import websockets
import asyncio


class TinderWebSocket:
    def __init__(self, client):
        self.client = client
        self.ws = None

    async def fetch_token(self):
        resp = await self.client.http.fetch_gateway()
        return resp['token']

    async def connect(self):
        token = await self.fetch_token()
        url = f"wss://keepalive.gotinder.com/ws?token={token}"
        self.ws = await websockets.connect(url)
        self.client.loop.create_task(self.run())
        self.client.loop.create_task(self.heartbeat())

    async def run(self):
        while True:
            msg = await self.ws.recv()
            print(msg)

    async def heartbeat(self):
        while True:
            print("sent")
            await self.ws.send(bytearray.fromhex("2a00"))
            await asyncio.sleep(60)


class KeepAliveHandler(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.daemon = True
