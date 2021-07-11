import os
import typing as t

from .printers import ITerm2Printer, SixelPrinter
from .printers._base import ImagePrinterBase


def get_printer(override: t.Optional[str] = None) -> t.Optional[ImagePrinterBase]:
    override = override or os.getenv("TERMIMG_PRINTER")
    if override == "iterm2":
        return ITerm2Printer()
    elif override == "sixel":
        return SixelPrinter()

    if ITerm2Printer.supported():
        return ITerm2Printer()
    elif SixelPrinter.supported():
        return SixelPrinter()
    return None


__all__ = ["get_printer"]
