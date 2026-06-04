# UP demo: static baseline vs LLM (showcase)

- **Static sweep**: `results-from-cluster/static-up-sweep-20260527-125059`
- **Primary LLM compare**: `showcase_UP/compare-up-sweep-20260525-231308` (RPS 220–260)
- **280 LLM**: `showcase_UP/compare-up-sweep-20260525-010051/run-1` (same profile; separate sweep)

## Headline table (performance)

| RPS | static status | static p95 ms | static achieved RPS | llm status | llm p95 ms | llm achieved RPS | llm iterations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 220 | 🟥 FAIL | 2985.0 | 166.8 | 🟩 PASS | 394.0 | 220.0 | 3 |
| 240 | 🟥 FAIL | 3288.0 | 155.1 | 🟩 PASS | 442.0 | 240.0 | 4 |
| 260 | 🟥 FAIL | 4184.0 | 165.2 | 🟩 PASS | 296.0 | 260.0 | 3 |
| 280 | 🟥 FAIL | 3091.0 | 190.2 | 🟩 PASS (010051 sweep) | 371.0 | 280.0 | 4 |

## Resources and cost (static vs LLM best PASS)

| RPS | static cpu m | static mem Mi | static cpu limit m | static mem limit Mi | static replicas | static prov cost | static util cost | llm cpu m | llm mem Mi | llm cpu limit m | llm mem limit Mi | llm replicas | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 220 | 50 | 25 | 100 | 50 | 5 | 0.2372 | 0.1897 | 70 | 35 | 150 | 75 | 2 | 0.1328 | 0.0684 |
| 240 | 50 | 25 | 100 | 50 | 5 | 0.2372 | 0.1551 | 43 | 22 | 150 | 100 | 3 | 0.1225 | 0.0749 |
| 260 | 50 | 25 | 100 | 50 | 5 | 0.2372 | 0.1374 | 115 | 58 | 300 | 150 | 2 | 0.2183 | 0.0787 |
| 280 | 50 | 25 | 100 | 50 | 5 | 0.2372 | 0.1349 | 105 | 53 | 300 | 150 | 4 | 0.3987 | 0.1414 |

## Winner per load

| RPS | Winner | Metric used | Cost outcome |
| --- | --- | --- | --- |
| 220 | LLM | SLO pass (p95 394.0 ms) vs static fail (p95 2985.0 ms) | LLM lower prov (0.1328 < 0.2372); LLM lower util (0.0684 < 0.1897) |
| 240 | LLM | SLO pass (p95 442.0 ms) vs static fail (p95 3288.0 ms) | LLM lower prov (0.1225 < 0.2372); LLM lower util (0.0749 < 0.1551) |
| 260 | LLM | SLO pass (p95 296.0 ms) vs static fail (p95 4184.0 ms) | LLM lower prov (0.2183 < 0.2372); LLM lower util (0.0787 < 0.1374) |
| 280 | LLM | SLO pass (p95 371.0 ms) vs static fail (p95 3091.0 ms) | LLM higher prov (0.3987 > 0.2372); LLM higher util (0.1414 > 0.1349) |

## Data sources used for this table

- **RPS 220**: static=`results-from-cluster/static-up-sweep-20260527-125059/run-1/experiment.json` · llm=`showcase_UP/compare-up-sweep-20260525-231308/run-2/llm-run/cost-effective-boundary.json`
- **RPS 240**: static=`results-from-cluster/static-up-sweep-20260527-125059/run-2/experiment.json` · llm=`showcase_UP/compare-up-sweep-20260525-231308/run-3/llm-run/cost-effective-boundary.json`
- **RPS 260**: static=`results-from-cluster/static-up-sweep-20260527-125059/run-3/experiment.json` · llm=`showcase_UP/compare-up-sweep-20260525-231308/run-4/llm-run/cost-effective-boundary.json`
- **RPS 280 (010051 sweep)**: static=`results-from-cluster/static-up-sweep-20260527-125059/run-4/experiment.json` · llm=`showcase_UP/compare-up-sweep-20260525-010051/run-1/llm-run/cost-effective-boundary.json`

## Per-RPS comparison files

Under the static sweep, each `run-N/comparison.md` is static vs LLM for that RPS.
Mirrored as `comparison-static.md` under the matching showcase compare run.

