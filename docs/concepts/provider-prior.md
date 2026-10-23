# Provider prior

[Back to the concepts](README.md) · [glossary](../glossary.md)

**What it means.** A provider-level suspicion score, here the shrunk ratio of high-level visits to what the patients predict (screen eb_upper_t), refreshed as claims arrive.

**Why it exists.** A workflow needs some starting suspicion before it sees a chart; the prior is that, using only claims received so far.

**Example.** A clinician bills 99214 or 99215 for 40% of visits when the patient mix predicts 25%; their prior is above 1.

**Where to find it.** `src/provider_prior.py`
