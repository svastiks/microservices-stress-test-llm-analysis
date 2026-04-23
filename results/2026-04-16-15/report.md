# **Analysis of Kubernetes Resource Optimization for `robot-shop-web` Service**  

## **Overview**  
The analysis is based on a stress-test experiment for the `robot-shop-web` service, focusing on the `POST /api/user/login` endpoint. The goal is to identify optimization headroom and recommend conservative resource adjustments while maintaining SLO compliance.  

## **Experiment Insights**  
- **SLO Compliance**:  
  - P95 Latency: **6ms** (Expected: **500ms**)  
  - Error Rate: **0.0%** (Expected: **0.01%**)  
- **Workload Details**:  
  - Target RPS: **25**  
  - Observed RPS: **25**  
- **Resource Usage**:  
  - CPU Request: **3m**; Limits: **100m**  
  - Memory Request: **15Mi**; Limits: **100Mi**  

## **Cost Analysis**  
- **Cost Score**: **0.0176**  
- **Provisioned Requests**:  
  - CPU: **3m**  
  - Memory: **15Mi**  

## **Headroom Assessment**  
- Given that the workload is compliant with the SLO and the observed latency is significantly below the SLO threshold, we conclude that there is headroom for optimization.  
- The high-level cost metrics indicate a **low cost score**, suggesting provisioned resources can be reduced further.  

## **Proposed Changes**  
### **Scaling Down Strategy**  
- **Replicas**: Remain at **1** (minimum config) as the load is manageable.  
- **Resource Requests/Limits**:  
  - Reduce CPU requests by **25%** to **2.25m** (rounded to **2m** to align with Kubernetes configurations).  
  - Maintain CPU limits as they are currently set significantly higher.  
  - Memory requests can also be reduced by **25%** to approximately **11.25Mi** (rounded to nearest lower significant value of **12Mi**).  
- This offers a conservative decrease in resource allocation while ensuring performance remains unaffected given current metrics.  

### **Updated Deployment YAML**  
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
              cpu: "100m"  
              memory: "100Mi"  
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

### **Updated HPA YAML**  
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

## **Final Summary**  
- **Optimization Headroom**: **MEDIUM**  
- **Over-Provisioned**: **true**  
- **Next Experiment**: Rerun the same workload after applying the leaner YAML configuration.