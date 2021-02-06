# Introduction 
Operator based on Python Kopf that is using custom resource named alidns in API group tools.newesis.com to create, update or delete cronjobs.

The cronjob is using python requests to check if a web application is providing a 200 response status on a specific path and hostname in two different IPs (main and backup) using HTTP or HTTPS, in GET or POST, and update the record on a Alibaba Public or Private Zone DNS to allow automatic failover (a sort of private traffic manager).

# Getting Started
1. Install the helm chart (it contains namespace, crd, serviceAccount, clusterrole, clusterrolebinding and deployment)
2. Helm chart is avaiable in this repo in the folder "operatorDeployment" or for public access in newesissrl.azurecr.io/helm/alidnsoperator:1.0.0
3. The operator image is avaible as docker pull newesissrl.azurecr.io/alidnsoperator:1.0.0
4. The dnsmanager image is available as docker pull newesissrl.azurecr.io/alidnsmanager:1.0.0
5. Operator code and dockerfile are in the path "operator" in this repo
6. Dnsmanager code and dockerfile are in the path "dnsmanager" in this repo
7. The file sampledeploy.yaml is a sample of an alidns resource

# Changes from previous versions

Update operator to operate not only on create and delete but also on update.
Update dnsmnanager to manage option to ignore certificate errors and to manage both private and public DNS zone in Alibaba.


## Usage: see sampledeploy.yaml

apiVersion: tools.newesis.com/v1
kind: AliDns
metadata:
  name: alidns-newesis # Mandatory, name of your deployment, used as cronjob name
  namespace: alidnsoperator # Mandatory, namespace of your deployment, where the cronjob will run
  labels:
    app: alidns-newesis
spec:
  cronSpec: "* * * * *" # Mandatory, cron frequency to run the job
  hostName: www # Mandatory, the hostname for the web application you want to manage in the private zone DNS
  domainName: newesis.com # Mandatory, the DNS zone for your private zone DNS. Combined with the hostName will create the FQDN of your web resource
  probeUrl: /about # Mandatory, path, relative to the root of the site, for the HTTP request used as probe, need to start with /
  probeVerb: GET # Mandatory, Method for the HTTP request used as probe; possible values GET or POST
  probeSchema: HTTPS # Mandatory, Protocol for the HTTP request used as probe; possible values HTTP and HTTPS
  mainIp: 52.164.227.161 # Mandatory, main IP for the DNS record
  backupIp: 40.85.114.137 # Mandatory, backup IP for the DNS record (to be used if the main one not working)
  image: newesissrl.azurecr.io/alidnsmanager:1.0.0 # Mandatory, image to be executed in the cronjob, you can replace it with a custom one, all specs here will be available as env variables
  privZoneId: 1a1a10a1100000000a0a0a000000aaa0 # Mandatory the ID of the Alibaba privateZone (if Public DNS used put any string)
  accessKey: AAAA111AAAAAAA11aAAaaa1 # Mandatory, Alibaba accessKey
  secretKey: aaAAAA111AAAAAAA11aAAaaa100000aa # Mandatory, Alibaba secretKey
  region: eu-central-1 # Mandatory, Alibaba region
  isPublicDns: True # Mandatory, Boolean to instruct to use Alibaba Private Zone or Public DNS
  ignoreCertError: False # Mandatory, Boolean to configure the probe to ignore certificate errors during the test, set to true if using self signed certificates or if there is a mismatch between hostname and certificate
  