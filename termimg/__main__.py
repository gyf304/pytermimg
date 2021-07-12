import argparse
import sys
import typing as t

import PIL.Image

from . import get_printer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--printer", type=str, help="Select a printer to use [iterm2|sixel|utf8]"
    )
    parser.add_argument("-o", "--output", type=str, help="Specify a output file")
    parser.add_argument(
        "-w", "--max-width", type=int, default=800, help="Specify the maximum width"
    )
    parser.add_argument("filename", nargs="?", help="Input file")

    args = parser.parse_args()
    if (args.output is not None or not sys.stdout.isatty()) and args.printer is None:
        print(
            "A printer [-p|--printer] must be selected when outputting to a file",
            file=sys.stderr,
        )
        exit(1)

    fin: t.Union[t.BinaryIO, str] = sys.stdin.buffer
    fout = sys.stdout.buffer
    if args.output is not None:
        fout = open(args.output, "wb")

    if args.filename is not None and args.filename != "-":
        fin = args.filename

    img = PIL.Image.open(fin)
    img.load()
    printer = get_printer(args.printer, max_width=args.max_width)
    if printer is None:
        print("No compatible image printer available.", file=sys.stderr)
        exit(1)
    printer.print(img, fout)


if __name__ == "__main__":
    main()
