import sys
import io
import os
import typing as t

import PIL.Image
import PIL.ImagePalette

from ._base import ImagePrinterBase
from ..utils import get_cursor, set_cursor, set_bg, set_fg, sgr0

_UNICODE_TEST = "\u2580".encode("utf-8")
_UNICODE_UPPER_BLOCK = "\u2580".encode("utf-8")
_UNICODE_LOWER_BLOCK = "\u2584".encode("utf-8")


_XTERM_PALATTE_BYTES = b"\x00\x00\x00\x80\x00\x00\x00\x80\x00\x80\x80\x00\x00\x00\x80\x80\x00\x80\x00\x80\x80\xc0\xc0\xc0\x80\x80\x80\xff\x00\x00\x00\xff\x00\xff\xff\x00\x00\x00\xff\xff\x00\xff\x00\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00_\x00\x00\x87\x00\x00\xaf\x00\x00\xd7\x00\x00\xff\x00_\x00\x00__\x00_\x87\x00_\xaf\x00_\xd7\x00_\xff\x00\x87\x00\x00\x87_\x00\x87\x87\x00\x87\xaf\x00\x87\xd7\x00\x87\xff\x00\xaf\x00\x00\xaf_\x00\xaf\x87\x00\xaf\xaf\x00\xaf\xd7\x00\xaf\xff\x00\xd7\x00\x00\xd7_\x00\xd7\x87\x00\xd7\xaf\x00\xd7\xd7\x00\xd7\xff\x00\xff\x00\x00\xff_\x00\xff\x87\x00\xff\xaf\x00\xff\xd7\x00\xff\xff_\x00\x00_\x00__\x00\x87_\x00\xaf_\x00\xd7_\x00\xff__\x00_____\x87__\xaf__\xd7__\xff_\x87\x00_\x87__\x87\x87_\x87\xaf_\x87\xd7_\x87\xff_\xaf\x00_\xaf__\xaf\x87_\xaf\xaf_\xaf\xd7_\xaf\xff_\xd7\x00_\xd7__\xd7\x87_\xd7\xaf_\xd7\xd7_\xd7\xff_\xff\x00_\xff__\xff\x87_\xff\xaf_\xff\xd7_\xff\xff\x87\x00\x00\x87\x00_\x87\x00\x87\x87\x00\xaf\x87\x00\xd7\x87\x00\xff\x87_\x00\x87__\x87_\x87\x87_\xaf\x87_\xd7\x87_\xff\x87\x87\x00\x87\x87_\x87\x87\x87\x87\x87\xaf\x87\x87\xd7\x87\x87\xff\x87\xaf\x00\x87\xaf_\x87\xaf\x87\x87\xaf\xaf\x87\xaf\xd7\x87\xaf\xff\x87\xd7\x00\x87\xd7_\x87\xd7\x87\x87\xd7\xaf\x87\xd7\xd7\x87\xd7\xff\x87\xff\x00\x87\xff_\x87\xff\x87\x87\xff\xaf\x87\xff\xd7\x87\xff\xff\xaf\x00\x00\xaf\x00_\xaf\x00\x87\xaf\x00\xaf\xaf\x00\xd7\xaf\x00\xff\xaf_\x00\xaf__\xaf_\x87\xaf_\xaf\xaf_\xd7\xaf_\xff\xaf\x87\x00\xaf\x87_\xaf\x87\x87\xaf\x87\xaf\xaf\x87\xd7\xaf\x87\xff\xaf\xaf\x00\xaf\xaf_\xaf\xaf\x87\xaf\xaf\xaf\xaf\xaf\xd7\xaf\xaf\xff\xaf\xd7\x00\xaf\xd7_\xaf\xd7\x87\xaf\xd7\xaf\xaf\xd7\xd7\xaf\xd7\xff\xaf\xff\x00\xaf\xff_\xaf\xff\x87\xaf\xff\xaf\xaf\xff\xd7\xaf\xff\xff\xd7\x00\x00\xd7\x00_\xd7\x00\x87\xd7\x00\xaf\xd7\x00\xd7\xd7\x00\xff\xd7_\x00\xd7__\xd7_\x87\xd7_\xaf\xd7_\xd7\xd7_\xff\xd7\x87\x00\xd7\x87_\xd7\x87\x87\xd7\x87\xaf\xd7\x87\xd7\xd7\x87\xff\xd7\xaf\x00\xd7\xaf_\xd7\xaf\x87\xd7\xaf\xaf\xd7\xaf\xd7\xd7\xaf\xff\xd7\xd7\x00\xd7\xd7_\xd7\xd7\x87\xd7\xd7\xaf\xd7\xd7\xd7\xd7\xd7\xff\xd7\xff\x00\xd7\xff_\xd7\xff\x87\xd7\xff\xaf\xd7\xff\xd7\xd7\xff\xff\xff\x00\x00\xff\x00_\xff\x00\x87\xff\x00\xaf\xff\x00\xd7\xff\x00\xff\xff_\x00\xff__\xff_\x87\xff_\xaf\xff_\xd7\xff_\xff\xff\x87\x00\xff\x87_\xff\x87\x87\xff\x87\xaf\xff\x87\xd7\xff\x87\xff\xff\xaf\x00\xff\xaf_\xff\xaf\x87\xff\xaf\xaf\xff\xaf\xd7\xff\xaf\xff\xff\xd7\x00\xff\xd7_\xff\xd7\x87\xff\xd7\xaf\xff\xd7\xd7\xff\xd7\xff\xff\xff\x00\xff\xff_\xff\xff\x87\xff\xff\xaf\xff\xff\xd7\xff\xff\xff\x08\x08\x08\x12\x12\x12\x1c\x1c\x1c&&&000:::DDDNNNXXXbbblllvvv\x80\x80\x80\x8a\x8a\x8a\x94\x94\x94\x9e\x9e\x9e\xa8\xa8\xa8\xb2\xb2\xb2\xbc\xbc\xbc\xc6\xc6\xc6\xd0\xd0\xd0\xda\xda\xda\xe4\xe4\xe4\xee\xee\xee"
_XTERM_PALATTE_BYTEARRAY = bytearray(_XTERM_PALATTE_BYTES)
# clear out the first 16 colors, as these colors are not consistent across implementations
for i in range(16 * 3):
    _XTERM_PALATTE_BYTEARRAY[i] = 0
