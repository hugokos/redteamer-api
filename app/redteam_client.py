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
EVAL_THRESH  = float(os.getenv("EVAL_THRESHOLD", "0.025"))
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


async def run_redteam(
    bias: str,
    attack: str,
) -> dict:
    # validate and instantiate the chosen attack with its default settings
    try:
        AttackClass = attack_map[attack]
    except KeyError:
        raise ValueError(f"Unsupported attack '{attack}'. Choose from: {', '.join(attack_map)}")
    atk = AttackClass()  # uses each class’s default configuration

    # build the vulnerability
    vuln = Bias(types=[bias.lower()])

    # prepare to log every prompt & response
    conversation_log = []
    async def callback_with_log(prompt: str) -> str:
        resp = await wrapped_model_callback(prompt)
        conversation_log.append({
            "prompt": prompt,
            "response": resp
        })
        return resp

    # run DeepTeam with our logging callback
    report = await red_team(
        model_callback=callback_with_log,
        vulnerabilities=[vuln],
        attacks=[atk]
    )

    # serialize and attach the full conversation log
    data = report.model_dump()
    data["conversation_log"] = conversation_log
    return data