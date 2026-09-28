from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.schemas import PromptRequest, GenerateResponse
from app.services.pipeline import generate_comic, load_job
from app.services.image_generator import generate_image

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        layout = generate_comic(data)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={"layout": layout},
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=500,
        )

@router.post("/generate-comic/json", response_model=GenerateResponse)
async def generate_json(payload: PromptRequest):
    try:
        layout = generate_comic(payload)
        return GenerateResponse(
            comic_id=layout.comic_id,
            layout=layout,
            pdf_url=layout.pdf_url or "",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/comic/{comic_id}", response_class=HTMLResponse)
async def comic_preview(request: Request, comic_id: str):
    try:
        layout = load_job(comic_id)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={"layout": layout},
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, comic_id: str):
    try:
        layout = load_job(comic_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"layout": layout},
    )

@router.get("/download/{comic_id}")
async def download_pdf(comic_id: str):
    settings = get_settings()
    path = settings.exports_dir / f"{comic_id}.pdf"
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(path, media_type="application/pdf", filename=f"{comic_id}.pdf")

@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    try:
        image_url = generate_image(prompt, "test", 1)
        return {"image_url": image_url}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
