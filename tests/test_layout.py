from app.schemas import PanelStory, StoryResponse
from app.services.layout_builder import build_comic_layout

def test_build_layout():
    story = StoryResponse(panels=[
        PanelStory(
            panel_number=1,
            title="Arrival",
            scene_description="A forest path.",
            caption="Morning.",
            narration="Lumi arrives.",
            dialogue="Hello!",
            image_prompt="fox in forest",
        )
    ])
    layout = build_comic_layout("abc", story, ["/static/panels/abc.png"])
    assert layout.comic_id == "abc"
    assert layout.panels[0].image_url.endswith("abc.png")
