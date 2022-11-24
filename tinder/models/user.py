from datetime import datetime
import logging

from . import abc
from ..state import ConnectionState
from .asset import Asset

log = logging.getLogger(__name__)


class BaseUser(abc.User):
    __slots__ = ("_state", "name", "bio", "id", "photos")

    def __init__(self, state: ConnectionState, *, data):
        self._state: ConnectionState = state
        BaseUser._update(self, data)

    def __str__(self):
        return self.name

    def _update(self, data):
        self.name: str = data["name"]
        self.bio: str = data.get("bio", "")
        self.id: str = data["_id"]

    def __repr__(self):
        return "<User name={0.name!r}>".format(self)


class User(BaseUser):
    __slots__ = BaseUser.__slots__ + ("distance_mi",)

    def __init__(self, state: ConnectionState, *, data):
        super().__init__(state, data=data)
        self._update(data)

    def _update(self, data):
        self.distance_mi = data["distance_mi"]
        self.photos = [Asset(self._state, data=photo) for photo in data["photos"]]

    async def like(self):
        log.debug(f"Liked user {self}")
        await self._state.http.like(self.id)

    async def skip(self):
        log.debug(f"Skipped user {self}")
        await self._state.http.skip(self.id)


class ClientUser(BaseUser):
    __slots__ = BaseUser.__slots__ + (
        "birth_date",
        "create_date",
        "distance_filter",
        "gender",
        "gender_filter",
    )

    def __init__(self, state: ConnectionState, *, data):
        super().__init__(state, data=data)
        self._update(data)

    def _update(self, data):
        self.name = data["name"]
        self.id = data["_id"]
        self.bio = data.get("bio", "")
        self.birth_date = datetime.strptime(data["birth_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.create_date = datetime.strptime(data["create_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.distance_filter = data["distance_filter"]
        self.gender = data["gender"]
        self.gender_filter = data["gender_filter"]
