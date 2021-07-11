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
    sys.stdout.buffer.write(b"\033[6n")
    sys.stdout.buffer.flush()
    buffer = read_until(b"R", 1.0)
    if buffer.startswith(b"\x1b[") and buffer.endswith(b"R"):
        row, col = [int(x) for x in buffer[2:-1].split(b";")]
        return (row, col)
    return None


def set_cursor(row: int, col: int) -> None:
    sys.stdout.buffer.write(f"\033[{row};{col}H".encode("ascii"))
    sys.stdout.buffer.flush()


def save_position() -> None:
    sys.stdout.buffer.write(b"\x1b7")
    sys.stdout.buffer.flush()


def restore_position() -> None:
    sys.stdout.buffer.write(b"\x1b8")
    sys.stdout.buffer.flush()
