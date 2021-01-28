import os
import sys
import json
import logging
from logging.config import dictConfig
import requests
from docopt import docopt
from requests_toolbelt.adapters import host_header_ssl
import ssl
ssl_context = ssl.create_default_context()
# Sets up old and insecure TLSv1.
ssl_context.options &= ~ssl.OP_NO_TLSv1_3 & ~ssl.OP_NO_TLSv1_2 & ~ssl.OP_NO_TLSv1_1
ssl_context.minimum_version = ssl.TLSVersion.TLSv1

logger = logging.getLogger(__name__)
dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s[%(levelname)s]%(name)s[%(lineno)s]: %(message)s'  # NOQA E502
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
    }
})

# Set taget_ip to be the main one, as default
targetIp = os.getenv('mainIp')

# Set variables
hostName = os.getenv('hostName')
accessKey = os.getenv('accessKey')
secretKey = os.getenv('secretKey')
region = os.getenv('region')
privZoneId = os.getenv('privZoneId')

# Probe mainIP and backupIP, if mainIP working use that one, if not working test backup, if working use that one, if not leave the main
headers = {
    "Host": os.getenv('hostName')+'.'+os.getenv('domainName')
}
logger.info(f'Request headers are: {headers}')

# Create a new requests session
s = requests.Session()
# Mount the adapter for https URLs in case of HTTPS
if os.getenv('probeSchema') == 'HTTPS':
    s.mount('https://', host_header_ssl.HostHeaderSSLAdapter())

# Execute the probe using GET or POST and check return status to be 200
if os.getenv('probeVerb') == 'GET':
    logger.info(f'Request method is: GET')
    url = os.getenv('probeSchema')+"://"+os.getenv('mainIp')+os.getenv('probeUrl')
    logger.info(f'Testing mainIp')
    logger.info(f'Request done to: {url}')
    try:
        r = s.get(url, headers=headers)
        logger.info(f'Request response is: {r.status_code}')
        statusCode = r.status_code
    except:
        logger.info(f'Exception on the request to mainIP')
        statusCode = 999
    if statusCode == 200:
        targetIp = os.getenv('mainIp')
    elif statusCode != 200:
        url = os.getenv('probeSchema')+"://"+os.getenv('backupIp')+os.getenv('probeUrl')
        logger.info(f'Testing backupIp')
        logger.info(f'Request done to: {url}')
        try:
            r = s.get(url, headers=headers)
            logger.info(f'Request response is: {r.status_code}')
            if r.status_code == 200:
                targetIp = os.getenv('backupIp')
        except:
            logger.info(f'Exception on the request to backupIP')
    
if os.getenv('probeVerb') == 'POST':
    logger.info(f'Request method is: POST')
    url = os.getenv('probeSchema')+"://"+os.getenv('mainIp')+os.getenv('probeUrl')
    logger.info(f'Testing mainIp')
    logger.info(f'Request done to: {url}')
    try:
        r = s.post(url, headers=headers)
        logger.info(f'Request response is: {r.status_code}')
        statusCode = r.status_code
    except:
        logger.info(f'Exception on the request to mainIP')
        statusCode = 999        
    if statusCode == 200:
        targetIp = os.getenv('mainIp')
    elif statusCode != 200:
        url = os.getenv('probeSchema')+"://"+os.getenv('backupIp')+os.getenv('probeUrl')
        logger.info(f'Testing backupIp')
        logger.info(f'Request done to: {url}')
        try:
            r = s.post(url, headers=headers)
            logger.info(f'Request response is: {r.status_code}')
            if r.status_code == 200:
                targetIp = os.getenv('backupIp')
        except:
            logger.info(f'Exception on the request to backupIP')

# Execute the Terraform apply for the DNS record update
logger.info(f'Updating domain record: {hostName} with IP {targetIp}')
initCommand = os.popen('./terraform init')
output = initCommand.read()
logger.info(f'Terraform init command output: {output}')
applyCommand = './terraform apply -auto-approve -compact-warnings -var \'accessKey='+accessKey+'\' -var \'secretKey='+secretKey+'\' -var \'region='+region+'\' -var \'privZoneId='+privZoneId+'\' -var \'hostName='+hostName+'\' -var \'targetIp='+targetIp+'\''
logger.info(f'Executing Terraform Command: {applyCommand}')
stream = os.popen(applyCommand)
output = stream.read()
logger.info(f'Terraform apply command output: {output}')







