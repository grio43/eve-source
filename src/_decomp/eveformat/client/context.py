#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveformat\client\context.py
import __builtin__

def get_service(service_name):
    from carbon.common.script.sys.serviceManager import ServiceManager
    return ServiceManager.Instance().GetService(service_name)


def get_session():
    return __builtin__.session
