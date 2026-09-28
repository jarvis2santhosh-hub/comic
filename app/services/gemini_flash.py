import time

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import OutlineResponse, PromptRequest


def _client() -> genai.Client:
    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    return genai.Client(api_key=settings.gemini_api_key)


def _generate_with_retry(
    client: genai.Client,
    model: str,
    contents: str,
    config: types.GenerateContentConfig,
    attempts: int = 4,
):
    last_error = None

    for attempt in range(attempts):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )

        except Exception as exc:
            last_error = exc
            message = str(exc)

            # Retry temporary Gemini availability errors.
            if "503" not in message and "UNAVAILABLE" not in message:
                raise

            if attempt == attempts - 1:
                raise

            wait_seconds = 2 ** attempt
            print(
                f"Gemini temporarily unavailable. "
                f"Retrying in {wait_seconds} seconds..."
            )
            time.sleep(wait_seconds)

    raise last_error


def generate_outline(request: PromptRequest) -> OutlineResponse:
    settings = get_settings()

    prompt = f"""
Create a cohesive {settings.max_panels}-panel comic outline.

User story idea: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Rules:
- Exactly {settings.max_panels} panels.
- Keep the same protagonist and visual identity throughout.
- Each panel must advance the story.
- image_prompt must be a clean text-to-image prompt and must not contain dialogue text.
- Avoid copyrighted characters, logos, or living artists' names.
- Return only data matching the supplied schema.
"""

    config = types.GenerateContentConfig(
        temperature=0.9,
        response_mime_type="application/json",
        response_schema=OutlineResponse,
    )

    response = _generate_with_retry(
        client=_client(),
        model=settings.gemini_outline_model,
        contents=prompt,
        config=config,
    )

    return OutlineResponse.model_validate_json(response.text)