![banner](https://user-images.githubusercontent.com/30515389/175213919-b0efccd9-c337-447a-b3f4-7c5ecb1d134e.png)

[![PyPI license](https://img.shields.io/pypi/l/tinder.py.svg)](https://pypi.python.org/pypi/tinder.py/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/tinder.py.svg)](https://pypi.python.org/pypi/tinder.py/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/tinder.py.svg)](https://pypi.python.org/pypi/tinder.py/)
[![DeepSource](https://deepsource.io/gh/tiagovla/tinder.py.svg/?label=active+issues)](https://deepsource.io/gh/tiagovla/tinder.py/?ref=repository-badge)
[![Documentation Status](https://readthedocs.org/projects/tinder-py/badge/?version=latest)](https://tinder-py.readthedocs.io/en/latest/)

Tinder.py is an asynchronous Python wrapper around the Tinder API. 

## Installation:

```sh
python -m pip install -U tinder.py
```
## Getting Started:

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
    client.run("12345678-1234-1234-1234-123456789abc") # api token
```

## Token:
Log in to [tinder](https://tinder.com) on a browser, use the "TinderWeb/APIToken" found in Developer Tools (Ctrl+Shift+I).
![image](https://user-images.githubusercontent.com/30515389/175216307-d5b1bf08-5080-41c7-a250-ae252b095ab6.png)
