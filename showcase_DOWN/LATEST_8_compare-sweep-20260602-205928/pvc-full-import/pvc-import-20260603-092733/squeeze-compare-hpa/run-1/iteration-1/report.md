## HPA-only evaluation

- **Optimizer**: Kubernetes HPA (replica scaling only; CPU/memory requests fixed).
- **SLO**: PASS; failed=False
- **Observed replicas**: 5 (max during window: 5)
- **CPU request**: 150m; **mem request**: 75 MiB
- No deployment/HPA YAML changes for the next iteration (single-shot arm).