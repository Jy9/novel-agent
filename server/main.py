from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import CORS_ORIGINS
from routes import llm, projects, outline, characters, worldview, chapters, chat

app = FastAPI(title="小说Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm.router)
app.include_router(projects.router)
app.include_router(outline.router)
app.include_router(characters.router)
app.include_router(worldview.router)
app.include_router(chapters.router)
app.include_router(chat.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
