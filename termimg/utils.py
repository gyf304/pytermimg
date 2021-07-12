import signal
import sys
import os
import time
import threading

import typing as t

try:
    import msvcrt
except:
    msvcrt = None
    import tty, termios


def _sigterm_after(timeout: float, state: t.Sequence[t.Any]):
    time.sleep(timeout)
    if state[0]:
        os.kill(os.getpid(), signal.SIGINT)


def read_until(delimiter: bytes, timeout: float) -> bytes:
    fd = 0
    attr: t.List[t.Any] = []
    if msvcrt is None:
        fd = sys.stdin.fileno()
        attr = termios.tcgetattr(fd)
        tty.setraw(fd)
    state = [True]
    threading.Thread(target=_sigterm_after, args=[timeout, state], daemon=True).start()
    buffer: bytes = b""
    try:
        while True:
            if msvcrt is not None:
                c: bytes = msvcrt.getch()  # type: ignore
            else:
                c = sys.stdin.buffer.read(1)
            buffer += c
            if c == delimiter:
                state[0] = False
                return buffer
    except KeyboardInterrupt:
        pass
    finally:
        if msvcrt is None:
            termios.tcsetattr(fd, termios.TCSADRAIN, attr)
        return buffer


def get_cursor() -> t.Optional[t.Tuple[int, int]]:
    sys.stdout.buffer.write(b"\x1b[6n")
    sys.stdout.buffer.flush()
    buffer = read_until(b"R", 1.0)
    if buffer.startswith(b"\x1b[") and buffer.endswith(b"R"):
        row, col = [int(x) for x in buffer[2:-1].split(b";")]
        return (row, col)
    return None


def set_cursor(row: int, col: int) -> None:
    sys.stdout.buffer.write(f"\033[{row};{col}H".encode("ascii"))
    sys.stdout.buffer.flush()


def save_cursor(f: t.BinaryIO = sys.stdout.buffer) -> None:
    f.write(b"\x1b7")
    f.flush()


def restore_cursor(f: t.BinaryIO = sys.stdout.buffer) -> None:
    f.write(b"\x1b8")
    f.flush()


def get_bg() -> t.Optional[t.Tuple[int, int, int]]:
    sys.stdout.buffer.write(b"\x1b]11;?\x07")
    sys.stdout.buffer.flush()
    buffer = read_until(b"\x07", 1.0)
    if buffer.startswith(b"\x1b]11;rgb:") and buffer.endswith(b"\x07"):
        try:
            r, g, b = [int(x, base=16) for x in buffer[9:-1].decode("ascii").split("/")]
            return (r, g, b)
        except:
            return None
    return None


def get_fg(bits: int = 8) -> t.Optional[t.Tuple[int, int, int]]:
    sys.stdout.buffer.write(b"\x1b]10;?\x07")
    sys.stdout.buffer.flush()
    buffer = read_until(b"\x07", 1.0)
    if buffer.startswith(b"\x1b]10;rgb:") and buffer.endswith(b"\x07"):
        try:
            color_str = buffer[9:-1].decode("ascii")
            input_bits = (len(color_str) - 2) // 3 * 4
            r, g, b = [
                int(x, base=16) * ((1 << bits) - 1) // ((1 << input_bits) - 1)
                for x in color_str.split("/")
            ]
            return (r, g, b)
        except:
            return None
    return None


def set_fg(
    color: t.Union[int, t.Tuple[int, int, int]],
    bits: int = 8,
    f: t.BinaryIO = sys.stdout.buffer,
) -> t.Optional[t.Tuple[int, int, int]]:
    assert bits == 8
    if type(color) is tuple:
        f.write(b"\x1b[38;2;%sm" % f"{color[0]};{color[1]};{color[2]}".encode("ascii"))
    else:
        f.write(b"\x1b[38;5;%sm" % f"{color}".encode("ascii"))
    f.flush()


def set_bg(
    color: t.Union[int, t.Tuple[int, int, int]],
    bits: int = 8,
    f: t.BinaryIO = sys.stdout.buffer,
) -> t.Optional[t.Tuple[int, int, int]]:
    assert bits == 8
    if type(color) is tuple:
        f.write(b"\x1b[48;2;%sm" % f"{color[0]};{color[1]};{color[2]}".encode("ascii"))
    else:
        f.write(b"\x1b[48;5;%sm" % f"{color}".encode("ascii"))
    f.flush()


def sgr0(f: t.BinaryIO = sys.stdout.buffer) -> None:
    f.write(b"\x1b\x28\x42\x1b\x5b\x6d")
    f.flush()
