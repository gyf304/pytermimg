import sys
import typing as t

import PIL.Image


class ImagePrinterBase:
    @classmethod
    def supported(cls) -> bool:
        raise NotImplementedError

    def encode(self, img: PIL.Image.Image) -> bytes:
        raise NotImplementedError

    def print(self, img: PIL.Image.Image, f: t.BinaryIO = sys.stdout.buffer) -> None:
        f.write(self.encode(img))
        f.write(b"\n")
        f.flush()
