"""The prepay seed registry is consistent, matches its pool formulas and the run scripts, and its checks raise. Free. Run: python tests/test_seed_registry.py"""
import copy
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "eval"))
import run_prepay_reference as ref  # noqa: E402
import seed_registry as sr  # noqa: E402
import seed_registry_report as rep  # noqa: E402

REG = sr.load()
DATA = "4.2"


def pool(pid):
    return next(p for p in REG["pools"] if p["id"] == pid)


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except sr.SeedRegistryError as e:
        return str(e)
    raise AssertionError("expected SeedRegistryError")


def test_fields_and_vocabulary():
    ids = [p["id"] for p in REG["pools"]]
    assert len(ids) == len(set(ids))
    for p in REG["pools"]:
        assert p["status"] in sr.STATUSES and p["kind"] in sr.KINDS, p["id"]
        assert p["seeds"] and len(p["seeds"]) == len(set(p["seeds"])), p["id"]
        for u in p["uses"]:
            assert u["role"] in sr.ROLES, (p["id"], u)
            assert {"arm", "role", "date", "reference", "note", "second_use"} <= set(u), (p["id"], u)
            assert set(u.get("seeds", p["seeds"])) <= set(p["seeds"]), (p["id"], u)
    for word in ("fit", "select", "confirm", "test", "burned", "fresh"):
        assert word in REG["vocabulary"]


def test_no_overlap_between_pools_of_the_same_data_version():
    seen = {}
    for p in REG["pools"]:
        for s in p["seeds"]:
            assert (p["data_version"], s) not in seen, f"data {p['data_version']} seed {s} is in both {seen[(p['data_version'], s)]} and {p['id']}"
            seen[(p["data_version"], s)] = p["id"]


def test_pools_match_their_formulas_and_the_run_script():
    assert pool("P-DEV")["seeds"] == [2001 + 41 * j for j in range(60)] == ref.DEV
    assert pool("P-CONFIRM")["seeds"] == [2002 + 41 * j for j in range(40)]
    assert pool("P-TEST")["seeds"] == [6001 + 41 * j for j in range(20)]
    assert pool("P-RESERVED")["seeds"] == [7001 + 41 * j for j in range(20)]
    assert pool("P-RESERVED")["status"] == "reserved" and pool("P-RESERVED")["uses"] == []
    assert pool("P-TEST")["kind"] == "test" and pool("P-TEST")["uses"] == []


def test_no_arm_fits_or_selects_on_a_seed_it_also_confirms_or_tests_on():
    for p in REG["pools"]:
        for a in p["uses"]:
            for b in p["uses"]:
                if a is b:
                    continue
                if sr.canonical(REG, a["arm"]) == sr.canonical(REG, b["arm"]) and a["role"] in ("fit", "select") and b["role"] in ("confirm", "test"):
                    both = set(a.get("seeds", p["seeds"])) & set(b.get("seeds", p["seeds"]))
                    assert not both, f"{p['id']}: {a['arm']} {a['role']} and {b['role']} on {sorted(both)}"


def test_test_pools_are_never_fitted_or_selected_on():
    for p in REG["pools"]:
        if p["kind"] == "test":
            assert not [u for u in p["uses"] if u["role"] in ("fit", "select")], p["id"]


def test_seeds_md_is_up_to_date():
    with open(os.path.join(ROOT, "docs", "seeds.md")) as f:
        assert f.read() == rep.render(REG), "docs/seeds.md is stale: run python eval/seed_registry_report.py --write"


def test_check_run_raises_on_reserved_fresh_and_test_pools():
    assert "reserved" in raises(sr.check_run, DATA, [7001], "WP1.0", "test")
    raises(sr.check_run, DATA, [7001], "WP1.0", "select")
    raises(sr.check_run, DATA, [6001], "WP1.0", "select")             # fresh test pool
    burned = copy.deepcopy(REG)
    next(p for p in burned["pools"] if p["id"] == "P-TEST")["status"] = "burned"
    assert "test pool" in raises(sr.check_run, DATA, [6001], "WP1.0", "select", reg=burned)
    assert "fresh" in raises(sr.check_run, DATA, [2002], "WP1.0", "select")
    raises(sr.check_run, DATA, [2002], "WP1.0", "confirm")         # P-CONFIRM is fresh until its declaration flips it to in_use
    raises(sr.check_development, DATA, [6001])
    raises(sr.check_development, DATA, [2002])
    sr.check_development(DATA, ref.DEV[:10])
    assert "in no pool" in raises(sr.check_run, DATA, [1], "WP1.0", "select")
    assert "in no pool" in raises(sr.check_run, "4.0", [2001], "WP1.0", "select")   # another data version, another dataset


def test_check_run_raises_on_a_hold_out_that_overlaps_a_fit():
    reg = copy.deepcopy(REG)
    reg["pools"][0]["uses"].append({"arm": "X", "role": "select", "date": "d", "reference": "r", "note": "n", "second_use": False, "seeds": ref.DEV[:5]})
    assert "fitted or selected" in raises(sr.check_run, DATA, ref.DEV[:5], "X", "confirm", reg=reg)
    sr.check_run(DATA, ref.DEV[5:10], "X", "confirm", reg=reg)
    reg["pools"][0]["uses"].append({"arm": "Y", "role": "confirm", "date": "d", "reference": "r", "note": "n", "second_use": False, "seeds": ref.DEV[:5]})
    assert "cannot then" in raises(sr.check_run, DATA, ref.DEV[:5], "Y", "select", reg=reg)


def test_a_planned_use_does_not_block_and_record_use_turns_it_into_a_record():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "reg.json")
        reg = copy.deepcopy(REG)
        import json
        json.dump(reg, open(path, "w"), indent=1)
        sr.plan_use(DATA, "P-DEV", "T-arm", "select", ref.DEV[:3], "ref", "plan", "2026-10-23", path=path)
        planned = sr.load(path)
        sr.check_run(DATA, ref.DEV[:3], "T-arm", "confirm", reg=planned)          # a plan is not a use
        sr.record_use(DATA, "P-DEV", "T-arm", "select", ref.DEV[:3], "ref", "ran", "2026-10-24", path=path)
        done = sr.load(path)
        u = [u for u in done["pools"][0]["uses"] if u["arm"] == "T-arm"]
        assert len(u) == 1 and "done" not in u[0] and u[0]["note"] == "ran"
        assert "fitted or selected" in raises(sr.check_run, DATA, ref.DEV[:3], "T-arm", "confirm", reg=done)


def test_agent_and_workflow_lines():
    assert sr.line("AP1.0") == "agent" and sr.line("WP1.0") == "workflow" and sr.line("REF-edits") == "workflow"


def test_the_reference_script_checks_the_registry():
    src = open(os.path.join(ROOT, "eval", "run_prepay_reference.py")).read()
    assert "check_run" in src
    for arm in ("REF-edits", "REF-auto_provider"):
        sr.check_run(DATA, ref.DEV[:10], arm, "select")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
