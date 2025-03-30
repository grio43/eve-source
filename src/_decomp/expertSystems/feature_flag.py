#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\feature_flag.py
import globalConfig
from carbon.common.script.sys.serviceManager import ServiceManager

def is_expert_systems_enabled():
    macho_net = ServiceManager.Instance().GetService('machoNet')
    return globalConfig.GetGlobalConfigBooleanValue(macho_net, configName='expert_system_feature_enabled', defaultValue=True)
