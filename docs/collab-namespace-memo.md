# Memo: Namespace resource ask & deployment strategy for shared K8s cluster

**Context:** I’m integrating with the shared Kubernetes cluster (AWS) and need a dedicated namespace with bounded resources so my stress-test + LLM analysis and verification runs don’t affect others’ experiments. This memo summarizes what I need and what I’d like to clarify.

---

## 1. What I’m running (brief)

- **Load testing:** K6 (constant arrival rate: 25 / 100 / **500 RPS** for low/medium/high; duration **90s**; high profile can go up to **600 RPS** in follow-up experiments).
- **System under test (SUT):** A microservice with HPA. I need to **scale replicas up and down** (and change HPA min/max and resource requests/limits) as part of experiments and verification (run 1 → LLM recommendation → apply → run 2 → compare).
- **Metrics:** Prometheus (CPU, memory, replica counts) + K6 metrics, then LLM analysis and verification.

So the **critical** requirement is: the SUT must run in a place where **I control replica count and scaling** (and optionally resource requests/limits) without impacting your workloads.

---

## 2. Do I need to deploy the SUT (microservice) in my namespace?

**Yes.** I need the **system under test** to live in **my** namespace so that:

- I can set replicas and HPA (min/max) independently.
- My load tests and scaling don’t affect your experiments (and vice versa).
- I can apply LLM-generated patches (replicas, HPA, resources) safely.

So I’m planning to use **either**:

- **Option A:** Your microservice **deployed into my namespace** (same app, separate Deployment/HPA so I control scaling), or  
- **Option B:** My current stress-service in my namespace, if we decide that’s sufficient for the collaboration.

I’m happy to use your microservice (Option A) for better alignment with your setup; I’d just need to deploy it in my namespace with my own replica/HPA/resource settings.

---

## 3. What runs in-cluster vs on my machine?

| Component | Where it runs today | In the shared cluster? |
|-----------|----------------------|-------------------------|
| **Microservice under test (SUT)** | In K8s (Deployment + HPA) | **Yes — in my namespace** |
| **K6 (load generator)** | On my laptop | No (I run `k6 run` locally and hit the service via port-forward or ingress) |
| **Prometheus** | In cluster (`monitoring` namespace) | Yes, but likely **shared** (I’d use existing cluster Prometheus if available) |
| **My pipeline (start.py, analysis, verify)** | On my laptop | No (Python + K6 local; no in-cluster runner today) |

So for the **namespace resource ask**, the main consumer is the **SUT** (and any in-cluster parts of your load/analysis stack, if we run those in my namespace — see below).

---

## 4. How many resources to ask for (safe numbers)

My experiments and past runs suggest the following.

- **Load:** Up to **500 RPS** (high profile), sometimes **600 RPS** in follow-up; **90s** duration.
- **Replicas:** My current HPA is 2–4, but in past experiment runs the LLM has recommended (and we’ve tested) configs with **max_replicas up to ~15–30**; observed replicas under load have gone up to **~15** in some runs.
- **Per-pod resources (current stress-service):**  
  - CPU: request 100m, limit 500m  
  - Memory: request 128Mi, limit 256Mi  

To have comfortable headroom for high load + LLM-driven scaling + a bit of buffer:

- Assume **up to ~20 replicas** of a similar small service (e.g. 500m CPU, 256Mi per pod).
- That’s roughly **10 cores** and **~5 Gi** for the SUT alone.
- Add margin for system overhead, any in-cluster load/analysis jobs, and growth.

**Suggested ask for the namespace (CPU and memory):**

- **CPU:** **12–16 cores** (e.g. 12 as minimum, 16 if you can spare it).
- **Memory:** **6–8 Gi** (e.g. 6 Gi minimum, 8 Gi with buffer).

You can implement this via **ResourceQuota** (and optionally LimitRange) on my namespace so I can’t exceed these and impact the rest of the cluster.

If your microservice has **larger** requests/limits than above, we can scale these numbers proportionally (e.g. if one pod is 1 CPU / 512Mi, then 20 pods ⇒ 20 CPU / 10 Gi; I’d ask for ~25 CPU / 12 Gi in that case).

---

## 5. My stress-test + LLM analysis software

- **Today:** My tooling (this repo: K6 scripts, `start.py`, analysis, verification) runs **on my machine**; it drives the cluster via `kubectl` (and port-forward). So I **don’t** need to deploy this repo into the cluster for my current workflow.
- **If we want runs from inside the cluster** (e.g. shared runner or CI): then we could run my pipeline as a **Job** (or small deployment) in my namespace. That would need a small amount of extra CPU/memory (e.g. 0.5–1 CPU, 1–2 Gi) on top of the SUT; the numbers in section 4 already include some headroom for that.

So: **no strict need** to deploy my pipeline into the namespace unless we agree to run it in-cluster; if we do, the suggested quota above should still be sufficient.

---

## 6. Your load-testing / analysis software (professor’s recommendation)

The professor suggested I **also use your** load-testing/analysis stack. To do that cleanly, I need a few clarifications:

1. **Where does your tool run?** (Same cluster, my namespace vs another namespace vs outside the cluster?)
2. **Does it need to be deployed in my namespace?** If yes, what are its **resource requests/limits** (CPU/memory) so I can add them to the namespace ask and stay within the quota?
3. **How does it target the SUT?** (URL/Service in my namespace, or do you need ingress/exposure?)

Once I know this, I can:
- Either add your tool’s resources to the same “12–16 CPU, 6–8 Gi” ask, or  
- Ask for a slightly larger quota so both my SUT and your tool fit in my namespace without affecting others.

---

## 7. Prometheus / metrics

- I need **Prometheus** (or a Prometheus-compatible endpoint) that can scrape **pods in my namespace** (CPU, memory, and any custom metrics the SUT exposes).
- Prefer reusing the **existing cluster Prometheus** (e.g. in `monitoring`) with a **ServiceMonitor** (or equivalent) for my namespace, so I don’t need a dedicated Prometheus in my namespace.
- If the cluster doesn’t have Prometheus yet, we can add “Prometheus in my namespace” to the resource ask (roughly 0.5–1 CPU, 1–2 Gi); again, the suggested quota has some headroom.

---

## 8. Summary: what I’m asking for and what I’ll do

**Ask for the namespace:**

- **Resource quota (example):** **12–16 CPU cores**, **6–8 Gi memory** (adjust if your SUT or tooling is heavier).
- **Clarifications:**  
  - Whether I should deploy **your microservice** in my namespace (with my own replica/HPA control).  
  - Where **your load-testing/analysis software** runs and whether it goes in my namespace; if yes, its resource needs.  
  - How I get **Prometheus** metrics for my namespace (shared Prometheus + ServiceMonitor vs dedicated).

**My plan:**

- Deploy the **SUT** (your microservice or my stress-service) **only in my namespace** so scaling and patches don’t affect your experiments.
- Keep using **my pipeline** from my machine unless we agree to run it in-cluster; if we do, I’ll stay within the agreed quota.
- Integrate **your** load-testing/analysis tool once I have the details above.

If you’re happy with this, we can fix the exact CPU/memory numbers and then you can create the namespace + quota (and optionally LimitRange). I’m also happy to sync on naming (e.g. namespace name) and access (kubeconfig / RBAC).
