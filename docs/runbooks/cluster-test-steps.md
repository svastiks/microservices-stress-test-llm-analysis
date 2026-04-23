# Cluster Test Steps (Start to End)

export KUBECONFIG=/path/to/your/kubeconfig.yaml

echo $KUBECONFIG

kubectl config get-contexts

kubectl config use-context monitoring

kubectl get pods

## 1) Set cluster context

```bash
export KUBECONFIG=/path/to/your/kubeconfig.yaml
kubectl config get-contexts
kubectl config use-context monitoring
kubectl get pods
kubectl get ns
```

## 2) Deploy Robot Shop in `svastik`

```bash
./scripts/deploy_spark_stack.sh
kubectl -n svastik get deploy,svc,hpa
kubectl -n svastik rollout status deployment/web --timeout=300s
kubectl -n svastik get endpoints web
```

## 3) Build and push analyzer image (multi-arch)

```bash
docker buildx create --use --name multiarch-builder 2>/dev/null || docker buildx use multiarch-builder
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f Dockerfile.analyzer \
  -t docker.io/svastik/microservices-stress-analyzer:latest \
  --push .
```

## 4) Set runtime env vars

```bash
export ANALYZER_IMAGE=docker.io/svastik/microservices-stress-analyzer:latest
export ANALYZER_IMAGE_PULL_POLICY=Always
export SQUEEZE_UNTIL_VIOLATION=false
export SQUEEZE_MAX_ITERATIONS=2
```

## 5) Ensure analyzer prerequisites

```bash
kubectl apply -f k8s/spark/analyzer-rbac.yaml
kubectl -n svastik create secret generic llm-api \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl -n svastik get sa stress-analyzer
kubectl -n svastik get secret llm-api
```

## 6) Launch analyzer job (closed loop with apply)

```bash
kubectl -n svastik delete job stress-analyzer-run --ignore-not-found
./scripts/run_analyzer_job.sh
kubectl -n svastik logs -f job/stress-analyzer-run
```

Switch stop mode per run:

```bash
# Option A: fixed cap (recommended for controlled runs)
RESULTS_DB_ENABLED=true
SQUEEZE_UNTIL_VIOLATION=false SQUEEZE_MAX_ITERATIONS=5 ./scripts/run_analyzer_job.sh

# Option B: run until first violation
SQUEEZE_UNTIL_VIOLATION=true ./scripts/run_analyzer_job.sh
```

## 7) Wait for completion

```bash
kubectl -n svastik wait --for=condition=complete --timeout=45m job/stress-analyzer-run \
  && echo DONE || echo FAILED_OR_TIMEOUT
kubectl -n svastik get job stress-analyzer-run
```

## 8) Retrieve persisted results from PVC

```bash
kubectl -n svastik apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: analyzer-results-reader
spec:
  restartPolicy: Never
  containers:
  - name: reader
    image: busybox
    command: ["sh","-c","sleep 3600"]
    volumeMounts:
    - name: results
      mountPath: /results
  volumes:
  - name: results
    persistentVolumeClaim:
      claimName: analyzer-results-pvc
EOF

kubectl -n svastik wait --for=condition=Ready pod/analyzer-results-reader --timeout=120s
kubectl -n svastik exec analyzer-results-reader -- ls -la /results
rm -rf ./results-from-cluster
kubectl -n svastik cp analyzer-results-reader:/results ./results-from-cluster
ls -la ./results-from-cluster
```

## 9) Review outputs

```bash
ls ./results-from-cluster/run-*/iteration-*/report.md
ls ./results-from-cluster/run-*/iteration-*/recommended.diff
ls ./results-from-cluster/run-*/cost-effective-boundary.md
```

## 10) Cleanup (optional)

```bash
kubectl -n svastik delete pod analyzer-results-reader --ignore-not-found
# Keep PVC to preserve history, or delete if you want a clean slate:
# kubectl -n svastik delete pvc analyzer-results-pvc
```

```
kubectl -n svastik delete pod analyzer-results-reader --ignore-not-found && \
kubectl -n svastik run analyzer-results-reader --image=busybox --restart=Never --overrides='{"spec":{"containers":[{"name":"reader","image":"busybox","command":["sh","-c","sleep 3600"],"volumeMounts":[{"name":"results","mountPath":"/results"}]}],"volumes":[{"name":"results","persistentVolumeClaim":{"claimName":"analyzer-results-pvc"}}]}}'
```

```
kubectl -n svastik get pvc analyzer-results-pvc
kubectl -n svastik describe pvc analyzer-results-pvc
kubectl -n svastik get pods -o wide
kubectl -n svastik exec analyzer-results-reader -- mount | grep results
kubectl -n svastik exec analyzer-results-reader -- ls -la /results
```

```
# 1) rebuild/push new analyzer image
docker buildx build --platform linux/amd64,linux/arm64 -f Dockerfile.analyzer -t docker.io/svastik/microservices-stress-analyzer:latest --push .

# 2) (one-time) ensure infra pieces exist
kubectl apply -f infra/k8s/spark/analyzer-rbac.yaml
kubectl apply -f infra/k8s/spark/analyzer-results-pvc.yaml
kubectl apply -f infra/k8s/spark/mongodb.yaml

# 3) rerun job cleanly
kubectl -n svastik delete job stress-analyzer-run --ignore-not-found
RESULTS_DB_ENABLED=true ./scripts/run_analyzer_job.sh
kubectl -n svastik logs -f job/stress-analyzer-run
```

Password decode
kubectl -n svastik get secret analyzer-mongodb -o jsonpath='{.data.MONGO_INITDB_ROOT_PASSWORD}' | base64 --decode; echo

Port forward
kubectl -n svastik get pod,svc | grep analyzer-mongodb
kubectl -n svastik port-forward svc/analyzer-mongodb 27017:27017
