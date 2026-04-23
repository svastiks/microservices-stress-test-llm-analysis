# **Experiment Analysis for stress-service**

## **Overview**
The experiment aimed to assess the efficiency of the `stress-service` under a constant arrival rate with a target of 25 requests per second over a duration of 90 seconds. The observed system performance was significantly below the SLO requirements, indicating an opportunity for resource optimization.

## **Results**
- **Requested Resources:** 45m CPU and 80Mi RAM per pod
- **Limit Resources:** 500m CPU and 256Mi RAM per pod
- **Deployment Replicas:** 2
- **Observed p95 Latency:** 6.0 ms (well below SLO of 500 ms)
- **Error Rate:** 0.0% (well below SLO of 1%)

## **Analysis**
- **Utilization:** The effective provisioned requests total 90m CPU and 160Mi RAM across two replicas, which translates to 45m CPU and 80Mi RAM for each pod, reflecting that CPU usage is efficient given the achieved performance.
- **Cost Consideration:** The cost score of 0.2462 indicates resource efficiency is maintained, but there may be room for conservative scaling down.
- **Headroom:** Given that the p95 latency is only 6 ms, this represents significant optimization headroom which justifies adjustments.

## **Optimization Recommendations**
- **Replicas Reduction:** It is advisable to reduce the replicas from 2 to 1, particularly when current utilization is low and SLO compliance is evident.
- **Resource Requests/Limit Adjustments:** It is also reasonable to modestly reduce resource requests and limits by approximately 10-25% to further optimize resource utilization and costs as the current requests are below what might be strictly necessary given the observed performance.

### **New Configuration Proposal**
- **Replicas:** 1 
- **Requests:** 40m CPU, 70Mi Memory
- **Limits:** 400m CPU, 240Mi Memory

### **Potential YAML Changes**

### **Deployment YAML Update**:
- The number of replicas will be changed to 1, and the resource requests and limits will be slightly reduced.

### **HPA YAML Update**:
- Minimum replicating limit will be updated to 1 accordingly.

## **Conclusion**
The current system shows a strong performance with considerable resource overhead. By following the recommendations for resource adjustments, we expect to see improved resource efficiency without compromising performance, especially under the defined SLO constraints.

## **Next Experiment**
Re-run the same fixed workload after applying the updated configuration to validate performance stability.

