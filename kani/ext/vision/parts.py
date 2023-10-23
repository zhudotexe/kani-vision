import abc
import base64
import pathlib
from io import BytesIO

from PIL import Image
from pydantic import SkipValidation

from kani import MessagePart
from kani.utils.typing import PathLike


class ImagePart(MessagePart, abc.ABC):
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

    # props
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

        Note that this is *not* a web-suitable ``data:image/...`` string; just the raw binary of the image.
        """
        return base64.b64encode(self.bytes).decode()


class FileImagePart(ImagePart):
    path: pathlib.Path

    @property
    def image(self):
        return Image.open(self.path)

    @property
    def bytes(self):
        with open(self.path, "rb") as f:
            return f.read()


class BytesImagePart(ImagePart):
    data: bytes

    @property
    def image(self):
        return Image.open(BytesIO(self.data))

    @property
    def bytes(self):
        return self.bytes


class PillowImagePart(ImagePart, arbitrary_types_allowed=True):
    pil_image: SkipValidation[Image.Image]

    @property
    def image(self):
        return self.pil_image
