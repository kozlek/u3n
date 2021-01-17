from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from wsgiref.handlers import format_date_time


class HttpMethod(str, Enum):
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    PATCH = "PATCH"


class HttpStatusCode(int, Enum):
    OK = 200
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


@dataclasses.dataclass()
class H11Request:
    method: HttpMethod
    target: str
    version: str
    headers: dict[str, str]
    body: Any

    @classmethod
    def from_raw_data(cls, raw_request_data: bytes) -> H11Request:
        request_data = raw_request_data.decode("ascii")
        request_parts = request_data.split("\r\n")
        iter_parts = iter(request_parts)

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages#http_requests
        start_line = next(iter_parts)
        method, target, version = start_line.split(" ")

        headers = {}
        header_line = next(iter_parts)
        while header_line != "":
            key, _, value = header_line.partition(":")
            headers[key] = value.strip()
            header_line = next(iter_parts)

        body = next(iter_parts)
        return H11Request(
            method=method, target=target, version=version, headers=headers, body=body
        )


@dataclasses.dataclass()
class H11Response:
    status_code: HttpStatusCode
    headers: dict[str, str]
    body: bytes
    version: str = "HTTP/1.1"

    @property
    def raw(self) -> bytes:
        # add some headers
        headers = {
            "Date": format_date_time(datetime.now(tz=timezone.utc).timestamp()),
            "Content-Length": len(self.body),
            "Server": "u3n",
        } | self.headers

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages#http_responses
        status_line = f"{self.version} {self.status_code.value} {self.status_code.name}"
        headers_block = "\r\n".join([f"{k}: {v}" for k, v in headers.items()])
        return f"{status_line}\r\n{headers_block}\r\n\r\n".encode("ascii") + self.body
