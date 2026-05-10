from fastapi import APIRouter, HTTPException
from db.mongo import get_collection
from core.oid import oid
from models.schemas import WorldviewUpdate

router = APIRouter(prefix="/api/projects/{project_id}/worldview", tags=["worldview"])


@router.get("/")
async def get_worldview(project_id: str):
    col = get_collection("worldviews")
    wv = await col.find_one({"project_id": oid(project_id)})
    if not wv:
        raise HTTPException(404, "世界观不存在")
    wv["id"] = str(wv["_id"])
    wv["project_id"] = str(wv["project_id"])
    del wv["_id"]
    return wv


@router.put("/")
async def update_worldview(project_id: str, data: WorldviewUpdate):
    col = get_collection("worldviews")
    update_fields = {k: v for k, v in data.dict().items() if v is not None}
    result = await col.update_one(
        {"project_id": oid(project_id)},
        {"$set": update_fields},
    )
    if result.matched_count == 0:
        raise HTTPException(404, "世界观不存在")
    return {"message": "世界观更新成功"}
