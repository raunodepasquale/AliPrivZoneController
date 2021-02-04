#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import yaml
import subprocess
import datetime
import logging
from logging.config import dictConfig
import requests
from docopt import docopt
from requests_toolbelt.adapters import host_header_ssl
import forcediphttpsadapter
from forcediphttpsadapter.adapters import ForcedIPHTTPSAdapter
from aliyunsdkcore.client import AcsClient
import ssl
# For Private Zone
from aliyunsdkpvtz.request.v20180101.DescribeZoneRecordsRequest import DescribeZoneRecordsRequest
from aliyunsdkpvtz.request.v20180101.UpdateZoneRecordRequest import UpdateZoneRecordRequest
# For Public Zone currently not used
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest


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

# Set initial value of status
mainIpStatus = "up"
backupIpStatus = "up"


# Set variables
hostName = os.getenv('hostName')
domainName = os.getenv('domainName')
accessKey = os.getenv('accessKey')
secretKey = os.getenv('secretKey')
region = os.getenv('region')
privZoneId = os.getenv('privZoneId')
mainIp = os.getenv('mainIp')
backupIp = os.getenv('backupIp')
probeSchema = os.getenv('probeSchema')
probeUrl = os.getenv('probeUrl')
probeVerb = os.getenv('probeVerb')

# Probe mainIP and backupIP, if mainIP working use that one, if not working test backup, if working use that one, if not leave the main
headers = {
    "Host": hostName+'.'+domainName
}
logger.info(f'Request headers are: {headers}')

# Set the default test URL
url = probeSchema+"://"+hostName+'.'+domainName+probeUrl
logger.info(f'Request URL is: {url}')

# Create a new requests session
s = requests.Session()

# Test against mainIP
logger.info(f'Testing mainIp')
logger.info(f'Request done to: {url} with IP: {mainIp}')
if probeSchema == 'HTTPS':
    logger.info(f'Request protocol is: HTTPS')
    # Set the destination IP for the connection to mainIp
    s.mount(probeSchema+"://"+hostName+'.'+domainName, ForcedIPHTTPSAdapter(dest_ip=mainIp))
    try:
        if probeVerb == 'GET':
            logger.info(f'GET request execution')
            r = s.get(url, headers=headers)
        elif probeVerb == 'POST':
            logger.info(f'POST request execution')
            r = s.post(url, headers=headers)
        logger.info(f'Request response is: {r.status_code}')
        statusCode = r.status_code
    except:
        logger.error(f'Exception on the request to mainIP')
        statusCode = 999
elif probeSchema == 'HTTP':
    logger.info(f'Request protocol is: HTTP')
    # Update the URL for the test to use the IP
    url = probeSchema+"://"+mainIp+probeUrl
    try:
        if probeVerb == 'GET':
            logger.info(f'GET request execution')
            r = s.get(url, headers=headers)
        elif probeVerb == 'POST':
            logger.info(f'POST request execution')
            r = s.post(url, headers=headers)
        logger.info(f'Request response is: {r.status_code}')
        statusCode = r.status_code
    except:
        logger.error(f'Exception on the request to mainIP')
        statusCode = 999
if statusCode == 200:
    targetIp = mainIp
elif statusCode != 200:
    logger.info(f'mainIp not working, going to test backupIp')
    mainIpStatus = "down" 

# Test against backupIp only fir mainIp down
if mainIpStatus == "down":
    logger.info(f'Testing backupIp')
    logger.info(f'Request done to: {url} with IP: {backupIp}')
    if probeSchema == 'HTTPS':
        logger.info(f'Request protocol is: HTTPS')
        # Set the destination IP for the connection to backupIp
        s.mount(probeSchema+"://"+hostName+'.'+domainName, ForcedIPHTTPSAdapter(dest_ip=backupIp))
        try:
            if probeVerb == 'GET':
                logger.info(f'GET request execution')
                r = s.get(url, headers=headers)
            elif probeVerb == 'POST':
                logger.info(f'POST request execution')
                r = s.post(url, headers=headers)
            logger.info(f'Request response is: {r.status_code}')
            statusCode = r.status_code
        except:
            logger.error(f'Exception on the request to backupIp')
            statusCode = 999
    elif probeSchema == 'HTTP':
        logger.info(f'Request protocol is: HTTP')
        # Update the URL for the test to use the IP
        url = probeSchema+"://"+backupIp+probeUrl
        try:
            if probeVerb == 'GET':
                logger.info(f'GET request execution')
                r = s.get(url, headers=headers)
            elif probeVerb == 'POST':
                logger.info(f'POST request execution')
                r = s.post(url, headers=headers)
            logger.info(f'Request response is: {r.status_code}')
            statusCode = r.status_code
        except:
            logger.error(f'Exception on the request to backupIp')
            statusCode = 999
    if statusCode == 200:
        targetIp = backupIp
    elif statusCode != 200:
        logger.info(f'backupIp not working, no changes on DNS setup')
        backupIpStatus = "down"


