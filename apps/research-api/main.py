
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Research API (stub)")

class Quote(BaseModel):
    source_type: str
    community: str
    published_at: str
    upvotes: int
    span: str
    url: str = ""
    stance: str = "other"
    topics: List[str] = []

class GenerateRequest(BaseModel):
    product: str
    notes: str
    quotes: List[Quote]

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/research/run")
def research_run(req: GenerateRequest):
    # TODO: call your LLM with the strict JSON schema prompt and return persona JSON
    return {"status": "stub", "personas": [], "received_quotes": len(req.quotes)}
