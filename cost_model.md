# Cost Model for LLM-Guided Microservice Right-Sizing

## Overview

Right-sizing a microservice involves two economically distinct costs that must both be accounted for in any fair evaluation of a search policy:

1. **Search cost** — the cumulative resource expenditure during iterative tuning
2. **Steady-state cost** — the ongoing provisioning cost at the final boundary configuration

The total cost of a right-sizing run is the sum of both. A controller that finds a cheaper configuration in fewer iterations dominates on both terms simultaneously.

---

## 1. Notation

| Symbol | Unit | Description |
|---|---|---|
| $k$ | — | Iteration index, $k = 1, 2, \ldots, K$ |
| $K$ | — | Total iterations until boundary is reached |
| $N^{(k)}$ | pods | Number of pod replicas at iteration $k$ |
| $r_{\text{cpu}}^{(k)}$ | mCores | CPU request per pod at iteration $k$ |
| $r_{\text{mem}}^{(k)}$ | MiB | Memory request per pod at iteration $k$ |
| $T$ | hours | Duration of one evaluation window (e.g., $90\,\text{s} = 1/40\,\text{h}$) |
| $H$ | hours | Deployment horizon — expected runtime of the final configuration |
| $p_{\text{cpu}}$ | \$/mCore/h | Per-unit CPU price from cloud provider |
| $p_{\text{mem}}$ | \$/MiB/h | Per-unit memory price from cloud provider |

---

## 2. Unit Prices

Real per-unit prices ground the cost model empirically and remove the need for arbitrary weighting factors $w_1, w_2$. For **GCP custom machine types** (us-central1, on-demand, as of 2024):

$$p_{\text{cpu}} = \frac{\$0.033174}{\text{vCPU} \cdot \text{h}} = \frac{\$0.033174}{1000\,\text{mCore} \cdot \text{h}}$$

$$p_{\text{mem}} = \frac{\$0.004446}{\text{GB} \cdot \text{h}} = \frac{\$0.004446}{1024\,\text{MiB} \cdot \text{h}}$$

For **AWS EC2** (on-demand, us-east-1), equivalent per-unit costs can be derived from the published vCPU and memory pricing for Fargate or custom instance families [3].

> **Note:** Substitute your actual cloud provider's published pricing. Using real prices makes the weights interpretable and reproducible across studies.

---

## 3. Search Cost

Every iteration consumes real cluster resources while the controller explores the configuration space. The **search cost** is the cumulative provisioning expenditure across all $K$ iterations:

$$C_{\text{search}} = \sum_{k=1}^{K} N^{(k)} \cdot T \cdot \left( p_{\text{cpu}} \cdot r_{\text{cpu}}^{(k)} + p_{\text{mem}} \cdot r_{\text{mem}}^{(k)} \right)$$

This term penalizes slow convergence directly: a controller that takes 11 iterations to reach the boundary incurs a larger search cost than one that takes 7, even if both land at the same final configuration. It captures the economic cost of the tuning process itself, which is non-trivial in production environments where re-tuning events occur regularly [1].

**Properties:**
- Monotonically increases with $K$ — more iterations always cost more
- Penalizes over-provisioned configurations explored early in DOWN runs (large $N^{(k)}, r^{(k)}$)
- Penalizes under-provisioned configurations lingered on in UP runs if the policy stalls

---

## 4. Steady-State Cost

Once the boundary configuration is found, the service runs at that configuration for an extended deployment horizon $H$. The **steady-state cost** is the ongoing hourly provisioning cost at the final configuration $k = K$:

$$C_{\text{steady}} = N^{(K)} \cdot H \cdot \left( p_{\text{cpu}} \cdot r_{\text{cpu}}^{(K)} + p_{\text{mem}} \cdot r_{\text{mem}}^{(K)} \right)$$

