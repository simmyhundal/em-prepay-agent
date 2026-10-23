"""WP1.0: the arm's cost copies equal score P1.0's, the arm never touches eval/ or the answer key, features and picks are causal, the daily cap holds.
Builds one D4.2 dataset from the pinned generator (skipped without it). Run: python tests/test_wp10.py"""
import os
import re
import subprocess
import sys
import tempfile
from datetime import timedelta

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "eval"))
GEN = os.path.join(ROOT, "external", "em-upcoding-agent", "src", "generate_v2.py")
ARM_FILES = ("wp10.py", "provider_prior.py", "prepay_env.py", "claim_stream.py", "ap10.py")


def test_cost_copies_equal_the_score_parameters():
    import score_prepay as sp
    import wp10
    for k, v in wp10.COSTS.items():
        assert sp.PARAMS[k] == v, k
    assert wp10.WAGE == sp.WAGE and wp10.HOURS == sp.HOURS and wp10.BENEFIT == sp.BENEFIT


def test_the_arm_never_reads_the_answer_key_or_eval():
    import ast
    evalmods = {f[:-3] for f in os.listdir(os.path.join(ROOT, "eval")) if f.endswith(".py")}
    for f in ARM_FILES:
        tree = ast.parse(open(os.path.join(ROOT, "src", f)).read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not {a.name.split(".")[0] for a in node.names} & evalmods, f
            if isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] not in evalmods, f
        docs = {id(n.body[0].value) for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body
                and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant)}
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs:
                assert not any(bad in node.value for bad in ("answer_key", "justified_cpt_by_claim", "fraud_claims")), (f, node.value)
        if f != "claim_stream.py":                           # the office (claim_stream) reads the records universe; the arm sees only its answers
            assert "unrendered" not in open(os.path.join(ROOT, "src", f)).read().replace("never rendered", ""), f


def test_features_and_picks_are_causal_and_the_cap_holds():
    if not os.path.exists(GEN):
        print("skip: run tools/get_generator.sh first")
        return
    import claim_stream as cs
    import provider_prior as pp
    import wp10
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "d")
        subprocess.run([sys.executable, GEN, out, "--seed", "1001", "--data-version", "4.2", "--answer-key", os.path.join(tmp, "k.json")], check=True, capture_output=True)
        s = cs.Stream(out, seed=1)
        cut_date = s.claims[len(s.claims) // 3].receipt_date
        cut = cs.Stream(out, seed=1)
        cut.claims = [c for c in s.claims if c.receipt_date <= cut_date]
        cut.by_id = {c.claim_id: c for c in cut.claims}
        cut._by_provider, cut._by_rendering = {}, {}
        for c in cut.claims:
            cut._by_provider.setdefault(c.provider, []).append(c)
            cut._by_rendering.setdefault(c.rendering, []).append(c)
        P, Pc = pp.CausalPrior(s, refresh_days=28, cache=False), pp.CausalPrior(cut, refresh_days=28, cache=False)
        X, Xc = wp10.claim_features(s, P), wp10.claim_features(cut, Pc)
        assert np.array_equal(X[:len(cut.claims)], Xc), "a later claim changed an earlier claim's features"
        score = X[:, 0] + 0.01 * X[:, wp10.FEATURES.index("n_today_clinician")]            # a fixed stand-in rule
        a = wp10.pick(s, score, cap=3, floor=-9)
        b = wp10.pick(cut, score[:len(cut.claims)], cap=3, floor=-9)
        assert [i for i in a if i < len(cut.claims)] == b, "picks before the cut changed"
        per_day = {}
        for i in a:
            per_day[s.claims[i].receipt_date] = per_day.get(s.claims[i].receipt_date, 0) + 1
        assert max(per_day.values()) <= 3 and len(per_day) > 100
        snaps_before = {d: v for d, v in P.snapshots.items() if d <= cut_date}
        assert all(P.snapshots[d] == Pc.snapshots[d] for d in snaps_before), "a refresh before the cut used later rows"
    print("ok test_wp10")


if __name__ == "__main__":
    test_cost_copies_equal_the_score_parameters()
    test_the_arm_never_reads_the_answer_key_or_eval()
    test_features_and_picks_are_causal_and_the_cap_holds()
