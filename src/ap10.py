"""Agent AP1.0 (prepay point 4, PAID when run with a model): a model chooses tools within caps; the workflow's advice sits inside the tool results.

The agent works one receipt day at a time. `next_day` returns the day's candidate claims (the highest `CANDIDATES` by the workflow's score, with the score and the
workflow's advice PEND or PAY); `provider_history` gives a clinician's earlier counts; `pend` requests the charts for claims (within the daily cap, one call for all); `read_chart` returns the
office's answers, with the level the rules would pay; `pay` closes a claim as billed; `adjust` pays a pended claim at a given level (or denies it) instead of the rule's level.
A claim the agent never touches is paid as billed, as in the workflow. A pended claim the agent does not adjust is resolved by the rules (src/prepay_env.resolve_pend).

Two drivers share the tools: `scripted_agent` follows the advice exactly (used for parity on development seeds, free) and `llm_agent` (a model call per decision turn;
needs ANTHROPIC_API_KEY and an approved cap; never run without Simmy's OK). The model driver makes one call per consulted day, with one tool (`pend`, all claims in one call);
`provider_history`, `adjust` and the per-claim `read_chart` turns of the first design were dropped to fit a $1 budget (docs/ap10.md): the charts are read for every pended claim and the rules decide. Nothing here reads the answer key.
"""
import json
import os

from prepay_env import resolve_pend, resolve_response
from wp10 import claim_features, days_index, CAP_PER_DAY

CANDIDATES = 15
MAX_TOOL_CALLS_PER_DAY = 30
PRICES = {"claude-opus-5-5": (4.00, 20.00), "claude-sonnet-5-5": (2.00, 10.00), "claude-haiku-5-5": (0.10, 0.50)}   # $ per million tokens, input and output (list prices up to 100K-token prompts)
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


PEND_TOOL = {"name": "pend", "description": "Request the medical record for the listed claims, and no others. Call it exactly once per day with every claim you choose to pend (an empty list pends nothing).",
             "input_schema": {"type": "object", "properties": {"claim_ids": {"type": "array", "items": {"type": "string"}}}, "required": ["claim_ids"]}}

SYSTEM = ("You review one day of incoming E/M claims for a payer before payment. Each candidate carries a workflow dollar estimate of what pending it is worth and the workflow's advice, PEND or PAY. "
          "A pend costs about $21 of staff time plus about $44 of provider burden if the claim was fine; a prevented overpayment is the dollars not paid. Records are requested only for claims you list. "
          "Follow the advice unless the numbers on the claim give a concrete reason not to. Never list more claims than the daily cap. Call the pend tool exactly once.")
MODEL = "claude-haiku-5-5"
SHOWN_NEAR_MISSES = 3


def day_prompt(day):
    """The compact view the model sees: the advised pends plus the best few near-misses, one line each."""
    rows = [c for c in day["candidates"] if c["advice"] == "PEND"]
    rows += [c for c in day["candidates"] if c["advice"] != "PEND"][:SHOWN_NEAR_MISSES]
    lines = [f'{c["claim_id"]} clinician={c["clinician"]} billed={c["billed"]} paid=${c["paid"]:.0f} test_line={int(c["has_test_line"])} est=${c["workflow_score_dollars"]} advice={c["advice"]}' for c in rows]
    return f'Receipt date {day["receipt_date"]}; {day["claims_received"]} claims received; pend cap {day["pend_cap"]}.\n' + "\n".join(lines), {c["claim_id"] for c in rows}


def llm_agent(tools, model=MODEL, cap_usd=0.0, log_path=None, max_days=None, client=None):
    """The model-driven driver. PAID. One model call per consulted day (a day where the workflow advises at least one pend), a forced-free tool call (`tool_choice` auto, one tool).
    Refuses to start without a positive cap and an API key. Stops calling the model when the running cost reaches `cap_usd`; every later day follows the workflow's advice, and the log
    says how many days were consulted. A reply with no usable tool call also falls back to the advice. Returns the Decisions."""
    if cap_usd <= 0 or (client is None and not os.environ.get("ANTHROPIC_API_KEY")):
        raise RuntimeError("llm_agent needs a positive cap_usd and ANTHROPIC_API_KEY (Simmy's approval required before any paid run)")
    if client is None:
        import anthropic
        client = anthropic.Anthropic()
    pin, pout = PRICES[model]
    spent, log, consulted, fallbacks = 0.0, [], 0, 0
    for k in range(len(tools.days) if max_days is None else max_days):
        day = tools.next_day(k)
        advised = [c["claim_id"] for c in day["candidates"] if c["advice"] == "PEND"]
        if not advised:
            continue
        if spent >= cap_usd:
            chosen = advised                                       # cap reached: follow the advice
            fallbacks += 1
        else:
            text, shown = day_prompt(day)
            resp = client.messages.create(model=model, max_tokens=1200, system=SYSTEM, tools=[PEND_TOOL], messages=[{"role": "user", "content": text}],
                                          output_config={"effort": "low"})
            cost = (resp.usage.input_tokens * pin + resp.usage.output_tokens * pout) / 1e6
            spent += cost
            consulted += 1
            use = next((b for b in resp.content if b.type == "tool_use" and b.name == "pend"), None)
            ids = [i for i in (use.input.get("claim_ids", []) if use else []) if i in shown]
            chosen = ids if use else advised
            if not use:
                fallbacks += 1
            log.append({"day": k, "in": resp.usage.input_tokens, "out": resp.usage.output_tokens, "usd": round(cost, 6), "advised": len(advised), "chose": len(chosen),
                        "agreed": set(chosen) == set(advised)})
        n = 0
        for cid in chosen:
            if "error" not in tools.pend(cid, n):
                n += 1
                tools.read_chart(cid)
    if log_path:
        json.dump({"model": model, "spent_usd": round(spent, 6), "consulted_days": consulted, "advice_fallback_days": fallbacks, "turns": log}, open(log_path, "w"))
    tools.spent_usd, tools.consulted_days, tools.fallback_days = spent, consulted, fallbacks
    return tools.decisions()
