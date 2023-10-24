import math


def tokens_from_image_size(size: tuple[int, int]) -> int:
    """Estimate the number of tokens used after providing this image."""
    long, short = size
    if long < short:
        long, short = short, long

    # rescale so the smaller side is 1024px
    if short > 1024:
        ratio = short / 1024
        short = 1024
        long //= ratio

    n_patches = math.ceil(long / 512) * math.ceil(short / 512)

    # +140 tokens for each 512x512 patch
    return 70 + (n_patches * 140)
