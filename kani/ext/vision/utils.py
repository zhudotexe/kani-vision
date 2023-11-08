import logging
from collections import namedtuple
from typing import IO

import aiohttp
from PIL import ImageFile

from .exceptions import ImageFormatException

log = logging.getLogger(__name__)

ImageMetadata = namedtuple("ImageMetadata", "size mime")


async def download_image(url: str, f: IO):
    """Download the image at the given URL to the given file-like object."""
    log.debug(f"Downloading image url: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            mime = resp.content_type
            if not mime.lower().startswith("image"):
                raise ImageFormatException(f"Expected an image/* MIME type, got {mime!r}")
            async for chunk in resp.content.iter_chunked(4096):
                f.write(chunk)


async def image_metadata_from_url(url: str) -> ImageMetadata:
    """Read the first few bytes of an image file to get its dimensions without downloading the entire image."""
    p = ImageFile.Parser()
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            mime = resp.content_type
            if not mime.lower().startswith("image"):
                raise ImageFormatException(f"Expected an image/* MIME type, got {mime!r}")
            async for chunk in resp.content.iter_chunked(256):
                p.feed(chunk)
                if p.image:
                    return ImageMetadata(size=p.image.size, mime=mime)
    return ImageMetadata(size=None, mime=mime)
