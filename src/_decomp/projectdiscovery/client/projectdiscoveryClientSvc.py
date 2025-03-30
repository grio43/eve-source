#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projectdiscoveryClientSvc.py
from projectdiscovery.client.projects.covid.service import CovidClientService
from projectdiscovery.client.baseservice import CommonProjectDiscoveryClientService
from projectdiscovery.common.const import ACTIVE_PROJECT_ID, COVID_PROJECT_ID

def get_client_service():
    if ACTIVE_PROJECT_ID == COVID_PROJECT_ID:
        return CovidClientService
    return CommonProjectDiscoveryClientService


ProjectDiscoveryClientService = get_client_service()
