"""The true test of release P1, once: the frozen workflow WP1.1, the previous workflow WP1.0, the controls (free) and the agent AP1.0 (PAID, Haiku 5.5) on P-TEST j = 0 to 9.
Usage: python eval/run_test_p1.py --free   (free arms only)      python eval/run_test_p1.py --paid cap=1.0   (adds the agent; Simmy's approval: $1 for the whole release)
The key is read from .env and never printed. Registry use is recorded at the end. Results: experiments/p1_test/."""
import json
import os
import sys
import time

import numpy as np
from scipy import stats

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
for d in ("src", "eval"):
    sys.path.insert(0, os.path.join(ROOT, d))
import ap10
import claim_stream as cs
import provider_prior
import score_prepay as sp
import seed_registry as reg
import wp10
import wp11_loop as L
from run_prepay_reference import build

TEST = [6001 + 41 * j for j in range(10)]
OUT = os.path.join(ROOT, "experiments", "p1_test")
PER_SEED_SHARE = 0.12                                   # no seed may take more than 12% of the dollar cap (ten seeds at 12% = 120%, so the total cap binds first)


def scored(stream, truth, dec, screened=True):
    r = sp.score(stream, truth, dec, screened=screened)
    r["sensitivity"] = sp.sensitivity(stream, truth, dec, screened)
    return {k: r[k] for k in ("score", "pended", "denied", "wrongful_pends", "wrongful_adjustments", "prevented", "staff", "abrasion", "fraud_dollars_prevented",
                              "share_overbilled_prevented", "median_days_to_pay", "sensitivity")}


def free_arms(seed):
    d, key = build(seed)
    stream, office = cs.Stream(d, seed=seed), cs.ClaimOffice(d, seed=seed)
    truth = sp.claim_truth(key, stream)
    prior = provider_prior.CausalPrior(stream)
    rule = L.frozen_rule()
    X = wp10.claim_features(stream, prior)
    j = wp10.FEATURES.index("n_today_clinician")
    import edit_rules
    arms = {"pay_all": [], "edits_tuned": edit_rules.run(stream, by="rendering", daily_max=20, member_max=6),
            "hand_rule_c1": wp10.decisions(stream, office, wp10.pick(stream, X[:, j], wp10.CAP_PER_DAY, 19.5)),
            "WP1.0": wp10.run(stream, office, prior, rule, cap=10, floor=0.0), "WP1.1": wp10.run(stream, office, prior, rule, cap=L.FROZEN["cap"], floor=L.FROZEN["floor"])}
    return seed, {n: scored(stream, truth, dec, n != "pay_all") for n, dec in arms.items()}


def agent_arm(seed, remaining):
    d, key = build(seed)
    stream, office = cs.Stream(d, seed=seed), cs.ClaimOffice(d, seed=seed)
    truth = sp.claim_truth(key, stream)
    prior = provider_prior.CausalPrior(stream)
    tools = ap10.PrepayTools(stream, office, prior, L.frozen_rule(), floor=L.FROZEN["floor"], cap=L.FROZEN["cap"])
    os.makedirs(OUT, exist_ok=True)
    dec = ap10.llm_agent(tools, cap_usd=min(remaining, PER_SEED_SHARE), log_path=os.path.join(OUT, f"agent_usage_{seed}.json"))
    return scored(stream, truth, dec), tools.spent_usd, tools.consulted_days, tools.fallback_days


def main():
    paid = "--paid" in sys.argv
    cap = float(next(a.split("=")[1] for a in sys.argv if a.startswith("cap="))) if paid else 0.0
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
    for arm in ("WP1.1-test", "WP1.0"):
        reg.check_run("4.2", TEST, arm, "test")
    if paid:
        reg.check_run("4.2", TEST, "AP1.0", "test")
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(8) as p:
        per = dict(p.map(free_arms, TEST))
    spent, extra = 0.0, {}
    if paid:
        for seed in TEST:
            r, usd, consulted, fb = agent_arm(seed, cap - spent)
            per[seed]["AP1.0"] = r
            extra[seed] = {"usd": round(usd, 5), "consulted_days": consulted, "advice_fallback_days": fb}
            spent += usd
            print(seed, "agent", r["score"], "spent so far", round(spent, 4), flush=True)
            if spent >= cap:
                print("cap reached; remaining seeds are not run with the agent")
                break
    names = ["pay_all", "edits_tuned", "hand_rule_c1", "WP1.0", "WP1.1"] + (["AP1.0"] if paid else [])
    seeds_with_agent = [s for s in TEST if "AP1.0" in per[s]]
    summ = L.summarize(per, TEST, [n for n in names if n != "AP1.0"])
    out = {"seeds": TEST, "summary": summ, "per_seed": per, "agent": {"spent_usd": round(spent, 5), "cap_usd": cap, "per_seed": extra, "seeds_run": seeds_with_agent}}
    if seeds_with_agent:
        w = np.array([per[s]["WP1.1"]["score"] for s in seeds_with_agent]); a = np.array([per[s]["AP1.0"]["score"] for s in seeds_with_agent])
        out["agent_vs_workflow"] = {"seeds": len(a), "agent_sum": round(float(a.sum())), "workflow_sum": round(float(w.sum())), "mean_diff_per_seed": round(float((a - w).mean())),
                                   "p_two_sided": float(stats.ttest_rel(a, w).pvalue) if np.any(a != w) else 1.0, "seeds_agent_better": int((a > w).sum())}
    w = np.array([per[s]["WP1.1"]["score"] for s in TEST]); e = np.array([per[s]["edits_tuned"]["score"] for s in TEST])
    t = stats.ttest_rel(w, e)
    cells = summ["WP1.1"]["cell_gains_sum"]
    out["workflow_vs_edit"] = {"mean_gain_per_seed": round(float((w - e).mean())), "p_one_sided": float(t.pvalue / 2 if t.statistic > 0 else 1 - t.pvalue / 2), "seeds_better": int((w > e).sum()),
                               "all_nine_cells_positive": all(v > 0 for v in cells.values()), "worst_cell_gain_per_seed": round(min(cells.values()) / len(TEST))}
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "results_paid.json" if paid else "results_free.json"), "w"), indent=1)
    print(json.dumps({"summary": {k: {kk: v[kk] for kk in ("sum", "median", "above_zero", "largest_seed_share", "worst_cell_gain_per_seed")} for k, v in summ.items()},
                      "workflow_vs_edit": out["workflow_vs_edit"], "agent": out["agent"], "agent_vs_workflow": out.get("agent_vs_workflow")}, indent=1))
    if "--record" in sys.argv:
        reg.record_use("4.2", "P-TEST", "WP1.1-test", "test", TEST, "docs/p1_test.md", "the frozen workflow's first test, with the agent run on the same seeds", "2026-10-25")
        reg.record_use("4.2", "P-TEST", "WP1.0", "test", TEST, "docs/p1_test.md", "the previous workflow re-run on the test seeds as a comparison (no tuning on them)", "2026-10-25")
        if paid:
            reg.record_use("4.2", "P-TEST", "AP1.0", "test", seeds_with_agent, "docs/p1_test.md", f"the agent (Haiku 5.5), once; spent ${spent:.4f} of a ${cap:.2f} cap", "2026-10-25")


if __name__ == "__main__":
    main()
