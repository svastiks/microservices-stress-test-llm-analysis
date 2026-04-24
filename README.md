# Efficiency Mapping: Cost-Optimal Microservice Configuration via Iterative LLM-Guided Stress Testing

Run **k6** against a service-under-test, pull **Prometheus** (or run without metrics), then get an **LLM** report plus a suggested **Kubernetes / resource** change per iteration. Optional modes **verify** (apply once, re-run, compare) and **squeeze** (iterative scale-down until failure or a stop condition).

**Layout:** the stress-test app is under **`apps/service/`**, k6 scripts under **`benchmarks/load-tests/k6/`**, and the cluster / analyzer manifests under **`infra/k8s/spark/`**. Commands and `start.py` defaults use these paths from the repo root.

---

## Repository layout

| Area | Path |
| --- | --- |
| Stress service (app, Dockerfiles, manifests, ServiceMonitor) | `apps/service/` |
| k6 scripts | `benchmarks/load-tests/k6/` |
| Cluster stack (Robot Shop on K8s, MongoDB, analyzer Job/RBAC/PVC, web HPA) | `infra/k8s/spark/` |
| LLM + experiment plumbing | `analysis/` |
| Automation (`deploy_spark_stack.sh`, analyzer image, `run_analyzer_job.sh`, …) | `scripts/` |
| Runbooks (local vs cluster end-to-end) | `docs/runbooks/` |

**Outputs**

- Local / generic runs: `results/` (dated folders, `run-*`, reports, diffs).
- Cluster pipeline exports: `results-from-cluster/` (when you copy analyzer output there).

**Experiments** — RPS, duration, and profiles: `experiments.json`.

---

## Setup

- [k6](https://k6.io/docs/get-started/installation/) (e.g. `brew install k6`)
- `pip install -r requirements.txt`
- `OPENAI_API_KEY` (e.g. `.env` and `source .env`)

---

## Quick run (repo root)

```bash
python3 start.py
```

Defaults: `benchmarks/load-tests/k6/login.js`, Prometheus port-forward when not using `--no-prometheus`, analysis writes under `results/YYYY-MM-DD-N/` (or `run-*` flows when using those modes).

Useful flags (see `python3 start.py --help`):

- `--profile low|medium|high` — RPS / duration from `experiments.json` (defaults include 60s workloads).
- `--script login|signup|robotshop_login`
- `--robot-shop` — shortcut for Robot Shop web on `localhost:8080` + `robotshop_login` script; pair with `--no-prometheus` for pure Docker.
- `--verify` / `--squeeze` / `--until-violation` — closed-loop against the YAML paths below (not with `--base-url` / `--robot-shop` for **verify**).
- `--efficiency` — squeeze-style cost / scale-down oriented LLM prompt.
- `--deployment-yaml` / `--hpa-yaml` — default `apps/service/k8s/deployment.yaml` and `apps/service/k8s/hpa.yaml`.

Typical artifacts per run: `k6-run-summary.json`, `report.md`, `recommended.diff` (or variant), optional verification markdown.

---

## Kubernetes: stress-service (local e.g. minikube)

Manifests and monitoring values live under **`apps/service/`**.

```bash
docker build -t stress-service:latest -f apps/service/Dockerfile apps/service/
docker build -t mock-dependency:latest -f apps/service/Dockerfile.mock apps/service/

kubectl apply -f apps/service/k8s/mock-dependency.yaml
kubectl apply -f apps/service/k8s/deployment.yaml
kubectl apply -f apps/service/k8s/hpa.yaml

helm install kps prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f apps/service/monitoring/helm-values.yaml

kubectl apply -f apps/service/monitoring/servicemonitor.yaml
```

Port-forwards and `kubectl get …` workflows are unchanged in spirit; see **`docs/runbooks/testing.md`** for the full **local K8s vs Robot Shop Docker** split, verify/squeeze behavior, and caveats.

---

## Cluster: Robot Shop + analyzer (closed loop on a real cluster)

For kubeconfig, image build/push, Helm deploy, analyzer Job, and pulling results into **`results-from-cluster/`**, use:

**`docs/runbooks/cluster-test-steps.md`**

Supporting pieces: `scripts/deploy_spark_stack.sh`, `Dockerfile.analyzer`, manifests under **`infra/k8s/spark/`**. Robot Shop Helm chart path is configurable (`CHART_PATH`; often `extra/robot-shop-msa/...` locally — `extra/` is gitignored; see runbook).

---

## Further reading

- **`docs/runbooks/testing.md`** — profiles, `--robot-shop`, Prometheus, verify/squeeze.
- **`docs/runbooks/cluster-test-steps.md`** — production-style cluster test from zero to artifacts.
