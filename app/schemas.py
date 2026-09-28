from typing import List
from pydantic import BaseModel, Field, field_validator

class PromptRequest(BaseModel):
    story_prompt: str = Field(min_length=5, max_length=2000)
    character_name: str = Field(min_length=1, max_length=80)
    setting: str = Field(min_length=1, max_length=120)
    tone: str = Field(min_length=1, max_length=60)
    art_style: str = Field(min_length=1, max_length=100)

    @field_validator("*")
    @classmethod
    def strip_values(cls, value: str) -> str:
        return value.strip()

class PanelOutline(BaseModel):
    panel_number: int = Field(ge=1, le=20)
    title: str
    scene_description: str
    image_prompt: str

class OutlineResponse(BaseModel):
    panels: List[PanelOutline] = Field(min_length=1, max_length=20)

class PanelStory(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str

class StoryResponse(BaseModel):
    panels: List[PanelStory]

class ComicPanel(BaseModel):
    panel_number: int
    title: str
    image_url: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str

class ComicLayout(BaseModel):
    comic_id: str
    panels: List[ComicPanel]
    pdf_url: str | None = None

class GenerateResponse(BaseModel):
    comic_id: str
    layout: ComicLayout
    pdf_url: str
