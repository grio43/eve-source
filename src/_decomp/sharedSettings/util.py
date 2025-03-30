#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sharedSettings\util.py
import yaml
from eveexceptions import UserError
from overviewPresets.overviewPresetUtil import GetDictFromList

def GetDataFromSettingKey(settingKey, cacheDict, userErrorName):
    yamlString = cacheDict.get(settingKey, None) if cacheDict else None
    if yamlString is None:
        yamlString = sm.RemoteSvc('sharedSettingsMgr').GetStoredSharedSetting(settingKey)
    if yamlString is None:
        raise UserError(userErrorName)
    if cacheDict is not None:
        cacheDict[settingKey] = yamlString
    dataList = yaml.safe_load(yamlString)
    data = GetDictFromList(dataList)
    return data


def GetSettingKeyFromKeyVal(settingKeyVal, userErorrName):
    if settingKeyVal is None:
        raise UserError(userErorrName)
    return (settingKeyVal.hashvalue, settingKeyVal.sqID, settingKeyVal.settingTypeID)
