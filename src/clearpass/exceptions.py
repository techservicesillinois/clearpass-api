class ClearPassAPI(Exception):
	pass

class TokenError(ClearPassAPI):
    def __init__(self) -> None:
		mesg = "Could not retrieve access token."
        super().__init__(mesg)
