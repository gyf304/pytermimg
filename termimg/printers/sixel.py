import io
import sys
import typing as t

import PIL.Image

from ._base import ImagePrinterBase
from ..utils import get_cursor, set_cursor

_SIXEL_TEST = b'\x1bPq"1;1;1;1#0;2;0;0;0-#0@\x1b\\'
TRANSPARENT_THRESHOLD = 128


class SixelPrinter(ImagePrinterBase):
    colors: int
    max_width: int

    def __init__(self, colors: int = 64, max_width: int = 800):
        self.colors = colors
        self.max_width = max_width

    @classmethod
    def supported(cls) -> bool:
        if not sys.stdin.isatty():
            return False
        saved_cur = get_cursor()
        if saved_cur is None:
            return False
        set_cursor(1, 1)
        sys.stdout.buffer.write(_SIXEL_TEST)
        sys.stdout.buffer.flush()
        cur = get_cursor()
        supported = cur is not None and cur[0] > 1
        set_cursor(*saved_cur)
        return supported

    def _encode(self, img: PIL.Image.Image, buf: t.BinaryIO) -> None:
        w, h = img.size
        if w > self.max_width:
            img = img.resize((self.max_width, h * self.max_width // w))
            w, h = img.size
        sixel_img = img.convert("RGBA").convert("P", colors=self.colors)

        # write header
        # write image size
        buf.write(b'\x1bPq"1;1;%d;%d' % (w, h))

        # write palette
        colors: t.Mapping[t.Tuple[int, int, int, int], int] = sixel_img.palette.colors
        for i, color in enumerate(colors.keys()):
            r, g, b, a = color
            if a < TRANSPARENT_THRESHOLD:  # skip transparent colors
                continue
            r = r * 100 // 255
            g = g * 100 // 255
            b = b * 100 // 255
            buf.write(b"#%d;2;%d;%d;%d" % (i, r, g, b))

        # write color data
        img_bytes: bytes = sixel_img.tobytes()  # type: ignore

        sixel_rows = (h + 5) // 6

        for sixel_row in range(sixel_rows):
            color_rows = [
                None if a < TRANSPARENT_THRESHOLD else bytearray(w)
                for _, _, _, a in colors.keys()
            ]
            for col in range(w):
                for sub_row in range(6):
                    row = sixel_row * 6 + sub_row
                    if row >= h:
                        continue
                    i = row * w + col
                    color_index = img_bytes[i]
                    color_row = color_rows[color_index]
                    if color_row is None:
                        continue
                    color_row[col] |= 1 << sub_row
            for i, color_row in enumerate(color_rows):
                if color_row is None:
                    continue
                for col in range(w):
                    color_row[col] += 63
                buf.write(b"#%d" % i)
                buf.write(color_row)
                buf.write(b"$")
            buf.write(b"-")
        buf.write(b"\x1b\\")

    def encode(self, img: PIL.Image.Image) -> bytes:
        buf = io.BytesIO()
        self._encode(img, buf)
        return buf.getvalue()

    def print(self, img: PIL.Image.Image, f: t.BinaryIO = sys.stdout.buffer) -> None:
        self._encode(img, f)
