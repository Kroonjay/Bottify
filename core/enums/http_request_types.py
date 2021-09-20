from enum import Enum


class HttpRequestType(Enum):
    Get = "GET"
    Post = "POST"
    Put = "PUT"
    Delete = "DELETE"
    Head = "HEAD"
