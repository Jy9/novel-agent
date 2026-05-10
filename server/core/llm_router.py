import httpx
from db.mongo import get_collection
from core.crypto import decrypt
from core.oid import oid


def _build_request_config(provider: dict) -> dict:
    api_key = decrypt(provider.get("api_key_encrypted", ""))
    provider_type = provider["type"]
    model = provider["model"]
    api_base = provider.get("api_base", "").rstrip("/")
    params = provider.get("params", {})

    if provider_type == "anthropic":
        return {
            "url": f"{api_base}/v1/messages",
            "headers": {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            "type": "anthropic",
            "model": model,
            "params": params,
        }
    else:
        base = api_base
        if provider_type == "ollama":
            base = api_base or "http://localhost:11434"
        elif provider_type == "openai":
            base = api_base or "https://api.openai.com/v1"
        elif provider_type == "custom":
            pass

        return {
            "url": f"{base}/chat/completions",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            "type": "openai",
            "model": model,
            "params": params,
        }


async def get_llm_config_for_agent(agent_name: str) -> dict | None:
    bindings_col = get_collection("agent_bindings")
    binding = await bindings_col.find_one({})
    if not binding:
        return None

    provider_id = binding.get(f"{agent_name}_provider_id")
    if not provider_id:
        return None

    providers_col = get_collection("llm_providers")
    provider = await providers_col.find_one({"_id": oid(provider_id)})
    if not provider:
        return None

    return _build_request_config(provider)


async def test_llm_connection(provider: dict) -> dict:
    config = _build_request_config(provider)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if config["type"] == "anthropic":
                resp = await client.post(
                    config["url"],
                    headers=config["headers"],
                    json={
                        "model": config["model"],
                        "max_tokens": 20,
                        "messages": [{"role": "user", "content": "你好，请回复连接成功"}],
                    },
                )
                data = resp.json()
                if resp.status_code == 200:
                    text = data.get("content", [{}])[0].get("text", "连接成功")
                    return {"success": True, "response": text}
                else:
                    return {"success": False, "error": data.get("error", {}).get("message", str(data))}
            else:
                resp = await client.post(
                    config["url"],
                    headers=config["headers"],
                    json={
                        "model": config["model"],
                        "max_tokens": 20,
                        "messages": [{"role": "user", "content": "你好，请回复连接成功"}],
                    },
                )
                data = resp.json()
                if resp.status_code == 200:
                    text = data.get("choices", [{}])[0].get("message", {}).get("content", "连接成功")
                    return {"success": True, "response": text}
                else:
                    return {"success": False, "error": data.get("error", {}).get("message", str(data))}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def test_llm_by_config(type: str, api_base: str, api_key: str, model: str) -> dict:
    provider = {
        "type": type,
        "api_base": api_base,
        "api_key_encrypted": "",
        "model": model,
        "params": {},
    }
    if api_key:
        from core.crypto import encrypt
        provider["api_key_encrypted"] = encrypt(api_key)
    return await test_llm_connection(provider)


async def stream_chat(config: dict, messages: list):
    if config["type"] == "anthropic":
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                config["url"],
                headers=config["headers"],
                json={
                    "model": config["model"],
                    "max_tokens": config["params"].get("max_tokens", 4096),
                    "temperature": config["params"].get("temperature", 0.7),
                    "stream": True,
                    "messages": messages,
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            return
                        import json
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get("delta", {})
                            text = delta.get("text", "")
                            if text:
                                yield text
                        except:
                            pass
    else:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                config["url"],
                headers=config["headers"],
                json={
                    "model": config["model"],
                    "max_tokens": config["params"].get("max_tokens", 4096),
                    "temperature": config["params"].get("temperature", 0.7),
                    "stream": True,
                    "messages": messages,
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            return
                        import json
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            text = delta.get("content", "")
                            if text:
                                yield text
                        except:
                            pass
