import sys
import io
import base64

import PIL.Image

from ._base import ImagePrinterBase
from ..utils import get_cursor, set_cursor

_ITERM2_TEST = b"\x1b]1337;File=name=L1VzZXJzL3lpZmFuZ3UvRGVza3RvcC8xeDEucG5n;size=1698;inline=1:iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAErmlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgZXhpZjpQaXhlbFhEaW1lbnNpb249IjEiCiAgIGV4aWY6UGl4ZWxZRGltZW5zaW9uPSIxIgogICBleGlmOkNvbG9yU3BhY2U9IjEiCiAgIHRpZmY6SW1hZ2VXaWR0aD0iMSIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMSIKICAgdGlmZjpSZXNvbHV0aW9uVW5pdD0iMiIKICAgdGlmZjpYUmVzb2x1dGlvbj0iNzIuMCIKICAgdGlmZjpZUmVzb2x1dGlvbj0iNzIuMCIKICAgcGhvdG9zaG9wOkNvbG9yTW9kZT0iMyIKICAgcGhvdG9zaG9wOklDQ1Byb2ZpbGU9InNSR0IgSUVDNjE5NjYtMi4xIgogICB4bXA6TW9kaWZ5RGF0ZT0iMjAyMS0wNy0xMFQxOTowNToyMi0wNDowMCIKICAgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMS0wNy0xMFQxOTowNToyMi0wNDowMCI+CiAgIDx4bXBNTTpIaXN0b3J5PgogICAgPHJkZjpTZXE+CiAgICAgPHJkZjpsaQogICAgICBzdEV2dDphY3Rpb249InByb2R1Y2VkIgogICAgICBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZmZpbml0eSBEZXNpZ25lciAxLjkuMyIKICAgICAgc3RFdnQ6d2hlbj0iMjAyMS0wNy0xMFQxOTowNToyMi0wNDowMCIvPgogICAgPC9yZGY6U2VxPgogICA8L3htcE1NOkhpc3Rvcnk+CiAgPC9yZGY6RGVzY3JpcHRpb24+CiA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgo8P3hwYWNrZXQgZW5kPSJyIj8+W6JXuAAAAYFpQ0NQc1JHQiBJRUM2MTk2Ni0yLjEAACiRdZHPK0RRFMc/ZujJjyiShcUkrNAYNbFRZtJQksYovzYzz7wZNTNe7z1pslW2ihIbvxb8BWyVtVJESnbKmtig57x5aiaZczv3fO733nO691zwxDJq1qz0QzZnGdFIyDczO+dTnlGooYVBlLhq6sOTk+OUtY87Kpx40+PUKn/uX6tdTJoqVFQLD6m6YQmPCo+vWrrD28LNajq+KHwq3G3IBYVvHT3h8ovDKZe/HDZi0TB4GoV9qRJOlLCaNrLC8nI6spkV9fc+zkvqkrnpKYnt4m2YRIkQwscYI4QJ0id9CcroIUCvrCiT7y/kT7AsuarMOnkMlkiRxqJb1BWpnpSoiZ6UkSHv9P9vX02tP+BWrwtB1ZNtv3WCsgXfm7b9eWjb30fgfYSLXDF/+QAG3kXfLGod+9CwDmeXRS2xA+cb0Pqgx414QfKKezQNXk+gfhaarqFm3u3Z7z7H9xBbk6+6gt096JLzDQs/WGBn31QqZkQAAAAJcEhZcwAACxMAAAsTAQCanBgAAAANSURBVAiZY2BgYGAAAAAFAAGHoU7UAAAAAElFTkSuQmCC\x07"


class ITerm2Printer(ImagePrinterBase):
    max_width: int

    def __init__(self, max_width: int = 800):
        self.max_width = max_width

    @classmethod
    def supported(cls) -> bool:
        if not sys.stdin.isatty():
            return False
        saved_cur = get_cursor()
        if saved_cur is None:
            return False
        set_cursor(1, 1)
        sys.stdout.buffer.write(_ITERM2_TEST)
        sys.stdout.buffer.flush()
        cur = get_cursor()
        supported = cur is not None and cur[1] > 1
        set_cursor(*saved_cur)
        return supported

    def encode(self, img: PIL.Image.Image) -> bytes:
        w, h = img.size
        if w > self.max_width:
            img = img.resize((self.max_width, h * self.max_width // w))
        f = io.BytesIO()
        img.save(f, "png")
        png_bytes = f.getvalue()
        return (
            b"\x1b]1337;File=name=dGVybWltZy5wbmc=;size="
            + f"{len(png_bytes)}".encode("ascii")
            + b";inline=1:"
            + base64.encodebytes(png_bytes)
            + b"\x07"
        )
