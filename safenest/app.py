from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from insights_transactions import get_trxn_viz, get_trxn_summary

app = FastAPI()

class VizRequest(BaseModel):
    user_id: int
    monthly: int | None = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/get_trxn_viz/")
async def trxn_viz(req: VizRequest):
    data = await get_trxn_viz(req.user_id, req.monthly)

    return data

@app.post("/api/get_trxn_summary/")
async def trxn_summary(req: VizRequest):
    data = await get_trxn_summary(req.user_id, req.monthly)

    return data
