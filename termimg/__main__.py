import sys
import typing as t

import PIL.Image

from . import get_printer

def main():
    f: t.Union[t.BinaryIO, str] = sys.stdin.buffer
    if len(sys.argv) > 1:
        f = sys.argv[1]
    img = PIL.Image.open(f)
    img.load()
    printer = get_printer()
    if printer is None:
        print("No compatible image printer available.", file=sys.stderr)
        exit(1)
    printer.print(img)

if __name__ == "__main__":
    main()
