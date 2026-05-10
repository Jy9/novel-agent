from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LLMProviderCreate(BaseModel):
    name: str
    type: str
    api_base: str
    api_key: str
    model: str
    params: Optional[dict] = {}


class LLMProviderUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    params: Optional[dict] = None


class LLMTestRequest(BaseModel):
    provider_id: Optional[str] = None
    type: Optional[str] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None


class AgentBindingUpdate(BaseModel):
    planner_provider_id: Optional[str] = None
    writer_provider_id: Optional[str] = None
    reviewer_provider_id: Optional[str] = None
    character_provider_id: Optional[str] = None


class ProjectCreate(BaseModel):
    name: str
    genre: Optional[str] = ""
    description: Optional[str] = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None


class CharacterCreate(BaseModel):
    name: str
    personality: Optional[str] = ""
    background: Optional[str] = ""
    appearance: Optional[str] = ""
    speaking_style: Optional[str] = ""
    arc_description: Optional[str] = ""
    relationships: Optional[list] = []


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    appearance: Optional[str] = None
    speaking_style: Optional[str] = None
    arc_description: Optional[str] = None
    relationships: Optional[list] = None


class OutlineUpdate(BaseModel):
    structure_type: Optional[str] = "three_act"
    plot_points: Optional[list] = []


class WorldviewUpdate(BaseModel):
    geography: Optional[str] = ""
    history: Optional[str] = ""
    magic_system: Optional[str] = ""
    tech_level: Optional[str] = ""
    social_structure: Optional[str] = ""
    custom_fields: Optional[dict] = {}


class ChapterCreate(BaseModel):
    title: str
    order: Optional[int] = 0


class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    order: Optional[int] = None


class ChatRequest(BaseModel):
    message: str
    agent: Optional[str] = "writer"
