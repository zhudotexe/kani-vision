import asyncio
import importlib.util
import logging
import os
import pathlib
import re
import shutil
import sys
import warnings

from kani import Kani
from kani.models import MessagePartType
from kani.utils.message_formatters import assistant_message_contents_thinking
from .parts import ImagePart

_has_ascii = importlib.util.find_spec("ascii_magic") is not None
_is_notebook = "ipykernel" in sys.modules


# ==== parsing helpers ====
def parts_from_cli_query(query: str) -> list[MessagePartType]:
    """Parse a string with paths to images prepended by ``!`` into the right messageparts."""
    query_parts = []
    last_idx = 0
    for image_match in re.finditer(
        r"!(?P<path>/?(\S+?/)*([^/\s]+\.[^/\s]+))|(?P<path_quot>\"/?(.+?/)*([^/]+\.[^/\s]+)\")", query
    ):
        # push everything between the end of the last path and the start of this one to the parts
        query_parts.append(query[last_idx : image_match.start()])
        last_idx = image_match.end()

        # ensure the path is valid
        if path := image_match["path"]:
            fp = pathlib.Path(path)
        else:
            fp = pathlib.Path(image_match["path_quot"].strip('"'))

        # if not, push the string to parts
        if not (fp.exists() and fp.is_file()):
            warnings.warn(f"The given image path ({fp}) either does not exist or is not a valid file.")
            query_parts.append(image_match[0])
        # otherwise, push a FileImagePart
        else:
            query_parts.append(ImagePart.from_path(fp))

    # and make sure the rest of the query is in the parts
    query_parts.append(query[last_idx:])
    return query_parts


# ==== image display helpers ====
def display_images_ipython(parts: list[MessagePartType]):
    from IPython.display import Image, display

    # show each ImagePart in an IPython display
    images = []
    for part in parts:
        if isinstance(part, ImagePart):
            images.append(Image(part.bytes, height=350))
    display(*images)


def print_parts_ascii(parts: list[MessagePartType]):
    import ascii_magic

    # clear the line the user just entered; we're making it fancy
    print("\033[FUSER: \033[K", end="")
    # print out each part; if it's an ImagePart ascii it
    for part in parts:
        if isinstance(part, ImagePart):
            # flush and ascii
            print()
            cols, _ = shutil.get_terminal_size()
            art = ascii_magic.from_pillow_image(part.image)
            art.to_terminal(columns=cols // 3 * 2)
        else:
            print(part, end="")
    # and flush
    print()


# ==== entrypoints ====
async def chat_in_terminal_vision_async(kani: Kani, rounds: int = 0, stopword: str = None):
    """Async version of :func:`.chat_in_terminal_vision`.
    Use in environments when there is already an asyncio loop running (e.g. Google Colab).
    """
    if os.getenv("KANI_DEBUG") is not None:
        logging.basicConfig(level=logging.DEBUG)

    try:
        round_num = 0
        while round_num < rounds or not rounds:
            round_num += 1

            # if we're in a notebook, enable a widget to upload files
            uploader = None
            if _is_notebook:
                from IPython.display import Image, display
                from ipywidgets import widgets

                uploader = widgets.FileUpload(accept="image/*", multiple=True, description="Upload images")
                display(uploader)

            # get user input
            query = input("USER: ").strip()
            if stopword and query == stopword:
                break

            # find !path/to/file.png parts and replace them with FileImageParts
            query_parts = parts_from_cli_query(query)

            # if we had files from the widget, append them to the parts too
            if uploader is not None:
                for uploaded_file in uploader.value:
                    query_parts.append(ImagePart.from_bytes(uploaded_file.content.tobytes()))
                uploader.close()

            # then print it out with whatever image backend a user has installed
            has_image = any(isinstance(p, ImagePart) for p in query_parts)
            # IPython
            if _is_notebook and has_image:
                display_images_ipython(query_parts)
            # ascii art
            elif _has_ascii and has_image:
                print_parts_ascii(query_parts)

            # and pass on to model
            async for msg in kani.full_round_str(query_parts, message_formatter=assistant_message_contents_thinking):
                print(f"AI: {msg}")
    except KeyboardInterrupt:
        pass
    finally:
        await kani.engine.close()


def chat_in_terminal_vision(kani: Kani, rounds: int = 0, stopword: str = None):
    """Chat with a vision-enabled kani right in your terminal.

    To provide an image to the vision kani, prepend its filepath with a ``!`` (e.g. "Describe this image: !image.png").
    Use quotes (e.g. ``!"path/to/my image.png"``) for paths with spaces in their names.

    Useful for playing with kani, quick prompt engineering, or demoing the library.

    If the environment variable ``KANI_DEBUG`` is set, debug logging will be enabled.

    If run in a Jupyter notebook or Google Colab, this function will use widgets to accept file uploads and display
    images.

    .. warning::

        This function is only a development utility and should not be used in production.

    :param rounds: The number of chat rounds to play (defaults to 0 for infinite).
    :param stopword: Break out of the chat loop if the user sends this message.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass
    else:
        try:
            # google colab comes with this pre-installed
            # let's try importing and patching the loop so that we can just use the normal asyncio.run call
            import nest_asyncio

            nest_asyncio.apply()
        except ImportError:
            print(
                f"WARNING: It looks like you're in an environment with a running asyncio loop (e.g. Google Colab).\nYou"
                f" should use `await chat_in_terminal_vision_async(...)` instead or install `nest-asyncio`."
            )
            return
    asyncio.run(chat_in_terminal_vision_async(kani, rounds=rounds, stopword=stopword))
