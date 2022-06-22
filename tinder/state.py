import gc


class ConnectionState:
    def __init__(self, *, dispatch, handlers, http, loop, **options):
        self.loop = loop
        self.http = http
        self.dispatch = dispatch
        self.handlers = handlers
        self.heartbeat_timeout = options.get("heartbeat_timeout", 60.0)

    def clear(self):
        self.client_user = None
        self._users = {}
        self._teasers = {}
        self._messages = []
        gc.collect()

    def call_handlers(self, key, *args, **kwargs):
        try:
            func = self.handlers[key]
        except KeyError:
            pass
        else:
            func(*args, **kwargs)

    def store_user(self, user):
        try:
            return self._users[user.id]
        except KeyError:
            self._users[user.id] = user
            return user
