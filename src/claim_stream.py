"""The prepay claim stream: E/M claims in order of receipt, a causal provider history, and a per-claim records office (issue 1).

What an arm sees (payer-visible): the claim (provider, service date, receipt date, billed E/M code, paid amount, diagnoses), the
provider's history of claims received BEFORE this one, and what the office sends back for a pended claim. Nothing here reads the
answer key; truth lives in eval/score_prepay.py (`claim_truth`).

Scope of release P1: only claims with an E/M line (99211 to 99215) are decisions; every other claim is paid as billed and left out.
The data come from the pinned generators (GENERATOR_PIN, tools/get_generator.sh): data 4.2, built with generate_v2.py.
"""
import csv
import os
import random
import sys
from collections import defaultdict
from datetime import date, timedelta

EM_CODES = ("99211", "99212", "99213", "99214", "99215")
LAG_DAYS = (1, 14)            # receipt date = service date + a seeded lag; assumption (data 4.2 has service dates only)
HERE = os.path.dirname(os.path.abspath(__file__))
GEN_SRC = os.path.join(HERE, "..", "external", "em-upcoding-agent", "src")


def _gen():
    """Import the postpay repository's modules (provider_sim tables, records) from the pinned checkout."""
    if GEN_SRC not in sys.path:
        sys.path.insert(0, GEN_SRC)
    import provider_sim, records
    return provider_sim, records


def _rows(path):
    with open(path) as f:
        return list(csv.DictReader(f))


class Claim:
    """One E/M claim as the payer sees it on receipt."""
    __slots__ = ("claim_id", "provider", "service_date", "receipt_date", "billed_cpt", "paid", "em_paid", "dx")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw[k])


class Stream:
    def __init__(self, data_dir, seed=1):
        self.data_dir, self.seed = data_dir, seed
        remit = {r["claim_id"]: float(r["paid_amount"]) for r in _rows(os.path.join(data_dir, "remittance.csv"))}
        em = {}
        for r in _rows(os.path.join(data_dir, "claim_lines.csv")):
            if r["cpt"] in EM_CODES:
                em[r["claim_id"]] = (r["cpt"], float(r["paid_amount"]))
        self.fee = {r["cpt"]: float(r["allowed_amount"]) for r in _rows(os.path.join(data_dir, "reference", "fee_schedule.csv")) if r["cpt"] in EM_CODES}
        claims = []
        for r in _rows(os.path.join(data_dir, "claims_header.csv")):
            cid = r["claim_id"]
            if cid not in em or r["claim_frequency"] != "1":
                continue
            lag = random.Random(f"{seed}:lag:{cid}").randint(*LAG_DAYS)
            sd = date.fromisoformat(r["service_date"])
            claims.append(Claim(claim_id=cid, provider=r["billing_npi"], service_date=sd, receipt_date=sd + timedelta(days=lag),
                                billed_cpt=em[cid][0], paid=remit[cid], em_paid=em[cid][1],
                                dx=tuple(r[f"dx{i}"] for i in range(1, 7) if r[f"dx{i}"])))
        self.claims = sorted(claims, key=lambda c: (c.receipt_date, c.claim_id))
        self.by_id = {c.claim_id: c for c in self.claims}
        self._by_provider = defaultdict(list)
        for c in self.claims:
            self._by_provider[c.provider].append(c)

    def __iter__(self):
        return iter(self.claims)

    def history(self, claim):
        """Claims of the same provider received strictly before this one (causal: never a later row)."""
        key = (claim.receipt_date, claim.claim_id)
        return [h for h in self._by_provider[claim.provider] if (h.receipt_date, h.claim_id) < key]

    def provider_counts(self, claim):
        """Counts of billed E/M codes in the provider's history before this claim, as the screen's raw input."""
        n = defaultdict(int)
        for h in self.history(claim):
            n[h.billed_cpt] += 1
        return dict(n)

    def paid_at(self, claim, cpt):
        """What the claim would pay with its E/M line at `cpt` (other lines unchanged); the plan's payment share is kept."""
        return claim.paid - claim.em_paid + claim.em_paid * self.fee[cpt] / self.fee[claim.billed_cpt]


class Response:
    """What came back for one pended claim. `day` counts from the request; `chart_cpt` is the level a coder reads from the chart."""
    __slots__ = ("day", "status", "chart_cpt", "no_record", "rounds")

    def __init__(self, day, status, chart_cpt, no_record, rounds):
        self.day, self.status, self.chart_cpt, self.no_record, self.rounds = day, status, chart_cpt, no_record, rounds


class ClaimOffice:
    """A per-claim records office. Behavior per provider (cooperative, slow, sloppy, evasive) and the response and delay tables are
    the postpay office's (provider_sim), drawn per claim. One automatic follow-up round is taken when the first answer is deficient.
    A claim for a service never rendered gets no chart: when the office answers it reports NO_RECORD. Deterministic per seed."""

    def __init__(self, data_dir, seed=1):
        self.ps, self.rec = _gen()
        self.seed = seed
        self.universe = {r["claim_id"]: r for r in _rows(os.path.join(data_dir, "records", "records_universe.csv"))}
        path = os.path.join(data_dir, "records", "unrendered_claims.csv")
        self.unrendered = {r["claim_id"] for r in _rows(path)} if os.path.exists(path) else set()
        self._beh = {}

    def behavior(self, provider):
        if provider not in self._beh:
            rng = random.Random(f"{self.seed}:behavior:{provider}")
            mix = self.ps.BEHAVIOR_MIX
            self._beh[provider] = rng.choices(list(mix), weights=list(mix.values()))[0]
        return self._beh[provider]

    def _read(self, claim_id, rng):
        chart = self.rec.read_chart(self.universe[claim_id], rng)
        mdm = self.rec.MDM_LEVELS.index(chart["documented_mdm_level"])
        return self.rec.CODES[self.rec.supported_level(mdm, chart["documented_minutes"])]

    def request(self, claim):
        ps = self.ps
        rng = random.Random(f"{self.seed}:claimreq:{claim.claim_id}")
        beh = self.behavior(claim.provider)
        lo, hi = ps.DAYS[beh]
        status = rng.choices(*zip(*ps.FIRST[beh].items()))[0]
        day, rounds = rng.randint(lo, hi), 1
        if claim.claim_id in self.unrendered:
            answers = status in ("complete", "partial")
            return Response(day if answers else None, status, None, answers, rounds)
        if status == "complete":
            return Response(day, status, self._read(claim.claim_id, rng), False, rounds)
        if status == "partial":                                   # the chart for this claim is there or not
            if rng.random() < 0.5:
                return Response(day, status, self._read(claim.claim_id, rng), False, rounds)
            status = "missing_visits"
        if status == "extension":
            day += rng.randint(20, 45)
            if rng.random() < 0.8:
                return Response(day, status, self._read(claim.claim_id, rng), False, rounds)
            return Response(None, status, None, False, rounds)
        code = ps.STATUS_TO_CODE.get(status)
        fix = ps.FIXABLE_BY_FOLLOWUP.get(code, 0.7 if status == "wrong_content" else 0.5 if status in ("clarification_requested", "objection", "missing_visits") else 0.0)
        if rng.random() < fix:
            return Response(day + rng.randint(lo, hi), status, self._read(claim.claim_id, rng), False, 2)
        return Response(None, status, None, False, 2 if status != "no_response" else 1)
