# microservices-stress-test-llm-analysis

Run k6 load test, then get an LLM report + suggested YAML fix per run.

**Setup**

- Install [k6](https://k6.io/docs/get-started/installation/) (e.g. `brew install k6`)
- `pip install -r requirements.txt`
- Set `OPENAI_API_KEY` (e.g. in `.env` and `source .env`)

**Run**

```bash
python3 start.py
```

This runs `load-tests/k6/basic.js`, exports the summary, then calls the analysis. Output goes under `results/YYYY-MM-DD-N/` (where N is the run index):

- `k6-run-summary.json`
- `report.md`
- `recommended.diff.yaml` (when the model suggests a fix)
