import os
from deepteam import red_team
from deepteam.vulnerabilities import Bias
from deepteam.attacks.single_turn import (
    PromptInjection, Leetspeak, MathProblem, ROT13
)
from deepteam.attacks.multi_turn import (
    LinearJailbreaking, TreeJailbreaking, CrescendoJailbreaking
)
from core.redteamer_callback import wrapped_model_callback
from core.evaluator import Evaluator

# Initialize evaluator using your KG JSON
EVAL_CONFIG = os.getenv("EVAL_CONFIG_PATH", "humor_risks.json")
EVAL_THRESH  = float(os.getenv("EVAL_THRESHOLD", "0.05"))
evaluator   = Evaluator(EVAL_CONFIG, thresh=EVAL_THRESH)

attack_map = {
    "PromptInjection":    PromptInjection,
    "Leetspeak":          Leetspeak,
    "MathProblem":        MathProblem,
    "ROT13":              ROT13,
    "LinearJailbreaking": LinearJailbreaking,
    "TreeJailbreaking":   TreeJailbreaking,
    "CrescendoJailbreaking": CrescendoJailbreaking,
}

async def run_redteam(bias: str, attack: str) -> dict:
    vuln = Bias(types=[bias.lower()])
    atk  = attack_map[attack]()
    report = red_team(
        model_callback=wrapped_model_callback,
        vulnerabilities=[vuln],
        attacks=[atk]
    )

    data = report.model_dump()
    # post-process each test case
    for tc in data.get("test_cases", []):
        bot_resp = tc.get("actual_output", "")
        tc["tone_evaluation"] = evaluator.evaluate("", bot_resp)
    return data