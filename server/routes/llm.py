from fastapi import APIRouter, HTTPException
from db.mongo import get_collection
from core.crypto import encrypt
from core.oid import oid
from core.llm_router import test_llm_connection, test_llm_by_config
from models.schemas import (
    LLMProviderCreate, LLMProviderUpdate,
    LLMTestRequest, AgentBindingUpdate,
)

router = APIRouter(prefix="/api/llm", tags=["llm"])


@router.get("/providers")
async def list_providers():
    col = get_collection("llm_providers")
    providers = []
    async for p in col.find({}):
        p["id"] = str(p["_id"])
        p["api_key"] = "••••••••" if p.get("api_key_encrypted") else ""
        del p["_id"]
        if "api_key_encrypted" in p:
            del p["api_key_encrypted"]
        providers.append(p)
    return providers


@router.post("/providers")
async def create_provider(data: LLMProviderCreate):
    col = get_collection("llm_providers")
    doc = data.dict()
    doc["api_key_encrypted"] = encrypt(doc.pop("api_key"))
    result = await col.insert_one(doc)
    return {"id": str(result.inserted_id), "message": "创建成功"}


@router.put("/providers/{provider_id}")
async def update_provider(provider_id: str, data: LLMProviderUpdate):
    col = get_collection("llm_providers")
    update_fields = {k: v for k, v in data.dict().items() if v is not None}
    if "api_key" in update_fields:
        update_fields["api_key_encrypted"] = encrypt(update_fields.pop("api_key"))
    if not update_fields:
        raise HTTPException(400, "没有更新内容")
    result = await col.update_one(
        {"_id": oid(provider_id)},
        {"$set": update_fields},
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Provider不存在")
    return {"message": "更新成功"}


@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str):
    col = get_collection("llm_providers")
    result = await col.delete_one({"_id": oid(provider_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "Provider不存在")
    return {"message": "删除成功"}


@router.post("/test")
async def test_connection(data: LLMTestRequest):
    if data.provider_id:
        col = get_collection("llm_providers")
        provider = await col.find_one({"_id": oid(data.provider_id)})
        if not provider:
            raise HTTPException(404, "Provider不存在")
        return await test_llm_connection(provider)
    else:
        return await test_llm_by_config(
            type=data.type or "openai",
            api_base=data.api_base or "",
            api_key=data.api_key or "",
            model=data.model or "",
        )


@router.get("/bindings")
async def get_bindings():
    col = get_collection("agent_bindings")
    binding = await col.find_one({})
    if not binding:
        return {
            "planner_provider_id": None,
            "writer_provider_id": None,
            "reviewer_provider_id": None,
            "character_provider_id": None,
        }
    binding["id"] = str(binding["_id"])
    del binding["_id"]
    for key in ["planner_provider_id", "writer_provider_id", "reviewer_provider_id", "character_provider_id"]:
        if binding.get(key):
            binding[key] = str(binding[key])
    return binding


@router.put("/bindings")
async def update_bindings(data: AgentBindingUpdate):
    col = get_collection("agent_bindings")
    update_fields = {k: v for k, v in data.dict().items() if v is not None}
    for key, val in update_fields.items():
        if val:
            update_fields[key] = oid(val)
    existing = await col.find_one({})
    if existing:
        await col.update_one({"_id": existing["_id"]}, {"$set": update_fields})
    else:
        await col.insert_one(update_fields)
    return {"message": "绑定更新成功"}
