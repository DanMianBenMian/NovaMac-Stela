"""Render the DM-ROOT PNG as the EFI header logo pixels.

Output: 64 x 64 RGB bytes, blue in the low byte (the same layout Stela's
framebuffer uses), already composited over the boot UI background so that
transparent corners land on the same colour as the header band.
"""
from pathlib import Path

from PIL import Image

SRC = Path(r"C:\Users\单面本面\Desktop\DM-ROOT.png")
DEST = Path(__file__).parent / (
    "work/DanMianBenMian-Stela-b2594f3/"
    "crates/stela-boot-core/src/dmroot_logo_64.rgb"
)
SIZE = 64
BACKGROUND_RGB = (0x18, 0x19, 0x1c)  # ui::BACKGROUND = 0x18191c

src = Image.open(SRC).convert("RGBA")
small = src.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
canvas = Image.new("RGBA", (SIZE, SIZE), (*BACKGROUND_RGB, 255))
canvas.alpha_composite(small)

out = bytearray()
for y in range(SIZE):
    for x in range(SIZE):
        red, green, blue, _ = canvas.getpixel((x, y))
        out += bytes((blue, green, red))

DEST.parent.mkdir(parents=True, exist_ok=True)
DEST.write_bytes(out)
print(f"{DEST} {len(out)} bytes sha256={__import__('hashlib').sha256(out).hexdigest()}")
