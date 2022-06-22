import aiohttp
import asyncio


class TinderWebSocket:
    def __init__(self, client):
        self.client = client
        self.url: str
        self.ws: aiohttp.ClientWebSocketResponse

    async def fetch_token(self):
        resp = await self.client.http.fetch_gateway()
        return resp["token"]

    async def connect(self):
        self.url = await self.client.http.get_gateway()
        self.ws = await self.client.http.ws_connect(self.url)

        self.client.loop.create_task(self.ping())
        self.client.loop.create_task(self.receive())


    async def receive(self):
        while True:
            resp = await self.ws.receive()
            resp = resp.data.hex()
            print(resp)

    async def ping(self):
        while True:
            await self.ws.send_bytes(bytearray.fromhex("2a00"))
            await asyncio.sleep(30)
