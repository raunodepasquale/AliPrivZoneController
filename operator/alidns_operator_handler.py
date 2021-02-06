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
    privZoneId = spec['privZoneId'] 
    accessKey = spec['accessKey'] 
    secretKey = spec['secretKey']
    region = spec['region'] 
    ignoreCertError = spec['ignoreCertError'] 
    isPublicDns = spec['isPublicDns'] 
    
    # Get if we have all the mandatory fields 
    if not secretKey: 
        raise kopf.HandlerFatalError(f"secretKey must be set. Got {secretKey}.") 
    if not accessKey: 
        raise kopf.HandlerFatalError(f"accessKey must be set. Got {accessKey}.") 
    if not region: 
        raise kopf.HandlerFatalError(f"region must be set. Got {region}.") 
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
    if not ignoreCertError: 
        ignoreCertError = False 
    if not isPublicDns: 
        isPublicDns = False 
    if not image: 
        raise kopf.HandlerFatalError(f"hostName must be set. Got {image}.")
    if not isPublicDns:    
        if not privZoneId: 
            raise kopf.HandlerFatalError(f"privZoneId must be set if isPublicDns is False. Got {privZoneId}.")
    elif isPublicDns:
        if not privZoneId: 
            privZoneId = 'RandomString'
    # Convert boolean values to string because boolean type is not accepted for env in v1.Container.Env
    ignoreCertError = str(ignoreCertError)
    isPublicDns = str(isPublicDns)

      
    # CronJob template 
    cronjob = {'apiVersion': 'batch/v1beta1', 'kind': 'CronJob','metadata': {'name' : name, 'namespace' : namespace },'spec': {'schedule': cronSpec , 'jobTemplate': { 'spec': { 'template': { 'spec' : {'restartPolicy' : 'OnFailure', 'containers' : [ {'env' : [ {'name': 'hostName', 'value' : hostName }, {'name': 'domainName', 'value' : domainName }, {'name': 'mainIp', 'value' : mainIp }, {'name': 'backupIp', 'value' : backupIp }, {'name': 'probeUrl', 'value' : probeUrl } , {'name': 'probeVerb', 'value' : probeVerb } , {'name': 'probeSchema', 'value' : probeSchema } , {'name': 'privZoneId', 'value' : privZoneId } , {'name': 'accessKey', 'value' : accessKey }, {'name': 'secretKey', 'value' : secretKey }, {'name': 'region', 'value' : region }, {'name': 'ignoreCertError', 'value' : ignoreCertError }, {'name': 'isPublicDns', 'value' : isPublicDns }],'image' : image , 'name' : 'alidnsmanager' } ] } } } }}} 
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

@kopf.on.update('tools.newesis.com', 'v1', 'alidns') 
def update_fn(body, spec, **kwargs): 

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
    privZoneId = spec['privZoneId'] 
    accessKey = spec['accessKey'] 
    secretKey = spec['secretKey']
    region = spec['region'] 
    ignoreCertError = spec['ignoreCertError'] 
    isPublicDns = spec['isPublicDns'] 
    
    # Get if we have all the mandatory fields 
    if not secretKey: 
        raise kopf.HandlerFatalError(f"secretKey must be set. Got {secretKey}.") 
    if not accessKey: 
        raise kopf.HandlerFatalError(f"accessKey must be set. Got {accessKey}.") 
    if not region: 
        raise kopf.HandlerFatalError(f"region must be set. Got {region}.") 
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
    if not ignoreCertError: 
        ignoreCertError = False 
    if not isPublicDns: 
        isPublicDns = False 
    if not image: 
        raise kopf.HandlerFatalError(f"hostName must be set. Got {image}.") 
    if not isPublicDns:    
        if not privZoneId: 
            raise kopf.HandlerFatalError(f"privZoneId must be set if isPublicDns is False. Got {privZoneId}.")
    elif isPublicDns:
        if not privZoneId: 
            privZoneId = 'RandomString'
    # Convert boolean values to string because boolean type is not accepted for env in v1.Container.Env
    ignoreCertError = str(ignoreCertError)
    isPublicDns = str(isPublicDns)

    # CronJob template 
    cronjob = {'apiVersion': 'batch/v1beta1', 'kind': 'CronJob','metadata': {'name' : name, 'namespace' : namespace },'spec': {'schedule': cronSpec , 'jobTemplate': { 'spec': { 'template': { 'spec' : {'restartPolicy' : 'OnFailure', 'containers' : [ {'env' : [ {'name': 'hostName', 'value' : hostName }, {'name': 'domainName', 'value' : domainName }, {'name': 'mainIp', 'value' : mainIp }, {'name': 'backupIp', 'value' : backupIp }, {'name': 'probeUrl', 'value' : probeUrl } , {'name': 'probeVerb', 'value' : probeVerb } , {'name': 'probeSchema', 'value' : probeSchema } , {'name': 'privZoneId', 'value' : privZoneId } , {'name': 'accessKey', 'value' : accessKey }, {'name': 'secretKey', 'value' : secretKey }, {'name': 'region', 'value' : region }, {'name': 'ignoreCertError', 'value' : ignoreCertError }, {'name': 'isPublicDns', 'value' : isPublicDns }],'image' : image , 'name' : 'alidnsmanager' } ] } } } }}} 
    # Make the CronJob the children of the alidns object 
    kopf.adopt(cronjob, owner=body)  
  
    # Object used to communicate with the API Server 
    api = kubernetes.client.BatchV1beta1Api() 

    # Create CronJob 
    obj = api.patch_namespaced_cron_job(name, namespace, cronjob) 
    print(f"CronJob {obj.metadata.name} updated") 

    # Update status 
    msg = f"CronJob update for alidns object {name}" 
    return {'message': msg}

@kopf.on.delete('tools.newesis.com', 'v1', 'alidns') 
def delete(body, **kwargs): 
    msg = f"alidns {body['metadata']['name']} and its CronJob children deleted" 
    return {'message': msg} 