# Agentic E/M upcoding prevention (prepay)

A prepay investigator for payment integrity teams: it decides, for each arriving synthetic Medicare-style claim, whether to pay, pend and request records, or pay at a lower level, so the money is never paid out instead of recovered later. It is the prepay sibling of [em-upcoding-agent](https://github.com/simmyhundal/em-upcoding-agent) (postpay: audit after payment) and starts on that repository's data 4.2.

Status: stream layer, score P1.0, the reference arms and the API-free workflow WP1.1 are built. WP1.1 beat the tuned claim edit by $8,589 a seed on a declared confirm and $6,837 a seed on a final development run ([result](docs/wp11_final_dev.md)). On ten fresh test seeds WP1.1 beat the edit by $5,709 a seed ([true test](docs/p1_test.md)); the small agent AP1.0 (Haiku 5.5, $0.30) did $2,824 a seed worse than the workflow it mirrors. Seed pools: [docs/seeds.md](docs/seeds.md); versions: [docs/versioning.md](docs/versioning.md). The plan is in the postpay repository: [discovery note](https://github.com/simmyhundal/em-upcoding-agent/blob/main/docs/prepay_discovery.md) and [copy-list](https://github.com/simmyhundal/em-upcoding-agent/blob/main/docs/prepay_copylist.md). Where this repository came from: [LINEAGE.md](LINEAGE.md).

Everything is synthetic. [MIT license](LICENSE).

## Results of release P1 (score P1.0, net dollars summed over ten fresh test seeds)
| Arm | Score | Seeds above zero |
|---|---|---|
| Pay everything | $0 | |
| Tuned claim edit (no records request) | $123,672 | 8 of 10 |
| First workflow WP1.0 | $130,677 | 8 of 10 |
| **Workflow WP1.1 (pend floor $15)** | **$180,757** | 9 of 10 |
| Agent AP1.0 (Haiku 5.5, cost $0.30) | $152,512 | 9 of 10 |

Most of what every arm earns is the generator's planted impossible-visit pattern; see the [true test](docs/p1_test.md), the [release notes](docs/releases/P1.md) and the [reflection](docs/reflection_P1.md).
