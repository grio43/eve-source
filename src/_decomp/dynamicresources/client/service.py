#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\service.py


def get_dynamic_resource_service(service_manager = None):
    if service_manager is None:
        from carbon.common.script.sys.serviceManager import ServiceManager
        service_manager = ServiceManager.Instance()
    return service_manager.GetService('dynamicResourceSvc')
