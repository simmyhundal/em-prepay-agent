# Agentic E/M upcoding prevention (prepay)

A prepay investigator for payment integrity teams: it decides, for each arriving synthetic Medicare-style claim, whether to pay, pend and request records, or pay at a lower level, so the money is never paid out instead of recovered later. It is the prepay sibling of [em-upcoding-agent](https://github.com/simmyhundal/em-upcoding-agent) (postpay: audit after payment) and starts on that repository's data 4.2.

Status: stream layer, score P1.0, the reference arms and the API-free workflow WP1.1 are built. WP1.1 beat the tuned claim edit by $8,589 a seed on a declared confirm and $6,837 a seed on a final development run ([result](docs/wp11_final_dev.md)); the fresh test seeds are unread. The agent AP1.0 is built and checked for parity, not yet run (paid, awaiting approval). Seed pools: [docs/seeds.md](docs/seeds.md); versions: [docs/versioning.md](docs/versioning.md). The plan is in the postpay repository: [discovery note](https://github.com/simmyhundal/em-upcoding-agent/blob/main/docs/prepay_discovery.md) and [copy-list](https://github.com/simmyhundal/em-upcoding-agent/blob/main/docs/prepay_copylist.md). Where this repository came from: [LINEAGE.md](LINEAGE.md).

Everything is synthetic. [MIT license](LICENSE).
