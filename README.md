# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application that turns a user's story idea, character, setting, tone, and art style into a five-panel illustrated comic and a downloadable PDF.

## Architecture

1. **Frontend:** Jinja2 + HTML/CSS.
2. **Backend:** FastAPI routes and Pydantic validation.
3. **Story AI:** Google Gemini generates a structured five-panel outline and then expands it into narration/dialogue.
4. **Image AI:** Hugging Face Inference Providers generate one image per panel.
5. **Export:** FPDF2 assembles the panel images and text into an A4 PDF.

The original project documentation names Gemini Flash/Pro and Stable Diffusion. This implementation keeps that architecture while making model names configurable because model availability changes over time. The default Gemini models are current configurable defaults; the image layer defaults to Hugging Face Inference Providers so a local GPU is not required.

## Requirements

- Python 3.11+
- A Gemini API key
- A Hugging Face token with inference access
- Internet access for the hosted AI providers

## VS Code setup

### 1. Open the project

Open the `ComicCraft` folder in VS Code.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure keys

Copy `.env.example` to `.env` and set:

```env
GEMINI_API_KEY=...
HF_TOKEN=...
```

Leave `IMAGE_BACKEND=huggingface` for the easiest setup.

### 5. Run

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## Testing

Run the automated tests:

```bash
pytest
```

These tests do not call paid AI services. They validate request schemas, layout construction, the health endpoint, and homepage rendering.

For an end-to-end AI test, submit the form at `/` after configuring both API keys. A complete generation calls Gemini twice and the image provider once per panel, so it can take a while and may incur provider usage charges.

## API

### POST `/generate`

HTML form fields:

- `story_prompt`
- `character_name`
- `setting`
- `tone`
- `art_style`

### POST `/generate-comic/json`

Example:

```json
{
  "story_prompt": "A brave fox exploring an enchanted forest.",
  "character_name": "Lumi",
  "setting": "Enchanted forest",
  "tone": "Funny",
  "art_style": "Comic book"
}
```

### POST `/test-image`

Form field:

```text
prompt=A fox hero in an enchanted forest, comic illustration
```

### GET `/download/{comic_id}`

Downloads the generated PDF.

## Optional local Stable Diffusion backend

The documentation also describes Hugging Face Diffusers and `runwayml/stable-diffusion-v1-5`. This project includes that backend, but it is optional because local diffusion requires a suitable machine and model download.

Install:

```bash
pip install -r requirements-local-diffusion.txt
```

Then set:

```env
IMAGE_BACKEND=local
LOCAL_DIFFUSION_MODEL=runwayml/stable-diffusion-v1-5
```

A CUDA-capable GPU is recommended for practical local image generation.

## Docker

Create `.env` first, then:

```bash
docker compose up --build
```

Open http://127.0.0.1:8000.

## Troubleshooting

### `GEMINI_API_KEY is not configured`

Check that `.env` exists in the project root and contains `GEMINI_API_KEY=...`.

### `HF_TOKEN is not configured`

Set `HF_TOKEN` in `.env`. Hugging Face Inference Providers require a token with inference permissions.

### Image provider/model unavailable

Set `HF_IMAGE_MODEL` to an image model currently available through Hugging Face Inference Providers, or switch to the local Diffusers backend.

### PDF export fails

Make sure generated panel files exist under `app/static/panels` and that the application has write permission for `app/static/exports`.

## Project structure

```text
ComicCraft/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── schemas.py
│   ├── services/
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   ├── image_generator.py
│   │   ├── layout_builder.py
│   │   ├── exporters.py
│   │   └── pipeline.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── comic_preview.html
│   │   └── export_success.html
│   ├── static/
│   │   ├── css/style.css
│   │   ├── panels/
│   │   └── exports/
│   └── storage/
├── tests/
├── requirements.txt
├── requirements-local-diffusion.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```
