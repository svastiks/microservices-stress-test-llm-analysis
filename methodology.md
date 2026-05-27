# Methodology: LLM-Guided Closed-Loop Right-Sizing

## 1. Positioning: LLM as the Method

The core contribution of this work is an **LLM-guided closed-loop controller** that navigates the configuration space of a microservice deployment to find the cost-optimal SLO-compliant boundary. The LLM is not one arm of an A/B comparison — it is the proposed system. All other controllers serve as baselines against which the LLM's convergence speed and boundary quality are evaluated.

This framing yields a clean research question:

> *Can an LLM-guided controller find the cost-optimal SLO boundary faster and at lower provisioning cost than algorithmic baselines, and which design decisions in the LLM controller are responsible for that advantage?*

---

## 2. System Architecture

The closed loop operates as follows:

```
┌─────────────┐     k6 load      ┌─────────────────┐
│   Workload  │ ───────────────► │   Kubernetes    │
│  Generator  │                  │    Cluster      │
└─────────────┘                  └────────┬────────┘
                                          │ metrics
                                          ▼
                                 ┌─────────────────┐
                                 │   Prometheus    │
                                 │   Telemetry     │
                                 └────────┬────────┘
                                          │ experiment.json
                                          ▼
                                 ┌─────────────────┐
                                 │  LLM Controller │  ◄── iteration history
                                 │  (proposed)     │  ◄── current YAML
                                 └────────┬────────┘
                                          │ recommended YAML
                                          ▼
                                 ┌─────────────────┐
                                 │  Safety Guards  │
                                 │  + Diff Apply   │
                                 └────────┬────────┘
                                          │ kubectl apply
                                          ▼
                                    (next iteration)
```

Each iteration proceeds as:
1. Apply workload via k6 constant-arrival-rate profile at target RPS
2. Collect Prometheus metrics into `experiment.json`
3. Compute SLO PASS/FAIL and cost score
4. LLM controller reads the full iteration history and current YAML, emits new Deployment/HPA YAML
5. Safety guards post-process the LLM output
6. Apply diff to cluster, wait for settle period, repeat

The loop terminates when the boundary condition is met:
- **DOWN mode:** first FAIL after a sequence of PASSes → boundary is the last PASS configuration
- **UP mode:** first PASS after a sequence of FAILs → boundary is the first PASS configuration

---

## 3. The Proposed LLM Controller

### 3.1 History-Aware Prompting

A key limitation of naive LLM-in-the-loop approaches is that the LLM sees only the current iteration state. The proposed controller passes the **full iteration trace** as a structured table in the prompt:

```
| iter | Rcpu (m) | Rmem (MiB) | N | p95 (ms) | err (%) | cost  | result |
|------|----------|------------|---|----------|---------|-------|--------|
|  1   |   500    |    256     | 2 |   312    |   0.0   | 0.84  | PASS   |
|  2   |   380    |    192     | 2 |   389    |   0.0   | 0.64  | PASS   |
|  3   |   280    |    140     | 2 |   611    |   2.1   | 0.47  | FAIL   |
```

This allows the LLM to:
- Detect the location of the boundary from the trajectory
- Identify which resource dimension is binding
- Avoid oscillating configurations it has already tried
- Estimate how much slack remains before the next failure

### 3.2 Structured Chain-of-Thought Output

The LLM is required to reason in fixed stages before emitting YAML. This makes the reasoning auditable and provides natural integration points for safety guards:

```
Stage 1 — Bottleneck diagnosis:
  Which signal is binding? (p95 / error rate / ucpu / umem)
  Answer: p95 is approaching SLO at 389ms with ucpu=71%

Stage 2 — Slack estimate:
  How much headroom exists on non-binding dimensions?
  Answer: umem=34%, safe to reduce memory further

Stage 3 — Proposed delta:
  (ΔRcpu, ΔRmem, ΔN) with justification
  Answer: reduce Rcpu by 15%, reduce Rmem by 25%, hold N=2

Stage 4 — Risk assessment:
  Confidence this config will PASS: 0.72
  Primary risk: cpu utilization may spike under burst

Stage 5 — YAML output
```

### 3.3 Few-Shot Exemplars

Two to three demonstrations of successful iteration sequences are prepended to the system prompt. These are drawn from prior runs on the same service and encode the pattern of a well-behaved search: monotone resource reduction, awareness of utilization, conservative steps near the boundary. Few-shot prompting is the highest single-leverage prompt engineering intervention for structured generation tasks [1].

### 3.4 Confidence-Gated Fallback

The LLM outputs a confidence score (0–1) on whether the proposed configuration will PASS. When confidence falls below a threshold $\tau$ (e.g., $\tau = 0.6$), the controller falls back to a bisection step for that iteration. This makes the system robust without concealing the LLM's uncertainty:

$$\text{action}^{(k)} = \begin{cases} \text{LLM proposal} & \text{if } \text{conf}^{(k)} \geq \tau \\ \text{bisection step} & \text{if } \text{conf}^{(k)} < \tau \end{cases}$$

### 3.5 Safety Guards

Post-processing enforces hard constraints on the LLM output regardless of its proposal:
- Veto scale-down on FAIL+UP (never reduce resources when already failing)
- Replica one-step clamp on DOWN (no more than $\Delta N = 1$ replica reduction per iteration)
- Memory saturation guard (block memory reduction if $u_{\text{mem}} > 80\%$)
- Near-SLO cap (block CPU reduction if $p95 > 0.85 \cdot p95_{\text{SLO}}$)

Guards are derived entirely from `experiment.json` and applied identically regardless of which controller is active.

---

