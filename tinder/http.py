import asyncio
import logging
from typing import Optional, Union, Any, Dict
from urllib.parse import quote as _uriquote

import aiohttp
from .errors import Forbidden, HTTPException, NotFound

log = logging.getLogger(__name__)


async def json_or_text(response) -> Union[Dict[str, Any], str]:
    try:
        if "application/json" in response.headers["content-type"]:
            return await response.json()
    except KeyError:
        pass
    return await response.text(encoding="utf-8")


class Route:
    BASE = "https://api.gotinder.com"

    def __init__(self, method, path, **params):
        self.path = path
        self.method = method
        url = self.BASE + self.path
        if params:
            self.url = url.format(
                **{k: _uriquote(v) if isinstance(v, str) else v for k, v in params.items()}
            )
        else:
            self.url = url


class HTTPClient:
    def __init__(
        self,
        connector: Optional[aiohttp.BaseConnector] = None,
        *,
        proxy: Optional[str] = None,
        proxy_auth: Optional[aiohttp.BasicAuth] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self.connector: Optional[aiohttp.BaseConnector] = connector
        self.__session: aiohttp.ClientSession
        self.token: Optional[str] = None
        self.proxy: Optional[str] = proxy
        self.proxy_auth: Optional[aiohttp.BasicAuth] = proxy_auth
        self.__global_over: asyncio.Event = asyncio.Event()
        self.__global_over.set()
        self.user_agent: str = " ".join(
            [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "AppleWebKit/537.36 (KHTML, like Gecko)",
                "Chrome/85.0.4183.121 Safari/537.36",
            ]
        )

    async def login(self, token) -> None:
        self.__session = aiohttp.ClientSession(connector=self.connector)
        self.token = token

    async def close(self) -> None:
        if self.__session:
            await self.__session.close()

    async def recreate(self) -> None:
        if self.__session and self.__session.closed:
            self.__session = aiohttp.ClientSession(connector=self.connector)

    async def get_asset(self, url):
        async with self.__session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 404:
                raise NotFound(resp, "asset not found")
            elif resp.status == 403:
                raise Forbidden(resp, "cannot retrieve asset")
            else:
                raise HTTPException(resp, "failed to get asset")

    async def request(self, route: Route, **kwargs) -> Any:
        method = route.method
        url = route.url
        headers = kwargs.get("headers")
        if headers is None:
            headers = {
                "app_version": "6.9.4",
                "platform": "ios",
                "Content-Type": "application/json",
                "User-Agent": "Tinder/7.5.3 (iPhone; iOs 10.3.2; Scale/2.00)",
                "Accept": "application/json",
            }
        if self.token:
            headers["X-Auth-Token"] = self.token
        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers
        if self.proxy:
            kwargs["proxy"] = self.proxy
        elif self.proxy_auth:
            kwargs["proxy_auth"] = self.proxy_auth
        if not self.__global_over.is_set():
            await self.__global_over.wait()
        for tries in range(3):
            async with self.__session.request(method, url, **kwargs) as r:
                data = await json_or_text(r)
                if 300 > r.status >= 200:
                    return data
                elif r.status in {500, 502}:
                    await asyncio.sleep(1 + tries * 2)
                    continue
                elif r.status == 403:
                    raise Forbidden(r, data)
                elif r.status == 404:
                    raise NotFound(r, data)
                else:
                    raise HTTPException(r, data)
        raise RuntimeError("Unreachable code in HTTP handling")

    async def fetch_gateway(self):
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9,pt;q=0.8",
            "platform": "web",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "tinder-version": "2.54.0",
            "x-auth-token": self.token,
            "x-supported-image-formats": "jpeg",
        }
        return await self.request(Route("GET", "/ws/generate?locale=en"), headers=headers)

    async def get_gateway(self) -> str:
        token = (await self.fetch_gateway())["token"]
        return f"wss://keepalive.gotinder.com/ws?token={token}"

    async def ws_connect(self, url: str, *, compress: int = 0) -> aiohttp.ClientWebSocketResponse:
        kwargs = {
            "proxy_auth": self.proxy_auth,
            "proxy": self.proxy,
            "max_msg_size": 0,
            "timeout": 30.0,
            "autoclose": False,
            "headers": {
                "User-Agent": self.user_agent,
            },
            "compress": compress,
        }

        return await self.__session.ws_connect(url, **kwargs)

    def get_profile(self):
        return self.request(Route("GET", "/profile"))

    def get_user_profile(self, user_id: Union[str, int]):
        return self.request(Route("GET", "/user/{user_id}", user_id=user_id))

    def get_recs(self):
        return self.request(Route("GET", "/user/recs"))

    def get_recs2(self):
        params = {"locale": "en"}
        return self.request(Route("GET", "/v2/recs/core"), params=params)

    def get_teasers(self):
        return self.request(Route("GET", "/v2/fast-match/teasers"))

    def like(self, user_id: Union[str, int]):
        return self.request(Route("POST", "/like/{user_id}", user_id=user_id))

    def skip(self, user_id: Union[str, int]):
        return self.request(Route("POST", "/pass/{user_id}", user_id=user_id))

    # untested:

    def get_teaser(self):
        params = {"locale": "en", "type": "recently-active"}
        return self.request(Route("GET", "/v2/fast-match/teaser"), params=params)

    def notification(self):
        params = {"locale": "en"}
        return self.request(Route("PUT", "/v2/push/notifications"), params=params)

    def matches(self, count: int = 60, message: int = 0):
        params = {"locale": "en", "count": count, "message": message}
        return self.request(Route("GET", "/v2/matches"), params=params)

    def explore(self):
        params = {"locale": "en"}
        return self.request(Route("GET", "/v2/explore"), params=params)

    def my_likes(self):
        params = {"locale": "en"}
        return self.request(Route("GET", "/v2/my-likes"), params=params)

    def unmatch(self, match_id: str):
        return self.request(Route("DELETE", "/user/matches/{match_id}", match_id=match_id))

    def send_message(self, match_id: str, message: str):
        payload = {"message", message}
        return self.request(
            Route("POST", "/user/matches/{match_id}", match_id=match_id), data=payload
        )

    def likes_count(self):
        return self.request(Route("POST", "/v2/fast-match/count"))

    def update(self):
        params = {"locale": "en"}
        return self.request(Route("GET", "/updates"), params=params)

    def meta(self, lat: float, lon: float, force_fetch_resources: bool = True):
        params = {"locale": "en"}
        payload = {"lat": lat, "lon": lon, "force_fetch_resources": str(force_fetch_resources)}
        return self.request(Route("POST", "/v2/meta"), params=params, data=payload)

    # TODO: support endpoints
    # https://api.gotinder.com/v2/matches/{id}/messages
    # https://api.gotinder.com/user/matches/{id}
    # https://api.gotinder.com/v2/matches
    # https://api.gotinder.com/like/id/super?locale=en POST
