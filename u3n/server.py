import asyncio
from functools import partial
from pathlib import Path
from typing import Optional

from .protocol import H11Protocol
from .request_handlers import FSBrowserRequestHandler


class HttpServer:
    def __init__(
        self,
        chroot_path: Optional[Path] = None,
        host: str = "127.0.0.1",
        port: int = 8000,
    ):
        self.chroot_path = Path.cwd() if chroot_path is None else chroot_path
        self.host = host
        self.port = port

        self.server = None

    def run(self):
        loop = asyncio.get_event_loop()
        protocol_factory = partial(
            H11Protocol,
            request_handler=FSBrowserRequestHandler(chroot_path=self.chroot_path),
        )
        server_coroutine = loop.create_server(
            protocol_factory, host=self.host, port=self.port
        )
        server = loop.run_until_complete(server_coroutine)

        print(f"Serving files at: http://{self.host}:{self.port}")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
