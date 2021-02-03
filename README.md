# Introduction 
Operator based on Python Kopf that is using custom resource named alidns in API group tools.newesis.com to create cronjobs 

The cronjob is using python requests to check if a web application is providing a 200 response status on a specific path and hostname in two different IPs (main and backup) and update the record on a Alibaba Private Zone DNS to allow automatic failover (a sort of private traffic manager)

# Getting Started
1. Install the helm chart (it contains namespace, crd, serviceAccount, clusterrole, clusterrolebinding and deployment)
2. Helm chart is avaiable in this repo in the folder "operatorDeployment" or for public access in newesissrl.azurecr.io/helm/alidnsoperator:0.2.0
3. The operator image is avaible as docker pull newesissrl.azurecr.io/alidnsoperator:0.2.0
4. The dnsmanager image is available as docker pull newesissrl.azurecr.io/alidnsmanager:0.3.0
5. Operator code and dockerfile are in the path "operator" in this repo
6. Dnsmanager code and dockerfile are in the path "dnsmanager" in this repo
7. The file sampledeploy.yaml is a sample of an alidns resource


# Contribute
TODO: 

1. HTTPS probes not working due to failure on SNI for certificate validation
2. The operator is able to get creation and deletion of resources but it does not react to udate
3. Insert option to manage a public Alibaba DNS instead of a Private Zone 
