import json
import uuid
from pathlib import Path

from app.config import get_settings
from app.schemas import ComicLayout, PromptRequest

def _write_job(comic_id: str, layout: ComicLayout) -> None:
    settings = get_settings()
    path = settings.storage_dir / f"{comic_id}.json"
    path.write_text(layout.model_dump_json(indent=2), encoding="utf-8")

def load_job(comic_id: str) -> ComicLayout:
    settings = get_settings()
    path = settings.storage_dir / f"{comic_id}.json"
    if not path.exists():
        raise FileNotFoundError("Comic not found.")
    return ComicLayout.model_validate_json(path.read_text(encoding="utf-8"))

def generate_comic(request: PromptRequest) -> ComicLayout:
    from app.services.gemini_flash import generate_outline
    from app.services.gemini_pro import generate_story
    from app.services.image_generator import generate_image
    from app.services.layout_builder import build_comic_layout
    from app.services.exporters import save_pdf
    comic_id = uuid.uuid4().hex
    outline = generate_outline(request)
    story = generate_story(request, outline)

    image_urls = []
    for panel in story.panels:
        prompt = (
            f"{panel.image_prompt}. "
            f"Consistent protagonist named {request.character_name}. "
            f"Setting: {request.setting}. Style: {request.art_style}. "
            "Cohesive comic illustration, clean composition, no readable text, no watermark."
        )
        image_urls.append(generate_image(prompt, comic_id, panel.panel_number))

    layout = build_comic_layout(comic_id, story, image_urls)
    _write_job(comic_id, layout)
    pdf_path = save_pdf(layout)
    layout.pdf_url = f"/static/exports/{pdf_path.name}"
    _write_job(comic_id, layout)
    return layout
