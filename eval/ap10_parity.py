"""AP1.0 parity and cost estimate on development seeds (free, no model calls). The scripted agent follows the workflow's advice through the agent's tools; its decisions must equal
the workflow's (match rate 1.0), and the number of model turns a real run would take is counted to estimate the paid run from token counts.
Usage: python eval/ap10_parity.py <seed> [<seed> ...]   (rule = the frozen workflow's, fitted per eval/wp11_loop.py FROZEN)"""
import json
import sys
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
for d in ("src", "eval"):
    sys.path.insert(0, os.path.join(ROOT, d))
import ap10
import claim_stream as cs
import provider_prior
import score_prepay as sp
import wp10
import wp11_loop as L
from run_prepay_reference import build

SYSTEM_TOKENS, TOKENS_PER_CANDIDATE, TOKENS_PER_TURN_OUT, TOKENS_PER_RESULT = 350, 120, 160, 140


def one(seed, rule):
    d, key = build(seed)
    stream, office = cs.Stream(d, seed=seed), cs.ClaimOffice(d, seed=seed)
    prior = provider_prior.CausalPrior(stream)
    tools = ap10.PrepayTools(stream, office, prior, rule, floor=L.FROZEN["floor"], cap=L.FROZEN["cap"])
    agent = ap10.scripted_agent(tools)
    flow = wp10.run(stream, office, prior, rule, cap=L.FROZEN["cap"], floor=L.FROZEN["floor"])
    same = {(x.claim_id, x.paid_cpt) for x in agent} == {(x.claim_id, x.paid_cpt) for x in flow}
    # a real run: a model call on each day with a candidate worth a look; one turn to see the day, then two per pend (pend, read_chart), then done
    turns = tin = tout = 0
    for k in range(len(tools.days)):
        day = tools.next_day(k)
        if not any(c["advice"] == "PEND" or c["workflow_score_dollars"] > -15 for c in day["candidates"]):
            continue
        n_pend = sum(c["advice"] == "PEND" for c in day["candidates"])
        t = 2 + n_pend                                          # day turn, one turn for all pends of the round, reads, done
        base = SYSTEM_TOKENS + TOKENS_PER_CANDIDATE * len(day["candidates"])
        for j in range(t):
            tin += base + TOKENS_PER_RESULT * j * max(1, n_pend) // 2 + 100
            tout += TOKENS_PER_TURN_OUT
        turns += t
    return {"seed": seed, "match": same, "agent_pends": len(agent), "workflow_pends": len(flow), "days_with_model_call": sum(1 for k in range(len(tools.days))
            if any(c["advice"] == "PEND" or c["workflow_score_dollars"] > -15 for c in tools.next_day(k)["candidates"])), "turns": turns, "input_tokens": tin, "output_tokens": tout}


if __name__ == "__main__":
    seeds = [int(s) for s in sys.argv[1:]]
    rule = L.frozen_rule()
    rows = [one(s, rule) for s in seeds]
    tin, tout = sum(r["input_tokens"] for r in rows), sum(r["output_tokens"] for r in rows)
    est = {m: round((tin * p[0] + tout * p[1]) / 1e6, 2) for m, p in ap10.PRICES.items()}
    print(json.dumps({"rows": rows, "per_seed_tokens": [tin // len(rows), tout // len(rows)], "estimated_usd_per_seed_no_cache": {m: round(v / len(rows), 2) for m, v in est.items()},
                      "estimated_usd_all_no_cache": est}, indent=1))
