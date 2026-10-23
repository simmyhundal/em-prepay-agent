"""The Decision record shared by the arms (src/) and the score (eval/score_prepay.py)."""
from collections import namedtuple

# action: "pay" | "pend" | "adjust"; paid_cpt: the E/M level finally paid, or None for a denial;
# days_to_pay: days from receipt to payment (0 for an immediate decision); rounds: records requests sent (pend: 1 + follow-ups); charts: charts reviewed
Decision = namedtuple("Decision", "claim_id action paid_cpt days_to_pay rounds charts", defaults=(0, 0))
