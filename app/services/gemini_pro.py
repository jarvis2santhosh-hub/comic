import time

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import OutlineResponse, PromptRequest, StoryResponse


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


def generate_story(
    request: PromptRequest,
    outline: OutlineResponse,
) -> StoryResponse:
    settings = get_settings()
    outline_json = outline.model_dump_json(indent=2)

    prompt = f"""
Expand this comic outline into polished panel-by-panel narration.

Character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}
Original idea: {request.story_prompt}

Outline:
{outline_json}

Rules:
- Preserve the panel order, titles, scene descriptions, and image prompts.
- Keep the character and setting consistent.
- caption: one short ambient/comic caption.
- narration: concise narrative prose.
- dialogue: natural dialogue; use an empty string if no dialogue is appropriate.
- Do not add panels.
- Do not put dialogue text inside image_prompt.
- Avoid copyrighted characters, logos, or living artists' names.
"""

    config = types.GenerateContentConfig(
        temperature=0.85,
        response_mime_type="application/json",
        response_schema=StoryResponse,
    )

    response = _generate_with_retry(
        client=_client(),
        model=settings.gemini_story_model,
        contents=prompt,
        config=config,
    )

    return StoryResponse.model_validate_json(response.text)