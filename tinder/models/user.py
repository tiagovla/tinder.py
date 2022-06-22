from . import abc

from .asset import Asset

import json

from datetime import datetime


class BaseUser(abc.User):
    __slots__ = ("name", "bio", "id", "photos")

    def __init__(self, *, data):
        self._update(data)

    def __str__(self):
        return self.name

    def _update(self, data):
        self.name: str = data["name"]
        self.bio: str = data["bio"]
        self.id: str = data["_id"]

    def __repr__(self):
        return "<User name={0.name!r}>".format(self)


class User(BaseUser):
    __slots__ = BaseUser.__slots__ + ("distance_mi",)

    def __init__(self, *, data):
        self._update(data)

    def _update(self, data):
        super()._update(data)
        self.distance_mi = data["distance_mi"]
        self.photos = [Asset(data=photo) for photo in data["photos"]]


class ClientUser(BaseUser):
    __slots__ = BaseUser.__slots__ + (
        "birth_date",
        "create_date",
        "distance_filter",
        "gender",
        "gender_filter",
    )

    def __init__(self, *, data):
        self._update(data)

    def _update(self, data):
        self.name = data["name"]
        self.id = data["_id"]
        self.bio = data["bio"]
        self.birth_date = datetime.strptime(data["birth_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.create_date = datetime.strptime(data["create_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.distance_filter = data["distance_filter"]
        self.gender = data["gender"]
        self.gender_filter = data["gender_filter"]