def get_aliyun_access_client(_id, secret, region):
    r"""
    Create an authenticated client for API calls to Aliyun.
    :param _id: access key id
    :param secret: secret of the access key
    :param region: e.g. "cn-hangzhou", "cn-shenzhen"
    :return: access client object
    """
    try:
        client = AcsClient(_id, secret, region)
        logging.info('Successfully obtained access client instance.')
        return client
    except Exception as e:
        logging.error("Aliyun access key authentication failed.")
        logging.error(e)
        sys.exit(-1)


# Get required parameters and methods are different for public DNS
def get_dns_record_id(client, domain, host, ip_address):
    try:
        request = DescribeZoneRecordsRequest()
        request.set_accept_format('json')
        request.set_ZoneId(privZoneId)
        request.set_Keyword(hostName)
        request.set_PageSize(100)
        response = client.do_action_with_exception(request)
        json_data = json.loads(str(response, encoding='utf-8'))

        for RecordId in json_data['Records']['Record']:
            if host == RecordId['Rr']:
                logging.info("Found a matched RecordId: {_record_id}.".format(
                    _record_id=RecordId["RecordId"]
                ))
                if ip_address == RecordId['Value']:
                    return None
                else:
                    return RecordId['RecordId']

    except Exception as e:
        logging.error("Unable to get RecordId.")
        logging.error(e)
        sys.exit(-1)

# Update on public and private DNS use the same input data and the same attributes
def update_domain_record(client, host, domain, _type, ip_address, record_id):
    try:
        request = UpdateZoneRecordRequest()
        request.set_accept_format('json')
        request.set_Value(ip_address)
        request.set_Type(_type)
        request.set_Rr(host)
        request.set_RecordId(record_id)
        response = client.do_action_with_exception(request)
        logging.info("Successfully updated domain record: {_host}.{_domain} ({__type} record) to {_ip_address}.".format(
            _host=host,
            _domain=domain,
            __type=_type,
            _ip_address=ip_address
        ))
        logging.debug(response)
    except Exception as e:
        logging.error("Failed to update domain record: {_host}.{_domain} ({__type} record) to {_ip_address}.".format(
            _host=host,
            _domain=domain,
            __type=_type,
            _ip_address=ip_address
        ))
        logging.error(e)

def main():
    t_start = datetime.datetime.now()
    logging.info("--- Task started at {time}".format(time=t_start.strftime("%Y-%m-%d %H:%M:%S %f")))
    
    # Configuration section
    access_key = os.getenv('accessKey')
    secret = os.getenv('secretKey')
    region = os.getenv('region')
    domain = os.getenv('domainName')
    host = os.getenv('hostName')
    _type = 'A'
    ip_address = targetIp
    logger.info(f'Target host {host} in domain {domain} and region {region} will be set to IP {ip_address}')

    client = get_aliyun_access_client(access_key, secret, region)
    record_id = get_dns_record_id(client, domain, host, ip_address)
    if record_id is None:
        logging.info("No DNS record to update, skip and exit")
    else:
        update_domain_record(client, host, domain, _type, ip_address, record_id)

    t_end = datetime.datetime.now()
    logging.info("--- Task ended at: {time}".format(time=t_end.strftime("%Y-%m-%d %H:%M:%S %f")))
    return 0

if backupIpStatus != "down" or mainIpStatus != "down":
    main()
