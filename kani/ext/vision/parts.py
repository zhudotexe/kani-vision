from PIL import Image

from kani import MessagePart
from kani.utils.typing import PathLike


class ImagePart(MessagePart):
    # constructors
    @classmethod
    def from_path(cls, fp: PathLike):
        pass

    @classmethod
    def from_bytes(cls, data: bytes):
        pass

    @classmethod
    def from_image(cls, image: Image):
        pass

    # props
    @property
    def image(self) -> Image:
        return

    @property
    def bytes(self) -> bytes:
        return

    @property
    def b64(self) -> str:
        return


class FileImagePart(ImagePart):
    pass


class BytesImagePart(ImagePart):
    pass


class PillowImagePart(ImagePart):
    pass