This is the dominant cost term at large $H$ (long deployments between re-tuning events). It directly captures the value of finding a leaner boundary: a 40% reduction in $r_{\text{cpu}}^{(K)}$ translates to a 40% reduction in steady-state CPU spend, compounding over the full horizon [1, 2].

**The deployment horizon $H$** is a configurable parameter representing how often the cluster is re-tuned. Typical values:

| Re-tuning cadence | $H$ |
|---|---|
| Daily | 24 h |
| Weekly | 168 h |
| Monthly | 720 h |
| Quarterly | 2,160 h |

---

## 5. Total Cost

The unified objective combines both terms:

$$\boxed{C_{\text{total}} = \underbrace{\sum_{k=1}^{K} N^{(k)} \cdot T \cdot \left( p_{\text{cpu}} \cdot r_{\text{cpu}}^{(k)} + p_{\text{mem}} \cdot r_{\text{mem}}^{(k)} \right)}_{\text{search cost}} + \underbrace{N^{(K)} \cdot H \cdot \left( p_{\text{cpu}} \cdot r_{\text{cpu}}^{(K)} + p_{\text{mem}} \cdot r_{\text{mem}}^{(K)} \right)}_{\text{steady-state cost}}}$$

A controller that minimizes $C_{\text{total}}$ must simultaneously:
- Converge to the boundary in few iterations (minimize $K$)
- Avoid wasteful configurations during search (minimize intermediate $N^{(k)}, r^{(k)}$)
- Land at a lean final configuration (minimize $N^{(K)}, r^{(K)}$ at boundary)

---

## 5b. Utilization-Effective Cost (Same Formula)

For each iteration, report a second scalar using the **same** linear cost as §3–§5, with effective resources $r \cdot u$ (fractional util from Prometheus, capped at 1):

$$C^{(k)}_{\text{util}} = N^{(k)} \cdot \left( p_{\text{cpu}} \cdot r_{\text{cpu}}^{(k)} u_{\text{cpu}}^{(k)} + p_{\text{mem}} \cdot r_{\text{mem}}^{(k)} u_{\text{mem}}^{(k)} \right)$$

- **Provisioned cost** ($C^{(k)}$ above with raw $r$): capacity reserved (invoice-style for requests).
- **Util cost** ($C^{(k)}_{\text{util}}$): same weights and prices, capacity actually consumed during the k6 window.

Search and steady-state totals (§3–§5) are computed separately for provisioned (`cost_search`, `cost_total`) and util (`cost_search_util`, `cost_total_util`) when comparing formula vs LLM. **Both optimizers use identical scoring** — only the proposed YAML differs.

Default weights $w_{\text{cpu}}=0.9$, $w_{\text{mem}}=0.1$ approximate GCP §2; set `COST_MODEL=gcp` for published $p_{\text{cpu}}, p_{\text{mem}}$.

---

## 6. SLO-Penalized Augmented Cost (Optional)

For training or reward shaping purposes, a single scalar that encodes both cost and SLO compliance is useful. Following the penalty method from constrained optimization [4]:

$$J^{(k)} = C^{(k)} + \lambda \cdot \max\!\left(0,\, \frac{p95^{(k)} - p95_{\text{SLO}}}{p95_{\text{SLO}}}\right) + \mu \cdot \max\!\left(0,\, \frac{\text{err}^{(k)} - \text{err}_{\text{SLO}}}{\text{err}_{\text{SLO}}}\right)$$

where $\lambda, \mu > 0$ are penalty weights that control the trade-off between cost minimization and SLO compliance. This formulation is useful as the LLM's optimization objective in the system prompt, but $C_{\text{total}}$ remains the primary evaluation metric for comparing controllers.

---

## 7. Resource Efficiency Ratio (Complementary Diagnostic)

Distinct from $C_{\text{util}}$: the **resource efficiency ratio** measures how tightly allocated resources match utilization at the boundary (unitless):

