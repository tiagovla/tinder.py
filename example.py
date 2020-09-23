import tinder
import asyncio
import logging

# Set up logging
log = logging.getLogger(__name__)
log_tinderpy = logging.getLogger("tinder")

log.setLevel(logging.DEBUG)
log_tinderpy.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

log.addHandler(ch)
log_tinderpy.addHandler(ch)


class Client(tinder.Client):

    async def get_teasers(self):
        while True:
            teasers = await self.fetch_teasers()
            print(teasers)
            await asyncio.sleep(60)

    async def get_recs(self):
        while True:
            users = await self.fetch_recs()
            print(users)
            await asyncio.sleep(15)

    async def main(self):
        await asyncio.gather(self.get_teasers(), self.get_recs())


client = Client()

client.run("01c62fd4-51e1-4cfa-a16a-9f4ed3d24121")
