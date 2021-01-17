import asyncio
from asyncio import transports
from typing import Awaitable, Callable, Optional

from .datastructures import H11Request, H11Response, HttpStatusCode
from .templates import INTERNAL_SERVER_ERROR_PAGE


class H11Protocol(asyncio.Protocol):
    def __init__(
        self, request_handler: Callable[[H11Request], Awaitable[H11Response]], loop=None
    ):
        self.request_handler = request_handler
        self.transport: Optional[transports.Transport] = None
        self.loop = loop or asyncio.get_event_loop()

    def connection_made(self, transport: transports.Transport) -> None:
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        request = H11Request.from_raw_data(raw_request_data=data)
        self.loop.create_task(self.process_request(request=request))

    async def process_request(self, request: H11Request) -> None:
        try:
            response = await self.request_handler(request)
        except Exception as e:  # noqa
            print(e)
            response = H11Response(
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                headers={},
                body=INTERNAL_SERVER_ERROR_PAGE.encode("utf-8"),
            )
        self.transport.write(response.raw)
        self.transport.close()
