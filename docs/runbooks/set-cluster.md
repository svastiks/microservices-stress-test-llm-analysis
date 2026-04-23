export KUBECONFIG=/path/to/your/kubeconfig.yaml

echo $KUBECONFIG

kubectl config get-contexts

kubectl config use-context monitoring

kubectl get pods
