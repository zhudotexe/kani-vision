from kani.exceptions import KaniException


class KaniVisionException(KaniException):
    """Base exception for all kani-vision exceptions."""


class RemoteImageError(KaniVisionException):
    """This engine does not support remote images."""


class ImageFormatException(KaniVisionException):
    """This image does not have a valid MIME type."""
