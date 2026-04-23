# Optimization Analysis for robot-shop-web Service

## Overview
The service under analysis is `robot-shop-web`, specifically the endpoint `POST /api/user/login`. The stress test was executed successfully without failure.

### Current Resource Requests and Limits
- **CPU Request:** 2m
- **CPU Limit:** 100m
- **Memory Request:** 12Mi
- **Memory Limit:** 100Mi

### Observed Performance
- **Total Requests:** 1500
- **Achieved RPS:** 25
- **P95 Latency:** 11ms (well below SLO of 500ms)
- **Error Rate:** 0.0 (within SLO of 1%)

### Cost Metrics
- **Cost Score:** 0.0137
- **Provisioned CPU:** 2m
- **Provisioned Memory:** 12Mi

## Findings
- The observed P95 latency is significantly lower than the SLO, indicating the service can handle more transactions efficiently with the current resources.
- The system is **not under load**, indicated by the low CPU (2m requested) and memory (12Mi requested) usage relative to limits (100m CPU and 100Mi memory).

## Optimization Recommendations
### Resource Reductions
Since the service is running effectively without failures, there is an opportunity to optimize resource usage conservatively:
1. **CPU Reduction:** Reduce CPU limit from 100m to 75m (25% reduction).
2. **Memory Reduction:** Reduce memory limit from 100Mi to 75Mi (25% reduction).

### HPA Adjustments
- The HPA is currently not scaling up or down since min and max replicas are both set to 1. Therefore, there is no need for changes in HPA settings at this moment.

### Overall Assessment
- **Optimization Headroom:** HIGH (due to strong performance and very low utilization)
- **Over-Provisioned:** true

## Updated YAML Configurations
### Deployment YAML
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stress-service
  labels:
    app: stress-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: stress-service
  template:
    metadata:
      labels:
        app: stress-service
    spec:
      containers:
        - name: app
          image: stress-service:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
          env:
            - name: CPU_WORK_MS
              value: "0"
            - name: MEMORY_MB
              value: "0"
            - name: LOG_LEVEL
              value: "INFO"
          resources:
            requests:
              cpu: "2m"
              memory: "12Mi"
            limits:
              cpu: "75m"
              memory: "75Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 3
            periodSeconds: 5
```
### HPA YAML
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: stress-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: stress-service
  minReplicas: 1
  maxReplicas: 1
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      selectPolicy: Max
      policies:
        - type: Pods
          value: 3
          periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 60
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 20
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 60
```

## Next Steps
- **Next Experiment:** Rerun the same fixed workload after applying the outlined changes to validate the stability and performance under a leaner configuration.