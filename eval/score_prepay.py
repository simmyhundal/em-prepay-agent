"""Score P1.0 (prepay): prevented minus wrongful loss minus staff cost minus abrasion, per seed. Spec and sources: docs/score_prepay.md.

Truth (the answer key) is read here only: `claim_truth` builds, per E/M claim, the amount the visit justifies. A `Decision` is what an
arm did with one claim; the module never sees how it decided. Once used, parameters are not edited: a change is score P1.1.
"""
import json
from collections import namedtuple
from datetime import timedelta

# action: "pay" | "pend" | "adjust"; paid_cpt: the E/M level finally paid, or None for a denial;
# days_to_pay: days from receipt to payment (0 for an immediate decision); rounds: records requests sent (pend: 1 + follow-ups); charts: charts reviewed
Decision = namedtuple("Decision", "claim_id action paid_cpt days_to_pay rounds charts", defaults=(0, 0))

HOURS, BENEFIT = 2080, 1.4
WAGE = {"analyst": 78000, "coder": 51140, "admin": 45930}
PARAMS = {
    "auto_screen": 0.05, "triage_min": 5, "admin_min": 10, "review_min": 15, "followup_min": 10, "appeal_min": 45,
    "copy_fee": 3.0, "wrongful_pend": 43.84, "wrongful_adjust": 200.0, "p_appeal": 0.5,
    "prompt_pay_days": 30, "interest": 0.18,
}
STAFF_KEYS = ("auto_screen", "triage_min", "admin_min", "review_min", "followup_min", "appeal_min", "copy_fee")
ABRASION_KEYS = ("wrongful_pend", "wrongful_adjust", "interest")


def hourly(role):
    return WAGE[role] * BENEFIT / HOURS


def scaled(params=PARAMS, staff=1.0, abrasion=1.0):
    """Sensitivity: multiply the staff-cost group and the abrasion group (docs/score_prepay.md, x0.5 to x2)."""
    p = dict(params)
    for k in STAFF_KEYS:
        p[k] *= staff
    for k in ABRASION_KEYS:
        p[k] *= abrasion
    return p


def claim_truth(key_path, stream):
    """{claim_id: {"payable": dollars the visit justifies, "overbilled": bool, "kind": fraud kind or None}} for every E/M claim in the stream.
    A claim for a service never rendered (or an impossible visit) justifies nothing; any other claim justifies its E/M line at the justified level."""
    key = json.load(open(key_path))
    fraud, just = key.get("fraud_claims", {}), key["justified_cpt_by_claim"]
    out = {}
    for c in stream:
        kind = fraud.get(c.claim_id)
        if kind in ("not_rendered", "impossible_days"):
            out[c.claim_id] = {"payable": 0.0, "overbilled": True, "kind": kind}
        else:
            j = just.get(c.claim_id, c.billed_cpt)
            out[c.claim_id] = {"payable": stream.paid_at(c, j), "overbilled": stream.fee[c.billed_cpt] > stream.fee[j] + 1e-9, "kind": kind}
    return out


def score(stream, truth, decisions, params=PARAMS):
    """decisions: one Decision per E/M claim the arm acted on; every claim without one is paid as billed. Returns the seed's components."""
    P = params
    dec = {d.claim_id: d for d in decisions}
    rows = {"prevented": 0.0, "wrongful_loss": 0.0, "staff": 0.0, "abrasion": 0.0}
    n = {"pended": 0, "adjusted": 0, "denied": 0, "wrongful_pends": 0, "wrongful_adjust": 0, "prevented_overbilled": 0.0, "overbilled_total": 0.0,
         "fraud_prevented": 0.0}
    days = []
    for c in stream:
        t = truth[c.claim_id]
        d = dec.get(c.claim_id)
        billed = c.paid
        paid = billed if d is None or d.action == "pay" else (0.0 if d.paid_cpt is None else stream.paid_at(c, d.paid_cpt))
        if t["overbilled"]:
            n["overbilled_total"] += billed - t["payable"]
        rows["prevented"] += billed - paid
        rows["wrongful_loss"] += max(0.0, t["payable"] - paid)
        rows["staff"] += P["auto_screen"]
        if d is None:
            continue
        w = 0.0 if t["overbilled"] else 1.0            # claim-level truth: a pend of an overbilled claim costs the provider nothing it did not owe
        if d.action == "pend":
            n["pended"] += 1
            rows["staff"] += P["triage_min"] / 60 * hourly("analyst") + P["admin_min"] / 60 * hourly("admin")
            rows["staff"] += d.charts * (P["review_min"] / 60 * hourly("coder") + P["copy_fee"])
            fol = max(0, d.rounds - 1)
            rows["staff"] += fol * (P["followup_min"] / 60 * hourly("admin") + P["copy_fee"])
            rows["abrasion"] += w * P["wrongful_pend"] * d.rounds
            late = max(0, d.days_to_pay - P["prompt_pay_days"])
            rows["abrasion"] += w * paid * P["interest"] * late / 365
            days.append(d.days_to_pay)
            n["wrongful_pends"] += int(w)
        elif d.action == "adjust":
            n["adjusted"] += 1
        if d.paid_cpt is None and d.action != "pay":
            n["denied"] += 1
        if paid < t["payable"] - 0.005:
            rows["abrasion"] += P["p_appeal"] * P["wrongful_adjust"]
            rows["staff"] += P["p_appeal"] * P["appeal_min"] / 60 * hourly("coder")
            n["wrongful_adjust"] += 1
        if t["overbilled"]:
            n["prevented_overbilled"] += max(0.0, billed - paid)
            if t["kind"] in ("not_rendered", "impossible_days"):
                n["fraud_prevented"] += billed - paid
    net = rows["prevented"] - rows["wrongful_loss"] - rows["staff"] - rows["abrasion"]
    days.sort()
    return {**{k: round(v, 2) for k, v in rows.items()}, "score": round(net, 2),
            "pended": n["pended"], "adjusted": n["adjusted"], "denied": n["denied"], "wrongful_pends": n["wrongful_pends"],
            "wrongful_adjustments": n["wrongful_adjust"], "share_overbilled_prevented": round(n["prevented_overbilled"] / n["overbilled_total"], 4) if n["overbilled_total"] else None,
            "fraud_dollars_prevented": round(n["fraud_prevented"], 2), "median_days_to_pay": days[len(days) // 2] if days else None,
            "p90_days_to_pay": days[int(len(days) * 0.9)] if days else None}


def sensitivity(stream, truth, decisions):
    """The score at the parameter grid of docs/score_prepay.md: staff and abrasion each x0.5, x1, x2."""
    return {f"staff x{s}, abrasion x{a}": score(stream, truth, decisions, scaled(staff=s, abrasion=a))["score"]
            for s in (0.5, 1.0, 2.0) for a in (0.5, 1.0, 2.0)}
