from kani.ext.vision.engines.openai.img_tokens import tokens_from_image_size

# resolutions validated by actually calling GPT-4
KNOWN_RES = [
    ((980, 970), 630),
    ((554, 536), 630),
    ((1054, 356), 490),
    # ((1920, 1080), 910),  # TODO: this is weird, we'll have to see how openai actually does it
    ((512, 512), 210),
    ((512, 513), 350),
    ((512, 1024), 350),
    ((1, 1025), 490),
    ((512, 1536), 490),
    ((513, 513), 630),
    ((4096, 4096), 630),
    ((513, 1025), 910),
    ((513, 1536), 910),
    ((513, 1537), 1190),
]


def test_known_resolutions():
    for size, toks in KNOWN_RES:
        assert tokens_from_image_size(size) == toks
