➜ microservices-stress-test-llm-analysis git:(main) ✗ kubectl config current-context
kubectl config get-contexts
kubectl cluster-info
kubectl get nodes -o wide
monitoring
CURRENT NAME CLUSTER AUTHINFO NAMESPACE

-         monitoring   spark     svastik-monitoring-admin   monitoring
          svastik      spark     svastik-monitoring-admin   svastik

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
Error from server (Forbidden): services is forbidden: User "system:serviceaccount:svastik:svastik-monitoring-admin" cannot list resource "services" in API group "" in the namespace "kube-system"
Error from server (Forbidden): nodes is forbidden: User "system:serviceaccount:svastik:svastik-monitoring-admin" cannot list resource "nodes" in API group "" at the cluster scope
➜ microservices-stress-test-llm-analysis git:(main) ✗ kubectl -n monitoring get pods,svc
kubectl -n svastik get pods,svc,deploy
kubectl auth can-i get pods -n monitoring
kubectl auth can-i get pods -n svastik
kubectl auth can-i get svc -n monitoring
NAME READY STATUS RESTARTS AGE
pod/alertmanager-my-kube-prometheus-stack-alertmanager-0 2/2 Running 0 12d
pod/grafana-core-6775cf76b6-bt849 1/1 Running 0 12d
pod/my-kube-prometheus-stack-grafana-7ffff64589-jvwzt 3/3 Running 0 10d
pod/my-kube-prometheus-stack-kube-state-metrics-75698b765f-f8qrr 1/1 Running 0 12d
pod/my-kube-prometheus-stack-operator-555675d959-dst7q 1/1 Running 0 12d
pod/my-kube-prometheus-stack-prometheus-node-exporter-4q2cr 1/1 Running 0 12d
pod/my-kube-prometheus-stack-prometheus-node-exporter-ff8js 1/1 Running 0 4d6h
pod/my-kube-prometheus-stack-prometheus-node-exporter-fwmnh 1/1 Running 0 12d
pod/my-kube-prometheus-stack-prometheus-node-exporter-gl9db 1/1 Running 0 12d
pod/prometheus-my-kube-prometheus-stack-prometheus-0 2/2 Running 0 29h

NAME TYPE CLUSTER-IP EXTERNAL-IP PORT(S) AGE
service/alertmanager-operated ClusterIP None <none> 9093/TCP,9094/TCP,9094/UDP 12d
service/my-kube-prometheus-stack-alertmanager ClusterIP redacted <none> 9093/TCP,8080/TCP 12d
service/my-kube-prometheus-stack-grafana ClusterIP redacted <none> 80/TCP 12d
service/my-kube-prometheus-stack-kube-state-metrics ClusterIP redacted <none> 8080/TCP 12d
service/my-kube-prometheus-stack-operator ClusterIP redacted <none> 443/TCP 12d
service/my-kube-prometheus-stack-prometheus ClusterIP redacted <none> 9090/TCP,8080/TCP 12d
service/my-kube-prometheus-stack-prometheus-node-exporter ClusterIP redacted <none> 9100/TCP 12d
service/prometheus-operated ClusterIP None <none> 9090/TCP 12d
NAME READY STATUS RESTARTS AGE
pod/node-debugger-worker1-4gqdz 0/1 Completed 0 4d6h
pod/node-debugger-worker2-26vkl 0/1 Completed 0 4d6h
pod/node-debugger-worker3-dv5gr 0/1 Completed 0 4d6h
yes
yes
yes
➜ microservices-stress-test-llm-analysis git:(main) ✗ kubectl -n monitoring get svc | grep -i prom
kubectl -n monitoring get svc,endpoints | grep -i prom
kubectl -n monitoring get pods -l app.kubernetes.io/name=prometheus
my-kube-prometheus-stack-alertmanager ClusterIP redacted <none> 9093/TCP,8080/TCP 12d
my-kube-prometheus-stack-grafana ClusterIP redacted <none> 80/TCP 12d
my-kube-prometheus-stack-kube-state-metrics ClusterIP redacted <none> 8080/TCP 12d
my-kube-prometheus-stack-operator ClusterIP redacted <none> 443/TCP 12d
my-kube-prometheus-stack-prometheus ClusterIP redacted <none> 9090/TCP,8080/TCP 12d
my-kube-prometheus-stack-prometheus-node-exporter ClusterIP redacted <none> 9100/TCP 12d
prometheus-operated ClusterIP None <none> 9090/TCP 12d
Warning: v1 Endpoints is deprecated in v1.33+; use discovery.k8s.io/v1 EndpointSlice
service/my-kube-prometheus-stack-alertmanager ClusterIP redacted <none> 9093/TCP,8080/TCP 12d
service/my-kube-prometheus-stack-grafana ClusterIP redacted <none> 80/TCP 12d
service/my-kube-prometheus-stack-kube-state-metrics ClusterIP redacted <none> 8080/TCP 12d
service/my-kube-prometheus-stack-operator ClusterIP redacted <none> 443/TCP 12d
service/my-kube-prometheus-stack-prometheus ClusterIP redacted <none> 9090/TCP,8080/TCP 12d
service/my-kube-prometheus-stack-prometheus-node-exporter ClusterIP redacted <none> 9100/TCP 12d
service/prometheus-operated ClusterIP None <none> 9090/TCP 12d
endpoints/my-kube-prometheus-stack-alertmanager redacted:8080,redacted:9093 12d
endpoints/my-kube-prometheus-stack-grafana redacted:3000 12d
endpoints/my-kube-prometheus-stack-kube-state-metrics redacted:8080 12d
endpoints/my-kube-prometheus-stack-operator redacted:10250 12d
endpoints/my-kube-prometheus-stack-prometheus redacted:9090,redacted:8080 12d
endpoints/my-kube-prometheus-stack-prometheus-node-exporter redacted:9100,redacted:9100,redacted:9100 + 1 more... 12d
endpoints/prometheus-operated redacted:9090 12d
NAME READY STATUS RESTARTS AGE
prometheus-my-kube-prometheus-stack-prometheus-0 2/2 Running 0 29h

