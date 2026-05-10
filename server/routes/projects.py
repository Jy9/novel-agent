from fastapi import APIRouter, HTTPException
from datetime import datetime
from db.mongo import get_collection
from core.oid import oid
from models.schemas import ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/")
async def list_projects():
    col = get_collection("projects")
    projects = []
    async for p in col.find({}).sort("updated_at", -1):
        p["id"] = str(p["_id"])
        del p["_id"]
        projects.append(p)
    return projects


@router.post("/")
async def create_project(data: ProjectCreate):
    col = get_collection("projects")
    doc = data.dict()
    now = datetime.utcnow().isoformat()
    doc["created_at"] = now
    doc["updated_at"] = now
    result = await col.insert_one(doc)

    outlines_col = get_collection("outlines")
    await outlines_col.insert_one({
        "project_id": result.inserted_id,
        "structure_type": "three_act",
        "plot_points": [],
    })

    worldviews_col = get_collection("worldviews")
    await worldviews_col.insert_one({
        "project_id": result.inserted_id,
        "geography": "",
        "history": "",
        "magic_system": "",
        "tech_level": "",
        "social_structure": "",
        "custom_fields": {},
    })

    return {"id": str(result.inserted_id), "message": "项目创建成功"}


@router.get("/{project_id}")
async def get_project(project_id: str):
    col = get_collection("projects")
    p = await col.find_one({"_id": oid(project_id)})
    if not p:
        raise HTTPException(404, "项目不存在")
    p["id"] = str(p["_id"])
    del p["_id"]
    return p


@router.put("/{project_id}")
async def update_project(project_id: str, data: ProjectUpdate):
    col = get_collection("projects")
    update_fields = {k: v for k, v in data.dict().items() if v is not None}
    update_fields["updated_at"] = datetime.utcnow().isoformat()
    if not update_fields:
        raise HTTPException(400, "没有更新内容")
    await col.update_one({"_id": oid(project_id)}, {"$set": update_fields})
    return {"message": "更新成功"}


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    _oid = oid(project_id)
    col = get_collection("projects")
    result = await col.delete_one({"_id": _oid})
    if result.deleted_count == 0:
        raise HTTPException(404, "项目不存在")

    for name in ["chapters", "characters", "outlines", "worldviews", "memories"]:
        await get_collection(name).delete_many({"project_id": _oid})

    return {"message": "项目已删除"}
