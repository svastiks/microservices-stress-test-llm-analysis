Minimal stress-test service (FastAPI). POST /login, /health, /metrics. Env-driven CPU/memory/downstream.

Build (from repo root)
  docker build -t stress-service:latest -f apps/service/Dockerfile apps/service/
  docker build -t mock-dependency:latest -f apps/service/Dockerfile.mock apps/service/

Run with Docker
  docker run -p 8000:8000 -e CPU_WORK_MS=10 -e MEMORY_MB=5 stress-service:latest
  # Optional: mock on 8080
  docker run -p 8080:8080 -e LATENCY_MS=50 -e ERROR_RATE=0.1 mock-dependency:latest
  # With downstream: -e DOWNSTREAM_URL=http://host.docker.internal:8080

Env (app): CPU_WORK_MS, MEMORY_MB, DOWNSTREAM_URL, DOWNSTREAM_ERROR_RATE, DOWNSTREAM_LATENCY_MS, MONGODB_URI, LOG_LEVEL.
Chaos: POST /chaos?action=oom or ?action=memory&mb=100

K8s (minikube)
  minikube start
  minikube image load stress-service:latest
  minikube image load mock-dependency:latest
  kubectl apply -f apps/service/k8s/mock-dependency.yaml
  kubectl apply -f apps/service/k8s/deployment.yaml
  kubectl apply -f apps/service/k8s/hpa.yaml
  kubectl port-forward svc/stress-service 8000:80

k6 (from repo root)
  k6 run -e BASE_URL=http://localhost:8000 -e RPS=100 -e DURATION=30s benchmarks/load-tests/k6/login.js --summary-export=./results/k6-summary.json

Logs/metrics
  kubectl logs -l app=stress-service -f
  curl http://localhost:8000/metrics
