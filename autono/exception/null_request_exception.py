class NullRequestException(Exception):
    def __init__(self):
        super().__init__("Request cannot be empty")
