from fastapi import FastAPI, HTTPException
from app.models import RedTeamRequest, RedTeamReport
from app.redteam_client import run_redteam

app = FastAPI(
    title="DeepTeam RedTeamer API",
    description="Run adversarial attacks + tone evaluation on your LLM."
)

@app.post("/report", response_model=RedTeamReport)
async def get_report(req: RedTeamRequest):
    try:
        result = await run_redteam(req.bias, req.attack)
        test_cases   = result.get("test_cases", [])
        overall_score = sum(tc.get("tone_evaluation", {}).get("score", 0)
                            for tc in test_cases)
        return RedTeamReport(
            test_cases=test_cases,
            overall_score=overall_score,
            details=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))