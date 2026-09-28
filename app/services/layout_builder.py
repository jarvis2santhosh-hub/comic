from app.schemas import ComicPanel, ComicLayout, StoryResponse

def build_comic_layout(comic_id: str, story: StoryResponse, image_urls: list[str]) -> ComicLayout:
    if len(story.panels) != len(image_urls):
        raise ValueError("Every story panel must have exactly one image.")
    panels = [
        ComicPanel(
            panel_number=panel.panel_number,
            title=panel.title,
            image_url=image_url,
            scene_description=panel.scene_description,
            caption=panel.caption,
            narration=panel.narration,
            dialogue=panel.dialogue,
            image_prompt=panel.image_prompt,
        )
        for panel, image_url in zip(story.panels, image_urls)
    ]
    return ComicLayout(comic_id=comic_id, panels=panels)
