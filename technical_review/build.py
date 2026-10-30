from pathlib import Path
from xml.sax.saxutils import escape

import pymupdf as fitz
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from .quality import validate_bbox


def build_review(data, path):
    """Reflowed bilingual review, never paints over source content."""
    path = Path(path)
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "Target",
            parent=styles["BodyText"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#124c55"),
            spaceAfter=12,
        )
    )
    story = [
        Paragraph("Traducción técnica para revisión", styles["Title"]),
        Paragraph(
            "Borrador de inglés a español. Verificar contra el original antes de uso operativo.",
            styles["BodyText"],
        ),
        Spacer(1, 12),
        Paragraph("Origen: " + escape(data["source_name"]), styles["BodyText"]),
        Paragraph("SHA256: " + data["source_sha256"], styles["Code"]),
        Spacer(1, 18),
    ]
    for pi, page in enumerate(data["pages"]):
        if pi:
            story.append(PageBreak())
        story.append(
            Paragraph(f"Página de origen {page['number']}", styles["Heading1"])
        )
        for warning in page["warnings"]:
            story.append(
                Paragraph(
                    "Revisión de cobertura: " + escape(warning["code"]),
                    styles["BodyText"],
                )
            )
        for block in page["blocks"]:
            validate_bbox(block["bbox"], page["width"], page["height"])
            story.append(
                Paragraph(
                    escape(
                        block["id"] + " · " + block["origin"] + " · " + block["status"]
                    ),
                    styles["Heading3"],
                )
            )
            story.append(
                Paragraph(
                    "EN: " + escape(block["text"]).replace("\n", "<br/>"),
                    styles["BodyText"],
                )
            )
            story.append(Spacer(1, 5))
            story.append(
                Paragraph(
                    "ES: " + escape(block["translated"]).replace("\n", "<br/>"),
                    styles["Target"],
                )
            )
            if block["flags"]:
                story.append(
                    Paragraph(
                        "Revisar: " + escape("; ".join(block["flags"])),
                        styles["BodyText"],
                    )
                )
        if not page["blocks"]:
            story.append(
                Paragraph(
                    "Sin bloques de texto extraídos. Consultar original y cobertura OCR.",
                    styles["BodyText"],
                )
            )

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.drawString(42, 24, "BORRADOR · Revisión humana requerida")
        canvas.drawRightString(550, 24, str(doc.page))

    SimpleDocTemplate(
        str(path), leftMargin=42, rightMargin=42, topMargin=42, bottomMargin=42
    ).build(story, onFirstPage=footer, onLaterPages=footer)
    # ReportLab reflows long paragraphs across pages instead of squeezing into tiny boxes.
    with fitz.open(path) as pdf:
        return {
            "review_pages": len(pdf),
            "layout": "reflowed_bilingual",
            "source_overlay": False,
        }