$$\eta^{(K)} = \frac{u_{\text{cpu}}^{(K)} \cdot r_{\text{cpu}}^{(K)} + u_{\text{mem}}^{(K)} \cdot r_{\text{mem}}^{(K)}}{r_{\text{cpu}}^{(K)} + r_{\text{mem}}^{(K)}}$$

where $u_{\text{cpu}}^{(K)}, u_{\text{mem}}^{(K)} \in [0, 1]$ are fractional utilization ratios at the boundary. Higher $\eta$ indicates a tighter fit between provisioned and consumed resources. This metric is adapted from cluster efficiency definitions in [2].

---

## 8. Sensitivity Analysis: Cost vs. Deployment Horizon

Since $C_{\text{steady}}$ scales linearly with $H$ while $C_{\text{search}}$ is fixed after convergence, the relative importance of each term depends on $H$:

$$C_{\text{total}}(H) = C_{\text{search}} + C_{\text{steady}}^{\text{per-hour}} \cdot H$$

Plotting $C_{\text{total}}$ vs. $H$ for each controller produces a family of lines whose slopes equal the steady-state hourly cost. A controller with a lower-cost boundary configuration has a shallower slope and dominates at large $H$, even if its search cost is higher. The **break-even horizon** $H^*$ between two controllers A and B is:

$$H^* = \frac{C_{\text{search}}^{A} - C_{\text{search}}^{B}}{C_{\text{steady/h}}^{B} - C_{\text{steady/h}}^{A}}$$

This analysis directly answers the practical question: *for how long must I run this configuration before the savings from a leaner boundary outweigh the cost of a longer search?*

---

## 9. Implementation (analyzer)

| Env | Default | Meaning |
|---|---|---|
| `COST_MODEL` | `weighted` | `weighted` (90/10 CPU/mem), `gcp` ($/h unit prices), or `legacy` (equal-weight sum) |
| `COST_CPU_WEIGHT` / `COST_MEM_WEIGHT` | `0.9` / `0.1` | Used when `COST_MODEL=weighted` |
| `COST_ITERATION_HOURS` | `STRESS_K6_DURATION` or 90s | Evaluation window $T$ for search cost |
| `COST_HORIZON_HOURS` | `720` | Horizon $H$ for steady-state cost |

| Field | Meaning |
|---|---|
| `cost.cost_score` | $C^{(k)}$ provisioned (§3–§5, per iter) |
| `cost.cost_score_util` | $C^{(k)}_{\text{util}}$ (§5b, same formula, $r \cdot u$) |
| `cost_search` / `cost_total` | Provisioned search + steady |
| `cost_search_util` / `cost_total_util` | Util-effective search + steady |

Formula and LLM runs share `analysis/cost_model.py`; comparison tables label **prov cost** and **util cost**.

---

## References

[1] Rzadca, K., Findeisen, P., Swiderski, J., Zych, P., Bronson, J., Brennan, C., Lennox, B., & Dehnert, J. (2020). **Autopilot: workload autoscaling at Google.** *Proceedings of the 15th European Conference on Computer Systems (EuroSys '20)*. ACM. https://doi.org/10.1145/3342195.3387524

[2] Delimitrou, C., & Kozyrakis, C. (2014). **Quasar: Resource-efficient and QoS-aware cluster management.** *Proceedings of the 19th International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '14)*. ACM. https://doi.org/10.1145/2541940.2541941

[3] Cortez, E., Bonde, A., Muzio, A., Russinovich, M., Fontoura, M., & Bianchini, R. (2017). **Resource central: Understanding and predicting workloads for improved resource management in large cloud platforms.** *Proceedings of the 26th ACM Symposium on Operating Systems Principles (SOSP '17)*. ACM. https://doi.org/10.1145/3132747.3132772

[4] Bertsekas, D. P. (1999). **Nonlinear Programming** (2nd ed.). Athena Scientific. *(Penalty and augmented Lagrangian methods, Chapter 4.)*
