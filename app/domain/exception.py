class ServerException(Exception):
    def __init__(
        self, user_message: str = "", log_message: str = "", http_code: int = 500
    ):
        self.http_code = http_code
        self.user_message = user_message
        self.log_message = log_message
        super().__init__(log_message)
