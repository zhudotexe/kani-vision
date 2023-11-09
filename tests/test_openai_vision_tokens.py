from kani.ext.vision.engines.openai.img_tokens import tokens_from_image_size

# from the openai docs
KNOWN_RES = [
    ((512, 512), 255),
    ((1024, 1024), 765),
    ((2048, 4096), 1105),
]


def test_known_resolutions():
    for size, toks in KNOWN_RES:
        assert tokens_from_image_size(size) == toks
