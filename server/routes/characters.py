from fastapi import APIRouter, HTTPException
from db.mongo import get_collection
from core.oid import oid
from models.schemas import CharacterCreate, CharacterUpdate

router = APIRouter(prefix="/api/projects/{project_id}/characters", tags=["characters"])


@router.get("/")
async def list_characters(project_id: str):
    col = get_collection("characters")
    characters = []
    async for c in col.find({"project_id": oid(project_id)}):
        c["id"] = str(c["_id"])
        c["project_id"] = str(c["project_id"])
        del c["_id"]
        characters.append(c)
    return characters


@router.post("/")
async def create_character(project_id: str, data: CharacterCreate):
    col = get_collection("characters")
    doc = data.dict()
    doc["project_id"] = oid(project_id)
    result = await col.insert_one(doc)
    return {"id": str(result.inserted_id), "message": "角色创建成功"}


@router.put("/{character_id}")
async def update_character(project_id: str, character_id: str, data: CharacterUpdate):
    col = get_collection("characters")
    update_fields = {k: v for k, v in data.dict().items() if v is not None}
    if not update_fields:
        raise HTTPException(400, "没有更新内容")
    result = await col.update_one(
        {"_id": oid(character_id), "project_id": oid(project_id)},
        {"$set": update_fields},
    )
    if result.matched_count == 0:
        raise HTTPException(404, "角色不存在")
    return {"message": "角色更新成功"}


@router.delete("/{character_id}")
async def delete_character(project_id: str, character_id: str):
    col = get_collection("characters")
    result = await col.delete_one({
        "_id": oid(character_id),
        "project_id": oid(project_id),
    })
    if result.deleted_count == 0:
        raise HTTPException(404, "角色不存在")
    return {"message": "角色已删除"}
