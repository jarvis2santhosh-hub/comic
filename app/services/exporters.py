
from pathlib import Path

from fpdf import FPDF
from PIL import Image

from app.config import get_settings
from app.schemas import ComicLayout


def _local_image_path(image_url: str) -> Path:
    settings = get_settings()
    prefix = "/static/"

    if not image_url.startswith(prefix):
        raise ValueError(f"Invalid image URL: {image_url}")

    return settings.static_dir / image_url.removeprefix(prefix)


def _safe_text(text: str, max_chars: int = 2000) -> str:
    """
    Make text safe for PDF rendering.

    FPDF can fail when a single word/string is wider than
    the available cell. Insert spaces into very long tokens.
    """
    if not text:
        return ""

    text = str(text).replace("\r", " ").replace("\n", " ")

    # Break extremely long unbroken strings.
    parts = text.split(" ")
    safe_parts = []

    for part in parts:
        if len(part) > 40:
            chunks = [
                part[i:i + 40]
                for i in range(0, len(part), 40)
            ]
            safe_parts.append(" ".join(chunks))
        else:
            safe_parts.append(part)

    result = " ".join(safe_parts)

    return result[:max_chars]


def _add_wrapped(pdf: FPDF, text: str) -> None:
    """Render text safely inside the current PDF page."""
    text = _safe_text(text)

    if not text:
        return

    pdf.multi_cell(
        0,
        5,
        text,
        new_x="LMARGIN",
        new_y="NEXT",
    )


def save_pdf(layout: ComicLayout) -> Path:
    settings = get_settings()

    output = settings.exports_dir / f"{layout.comic_id}.pdf"

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=12,
    )

    for panel in layout.panels:
        pdf.add_page()

        # Panel title
        pdf.set_font("Helvetica", "B", 16)

        title = _safe_text(
            f"Panel {panel.panel_number}: {panel.title}",
            max_chars=200,
        )

        pdf.multi_cell(
            0,
            10,
            title,
            new_x="LMARGIN",
            new_y="NEXT",
        )

        # Panel image
        image_path = _local_image_path(panel.image_url)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Panel image not found: {image_path}"
            )

        with Image.open(image_path) as img:
            width, height = img.size

        max_w = 180
        max_h = 105

        scale = min(
            max_w / width,
            max_h / height,
        )

        draw_w = width * scale
        draw_h = height * scale

        x = (210 - draw_w) / 2

        pdf.image(
            str(image_path),
            x=x,
            y=pdf.get_y(),
            w=draw_w,
            h=draw_h,
        )

        pdf.set_y(pdf.get_y() + draw_h + 5)

        # Scene description
        pdf.set_font("Helvetica", "I", 10)

        _add_wrapped(
            pdf,
            panel.scene_description,
        )

        pdf.ln(2)

        # Caption
        pdf.set_font("Helvetica", "", 11)

        _add_wrapped(
            pdf,
            f"Caption: {panel.caption}",
        )

        # Narration
        _add_wrapped(
            pdf,
            f"Narration: {panel.narration}",
        )

        # Dialogue
        if panel.dialogue:
            _add_wrapped(
                pdf,
                f"Dialogue: {panel.dialogue}",
            )

    pdf.output(str(output))

    return output

