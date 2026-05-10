from fastapi import APIRouter, HTTPException
from db.mongo import get_collection
from core.oid import oid
from models.schemas import OutlineUpdate

router = APIRouter(prefix="/api/projects/{project_id}/outline", tags=["outline"])


@router.get("/")
async def get_outline(project_id: str):
    col = get_collection("outlines")
    outline = await col.find_one({"project_id": oid(project_id)})
    if not outline:
        raise HTTPException(404, "大纲不存在")
    outline["id"] = str(outline["_id"])
    outline["project_id"] = str(outline["project_id"])
    del outline["_id"]
    return outline


@router.put("/")
async def update_outline(project_id: str, data: OutlineUpdate):
    col = get_collection("outlines")
    update_fields = {k: v for k, v in data.dict().items() if v is not None}
    result = await col.update_one(
        {"project_id": oid(project_id)},
        {"$set": update_fields},
    )
    if result.matched_count == 0:
        raise HTTPException(404, "大纲不存在")
    return {"message": "大纲更新成功"}
