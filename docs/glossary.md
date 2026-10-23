# Glossary

[Back to the README](../README.md)



## Terms
| Term | Meaning |
|---|---|
| E/M visit | An ordinary office visit (evaluation and management) that a doctor bills by complexity |
| CPT 99211 to 99215 | Five billing codes for established-patient office visits; a higher number means a more complex, higher-paying visit; 99215 is the top |
| Upcoding | Billing a higher visit code than the visit justified |
| Upcoding rate | From data 4.0: the share of a provider's visits billed above the justified level minus the share billed below; upcoders' net rate is 15% to 40%, everyone else centred between -15% and +15% |
| Habit | From data 4.0: how an upcoder upcodes: systematic (99214 for every 99213-level visit), opportunistic (borderline visits only) or template-driven (an EHR default, no intent) |
| Staff-hours cost | From score 4.0: the payer's staff time on a case (triage, requests, chart review, demand) at loaded wages, plus copy fees and model costs |
| Provider abrasion | From score 4.0: the cost a review puts on a provider, larger the less the provider truly overbilled |
| Medical decision-making (MDM) | The doctor's documented reasoning that supports a visit's level |
| Medicare | US government health insurance; its public billing statistics shape the synthetic data |
| Payment integrity | The team that checks claims were paid correctly and recovers overpayments |
| SIU | Special Investigations Unit: reviewers who look into suspected billing abuse |
| Synthetic data | Invented data with realistic statistical shape, so no real person is involved |
| Z-score | How far a number sits from the average, in units of typical variation |
| Confidence interval | A range that likely contains the true value |
| Guardrail | An automatic check that blocks bad output |
| LLM | "Large language model": the kind of AI that writes the case summaries |
| Hard negative | An honest provider who looks suspicious at first glance |

**Postpay and prepay.** Postpay (post-payment) review audits claims after they were paid and recovers any overpayment, usually from a sample of records. Prepay (pre-payment) review checks claims before payment and can deny or adjust them. This project is a postpay audit tool; prepay edits and automatic downcoding policies are the alternatives it competes with.

## Words this project uses one way
| Word | Used for | Not used for |
|---|---|---|
| Provider | the clinician or group billing under one ID: what the screen ranks, what is accused or cleared, and the party that answers record requests | "doctor" or "practice" (older pages still use them; they mean the same thing) |
| Chart | the medical record a provider returns for one visit, in answer to a records request | the claim itself |
| Note | the clinician's visit note inside a chart, when the point is about the note's text or signs: signatures, late signing, copied text ("cloned notes") | a synonym for chart |
| Version | one built release of a design, such as workflow v2.5 or agent v3.5; a row in a results table | "arm" or "line" (an arm is a version as run in one test, for example a variant with a gate; avoid in new text) |
| Workflow and agent | the two designs: code fixes the steps, or a model chooses them within caps | "pipeline" |
| PI team | the payment integrity staff who review drafts | "people" |
| Net dollars | the score since release 5: the overpayment a records sample supports for the upcoders found (90% lower bound) minus request and false-accusation costs | the release 1 to 4 point scores |

## Results columns
| Term | Meaning |
|---|---|
| Data model | The synthetic data a version was tested on. **Easy** (release 1, data 2.1): clean coding, documentation generated from the true visit level, clone signs planted in the notes. **Hard** (releases 2 to 5, data 2.2): adds honest coding noise (honest providers sometimes bill one level up), group and incident-to billing, truncated diagnoses, claims lag, corrections that change a level, and injected data defects |
| Recall | Upcoders found out of those planted |
| Precision | Upcoders found out of all providers called upcoding (found plus honest providers accused) |
| Net $ per seed | The RL score: the overpayment a records sample supports for the upcoders found (90% lower bound) minus request and false-accusation costs, averaged over the ten seeds. Compare rows within one seed set only; each release has its own ten seeds |

## Abbreviations
Versions are written short in notes, issues and tables: **S4.0, S4.1** are score versions (score 4.0, score 4.1); **D2.2, D4.0** are data versions (data 2.2, data 4.0); **W2.5, W4.0** are workflow versions and **A3.5, A5.0** agent versions (workflow v4.0, agent v5.0); **H8** is a hypothesis of the workflow's development loop (H8 is workflow v4.0). In the README and release notes the long form stays.