➜ microservices-stress-test-llm-analysis git:(main) ✗ curl -sS "http://my-kube-prometheus-stack-prometheus.monitoring.svc:9090/-/ready"
curl: (6) Could not resolve host: my-kube-prometheus-stack-prometheus.monitoring.svc
➜ microservices-stress-test-llm-analysis git:(main) ✗ kubectl -n svastik get networkpolicy
kubectl -n monitoring get networkpolicy
No resources found in svastik namespace.
No resources found in monitoring namespace.
➜ microservices-stress-test-llm-analysis git:(main) ✗ kubectl -n svastik describe resourcequota
kubectl -n svastik describe limitrange
Name: svastik-quota
Namespace: svastik
Resource Used Hard

---

limits.cpu 0 8
limits.memory 0 16Gi
Name: svastik-default-limits
Namespace: svastik
Type Resource Min Max Default Request Default Limit Max Limit/Request Ratio

---

Container cpu - - 100m 100m -
Container memory - - 100Mi 100Mi -
➜ microservices-stress-test-llm-analysis git:(main) ✗ kubectl -n svastik get deploy,svc,pods
kubectl -n svastik get deploy web -o yaml | sed -n '1,120p'
NAME READY STATUS RESTARTS AGE
pod/node-debugger-worker1-4gqdz 0/1 Completed 0 4d6h
pod/node-debugger-worker2-26vkl 0/1 Completed 0 4d6h
pod/node-debugger-worker3-dv5gr 0/1 Completed 0 4d6h
Error from server (NotFound): deployments.apps "web" not found
➜ microservices-stress-test-llm-analysis git:(main) ✗ kubectl -n svastik get secrets | grep -i docker\|regcred\|ghcr\|ecr
kubectl -n svastik get sa default -o yaml
apiVersion: v1
kind: ServiceAccount
metadata:
creationTimestamp: "2026-04-14T13:01:03Z"
name: default
namespace: svastik
resourceVersion: "redacted"
uid: redacted
➜ microservices-stress-test-llm-analysis git:(main) ✗ kubectl -n svastik get pvc
kubectl -n svastik get storageclass
No resources found in svastik namespace.
Error from server (Forbidden): storageclasses.storage.k8s.io is forbidden: User "system:serviceaccount:svastik:svastik-monitoring-admin" cannot list resource "storageclasses" in API group "storage.k8s.io" at the cluster scope
➜ microservices-stress-test-llm-analysis git:(main) ✗
