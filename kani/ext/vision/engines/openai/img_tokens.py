import math


def tokens_from_image_size(size: tuple[int, int], low_detail: bool = False) -> int:
    """Estimate the number of tokens used after providing this image.

    See https://platform.openai.com/docs/guides/vision/calculating-costs for more details.
    """
    if low_detail:
        return 85

    long, short = size
    if long < short:
        long, short = short, long

    # rescale so the larger side is 2048px
    if long > 2048:
        ratio = long / 2048
        long = 2048
        short //= ratio

    # rescale so the smaller side is 768px
    if short > 768:
        ratio = short / 768
        short = 768
        long //= ratio

    n_patches = math.ceil(long / 512) * math.ceil(short / 512)

    # +170 tokens for each 512x512 patch
    return 85 + (n_patches * 170)