## 4. Baseline Hierarchy

The following baselines are evaluated against the proposed LLM controller, forming a clean ablation structure:

| # | Baseline | Description | What it isolates |
|---|---|---|---|
| B1 | **Static** | Fixed allocation, no adaptation across iterations | Lower bound — production over-provisioning |
| B2 | **HPA-default** | Reactive utilization-based horizontal scaling | Standard production comparator |
| B3 | **Formula (bisection)** | Deterministic binary search on PASS/FAIL signal | Strong algorithmic ceiling |
| B4 | **Vanilla LLM** | LLM with minimal prompt, no history, no CoT, no guards | Effect of prompt engineering and history |
| **P** | **Proposed LLM** | History-aware + CoT + few-shot + confidence gate + guards | Full contribution |

The gap between **B4 and P** isolates the contribution of the proposed engineering decisions. The gap between **B3 and P** is the headline result — whether the LLM can beat the theoretically well-motivated bisection baseline.

### Why bisection is the correct formula baseline

A bisection controller exploits the monotone feasibility signal (PASS/FAIL) optimally, converging to the boundary in $O(\log_2 n)$ iterations over a discretized resource grid of size $n$. For example, over a 1024-step CPU range, bisection converges in at most 10 iterations. Linear fractional step methods (used in prior work) make no use of this monotonicity and converge in $O(n)$ in the worst case. If the proposed LLM controller cannot outperform bisection, the contribution requires revisiting. If it matches or beats bisection while also finding a leaner boundary, that is a strong and defensible result [2].

---

## 5. Evaluation Protocol

### 5.1 Experimental design

To ensure statistical validity, each controller is evaluated under the following protocol:
- $\geq 10$ independent trials per controller per direction (DOWN / UP)
- Randomized arm ordering within each trial to control for cluster state and cache warmth
- Fresh cluster reset between arms (same baseline configuration)
- Results reported as mean $\pm$ std with Mann-Whitney U test for pairwise significance ($\alpha = 0.05$)

### 5.2 Primary metrics

| Metric | Symbol | Definition |
|---|---|---|
| Iterations to boundary | $K$ | Number of iterations until termination condition |
| Search cost | $C_{\text{search}}$ | Cumulative provisioning cost across all iterations |
| Steady-state cost | $C_{\text{steady}}$ | Provisioning cost at boundary per hour |
| Total cost | $C_{\text{total}}(H)$ | $C_{\text{search}} + C_{\text{steady}} \cdot H$ |
| SLO compliance rate | — | Fraction of PASS iterations in UP recovery |
| Boundary efficiency | $\eta^{(K)}$ | Resource utilization ratio at boundary |

### 5.3 Ablation structure

| Ablation | Removes | Answers |
|---|---|---|
| P $\setminus$ history | Iteration trace from prompt | How much does history awareness contribute? |
| P $\setminus$ CoT | Chain-of-thought reasoning stages | How much does structured reasoning contribute? |
| P $\setminus$ few-shot | Exemplar demonstrations | How much do exemplars contribute? |
| P $\setminus$ conf-gate | Confidence-gated fallback | How much does graceful degradation contribute? |
| P $\setminus$ guards | Safety post-processing | What is the cost of removing hard constraints? |

### 5.4 Sensitivity analysis

Plot $C_{\text{total}}(H)$ vs. $H$ for each controller. The slope of each line equals the steady-state hourly cost at the boundary. A controller with a leaner boundary has a shallower slope and dominates at large $H$. The break-even horizon between controller A and B is:

$$H^* = \frac{C_{\text{search}}^{A} - C_{\text{search}}^{B}}{C_{\text{steady/h}}^{B} - C_{\text{steady/h}}^{A}}$$

This directly answers: *for how long must the final configuration run before the savings from a leaner boundary outweigh the cost of a longer search?*

---

## 6. Contribution Statement

This work makes the following contributions:

1. **An LLM-guided closed-loop right-sizing controller** that integrates history-aware prompting, chain-of-thought reasoning, few-shot exemplars, and confidence-gated fallback into a coherent system
2. **A unified cost model** that accounts for both search cost and steady-state cost, grounded in real cloud pricing rather than arbitrary weights
3. **A rigorous evaluation protocol** comparing the proposed controller against a bisection baseline and two ablation levels (static, vanilla LLM), with statistical testing across $\geq 10$ trials per condition
4. **A break-even sensitivity analysis** that quantifies the deployment horizon at which each controller becomes cost-optimal, providing practitioners with a principled selection criterion

---

## References

[1] Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., ... & Amodei, D. (2020). **Language models are few-shot learners.** *Advances in Neural Information Processing Systems (NeurIPS '20)*, 33, 1877–1901.

[2] Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). **Introduction to Algorithms** (3rd ed.). MIT Press. *(Binary search and optimal search under monotone predicates, Chapter 2.)*

[3] Rzadca, K., Findeisen, P., Swiderski, J., Zych, P., Bronson, J., Brennan, C., Lennox, B., & Dehnert, J. (2020). **Autopilot: workload autoscaling at Google.** *Proceedings of the 15th European Conference on Computer Systems (EuroSys '20)*. ACM. https://doi.org/10.1145/3342195.3387524

[4] Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., ... & Zhou, D. (2022). **Chain-of-thought prompting elicits reasoning in large language models.** *Advances in Neural Information Processing Systems (NeurIPS '22)*, 35, 24824–24837.

[5] Delimitrou, C., & Kozyrakis, C. (2014). **Quasar: Resource-efficient and QoS-aware cluster management.** *Proceedings of the 19th International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '14)*. ACM. https://doi.org/10.1145/2541940.2541941
