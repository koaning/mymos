# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "anthropic==0.45.2",
#     "instructor==1.7.2",
#     "jinja2==3.1.5",
#     "marimo",
#     "matplotlib==3.10.0",
#     "mohtml==0.1.2",
#     "openai-whisper==20240930",
#     "opencv-python==4.11.0.86",
#     "pydantic==2.10.6",
#     "python-dotenv==1.0.1",
#     "yt-dlp==2025.1.26",
# ]
# ///

import marimo

__generated_with = "0.10.19"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import matplotlib.pylab as plt
    import cv2
    from yt_dlp import YoutubeDL
    from pathlib import Path

    def download_yt(yt_url: str): 
        yt_id = yt_url[-11:]
        video_path = f"{yt_id}.m4a"
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]
        }

        if not Path(video_path).exists():
            URLS = [yt_url]
            with YoutubeDL() as ydl:
                ydl.download(URLS)
            video_file = list(Path().glob("*.mp4"))[0]
            video_file.rename(video_path)
        else:
            print("Video has been downloaded already")
    return Path, YoutubeDL, cv2, download_yt, mo, plt


@app.cell
def _(mo):
    text_input = mo.ui.text(label="YouTube URL")
    text_input
    return (text_input,)


@app.cell
def _(text_input):
    f"{text_input.value[-11:]}.m4a"
    return


@app.cell
def _(download_yt, text_input):
    if text_input.value:
        download_yt(text_input.value)
    return


@app.cell
def _(text_input):
    import whisper

    model = whisper.load_model("base")
    result = model.transcribe(f"{text_input.value[-11:]}.m4a")
    print(result["text"])
    return model, result, whisper


@app.cell
def _(YoutubeDL, text_input):
    with YoutubeDL() as ydl:
        info = ydl.extract_info(text_input.value, download=False)
    return info, ydl


@app.cell
def _():
    from typing import List
    import instructor
    from pydantic import BaseModel


    class YouTubeOutput(BaseModel):
        """
        Output of a YouTube video that reviews ergonomic keyboards.

        Make sure that you have a clear summary that highlights some of the findings. Refer to the reviewer as "me" and write as if it was written by the reviewer. But not in the present tense, it needs to be past tense. Avoid a formal style, write as if it was written on an informal tech-blog. Also make sure that you create a sequences of pros and cons of the keyboard. No more than 4 pros and 4 cons. Also add a oneliner tldr for the review, typically you can just copy what is in the title. The name of the keyboard should also include the brand if there is one. 
        """
        summary: str
        pros: List[str]
        cons: List[str]
        tldr: str
        keyboard_name: str
    return BaseModel, List, YouTubeOutput, instructor


@app.cell
def _(instructor):
    from instructor import Instructor, Mode, patch
    from anthropic import Anthropic
    from dotenv import load_dotenv
    import os

    load_dotenv(".env")

    client = instructor.from_anthropic(
        Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"]),
    )
    return Anthropic, Instructor, Mode, client, load_dotenv, os, patch


@app.cell
def _(YouTubeOutput, client, info, result):
    response = client.chat.completions.create(
        model="claude-3-5-sonnet-20241022",
        messages=[
            {
                "role": "user",
                "content": f"Create a proper summary of the following keyboard review. This is the title: {info['title']}. This is the text for the full review: {result['text']}",
            }
        ],
        max_tokens=1500,
        response_model=YouTubeOutput,
    )
    return (response,)


@app.cell
def _(response):
    response.keyboard_name
    return


@app.cell
def _(info, response, text_input):
    from mohtml import pre, p, code
    from jinja2 import Template

    template = Template("""
    ---
    hide:
    - toc
    - navigation
    title: {{keyboard_name}}
    ---

    ## {{tldr}}

    <iframe width="100%" height="500" src="https://www.youtube.com/embed/{{video_idx}}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

    {{summary}}

    ## Pros
    {% for pro in pros %}
    - {{ pro }}
    {% endfor %}

    ## Cons
    {% for con in cons %}
    - {{ con }}
    {% endfor %}

    """)


    template.render(
        summary=response.summary, 
        pros=response.pros, 
        cons=response.cons,
        title=info["title"], 
        thumbnail=info["thumbnail"],
        keyboard_name=response.keyboard_name,
        tldr=response.tldr, 
        video_idx=f"{text_input.value[-11:]}"
    )
    return Template, code, p, pre, template


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
