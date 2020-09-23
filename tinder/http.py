import asyncio
import json
import logging
from urllib.parse import quote as _uriquote

import aiohttp

from .errors import Forbidden, HTTPException, LoginFailure, NotFound

log = logging.getLogger(__name__)


async def json_or_text(response):
    try:
        if 'application/json' in response.headers['content-type']:
            return await response.json()
    except KeyError:
        pass
    return await response.text(encoding='utf-8')


class Route:
    BASE = "https://api.gotinder.com"

    def __init__(self, method, path, **params):
        self.path = path
        self.method = method
        url = self.BASE + self.path
        if params:
            self.url = url.format(
                **{k: _uriquote(v) if isinstance(v, str) else v for k, v in params.items()})
        else:
            self.url = url


class HTTPClient:
    def __init__(self, connector=None, *, proxy=None, proxy_auth=None, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.connector = connector
        self.__session = None
        self.token = None
        self.proxy = proxy
        self.proxy_auth = proxy_auth
        self.__global_over = asyncio.Event()
        self.__global_over.set()

        self.user_agent = ' '.join(["Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                                    "AppleWebKit/537.36 (KHTML, like Gecko)",
                                    "Chrome/85.0.4183.121 Safari/537.36"])

    async def login(self, token):
        self.__session = aiohttp.ClientSession(connector=self.connector)
        self.token = token

    async def close(self):
        if self.__session:
            await self.__session.close()

    async def recreate(self):
        if self.__session.closed:
            self.__session = aiohttp.ClientSession(connector=self.connector)

    async def get_asset(self, url):
        async with self.__session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 404:
                raise NotFound(resp, 'asset not found')
            elif resp.status == 403:
                raise Forbidden(resp, 'cannot retrieve asset')
            else:
                raise HTTPException(resp, 'failed to get asset')

    async def fetch_gateway(self):
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9,pt;q=0.8",
            "platform": "web",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "tinder-version": "2.54.0",
            "x-auth-token": "a8a9b9c4-5c3b-41b6-b55a-4c58fa0b47f1",
            "x-supported-image-formats": "jpeg"
        }
        return await self.request(Route('GET', '/ws/generate?locale=en'), headers=headers)

    async def request(self, route, **kwargs):
        method = route.method
        url = route.url
        headers = kwargs.get('headers')
        if headers is None:
            headers = {
                'app_version': '6.9.4',
                'platform': 'ios',
                'Content-Type': 'application/json',
                'User-Agent': 'Tinder/7.5.3 (iPhone; iOs 10.3.2; Scale/2.00)',
                'Accept': 'application/json'
            }
        if self.token:
            headers['X-Auth-Token'] = self.token
        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
        kwargs['headers'] = headers
        if self.proxy:
            kwargs['proxy'] = self.proxy
        elif self.proxy_auth:
            kwargs['proxy_auth'] = self.proxy_auth
        if not self.__global_over.is_set():
            await self.__global_over.wait()
        for tries in range(3):
            async with self.__session.request(method, url, **kwargs) as r:
                data = await json_or_text(r)

                if 300 > r.status >= 200:
                    # change to {data}
                    return data
                elif r.status in {500, 502}:
                    await asyncio.sleep(1 + tries*2)
                    continue
                elif r.status == 403:
                    raise Forbidden(r, data)
                elif r.status == 404:
                    raise NotFound(r, data)
                else:
                    raise HTTPException(r, data)

        raise HTTPException(r, data)

    def get_profile(self):
        return self.request(Route('GET', '/profile'))

    def get_user_profile(self, user_id):
        return self.request(Route('GET', '/user/{user_id}', user_id=user_id))

    def get_recs(self):
        return self.request(Route('GET', '/user/recs'))

    def get_recs2(self):
        return self.request(Route('GET', '/v2/recs/core?locale=en-US'))

    def get_teasers(self):
        return self.request(Route('GET', '/v2/fast-match/teasers'))