_XTERM_PALATTE = PIL.ImagePalette.ImagePalette(
    mode="RGB", palette=_XTERM_PALATTE_BYTEARRAY
)
_XTERM_PALATTE_IMG = PIL.Image.new("P", (1, 1))
_XTERM_PALATTE_IMG.putpalette(_XTERM_PALATTE)

TRANSPARENT_THRESHOLD = 128


class UTF8Printer(ImagePrinterBase):
    w_shrink: int
    h_shrink: int
    max_width: int
    truecolor: bool

    def __init__(
        self,
        max_width: int = 800,
        w_shrink: int = 16,
        h_shrink: int = 16,
        truecolor: t.Optional[bool] = None,
    ):
        self.w_shrink = w_shrink
        self.h_shrink = h_shrink
        self.max_width = max_width
        if truecolor is None:
            self.truecolor = self.has_truecolor()
        else:
            self.truecolor = truecolor

    @classmethod
    def has_truecolor(cls) -> bool:
        hint = os.getenv("COLORTERM", "")
        return "truecolor" in hint or "24" in hint

    @classmethod
    def supported(cls) -> bool:
        if "256" not in os.getenv("TERM", "") and not cls.has_truecolor():
            return False
        if not sys.stdin.isatty():
            return False
        saved_cur = get_cursor()
        if saved_cur is None:
            return False
        set_cursor(1, 1)
        sys.stdout.buffer.write(_UNICODE_TEST)
        sys.stdout.buffer.flush()
        cur = get_cursor()
        supported = cur is not None and cur[1] == 2
        set_cursor(*saved_cur)
        return supported

    def _encode(self, img: PIL.Image.Image, f: t.BinaryIO):
        w, h = img.size
        if w > (self.max_width // self.w_shrink):
            w, h = (
                self.max_width // self.w_shrink,
                h * self.max_width // w // self.h_shrink,
            )
            img = img.resize((w, h))
            w, h = img.size

        img = img.convert("RGBA")

        if self.truecolor:
            for row in range(h // 2):
                for col in range(w):
                    tc1: t.Tuple[int, int, int, int] = img.getpixel((col, row * 2))  # type: ignore
                    bc1: t.Tuple[int, int, int, int] = img.getpixel((col, row * 2 + 1))  # type: ignore
                    tt1 = tc1[3]
                    bt1 = bc1[3]
                    if tt1 < TRANSPARENT_THRESHOLD and bt1 < TRANSPARENT_THRESHOLD:
                        # both pixels are transparent
                        sgr0(f)
                        f.write(b" ")
                    elif tt1 < TRANSPARENT_THRESHOLD:
                        # top pixel is transparent
                        sgr0(f)
                        set_fg(bc1[:3], f=f)
                        f.write(_UNICODE_LOWER_BLOCK)
                    elif bt1 < TRANSPARENT_THRESHOLD:
                        # bottom pixel is transparent
                        sgr0(f)
                        set_fg(tc1[:3], f=f)
                        f.write(_UNICODE_UPPER_BLOCK)
                    else:
                        set_fg(tc1[:3], f=f)
                        set_bg(bc1[:3], f=f)
                        f.write(_UNICODE_UPPER_BLOCK)
                sgr0(f)
                f.write(b" \n")
        else:
            pimg = img.convert("RGB").quantize(palette=_XTERM_PALATTE_IMG)
            for row in range(h // 2):
                for col in range(w):
                    tc2: int = pimg.getpixel((col, row * 2))  # type: ignore
                    bc2: int = pimg.getpixel((col, row * 2 + 1))  # type: ignore
                    tt2: int = img.getpixel((col, row * 2))[3]  # type: ignore
                    bt2: int = img.getpixel((col, row * 2 + 1))[3]  # type: ignore
                    if tt2 < TRANSPARENT_THRESHOLD and bt2 < TRANSPARENT_THRESHOLD:
                        # both pixels are transparent
                        sgr0(f)
                        f.write(b" ")
                    elif tt2 < TRANSPARENT_THRESHOLD:
                        # top pixel is transparent
                        sgr0(f)
                        set_fg(bc2, f=f)
                        f.write(_UNICODE_LOWER_BLOCK)
                    elif bt2 < TRANSPARENT_THRESHOLD:
                        # bottom pixel is transparent
                        sgr0(f)
                        set_fg(tc2, f=f)
                        f.write(_UNICODE_UPPER_BLOCK)
                    else:
                        set_fg(tc2, f=f)
                        set_bg(bc2, f=f)
                        f.write(_UNICODE_UPPER_BLOCK)
                sgr0(f)
                f.write(b"\n")

    def encode(self, img: PIL.Image.Image) -> bytes:
        f = io.BytesIO()
        self._encode(img, f)
        return f.getvalue()

    def print(self, img: PIL.Image.Image, f: t.BinaryIO = sys.stdout.buffer) -> None:
        self._encode(img, f)
