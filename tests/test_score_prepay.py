"""Score P1.0 on a hand-built stream: every number below is worked out by hand. Run: python tests/test_score_prepay.py"""
import os
import sys
from datetime import date

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "eval"))
sys.path.insert(0, os.path.join(ROOT, "src"))
import score_prepay as sp
from claim_stream import Claim

FEE = {"99213": 100.0, "99214": 150.0, "99215": 200.0}


class Mini:
    fee = FEE

    def __init__(self, claims):
        self.claims = claims

    def __iter__(self):
        return iter(self.claims)

    def paid_at(self, c, cpt):
        return c.paid - c.em_paid + c.em_paid * FEE[cpt] / FEE[c.billed_cpt]


def claim(cid, cpt, em_paid):
    return Claim(claim_id=cid, provider="P", service_date=date(2024, 1, 1), receipt_date=date(2024, 1, 3), billed_cpt=cpt, paid=em_paid + 10, em_paid=em_paid, dx=())


A = claim("A", "99215", 160.0)      # billed 99215, justified 99213: overbilled; at 99213 it would pay 80 + 10
B = claim("B", "99214", 120.0)      # billed 99214, justified 99214: correct
C = claim("C", "99214", 120.0)      # phantom claim: justifies nothing
S = Mini([A, B, C])
T = {"A": {"payable": 90.0, "overbilled": True, "kind": None},
     "B": {"payable": 130.0, "overbilled": False, "kind": None},
     "C": {"payable": 0.0, "overbilled": True, "kind": "not_rendered"}}
P = dict(sp.PARAMS)


def close(a, b, tol=0.02):
    assert abs(a - b) < tol, (a, b)


def test_pay_all_is_zero_up_to_screening_cost():
    r = sp.score(S, T, [])
    assert r["prevented"] == 0 and r["wrongful_loss"] == 0 and r["abrasion"] == 0
    close(r["staff"], 3 * P["auto_screen"])
    close(r["score"], -0.15)


def test_correct_pend_of_overbilled_claim():
    # pend A, a chart is read, paid at 99213: prevented 170 - 90 = 80, no wrongful loss, no abrasion (the claim is overbilled)
    d = [sp.Decision("A", "pend", "99213", 20, 1, 1)]
    r = sp.score(S, T, d)
    close(r["prevented"], 80.0)
    assert r["wrongful_loss"] == 0 and r["abrasion"] == 0
    staff = 3 * P["auto_screen"] + 5 / 60 * sp.hourly("analyst") + 10 / 60 * sp.hourly("admin") + 15 / 60 * sp.hourly("coder") + 3
    close(r["staff"], staff)


def test_wrongful_pend_costs_abrasion_and_delay():
    # pend B (correct claim), paid as billed after 45 days: 15 days late -> interest 130 * 0.18 * 15 / 365
    d = [sp.Decision("B", "pend", "99214", 45, 1, 1)]
    r = sp.score(S, T, d)
    assert r["prevented"] == 0 and r["wrongful_loss"] == 0
    close(r["abrasion"], 43.84 + 130 * 0.18 * 15 / 365)


def test_wrongful_denial_cannot_score():
    # deny B outright: prevented 130 but wrongful loss 130 (net 0), plus appeal abrasion and handling
    d = [sp.Decision("B", "adjust", None, 0, 0, 0)]
    r = sp.score(S, T, d)
    close(r["prevented"], 130.0)
    close(r["wrongful_loss"], 130.0)
    close(r["abrasion"], 0.5 * 200.0)
    assert r["denied"] == 1 and r["wrongful_adjustments"] == 1


def test_adjusting_an_overbilled_claim_one_level():
    # A: 99215 -> 99214 by rule pays 160*150/200 + 10 = 130; prevented 40 of the 80 overbilled; paid above payable (90), so no loss
    d = [sp.Decision("A", "adjust", "99214", 0, 0, 0)]
    r = sp.score(S, T, d)
    close(r["prevented"], 40.0)
    assert r["wrongful_loss"] == 0 and r["abrasion"] == 0


def test_phantom_claim_denied_prevents_all_and_no_abrasion():
    d = [sp.Decision("C", "pend", None, 30, 1, 0)]
    r = sp.score(S, T, d)
    close(r["prevented"], 130.0)
    assert r["wrongful_loss"] == 0 and r["abrasion"] == 0
    close(r["fraud_dollars_prevented"], 130.0)


def test_sensitivity_grid_has_nine_cells_and_x1_equals_score():
    d = [sp.Decision("A", "pend", "99213", 20, 1, 1)]
    g = sp.sensitivity(S, T, d)
    assert len(g) == 9
    close(g["staff x1.0, abrasion x1.0"], sp.score(S, T, d)["score"])
    assert g["staff x0.5, abrasion x1.0"] > g["staff x2.0, abrasion x1.0"]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
