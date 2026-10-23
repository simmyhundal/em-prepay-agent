# Claim edit

[Back to the concepts](README.md) · [glossary](../glossary.md)

**What it means.** A rule applied to the claim (and the provider's earlier claims) at adjudication, with no records request, that denies or flags claims that trip it.

**Why it exists.** It is the cheap competitor every records-based strategy must beat. Industry calls this a prepayment edit.

**Example.** Deny a claim when one clinician already has more than 20 claims for the same service date.

**Where to find it.** `src/edit_rules.py`, [reference arms](../prepay_reference_arms.md)
