from urllib.parse import parse_qs, urlparse
from pathlib import Path

from .datastructures import H11Request, H11Response
from .renderers import AbstractRenderer, BasicHtmlRenderer
from .utils import run_in_thread


class FSBrowserRequestHandler:
    __slots__ = ("chroot_path", "renderer_class")

    def __init__(
        self,
        chroot_path: Path,
        renderer_class: type[AbstractRenderer] = BasicHtmlRenderer,
    ):
        self.chroot_path = chroot_path
        self.renderer_class = renderer_class

    async def __call__(self, request: H11Request) -> H11Response:
        parse_result = urlparse(request.target)
        query_params = parse_qs(parse_result.query)

        relative_requested_path = Path(parse_result.path)
        action = query_params["action"][0] if "action" in query_params else None

        renderer = self.renderer_class(
            chroot_path=self.chroot_path,
            relative_requested_path=relative_requested_path,
            action=action,
        )
        # run the renderer in a thread as it does a lot of fs calls
        return await run_in_thread(renderer.render)
