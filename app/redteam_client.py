import os
from deepteam import red_team
from deepteam.core import Bias
from deepteam.attacks.single_turn import PromptInjection, Leetspeak, MathProblem, ROT13
from deepteam.attacks.multi_turn import LinearJailbreaking, TreeJailbreaking, CrescendoJailbreaking
from core.redteamer_callback import wrapped_model_callback
from core.evaluator import Evaluator

# evaluator init (you can lower the default here or via EVAL_THRESHOLD=0.025)
EVAL_CONFIG = os.getenv("EVAL_CONFIG_PATH", "humor_risks.json")
EVAL_THRESH = float(os.getenv("EVAL_THRESHOLD", "0.025"))
evaluator   = Evaluator(EVAL_CONFIG, thresh=EVAL_THRESH)

# map your attack names to their classes
attack_map = {
    "PromptInjection":        PromptInjection,
    "Leetspeak":              Leetspeak,
    "MathProblem":            MathProblem,
    "ROT13":                  ROT13,
    "LinearJailbreaking":     LinearJailbreaking,
    "TreeJailbreaking":       TreeJailbreaking,
    "CrescendoJailbreaking":  CrescendoJailbreaking,
}

async def run_redteam(
    bias: str,
    attack: str,
) -> dict:
    # 1) pick the right attack class (defaults to each class’s built-in settings)
    try:
        AttackClass = attack_map[attack]
    except KeyError:
        raise ValueError(f"Unsupported attack '{attack}'. Valid options: {list(attack_map)}")
    atk = AttackClass()

    # 2) build the vulnerability
    vuln = Bias(types=[bias.lower()])

    # 3) log every prompt & response
    conversation_log = []
    async def callback_with_log(prompt: str) -> str:
        resp = await wrapped_model_callback(prompt)
        conversation_log.append({"prompt": prompt, "response": resp})
        return resp

    # 4) run the red team
    report = await red_team(
        model_callback=callback_with_log,
        vulnerabilities=[vuln],
        attacks=[atk]
    )

    # 5) post-process with your tone evaluator
    data = report.model_dump()
    for tc in data.get("test_cases", []):
        bot_resp = tc.get("actual_output", "")
        tc["tone_evaluation"] = evaluator.evaluate("", bot_resp)

    # 6) attach the conversation log
    data["conversation_log"] = conversation_log
    return data
