import io

import aiohttp
from collections import OrderedDict
from tinder.errors import (
    Forbidden,
    HTTPException,
    LoginFailure,
    NotFound,
    TinderException,
)


class Asset:
    __slots__ = ("url", "processed", "id")

    def __init__(self, *, data=None, url=None):
        self.url = data["url"] if data else url
        self.processed = OrderedDict()
        self.id = None

        if data:
            self.id = data["id"]
            for pf in data["processedFiles"]:
                key = f"{pf['width']}x{pf['height']}"
                value = Asset(url=pf["url"])
                self.processed[key] = value

    async def read(self):
        if not self.url:
            raise TinderException("Invalid asset (no URL)")

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                if resp.status == 200:
                    return await resp.read()
                elif resp.status == 404:
                    raise NotFound(resp, "asset not found")
                elif resp.status == 403:
                    raise Forbidden(resp, "cannot retrieve asset")
                else:
                    raise HTTPException(resp, "failed to get asset")

    async def save(self, fp, *, seek_begin=True):
        data = await self.read()
        if isinstance(fp, io.IOBase) and fp.writable():
            wf = fp.write(data)
            if seek_begin:
                fp.seek(0)
            return wf
        else:
            with open(fp, "wb") as f:
                return f.write(data)

    def __str__(self):
        return self.url if self.url else ""

    def __bool__(self):
        return self.url is not None

    def __repr__(self):
        return "<Asset url={0.url!r}>".format(self)
