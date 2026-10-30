"""Original synthetic technical examples, MIT. No third-party documents."""

import io
from pathlib import Path

import reportlab
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def create_fixtures(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1500, 360), "white")
    font = ImageFont.truetype(
        str(Path(reportlab.__file__).parent / "fonts" / "Vera.ttf"), 42
    )
    draw = ImageDraw.Draw(image)
    for i, text in enumerate(
        ("Pressure sensor", "Rated voltage: 24 V", "Measuring range: 0 to 10 bar")
    ):
        draw.text((45, 35 + i * 90), text, font=font, fill="black")
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    stream.seek(0)
    for name in ("digital", "scanned", "mixed", "table", "equation", "long"):
        c = canvas.Canvas(
            str(directory / (name + ".pdf")), pagesize=(612, 792), invariant=1
        )
        c.setTitle("Synthetic technical fixture: " + name)
        if name in ("digital", "mixed"):
            c.setFont("Helvetica", 18)
            c.drawString(48, 730, "Power supply specification")
            c.setFont("Helvetica", 12)
            c.drawString(48, 695, "Rated voltage: 24 V. Rated current: 5 A.")
            c.drawString(48, 670, "Inspect the circuit breaker before maintenance.")
        if name in ("scanned", "mixed"):
            c.drawImage(
                ImageReader(stream),
                48,
                440 if name == "mixed" else 580,
                width=500,
                height=120,
            )
        if name == "table":
            for y in (720, 680, 640, 600):
                c.line(48, y, 550, y)
            for x in (48, 300, 550):
                c.line(x, 600, x, 720)
            for y, left, right in (
                (695, "Parameter", "Value"),
                (655, "Voltage", "24 V"),
                (615, "Current", "5 A"),
            ):
                c.drawString(60, y, left)
                c.drawString(310, y, right)
        if name == "equation":
            c.drawString(48, 720, "Electrical relationship")
            c.drawString(48, 680, "P = V * I")
        if name == "long":
            for page in range(3):
                for line in range(40):
                    c.drawString(
                        48,
                        740 - line * 16,
                        f"Inspection record {page * 40 + line + 1}: verify the sensor and wiring.",
                    )
                if page < 2:
                    c.showPage()
        c.save()
    return directory


if __name__ == "__main__":
    create_fixtures(Path("examples/fixtures"))
