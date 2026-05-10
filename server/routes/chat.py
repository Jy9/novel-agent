from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
from bson import ObjectId
from db.mongo import get_collection
from models.schemas import ChatRequest
from core.workflow import run_agent_stream

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/{project_id}")
async def chat(project_id: str, data: ChatRequest):
    try:
        ObjectId(project_id)
    except Exception:
        raise HTTPException(400, "无效的项目ID")

    async def event_generator():
        full_content = ""
        async for chunk in run_agent_stream(data.agent, project_id, data.message):
            full_content += chunk
            yield {"data": chunk, "event": "message"}
        yield {"data": "__done__", "event": "done"}

    return EventSourceResponse(event_generator())
