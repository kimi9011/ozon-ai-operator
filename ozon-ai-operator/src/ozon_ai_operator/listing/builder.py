from __future__ import annotations
import os, json

def deterministic_listing(name:str, category:str, features:list[str]|None=None)->dict:
    features=features or []
    title=(name[:120]).strip()
    bullets=[f"{x}" for x in features[:5]] or ["Практичный товар для повседневного использования"]
    return {"title_ru":title,"category":category,"bullets_ru":bullets,"description_ru":". ".join(bullets)+".","status":"READY_FOR_REVIEW"}

def ai_listing(name:str, category:str, features:list[str]|None=None)->dict:
    """Optional AI generator. Falls back safely if SDK/key is unavailable."""
    if not os.getenv("OPENAI_API_KEY"):
        return deterministic_listing(name,category,features)
    try:
        from openai import OpenAI
        client=OpenAI()
        prompt={"name":name,"category":category,"features":features or [],"task":"Generate compliant concise Russian Ozon title, bullets and description. Return JSON."}
        r=client.responses.create(model=os.getenv("AI_MODEL","gpt-5-mini"),input=json.dumps(prompt,ensure_ascii=False))
        data=json.loads(r.output_text); data["status"]="READY_FOR_REVIEW"; return data
    except Exception:
        return deterministic_listing(name,category,features)
