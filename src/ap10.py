"""Agent AP1.0 (prepay point 4, PAID when run with a model): a model chooses tools within caps; the workflow's advice sits inside the tool results.

The agent works one receipt day at a time. `next_day` returns the day's candidate claims (the highest `CANDIDATES` by the workflow's score, with the score and the
workflow's advice PEND or PAY); `provider_history` gives a clinician's earlier counts; `pend` requests the chart for a claim (within the daily cap); `read_chart` returns the
office's answer, with the level the rules would pay; `pay` closes a claim as billed; `adjust` pays a pended claim at a given level (or denies it) instead of the rule's level.
A claim the agent never touches is paid as billed, as in the workflow. A pended claim the agent does not adjust is resolved by the rules (src/prepay_env.resolve_pend).

Two drivers share the tools: `scripted_agent` follows the advice exactly (used for parity on development seeds, free) and `llm_agent` (a model call per decision turn;
needs ANTHROPIC_API_KEY and an approved cap; never run without Simmy's OK). Nothing here reads the answer key.
"""
import json
import os

from prepay_env import resolve_pend, resolve_response
from wp10 import claim_features, days_index, CAP_PER_DAY

CANDIDATES = 15
MAX_TOOL_CALLS_PER_DAY = 30
PRICES = {"claude-opus-5-5": (4.00, 20.00), "claude-sonnet-5-5": (2.00, 10.00), "claude-haiku-5-5": (1.00, 5.00)}   # $ per million tokens, input and output (list prices, estimates)
FLOOR = 0.0


class PrepayTools:
    def __init__(self, stream, office, prior, rule, floor=FLOOR, cap=CAP_PER_DAY):
        self.stream, self.office, self.cap, self.floor = stream, office, cap, floor
        X = claim_features(stream, prior)
        self.score = rule.predict(X)
        self.days = days_index(stream)
        self.pos = {c.claim_id: i for i, c in enumerate(stream.claims)}
        self.pended, self.adjusted, self.responses = {}, {}, {}
        self.calls = 0

    # --- tools ---------------------------------------------------------------------------------------------------------------------------------------
    def next_day(self, k):
        """Day k's candidates (claims received that day, best first) with the workflow's advice."""
        date, pos = self.days[k]
        cand = sorted(pos, key=lambda i: -self.score[i])[:CANDIDATES]
        top = {i for i in sorted([i for i in pos if self.score[i] > self.floor], key=lambda i: -self.score[i])[:self.cap]}
        out = []
        for i in cand:
            c = self.stream.claims[i]
            out.append({"claim_id": c.claim_id, "clinician": c.rendering, "group": c.provider, "service_date": str(c.service_date), "billed": c.billed_cpt,
                        "paid": c.paid, "has_test_line": c.has_test, "diagnoses": len(c.dx), "workflow_score_dollars": round(float(self.score[i]), 1),
                        "advice": "PEND" if i in top else "PAY"})
        return {"receipt_date": str(date), "day": k, "claims_received": len(pos), "pend_cap": self.cap, "candidates": out}

    def provider_history(self, claim_id):
        c = self.stream.by_id[claim_id]
        h = self.stream.rendering_history(c)
        n = {}
        for x in h:
            n[x.billed_cpt] = n.get(x.billed_cpt, 0) + 1
        same_day = sum(1 for x in h if x.service_date == c.service_date)
        return {"clinician": c.rendering, "earlier_claims": len(h), "billed_levels": n, "earlier_claims_same_service_date": same_day}

    def pend(self, claim_id, day_pends):
        if claim_id in self.pended:
            return {"error": "already pended"}
        if day_pends >= self.cap:
            return {"error": f"daily pend cap of {self.cap} reached"}
        self.pended[claim_id] = True
        return {"ok": True, "message": "records requested"}

    def read_chart(self, claim_id):
        if claim_id not in self.pended:
            return {"error": "pend the claim first"}
        c = self.stream.by_id[claim_id]
        r = self.responses.setdefault(claim_id, self.office.request(c))
        d = resolve_response(self.stream, c, r)
        return {"status": r.status, "days_to_answer": r.day, "no_record": r.no_record, "chart_supported_level": r.chart_cpt,
                "rule_pays_level": d.paid_cpt, "rule": "pay the supported level (never above billed); no record or no answer by day 45 denies"}

    def pay(self, claim_id):
        self.pended.pop(claim_id, None)
        return {"ok": True}

    def adjust(self, claim_id, level):
        if claim_id not in self.pended:
            return {"error": "only a pended claim can be adjusted"}
        self.adjusted[claim_id] = None if level in (None, "deny") else level
        return {"ok": True}

    # --- outcome -------------------------------------------------------------------------------------------------------------------------------------
    def decisions(self):
        from score_prepay_decision import Decision
        out = []
        for cid in self.pended:
            c = self.stream.by_id[cid]
            d = resolve_pend(self.stream, self.office, c)
            if cid in self.adjusted:
                d = Decision(cid, "pend", self.adjusted[cid], d.days_to_pay, d.rounds, d.charts)
            out.append(d)
        return out


