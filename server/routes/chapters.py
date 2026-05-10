from fastapi import APIRouter, HTTPException
from datetime import datetime
from db.mongo import get_collection
from core.oid import oid
from models.schemas import ChapterCreate, ChapterUpdate

router = APIRouter(prefix="/api/projects/{project_id}/chapters", tags=["chapters"])


@router.get("/")
async def list_chapters(project_id: str):
    col = get_collection("chapters")
    chapters = []
    async for ch in col.find({"project_id": oid(project_id)}).sort("order", 1):
        ch["id"] = str(ch["_id"])
        ch["project_id"] = str(ch["project_id"])
        del ch["_id"]
        chapters.append(ch)
    return chapters


@router.post("/")
async def create_chapter(project_id: str, data: ChapterCreate):
    col = get_collection("chapters")
    doc = data.dict()
    doc["project_id"] = oid(project_id)
    doc["content"] = ""
    doc["status"] = "draft"
    doc["summary"] = ""
    doc["reviews"] = []
    doc["created_at"] = datetime.utcnow().isoformat()
    doc["updated_at"] = datetime.utcnow().isoformat()
    result = await col.insert_one(doc)
    return {"id": str(result.inserted_id), "message": "章节创建成功"}


@router.put("/{chapter_id}")
async def update_chapter(project_id: str, chapter_id: str, data: ChapterUpdate):
    col = get_collection("chapters")
    update_fields = {k: v for k, v in data.dict().items() if v is not None}
    update_fields["updated_at"] = datetime.utcnow().isoformat()
    if not update_fields:
        raise HTTPException(400, "没有更新内容")
    result = await col.update_one(
        {"_id": oid(chapter_id), "project_id": oid(project_id)},
        {"$set": update_fields},
    )
    if result.matched_count == 0:
        raise HTTPException(404, "章节不存在")
    return {"message": "章节更新成功"}


@router.delete("/{chapter_id}")
async def delete_chapter(project_id: str, chapter_id: str):
    col = get_collection("chapters")
    result = await col.delete_one({
        "_id": oid(chapter_id),
        "project_id": oid(project_id),
    })
    if result.deleted_count == 0:
        raise HTTPException(404, "章节不存在")
    return {"message": "章节已删除"}
