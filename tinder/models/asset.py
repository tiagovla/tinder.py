import io
import os
from typing import Union

from collections import OrderedDict
from tinder.errors import TinderException
from tinder.state import ConnectionState


class Asset:
    __slots__ = ("_state", "url", "processed", "id")

    def __init__(self, state: ConnectionState, *, data=None, url=None):
        self._state: ConnectionState = state
        self.url = data["url"] if data else url
        self.processed = OrderedDict()
        self.id = None

        if data:
            self.id = data["id"]
            for pf in data["processedFiles"]:
                key = f"{pf['width']}x{pf['height']}"
                value = Asset(state, url=pf["url"])
                self.processed[key] = value

    async def read(self):
        if not self.url:
            raise TinderException("Invalid asset (no URL)")
        return await self._state.http.get_asset(self.url)

    async def save(self, fp: Union[str, bytes, os.PathLike, io.BytesIO], *, seek_begin=True):
        data = await self.read()
        if isinstance(fp, io.BytesIO) and fp.writable():
            wf = fp.write(data)
            if seek_begin:
                fp.seek(0)
            return wf
        else:
            with open(fp, "wb") as f:  # type: ignore
                return f.write(data)

    def __str__(self):
        return self.url if self.url else ""

    def __bool__(self):
        return self.url is not None

    def __repr__(self):
        return "<Asset url={0.url!r}>".format(self)