def scripted_agent(tools):
    """Follows the advice: pend every PEND, read each chart, leave the rules' level. Must reproduce the workflow's decisions exactly (parity)."""
    asks = []
    for k in range(len(tools.days)):
        day = tools.next_day(k)
        n = 0
        for c in day["candidates"]:
            if c["advice"] == "PEND" and "error" not in tools.pend(c["claim_id"], n):
                n += 1
                tools.read_chart(c["claim_id"])
                asks.append(c["claim_id"])
    return tools.decisions()


TOOL_SPECS = [
    {"name": "provider_history", "description": "Earlier claims of the claim's clinician: counts by billed level and earlier claims on the same service date.", "input_schema": {"type": "object", "properties": {"claim_id": {"type": "string"}}, "required": ["claim_id"]}},
    {"name": "pend", "description": "Request the medical record for a claim (costs staff time; a wrongful pend burdens an honest provider). Within the daily cap.", "input_schema": {"type": "object", "properties": {"claim_id": {"type": "string"}}, "required": ["claim_id"]}},
    {"name": "read_chart", "description": "Read the office's answer for a pended claim and the level the rules would pay.", "input_schema": {"type": "object", "properties": {"claim_id": {"type": "string"}}, "required": ["claim_id"]}},
    {"name": "adjust", "description": "Pay a pended claim at a level (99211 to 99215) or 'deny' instead of the rule's level.", "input_schema": {"type": "object", "properties": {"claim_id": {"type": "string"}, "level": {"type": "string"}}, "required": ["claim_id", "level"]}},
    {"name": "done", "description": "Finish the day. Claims not pended are paid as billed.", "input_schema": {"type": "object", "properties": {}}},
]

SYSTEM = ("You review one day of incoming E/M claims for a payer before payment. For each candidate claim you may request records (pend) or let it pay as billed. "
          "A pend costs about $21 of staff time and, if the claim was fine, about $44 of provider burden; a prevented overpayment is worth the dollars not paid. "
          "The workflow's advice and its dollar estimate come with each claim: follow the advice unless the claim's history gives a concrete reason not to. "
          "Never pend more than the daily cap. Call done when finished.")


def llm_agent(tools, model="claude-sonnet-5-5", cap_usd=0.0, log_path=None, max_days=None):
    """The model-driven driver. PAID. Refuses to start without a positive cap and an API key; stops cleanly when the running cost reaches the cap."""
    if cap_usd <= 0 or not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("llm_agent needs a positive cap_usd and ANTHROPIC_API_KEY (Simmy's approval required before any paid run)")
    import anthropic
    client = anthropic.Anthropic()
    pin, pout = PRICES[model]
    spent, log = 0.0, []
    for k in range(len(tools.days) if max_days is None else max_days):
        day = tools.next_day(k)
        if not any(c["advice"] == "PEND" or c["workflow_score_dollars"] > -15 for c in day["candidates"]):
            continue                                              # nothing worth a model call: everything pays as billed
        msgs = [{"role": "user", "content": json.dumps(day)}]
        pends = 0
        for _ in range(MAX_TOOL_CALLS_PER_DAY):
            resp = client.messages.create(model=model, max_tokens=800, system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}], tools=TOOL_SPECS, messages=msgs)
            spent += (resp.usage.input_tokens * pin + resp.usage.output_tokens * pout) / 1e6
            log.append({"day": k, "in": resp.usage.input_tokens, "out": resp.usage.output_tokens, "spent": round(spent, 4)})
            if spent >= cap_usd:
                break
            uses = [b for b in resp.content if b.type == "tool_use"]
            if not uses:
                break
            msgs.append({"role": "assistant", "content": resp.content})
            results, finished = [], False
            for u in uses:
                a = u.input
                if u.name == "done":
                    finished = True
                    out = {"ok": True}
                elif u.name == "pend":
                    out = tools.pend(a["claim_id"], pends)
                    pends += "error" not in out
                else:
                    out = getattr(tools, u.name)(**a)
                results.append({"type": "tool_result", "tool_use_id": u.id, "content": json.dumps(out)})
            msgs.append({"role": "user", "content": results})
            if finished:
                break
        if spent >= cap_usd:
            break
    if log_path:
        json.dump({"model": model, "spent_usd": round(spent, 4), "turns": log}, open(log_path, "w"))
    return tools.decisions()
