# tinder.py
Tinder.py is an asynchronous Python wrapper around the Tinder API. 

## Demo

```python
import asyncio
import tinder

class Client(tinder.Client):
    teaser_ids = set()

    async def get_teasers(self):
        while True:
            teasers = await self.fetch_teasers()
            self.teaser_ids |= {teaser.id for teaser in teasers}
            await asyncio.sleep(60)

    async def get_recs(self):
        while True:
            users = await self.fetch_recs()
            print(f"fetched {len(users)} users")
            for user in users:
                photo_ids = {photo.id for photo in user.photos}
                if not self.teaser_ids.isdisjoint(photo_ids):
                    await user.like()
            await asyncio.sleep(60)

    async def main(self):
        await asyncio.gather(self.get_teasers(), self.get_recs())


if __name__ == "__main__":
    client = Client()
    client.run("12345678-1234-1234-1234-123456789abc")
```
