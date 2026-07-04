# Engineer vs Advanced archive summary

- **RPS**: 260 (UP)
- **Source archive**: /Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts_latest/FORMULA_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps260-20260609-204250
- **Advanced subdir**: llm-run (formula llm-run = advanced LLM)
- **Engineer verify**: FAIL 1×180m/32Mi prov_cost=0.4954
- **Advanced best_pass prov_cost**: 0.2805
- **Advanced wins cost**: True

## Contents

- profiling-source/experiment.json — fat static-baseline k6 pass used to derive engineer baseline
- engineer-baseline/ — derived YAML + verify-run cluster test
- advanced-benchmark/advanced-llm-run/ — full advanced squeeze (from llm-run or advanced-llm-run)
- advanced-benchmark/source-comparison.md — original vanilla/formula comparison
- comparison.md — engineer vs advanced comparison table
