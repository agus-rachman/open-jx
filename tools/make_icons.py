#!/usr/bin/env python3
"""Generate the Copilot Cowork icons: color.png (192x192) and outline.png (32x32, white on transparent)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "plugin" / "assets"
ACCENT = (31, 92, 153, 255)


def font(size):
    for name in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "Arial Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def centred(draw, box, text, f, fill):
    l, t, r, b = draw.textbbox((0, 0), text, font=f)
    x = box[0] + (box[2] - box[0] - (r - l)) / 2 - l
    y = box[1] + (box[3] - box[1] - (b - t)) / 2 - t
    draw.text((x, y), text, font=f, fill=fill)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (192, 192), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, 191, 191), radius=36, fill=ACCENT)
    centred(d, (0, 0, 192, 150), "jx", font(96), (255, 255, 255, 255))
    d.rounded_rectangle((44, 146, 148, 154), radius=4, fill=(255, 255, 255, 200))
    img.save(OUT / "color.png")

    o = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(o)
    d.rounded_rectangle((1, 1, 30, 30), radius=6, outline=(255, 255, 255, 255), width=2)
    centred(d, (0, 0, 32, 30), "jx", font(15), (255, 255, 255, 255))
    o.save(OUT / "outline.png")
    print("icons written to", OUT)


if __name__ == "__main__":
    main()
