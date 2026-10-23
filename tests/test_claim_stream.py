"""Claim stream and per-claim office on a D4.2 dataset built from the pinned generator (skipped without it). Run: python tests/test_claim_stream.py"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "eval"))
GEN = os.path.join(ROOT, "external", "em-upcoding-agent", "src", "generate_v2.py")


def build(seed, tmp):
    out, key = os.path.join(tmp, f"d{seed}"), os.path.join(tmp, f"k{seed}.json")
    subprocess.run([sys.executable, GEN, out, "--seed", str(seed), "--data-version", "4.2", "--answer-key", key], check=True, capture_output=True)
    return out, key


def main():
    if not os.path.exists(GEN):
        print("skip: run tools/get_generator.sh first")
        return
    import claim_stream as cs
    import score_prepay as sp
    with tempfile.TemporaryDirectory() as tmp:
        d, key = build(1001, tmp)
        s = cs.Stream(d, seed=1)
        assert len(s.claims) > 1000
        order = [(c.receipt_date, c.claim_id) for c in s]
        assert order == sorted(order), "stream out of order"
        assert all(c.receipt_date > c.service_date for c in s)
        # causality: history of a claim holds only earlier-received claims of the same provider
        for c in s.claims[::500]:
            h = s.history(c)
            assert all((x.receipt_date, x.claim_id) < (c.receipt_date, c.claim_id) and x.provider == c.provider for x in h)
        # a later claim's features cannot change a decision: counts at a claim are identical with later rows removed
        c = s.claims[len(s.claims) // 2]
        before = s.provider_counts(c)
        cut = cs.Stream.__new__(cs.Stream)
        cut.__dict__.update(s.__dict__)
        cut.claims = [x for x in s.claims if (x.receipt_date, x.claim_id) <= (c.receipt_date, c.claim_id)]
        cut._by_provider = {}
        for x in cut.claims:
            cut._by_provider.setdefault(x.provider, []).append(x)
        assert cut.provider_counts(c) == before
        # billing NPIs are groups, rendering NPIs are clinicians; the rendering history is causal too
        assert len({x.provider for x in s}) < len({x.rendering for x in s if x.rendering}) and any(x.has_test for x in s)
        for x in s.claims[::700]:
            assert all((h.receipt_date, h.claim_id) < (x.receipt_date, x.claim_id) and h.rendering == x.rendering for h in s.rendering_history(x))
        # the office: deterministic, unrendered claims never produce a chart, rendered ones sometimes do
        o1, o2 = cs.ClaimOffice(d, seed=1), cs.ClaimOffice(d, seed=1)
        got, none, unr = 0, 0, 0
        for x in s.claims[:600]:
            a, b = o1.request(x), o2.request(x)
            assert (a.day, a.status, a.chart_cpt, a.no_record) == (b.day, b.status, b.chart_cpt, b.no_record)
            if x.claim_id in o1.unrendered:
                assert a.chart_cpt is None
                unr += 1
            elif a.chart_cpt:
                assert a.chart_cpt in cs.EM_CODES
                got += 1
            else:
                none += 1
        assert got > 0 and none > 0
        # truth and a trivial arm: pay-all scores only the screening cost; denying phantom claims after NO_RECORD prevents money
        t = sp.claim_truth(key, s)
        assert set(t) == set(x.claim_id for x in s)
        r0 = sp.score(s, t, [])
        assert r0["prevented"] == 0 and r0["score"] < 0
        ph = [x for x in s if t[x.claim_id]["kind"] == "not_rendered"]
        assert ph, "no phantom claims in this build"
        dec = [sp.Decision(x.claim_id, "pend", None, 30, 1, 0) for x in ph]
        r1 = sp.score(s, t, dec)
        assert r1["fraud_dollars_prevented"] > 0 and r1["wrongful_adjustments"] == 0
    print("ok test_claim_stream")


if __name__ == "__main__":
    main()
