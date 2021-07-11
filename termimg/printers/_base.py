import sys

import PIL.Image


class ImagePrinterBase:
    @classmethod
    def supported(cls) -> bool:
        raise NotImplementedError

    def encode(self, img: PIL.Image.Image) -> bytes:
        raise NotImplementedError

    def print(self, img: PIL.Image.Image) -> None:
        sys.stdout.buffer.write(self.encode(img))
        sys.stdout.buffer.write(b"\n")
        sys.stdout.flush()
