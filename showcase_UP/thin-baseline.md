# web deployment (thin baseline)

name: web
namespace: svastik
replicas: 1

container: web
image: robotshop/rs-web:latest
port: 8080

resources:
requests:
cpu: 50m
memory: 25Mi
limits:
cpu: 100m
memory: 50Mi

# web HPA baseline

targetDeployment: web
minReplicas: 1
maxReplicas: 5

metric:
type: cpu
targetUtilization: 60

behavior:
scaleUp:
stabilizationWindowSeconds: 0
policy: +2 pods / 15s
scaleDown:
stabilizationWindowSeconds: 60

LLM passed because it could tune more than replica count.

Static baseline only had HPA replica scaling (1 → 5), while each pod stayed tiny.
LLM iteratively changed:
CPU/memory requests
CPU/memory limits
effective replica plan
That gave enough per-pod capacity + better total capacity distribution to bring p95 under SLO.
