import abc
import base64
import functools
import pathlib
from io import BytesIO

from PIL import Image
from pydantic import ConfigDict, SkipValidation

from kani import MessagePart
from kani.utils.typing import PathLike
from .exceptions import RemoteImageError
from .utils import download_image, image_metadata_from_url


class ImagePart(MessagePart, abc.ABC):
    """Base class for all image message parts.

    Generally, you shouldn't construct this directly - instead, use one of the classmethods to initialize the image from
    a file path, binary, or Pillow image.
    """

    model_config = ConfigDict(ignored_types=(functools.cached_property,))

    # constructors
    @staticmethod
    def from_path(fp: PathLike):
        """Load an image from a path on the local filesystem."""
        return FileImagePart(path=fp)

    @staticmethod
    def from_bytes(data: bytes):
        """Load an image from binary data in memory."""
        return BytesImagePart(data=data)

    @staticmethod
    def from_image(image: Image.Image):
        """Create an image part from an existing :class:`PIL.Image.Image`."""
        return PillowImagePart(pil_image=image)

    @classmethod
    async def from_url(cls, url: str, remote: bool = True):
        """Create an image part from a URL.

        If *remote* is True, this will not download the image - it will be up to the engine to do so!

        .. attention::
            Note that this classmethod is *asynchronous*, unlike the other classmethods!

            This is because we need to check the image headers and metadata before returning a valid image part.
        """
        if not remote:
            io = BytesIO()
            await download_image(url, io)
            return BytesImagePart(data=io.getvalue())
        size, mime = await image_metadata_from_url(url)
        return RemoteURLImagePart(url=url, size_=size, mime_=mime)

    # interface
    @property
    def image(self) -> Image.Image:
        """Get a :class:`PIL.Image.Image` representing the image."""
        raise NotImplementedError

    @property
    def bytes(self) -> bytes:
        """The binary image data."""
        io = BytesIO()
        self.image.save(io, format="PNG")
        return io.getvalue()

    @property
    def b64(self) -> str:
        """The binary image data encoded in a base64 string.

        Note that this is *not* a web-suitable ``data:image/...`` string; just the raw binary of the image. Use
        :attr:`b64_uri` for a web-suitable string.
        """
        return base64.b64encode(self.bytes).decode()

    @property
    def b64_uri(self) -> str:
        """Get the binary image data encoded in a web-suitable base64 string."""
        return f"data:{self.mime};base64,{self.b64}"

    # metadata
    @property
    def size(self) -> tuple[int, int]:
        """Get the size of the image, in pixels."""
        return self.image.size

    @property
    def mime(self) -> str:
        """Get the MIME filetype of the image."""
        img_format = self.image.format
        return Image.MIME.get(img_format, f"image/{img_format.lower()}")


class FileImagePart(ImagePart):
    """An image whose data lives at the given file path.

    Use :meth:`.ImagePart.from_path` to construct.
    """

    path: pathlib.Path

    @property
    def image(self):
        return Image.open(self.path)

    @property
    def bytes(self):
        with open(self.path, "rb") as f:
            return f.read()


class BytesImagePart(ImagePart):
    """An image whose data lives in memory.

    Use :meth:`.ImagePart.from_bytes` to construct.
    """

    data: bytes

    @property
    def image(self):
        return Image.open(BytesIO(self.data))

    @property
    def bytes(self):
        return self.data


class PillowImagePart(ImagePart, arbitrary_types_allowed=True):
    """An image represented by a Pillow Image.

    Use :meth:`.ImagePart.from_image` to construct.
    """

    pil_image: SkipValidation[Image.Image]

    @property
    def image(self):
        return self.pil_image


class RemoteURLImagePart(ImagePart):
    """A reference to a remote image stored at the given URL.

    Use :meth:`.ImagePart.from_url` to construct.
    """

    url: str
    size_: tuple[int, int]
    mime_: str

    @property
    def image(self):
        raise RemoteImageError(
            "This engine does not support remote images. Use `await ImagePart.from_url(url, remote=False)` to download"
            " the image before using it in this engine."
        )

    @property
    def size(self):
        return self.size_

    @property
    def mime(self):
        return self.mime_
