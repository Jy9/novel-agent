from db.mongo import get_collection
from core.llm_router import get_llm_config_for_agent, stream_chat
from core.oid import oid


async def load_project_context(project_id: str) -> dict:
    _oid = oid(project_id)

    chapters_col = get_collection("chapters")
    characters_col = get_collection("characters")
    worldviews_col = get_collection("worldviews")
    outlines_col = get_collection("outlines")

    recent_chapters = await chapters_col.find({"project_id": _oid}).sort("order", -1).to_list(3)
    characters = await characters_col.find({"project_id": _oid}).to_list(100)
    worldview = await worldviews_col.find_one({"project_id": _oid})
    outline = await outlines_col.find_one({"project_id": _oid})

    chapter_summaries = []
    for ch in reversed(recent_chapters):
        content = ch.get("content", "")
        summary = content[:500] if content else ""
        chapter_summaries.append({
            "title": ch.get("title", ""),
            "summary": summary,
            "status": ch.get("status", "draft"),
        })

    character_descs = []
    for c in characters:
        character_descs.append(
            f"- {c['name']}: 性格({c.get('personality', '')}), 背景({c.get('background', '')})"
        )

    worldview_text = ""
    if worldview:
        parts = []
        if worldview.get("geography"):
            parts.append(f"地理: {worldview['geography']}")
        if worldview.get("history"):
            parts.append(f"历史: {worldview['history']}")
        if worldview.get("magic_system"):
            parts.append(f"魔法体系: {worldview['magic_system']}")
        if worldview.get("tech_level"):
            parts.append(f"科技水平: {worldview['tech_level']}")
        if worldview.get("social_structure"):
            parts.append(f"社会结构: {worldview['social_structure']}")
        worldview_text = "\n".join(parts)

    outline_text = ""
    if outline and outline.get("plot_points"):
        points = []
        for p in outline["plot_points"]:
            points.append(f"  {p.get('order', 0)}. {p.get('title', '')}: {p.get('description', '')}")
        outline_text = "\n".join(points)

    return {
        "chapters": chapter_summaries,
        "characters": character_descs,
        "worldview": worldview_text,
        "outline": outline_text,
    }


def build_planner_prompt(context: dict, user_message: str) -> str:
    return f"""你是一位专业的小说策划师。根据以下信息，帮助用户规划故事。

## 已有世界观
{context.get('worldview', '暂无')}

## 已有角色
{chr(10).join(context.get('characters', ['暂无']))}

## 已有大纲
{context.get('outline', '暂无')}

## 已有章节摘要
{chr(10).join([f'- {c["title"]}: {c["summary"]}' for c in context.get('chapters', [])])}

## 用户需求
{user_message}

请提供详细的故事规划建议，包括情节走向、冲突设计、节奏安排等。"""


def build_writer_prompt(context: dict, user_message: str) -> str:
    return f"""你是一位才华横溢的小说作家。根据以下信息进行创作。

## 世界观
{context.get('worldview', '暂无')}

## 角色信息
{chr(10).join(context.get('characters', ['暂无']))}

## 大纲
{context.get('outline', '暂无')}

## 前文摘要
{chr(10).join([f'- {c["title"]}: {c["summary"]}' for c in context.get('chapters', [])])}

## 创作要求
{user_message}

请直接输出小说正文内容，不要输出解释说明。注意保持与前文的一致性，角色对话要符合其性格。"""


def build_reviewer_prompt(context: dict, content: str) -> str:
    return f"""你是一位严格的小说编辑和审查员。请审查以下内容。

## 世界观
{context.get('worldview', '暂无')}

## 角色信息
{chr(10).join(context.get('characters', ['暂无']))}

## 待审查内容
{content}

请从以下维度审查并打分(1-10)：
1. 角色行为一致性
2. 情节逻辑性
3. 文学质量
4. 节奏把控
5. 与前文一致性

输出格式：
- 总分: X/10
- 各维度评分
- 具体问题列表
- 修改建议"""


def build_character_prompt(context: dict, user_message: str) -> str:
    return f"""你是一位角色设计专家。根据以下信息，帮助用户设计或完善角色。

## 已有角色
{chr(10).join(context.get('characters', ['暂无']))}

## 世界观
{context.get('worldview', '暂无')}

## 用户需求
{user_message}

请提供详细的角色设计，包括：姓名、性格、背景故事、外貌描述、说话风格、角色弧线。"""


AGENT_PROMPT_BUILDERS = {
    "planner": build_planner_prompt,
    "writer": build_writer_prompt,
    "reviewer": build_reviewer_prompt,
    "character": build_character_prompt,
}


async def run_agent_stream(agent_name: str, project_id: str, user_message: str):
    config = await get_llm_config_for_agent(agent_name)
    if not config:
        for fallback in ["writer", "planner", "reviewer", "character"]:
            config = await get_llm_config_for_agent(fallback)
            if config:
                break
    if not config:
        yield "错误：未配置LLM模型，请先在设置中配置。"
        return

    context = await load_project_context(project_id)

    if agent_name == "reviewer":
        prompt = build_reviewer_prompt(context, user_message)
    else:
        builder = AGENT_PROMPT_BUILDERS.get(agent_name, build_writer_prompt)
        prompt = builder(context, user_message)

    messages = [{"role": "user", "content": prompt}]

    try:
        async for chunk in stream_chat(config, messages):
            yield chunk
    except Exception as e:
        yield f"\n\n[生成错误: {str(e)}]"
