from pydantic import BaseModel
from typing import Literal, List, Dict, Any

BiasType = Literal["Gender", "Race", "Political", "Religion"]
AttackType = Literal[
    "PromptInjection",
    "Leetspeak",
    "MathProblem",
    "ROT13",
    "LinearJailbreaking",
    "TreeJailbreaking",
    "CrescendoJailbreaking",
]

class RedTeamRequest(BaseModel):
    bias: BiasType
    attack: AttackType

class RedTeamReport(BaseModel):
    test_cases: List[Dict[str, Any]]
    overall_score: int
    details: Dict[str, Any]