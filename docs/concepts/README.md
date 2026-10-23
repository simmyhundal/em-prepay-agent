# Concepts

[Back to the README](../README.md) · [glossary](../glossary.md)

One short page for each term this project defines. Each page says what the term means, why it exists, gives an example and points to where it is used. Industry terms are used where they exist (pend, prepayment edit, prompt-pay deadline); project terms are kept to what no industry word covers.

- [Pend](pend.md): Holding a claim unpaid while the payer asks the provider for the medical record (the chart).
- [Prompt-pay deadline](prompt-pay-deadline.md): The date by which a clean claim must be paid under state law or contract; paying later costs interest.
- [Abrasion](abrasion.md): The cost a review puts on an honest provider: a wrongful pend, a wrongful adjustment or denial, and late payment.
- [Wrongful pend](wrongful-pend.md): Pending a claim whose billed level the chart supports (or that was underbilled).
- [Oracle](oracle.md): The best conceivable strategy under the same score and costs, built by reading the answer key; an upper bound, not a competitor.
- [Claim edit](claim-edit.md): A rule applied to the claim (and the provider's earlier claims) at adjudication, with no records request, that denies or flags claims that trip it.
- [Provider prior](provider-prior.md): A provider-level suspicion score, here the shrunk ratio of high-level visits to what the patients predict (screen eb_upper_t), refreshed as claims arrive.
- [Daily pend cap](daily-pend-cap.md): The most claims a strategy may pend on one receipt day, standing in for review staff capacity.
- [Resolved pend](resolved-pend.md): A pend that returned something a coder can read: a chart inside the wait limit, or a statement that no record exists.
- [Final development run](final-development-run.md): A last free run of a frozen strategy on development seeds no hypothesis has read, to catch a result that depended on the seeds used to choose and confirm it.
- [Workflow and agent](workflow-and-agent.md): Two designs of the same system: in a workflow, code fixes the order of steps; in an agent, a language model chooses the steps within caps.
