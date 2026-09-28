from pathlib import Path
from PIL import Image
from huggingface_hub import InferenceClient

from app.config import get_settings

_LOCAL_PIPELINE = None

def _safe_name(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in text).strip("-")[:60] or "panel"

def _generate_huggingface(prompt: str) -> Image.Image:
    settings = get_settings()
    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is not configured.")
    client = InferenceClient(
        provider=settings.hf_provider,
        api_key=settings.hf_token,
    )
    return client.text_to_image(
        prompt,
        model=settings.hf_image_model,
        width=settings.image_width,
        height=settings.image_height,
    )

def _generate_local(prompt: str) -> Image.Image:
    global _LOCAL_PIPELINE
    settings = get_settings()
    try:
        import torch
        from diffusers import StableDiffusionPipeline
    except ImportError as exc:
        raise RuntimeError(
            "Local Diffusers backend requires torch and diffusers. "
            "Install the optional local dependencies."
        ) from exc

    if _LOCAL_PIPELINE is None:
        device = settings.local_device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        _LOCAL_PIPELINE = StableDiffusionPipeline.from_pretrained(
            settings.local_diffusion_model,
            torch_dtype=dtype,
        )
        _LOCAL_PIPELINE = _LOCAL_PIPELINE.to(device)

    result = _LOCAL_PIPELINE(
        prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=25,
        guidance_scale=7.0,
    )
    return result.images[0]

def generate_image(prompt: str, comic_id: str, panel_number: int) -> str:
    settings = get_settings()
    if settings.image_backend == "local":
        image = _generate_local(prompt)
    else:
        image = _generate_huggingface(prompt)

    filename = f"{comic_id}-panel-{panel_number:02d}-{_safe_name(prompt)}.png"
    output = settings.panels_dir / filename
    image.save(output, format="PNG")
    return f"/static/panels/{filename}"
