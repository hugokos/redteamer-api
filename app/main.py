# app/main.py
import os
import logging
import traceback

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader

from app.models import RedTeamRequest, RedTeamReport
from app.redteam_client import run_redteam

# --- API key setup
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("Missing API_KEY env-var")

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

def get_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return key

# --- FastAPI app & logger
app = FastAPI(title="DeepTeam RedTeamer API (key-protected)")
logger = logging.getLogger("uvicorn.error")

@app.post(
    "/report",
    response_model=RedTeamReport,
    dependencies=[Depends(get_api_key)],
)
async def get_report(req: RedTeamRequest):
    try:
        result = await run_redteam(req.bias, req.attack)
        test_cases = result.get("test_cases", [])
        overall_score = sum(
            tc.get("tone_evaluation", {}).get("score", 0)
            for tc in test_cases
        )
        return RedTeamReport(
            test_cases=test_cases,
            overall_score=overall_score,
            details=result
        )
    except Exception as e:
        # log full traceback to Cloud Run logs
        tb = traceback.format_exc()
        logger.error(tb)
        # return the exception message to the client
        raise HTTPException(status_code=500, detail=str(e))
