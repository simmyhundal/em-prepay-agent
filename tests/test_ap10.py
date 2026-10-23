"""AP1.0: the model driver refuses to run without an approved cap and key, the tools enforce the daily cap and the order pend -> read_chart -> adjust, and the scripted agent
reproduces the workflow's decisions (parity). Uses a small stand-in rule on one D4.2 dataset (skipped without the generator). Run: python tests/test_ap10.py"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
GEN = os.path.join(ROOT, "external", "em-upcoding-agent", "src", "generate_v2.py")


class StandIn:
    """A fixed rule on the features (no training): value grows with the clinician's claims already seen that service date."""
    def predict(self, X):
        import wp10
        return (X[:, wp10.FEATURES.index("n_today_clinician")] - 18.0) * 6.0


def main():
    import ap10
    try:
        ap10.llm_agent(None, cap_usd=0.0)
        raise AssertionError("llm_agent ran without a cap")
    except RuntimeError:
        pass
    old = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        ap10.llm_agent(None, cap_usd=5.0)
        raise AssertionError("llm_agent ran without a key")
    except RuntimeError:
        pass
    finally:
        if old:
            os.environ["ANTHROPIC_API_KEY"] = old
    if not os.path.exists(GEN):
        print("skip: run tools/get_generator.sh first")
        return
    import claim_stream as cs
    import provider_prior as pp
    import wp10
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "d")
        subprocess.run([sys.executable, GEN, out, "--seed", "1001", "--data-version", "4.2", "--answer-key", os.path.join(tmp, "k.json")], check=True, capture_output=True)
        s, o = cs.Stream(out, seed=1), cs.ClaimOffice(out, seed=1)
        prior = pp.CausalPrior(s, refresh_days=28, cache=False)
        rule = StandIn()
        tools = ap10.PrepayTools(s, o, prior, rule, floor=0.0, cap=3)
        agent = ap10.scripted_agent(tools)
        flow = wp10.run(s, o, prior, rule, cap=3, floor=0.0)
        assert {(d.claim_id, d.paid_cpt) for d in agent} == {(d.claim_id, d.paid_cpt) for d in flow} and len(flow) > 0, "scripted agent differs from the workflow"
        t2 = ap10.PrepayTools(s, o, prior, rule, floor=0.0, cap=2)
        day = t2.next_day(0)
        cid = day["candidates"][0]["claim_id"]
        assert "error" in t2.read_chart(cid) and "error" in t2.adjust(cid, "99213"), "chart read or adjust before a pend"
        assert "ok" in t2.pend(cid, 0) and "error" in t2.pend(cid, 0)
        assert "error" in t2.pend(day["candidates"][1]["claim_id"], 2), "daily cap not enforced"
        assert "ok" in t2.adjust(cid, "99213")
    print("ok test_ap10")


if __name__ == "__main__":
    main()
