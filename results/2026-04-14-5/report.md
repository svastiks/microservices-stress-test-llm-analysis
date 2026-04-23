# **Analysis of Stress-Test Experiment for robot-shop-web**  

### Summary  
- **Experiment ID:** low-20260415T013058Z-68203a87  
- **Service:** robot-shop-web  
- **Endpoint:** POST /api/user/login  
- **Observations:**  
  - **Total Requests:** 2250  
  - **Achieved RPS:** 25.0  
  - **P95 Latency:** 7.0 ms  
  - **Error Rate:** 0.0%  

### Analysis  
- **SLO Compliance:**  
  - **P95 Latency SLO:** 500 ms  
  - **Achieved P95 Latency:** 7.0 ms (well within SLO)  
  - **Error Rate SLO:** 0.01  
  - **Achieved Error Rate:** 0.0% (SLO compliant)  

### Headroom Analysis  
- **Resource Utilization:**  
  - Current CPU Requests: 60m (3 replicas total: 180m)  
  - Provisioned Requests CPU: 180m (currently utilizing significantly below available resources)  
  - **Cost Score:** 0.4144 indicates overhead for current provisioning.  
- **Cost Provisioning:**  
  - **Provisioned Request Memory:** 240 MiB vs allocated memory limits of 256 MiB indicates potential for reduction.  
  
### Recommendations  
- **Optimization Headroom:** HIGH  
- **Over-Provisioning Signals:**  
  - High over-provisioning indicated by low observed utilization and low latency compared to the SLO.  
- **Suggested Changes:**  
  - Reduce replicas from 3 to 2.  
  - Consider reducing CPU requests from 60m to 45m in a conservative step.  
  - Maintain current memory requests and limits as they are already minimal.  

### Proposed YAML Changes  
- **Deployment YAML:**  
```yaml  
apiVersion: apps/v1  
kind: Deployment  
metadata:  
  name: stress-service  
  labels:  
    app: stress-service  
spec:  
  replicas: 2  
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
              cpu: "45m"  
              memory: "80Mi"  
            limits:  
              cpu: "500m"  
              memory: "256Mi"  
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
---  
apiVersion: v1  
kind: Service  
metadata:  
  name: stress-service  
spec:  
  selector:  
    app: stress-service  
  ports:  
    - port: 80  
      targetPort: 8000  
  type: ClusterIP  
```  
- **HPA YAML:**  
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
  minReplicas: 2  
  maxReplicas: 2  
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
          averageUtilization: 70  
```  

### Next Experiment  
- Rerun the same fixed workload after applying the above changes to ensure SLO compliance remains intact.