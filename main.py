from fastapi import FastAPI
from pydantic import BaseModel

# from playwright_loader import PlaywrightLoader, html_to_markdown

app = FastAPI()


class UrlRequest(BaseModel):
    url: str


@app.get("/")
async def root():
    return {"message": "Hello World"}
