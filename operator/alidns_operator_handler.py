import kopf 
import kubernetes 
import yaml 
@kopf.on.create('tools.newesis.com', 'v1', 'alidns') 
def create_fn(body, spec, **kwargs): 

    # Get info from alidns object 
    name = body['metadata']['name'] 
    namespace = body['metadata']['namespace'] 
    cronSpec = spec['cronSpec'] 
    hostName = spec['hostName']
    domainName = spec['domainName']
    mainIp = spec['mainIp']
    backupIp = spec['backupIp']
    probeSchema = spec['probeSchema']
    probeUrl = spec['probeUrl']
    probeVerb = spec['probeVerb']
    image = spec['image']
    accessKey = spec['accessKey'] 
    secretKey = spec['secretKey'] 
    region = spec['region'] 
    privZoneId = spec['privZoneId'] 
    
    # Get if we have all the mandatory fields 
    if not secretKey: 
        raise kopf.HandlerFatalError(f"secretKey must be set. Got {secretKey}.") 
    if not accessKey: 
        raise kopf.HandlerFatalError(f"accessKey must be set. Got {accessKey}.") 
    if not region: 
        raise kopf.HandlerFatalError(f"region must be set. Got {region}.") 
    if not privZoneId: 
        raise kopf.HandlerFatalError(f"privZoneId must be set. Got {privZoneId}.") 
    if not hostName: 
        raise kopf.HandlerFatalError(f"hostName must be set. Got {hostName}.") 
    if not domainName: 
        raise kopf.HandlerFatalError(f"domainName must be set. Got {domainName}.") 
    if not cronSpec: 
        raise kopf.HandlerFatalError(f"cronSpec must be set. Got {cronSpec}.") 
    if not mainIp: 
        raise kopf.HandlerFatalError(f"mainIp must be set. Got {mainIp}.") 
    if not backupIp: 
        raise kopf.HandlerFatalError(f"backupIp must be set. Got {backupIp}.") 
    if not probeUrl: 
        probeUrl = '/'
    if not probeVerb: 
        probeVerb = 'GET' 
    if not probeSchema: 
        probeSchema = 'HTTP' 
    if not image: 
        raise kopf.HandlerFatalError(f"hostName must be set. Got {image}.") 

      
    # CronJob template 
    cronjob = {'apiVersion': 'batch/v1beta1', 'kind': 'CronJob','metadata': {'name' : name, 'namespace' : namespace },'spec': {'schedule': cronSpec , 'jobTemplate': { 'spec': { 'template': { 'spec' : {'restartPolicy' : 'OnFailure', 'containers' : [ {'env' : [ {'name': 'hostName', 'value' : hostName }, {'name': 'domainName', 'value' : domainName }, {'name': 'mainIp', 'value' : mainIp }, {'name': 'backupIp', 'value' : backupIp }, {'name': 'probeUrl', 'value' : probeUrl } , {'name': 'probeVerb', 'value' : probeVerb } , {'name': 'probeSchema', 'value' : probeSchema } , {'name': 'privZoneId', 'value' : privZoneId } , {'name': 'accessKey', 'value' : accessKey }, {'name': 'secretKey', 'value' : secretKey }, {'name': 'region', 'value' : region }],'image' : image , 'name' : 'alidnsmanager' } ] } } } }}} 
    # Make the CronJob the children of the alidns object 
    kopf.adopt(cronjob, owner=body)  
  
    # Object used to communicate with the API Server 
    api = kubernetes.client.BatchV1beta1Api() 

    # Create CronJob 
    obj = api.create_namespaced_cron_job(namespace, cronjob) 
    print(f"CronJob {obj.metadata.name} created") 

    # Update status 
    msg = f"CronJob created for alidns object {name}" 
    return {'message': msg}
@kopf.on.delete('tools.newesis.com', 'v1', 'alidns') 
def delete(body, **kwargs): 
    msg = f"alidns {body['metadata']['name']} and its CronJob children deleted" 
    return {'message': msg} 