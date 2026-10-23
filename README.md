# Agentic E/M upcoding prevention (prepay)

A prepay investigator for payment integrity teams: it decides, for each arriving synthetic Medicare-style claim, whether to pay, pend and request records, or pay at a lower level, so the money is never paid out instead of recovered later. It is the prepay sibling of [em-upcoding-agent](https://github.com/simmyhundal/em-upcoding-agent) (postpay: audit after payment) and starts on that repository's data 4.2.

Status: stream layer, score P1.0 and the reference arms are built ([results on 10 development seeds](docs/prepay_reference_arms.md)); the workflow WP1.0 is next. Seed pools: [docs/seeds.md](docs/seeds.md); versions: [docs/versioning.md](docs/versioning.md). The plan is in the postpay repository: [discovery note](https://github.com/simmyhundal/em-upcoding-agent/blob/main/docs/prepay_discovery.md) and [copy-list](https://github.com/simmyhundal/em-upcoding-agent/blob/main/docs/prepay_copylist.md). Where this repository came from: [LINEAGE.md](LINEAGE.md).

Everything is synthetic. [MIT license](LICENSE).
