from app.schemas import PromptRequest

def test_prompt_request_strips_whitespace():
    item = PromptRequest(
        story_prompt="  fox adventure  ",
        character_name=" Lumi ",
        setting="forest",
        tone="funny",
        art_style="comic book",
    )
    assert item.story_prompt == "fox adventure"
    assert item.character_name == "Lumi"
