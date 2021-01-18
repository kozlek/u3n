import mimetypes
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cached_property
from pathlib import Path
from stat import S_ISDIR
from typing import Literal, Optional, TypedDict, Union

from u3n.datastructures import H11Response, HttpStatusCode
from u3n.templates import (
    DIRECTORY_LISTING_ITEM_TEMPLATE,
    DIRECTORY_LISTING_TEMPLATE,
    NOT_FOUND_PAGE,
)


class ListingItem(TypedDict):
    name: str
    last_modified: str
    size: str
    html_path: str
    type: Union[Literal["dir"], Literal["file"]]


class FileContainer(TypedDict):
    name: str
    mime: str
    content: bytes


class AbstractRenderer(ABC):
    """Abstract renderer for FSBrowserRequestHandler.

    You must subclass it and implements render_directory, render_file and
    render_not_found to use it.

    It already provides utils methods like get_directory_listing and get_file_info.
    """
    __slots__ = ("chroot_path", "relative_requested_path", "action")

    def __init__(
        self,
        chroot_path: Path,
        relative_requested_path: Path,
        action: Optional[str] = None,
    ):
        self.chroot_path = chroot_path
        self.relative_requested_path = relative_requested_path
        self.action = action

    @cached_property
    def absolute_requested_path(self) -> Path:
        return self.chroot_path / self.relative_requested_path.relative_to(
            self.relative_requested_path.anchor
        )

    @cached_property
    def is_root_directory(self) -> bool:
        return self.chroot_path == self.absolute_requested_path

    @staticmethod
    def format_mtime(mtime: float) -> str:
        return datetime.fromtimestamp(mtime).isoformat()

    def get_directory_listing(self) -> list[ListingItem]:
        listing: list[ListingItem] = []
        if not self.is_root_directory:
            mtime = self.absolute_requested_path.parent.stat().st_mtime
            listing.append(
                ListingItem(
                    name="..",
                    last_modified=self.format_mtime(mtime),
                    size="-",
                    html_path=str(self.relative_requested_path.parent),
                    type="dir",
                )
            )

        for item in self.absolute_requested_path.iterdir():
            item_stat = item.stat()
            # TODO: handle browser TZ
            last_modified = datetime.fromtimestamp(item_stat.st_mtime).isoformat()
            html_path = str(self.relative_requested_path / item.name)

            # use S_ISDIR to avoid a second call to stat()
            if S_ISDIR(item_stat.st_mode):
                listing_item = ListingItem(
                    name=item.name,
                    last_modified=last_modified,
                    size="-",
                    html_path=html_path,
                    type="dir",
                )
            else:
                listing_item = ListingItem(
                    name=item.name,
                    last_modified=last_modified,
                    size=str(item_stat.st_size),  # TODO: make size human readable
                    html_path=html_path,
                    type="file",
                )
            listing.append(listing_item)

        return listing

    def get_file_info(self) -> FileContainer:
        mime, _ = mimetypes.guess_type(self.absolute_requested_path)
        return FileContainer(
            name=self.absolute_requested_path.name,
            mime=mime,
            content=self.absolute_requested_path.read_bytes(),
        )

    @abstractmethod
    def render_directory(self, directory_listing: list[ListingItem]) -> H11Response:
        ...

    @abstractmethod
    def render_file(self, file_container: FileContainer) -> H11Response:
        ...

    @abstractmethod
    def render_not_found(self) -> H11Response:
        ...

    def render(self) -> H11Response:
        if self.absolute_requested_path.is_dir():
            return self.render_directory(directory_listing=self.get_directory_listing())
        elif self.absolute_requested_path.is_file():
            return self.render_file(file_container=self.get_file_info())
        else:  # not found
            return self.render_not_found()


class BasicHtmlRenderer(AbstractRenderer):
    """Render directories with a pure (basic) HTML interface.
    It offers a direct download button to download files as attachment.
    """

    def render_directory(self, directory_listing: list[ListingItem]) -> H11Response:
        rows = []
        for item in directory_listing:
            if item["type"] == "dir":
                rows.append(DIRECTORY_LISTING_ITEM_TEMPLATE % (item | {"actions": ""}))
            elif item["type"] == "file":
                actions = f"""
                <a href="{item["html_path"]}?action=download" target="_blank">Download</a>
                """
                rows.append(
                    DIRECTORY_LISTING_ITEM_TEMPLATE % (item | {"actions": actions})
                )

        content = DIRECTORY_LISTING_TEMPLATE % {
            "relative_requested_path": str(self.relative_requested_path),
            "listing_html": "".join(rows),
        }
        raw_content = content.encode("utf-8")

        return H11Response(
            status_code=HttpStatusCode.OK,
            headers={"Content-Type": "text/html; charset=utf-8"},
            body=raw_content,
        )

    def render_file(self, file_container: FileContainer) -> H11Response:
        headers = {}
        if (mime := file_container["mime"]) is not None:
            headers["Content-Type"] = mime
        if self.action == "download":
            headers[
                "Content-Disposition"
            ] = f"attachment; filename={file_container['name']}"

        body = file_container["content"]
        return H11Response(status_code=HttpStatusCode.OK, headers=headers, body=body)

    def render_not_found(self) -> H11Response:
        return H11Response(
            status_code=HttpStatusCode.NOT_FOUND,
            headers={},
            body=NOT_FOUND_PAGE.encode("utf-8"),
        )
