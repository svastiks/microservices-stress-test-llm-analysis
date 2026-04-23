### Testing guide

This repo now supports **two practical paths**:

1. **Kubernetes `stress-service` path**  
   This is the **fully closed-loop** path: k6 + Prometheus + YAML apply + verify/squeeze.
2. **Robot Shop on Docker path**  
   This is useful for exercising the **LLM + k6 + efficiency analysis** path, but it is **not a true closed-loop config validation** because Docker is not updated from `service/k8s/*.yaml`.

Built-in profiles now use **60 seconds** by default:

- `low` → **25 RPS**
- `medium` → **100 RPS**
- `high` → **500 RPS**

---

### Step 0 – Pick the path

#### A. Kubernetes `stress-service` (full loop)

Use this when you want:

- Prometheus-backed CPU / memory / replicas
- `verify`
- `squeeze` with real config application between runs

Prep:

1. Apply:
   - `service/k8s/deployment.yaml`
   - `service/k8s/hpa.yaml`
2. Confirm the service is healthy:
   - `kubectl get deploy,po,hpa`
3. Optional for clearer scaling demos:
   - set `CPU_WORK_MS` in `service/k8s/deployment.yaml` to something like `50` to `100`

#### B. Robot Shop on Docker (analysis / dry-run squeeze)

Use this when Robot Shop containers are already running locally and you want k6 + LLM analysis against the live app:

- `python3 start.py --robot-shop --no-prometheus`

Important:

- `--robot-shop` targets `http://localhost:8080`
- it uses `load-tests/k6/robotshop_login.js`
- it sets the endpoint to `POST /api/user/login`
- `verify` is **not supported** here
- `squeeze` works, but when `BASE_URL` is set the code **skips `kubectl apply`**, so the repo YAML changes while the Docker app keeps running unchanged

---

### Step 1 – Single-run smoke tests

#### Kubernetes `stress-service`

Run a low-load smoke test:

- `python3 start.py --profile low --script login`

Expected artifacts:

- `experiment.json`
- `analysis.json`
- `report.md`
- `recommended.diff`

Prometheus (already port-forwarded by `start.py`) can be checked with:

- `kube_deployment_status_replicas_available{deployment="stress-service",namespace="default"}`
- `sum(rate(container_cpu_usage_seconds_total{namespace="default",pod=~"stress-service.+",cpu="total"}[1m])) * 1000`
- `sum(container_memory_working_set_bytes{namespace="default",pod=~"stress-service.+"})`

#### Robot Shop on Docker

Run a low-load smoke test:

- `python3 start.py --profile low --robot-shop --no-prometheus`

This should:

- hit `http://localhost:8080/api/user/login`
- produce an `experiment.json` with:
  - `analysis_goal: "efficiency"`
  - `service: "robot-shop-web"`
  - `endpoint: "POST /api/user/login"`

---

### Step 2 – Verification mode

Use only with Kubernetes `stress-service`.

Command:

- `python3 start.py --profile high --script login verify`
  - (new CLI) `python3 start.py --profile high --script login --verify`

Behavior:

1. Run 1 executes
2. `recommended.diff` is applied via `kubectl apply`
3. Run 2 executes with the same profile/script
4. `verification/llm-result-verification.md` compares the two runs

Use this when you want to answer:  
Did the recommendation from Run 1 actually improve things?

---

### Step 3 – Squeeze mode

Use this when you want iterative cost reduction toward an efficiency frontier.

#### Kubernetes `stress-service` (real closed loop)

Bounded squeeze:

- `python3 start.py --profile low --script login squeeze --max-iterations 5`
  - (new CLI) `python3 start.py --profile low --script login --squeeze --max-iterations 5`

Unbounded until failure:

- `python3 start.py --profile low --script login squeeze --until-violation`
  - (new CLI) `python3 start.py --profile low --script login --until-violation`

Behavior:

1. Run baseline config
2. If SLO is `PASS`, apply `recommended.diff`
3. Re-run the same profile
4. Repeat until:
   - first `FAIL`
   - empty `recommended.diff`
   - execution error

Interpretation:

- `Optimal frontier (last PASS)` = current best candidate
- `First FAIL` = first configuration that violated the stop rule

#### Robot Shop on Docker (dry-run squeeze)

Bounded squeeze:

- `python3 start.py --profile low --robot-shop --no-prometheus squeeze --max-iterations 5`
  - (new CLI) `python3 start.py --profile low --robot-shop --no-prometheus --squeeze --max-iterations 5`

Until violation:

- `python3 start.py --profile low --robot-shop --no-prometheus squeeze --until-violation`
  - (new CLI) `python3 start.py --profile low --robot-shop --no-prometheus --until-violation`

Important caveat:

- with `--robot-shop` / `--base-url`, the squeeze loop **does not apply YAML to the live app**
- it still writes `recommended.diff` and updates repo YAML each iteration
- k6 keeps hitting the same Docker app
- so this path is useful for:
  - testing the orchestration
  - testing the LLM’s reduction logic
  - generating paper-trail configs
- but it is **not sufficient** to claim a real efficiency frontier for Robot Shop unless the live service is actually reconfigured between iterations

---

### Step 4 – Reading the artifacts

#### `experiment.json`

Contains the run record:

- workload
- SLO
- config
- observed metrics
- failure status
- cost block

Key fields:

- `analysis_goal`
- `observed.achieved_requests_per_second`
- `observed.latency_ms.p95`
- `failure.failed`
- `cost.cost_score`

#### `analysis.json`

Contains the compact LLM outcome:

- `slo_status`
- `optimization_headroom`
- `over_provisioned`
- `failure_archetype`
- `next_experiment`

#### `recommended.diff`

The LLM’s proposed YAML reduction or adjustment for:

- `service/k8s/deployment.yaml`
- `service/k8s/hpa.yaml`

---

### Step 5 – Current limitations

1. **Robot Shop + Docker is not a true config-apply loop**
   - `recommended.diff` changes repo YAML only
   - Docker containers do not automatically pick up those changes

2. **Prometheus-free Robot Shop runs have weaker signals**
   - CPU / memory / replica observations are missing
   - the LLM relies mostly on latency, error rate, and cost metadata

3. **The strongest research claim still comes from Kubernetes**
   - for a real “last PASS before first FAIL” efficiency frontier, the live SUT must actually be updated between runs

---

### Recommended commands

#### Fast smoke test against Robot Shop

- `python3 start.py --profile low --robot-shop --no-prometheus`

#### Dry-run efficiency squeeze against Robot Shop

- `python3 start.py --profile low --robot-shop --no-prometheus squeeze --max-iterations 5`
  - (new CLI) `python3 start.py --profile low --robot-shop --no-prometheus --squeeze --max-iterations 5`

#### Real closed-loop squeeze on Kubernetes `stress-service`

- `python3 start.py --profile low --script login squeeze --until-violation`
  - (new CLI) `python3 start.py --profile low --script login --until-violation`

