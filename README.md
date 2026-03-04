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

**K8s Commands**

```bash
# Watch stress-service pods (live)
kubectl get pods -l app=stress-service -w

# Deploy / update app and HPA
kubectl apply -f service/k8s/deployment.yaml
kubectl apply -f service/k8s/hpa.yaml

# Check deployment, pods, HPA
kubectl get deploy,po,hpa | grep stress-service
kubectl get hpa

# Port-forwards (run in separate terminals if running without start.py)

# Prometheus → http://localhost:9090 (open in browser to view dashboard and run queries for live metrics)
kubectl -n monitoring port-forward svc/kps-kube-prometheus-stack-prometheus 9090:9090

# stress-service → http://localhost:8000
kubectl port-forward svc/stress-service 8000:80

# Sanity checks
kubectl get pods
kubectl get svc
kubectl get pods -n monitoring
kubectl get svc -n monitoring
```

**ENVIRONMENT SETUP**

# 0) (Optional) Reset minikube if things are broken

minikube delete

# 1) Start local Kubernetes

minikube start --cpus=4 --memory=8192mb
minikube addons enable metrics-server # needed for HPA

# 2) Build Docker images

docker build -t stress-service:latest -f service/Dockerfile service/
docker build -t mock-dependency:latest -f service/Dockerfile.mock service/

# 3) Load images into minikube

minikube image load stress-service:latest
minikube image load mock-dependency:latest

# 4) Deploy app + mock dependency + HPA

kubectl apply -f service/k8s/mock-dependency.yaml
kubectl apply -f service/k8s/deployment.yaml
kubectl apply -f service/k8s/hpa.yaml

# 5) Install Prometheus stack (metrics + Prometheus UI/API)

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kps prometheus-community/kube-prometheus-stack \
 -n monitoring --create-namespace \
 -f service/monitoring/helm-values.yaml

# 6) Register ServiceMonitor so Prometheus scrapes stress-service

kubectl apply -f service/monitoring/servicemonitor.yaml

# 7) Sanity-check cluster + monitoring

kubectl get pods
kubectl get svc
kubectl get pods -n monitoring
kubectl get svc -n monitoring

# 8) Run an experiment (from repo root)

python start.py --profile low --script login
