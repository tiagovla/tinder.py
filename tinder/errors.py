class TinderException(Exception):
    pass


class ClientException(TinderException):
    pass


class HTTPException(TinderException):
    def __init__(self, response, message):
        self.response = response
        self.status = response.status
        self.text = message

        if isinstance(message, dict):
            self.text = message.get("error")

        fmt = "Status: {0.status} Error: {1}"
        super().__init__(fmt.format(self.response, message))


class Forbidden(HTTPException):
    pass


class NotFound(HTTPException):
    pass


class InvalidData(ClientException):
    pass


class LoginFailure(ClientException):
    pass
