class ClearPassAPI(Exception):
    pass


class TokenError(ClearPassAPI):
    def __init__(self, msg="Could not retrieve access token.") -> None:
        super().__init__(msg)
