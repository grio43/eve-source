#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\extaColumnUtil.py
from eve.client.script.ui.station.stationServiceConst import serviceDataByNameID, serviceIDAlwaysPresent
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel
import structures

def GetSettingDataObjectForServiceName(serviceName):
    serviceData = serviceDataByNameID.get(serviceName, None)
    if not serviceData or serviceData.serviceID == serviceIDAlwaysPresent:
        return
    settingIDForService = structures.SERVICES_ACCESS_SETTINGS.get(serviceData.serviceID, None)
    if settingIDForService is None:
        return
    settingInfo = structures.SETTING_OBJECT_BY_SETTINGID.get(settingIDForService, None)
    return settingInfo


def GetHeaderForService(serviceName):
    settingData = GetSettingDataObjectForServiceName(serviceName)
    if settingData is None:
        return
    labelPath = settingData.labelPath
    if labelPath:
        return GetByLabel(labelPath)


class ExtraColumnProvider(object):
    NO_VALUE_FOUND_CHAR = '-'
    NOT_AVAILABLE = '_'

    def GetServicesForUniqueColumns(self, allServicesChecked):
        settingsAdded = []
        servicesToUseForColumns = []
        for eachServiceName in allServicesChecked:
            settingData = GetSettingDataObjectForServiceName(eachServiceName)
            if settingData and settingData.settingID not in settingsAdded:
                settingsAdded.append(settingData.settingID)
                servicesToUseForColumns.append(eachServiceName)

        return servicesToUseForColumns

    def GetColumnText(self, controller, serviceName):
        dataAndValue = self._GetSettingDataAndValueForColumn(controller, serviceName)
        if dataAndValue == self.NOT_AVAILABLE:
            return
        settingData, value = dataAndValue
        if value is None:
            return self.NO_VALUE_FOUND_CHAR
        text = FormatColumnValue(value, settingData.valueType, settingData.settingID)
        return text

    def GetValueForColumn(self, controller, serviceName):
        dataAndValue = self._GetSettingDataAndValueForColumn(controller, serviceName)
        if dataAndValue == self.NOT_AVAILABLE:
            return self.NOT_AVAILABLE
        return dataAndValue[1]

    def _GetSettingDataAndValueForColumn(self, controller, serviceName):
        serviceData = serviceDataByNameID.get(serviceName, None)
        if not serviceData:
            return self.NOT_AVAILABLE
        settingData = GetSettingDataObjectForServiceName(serviceName)
        if settingData is None:
            return self.NOT_AVAILABLE
        value = controller.GetInfoForExtraColumns(serviceData.serviceID)
        return (settingData, value)


def FormatColumnValue(value, valueType, settingID):
    if settingID == structures.SETTING_HOUSING_CAN_DOCK:
        return bool(value is not None)
    if valueType == structures.SETTINGS_TYPE_INT:
        return int(value)
    if valueType == structures.SETTINGS_TYPE_PERCENTAGE:
        return GetByLabel('UI/Structures/Browser/PercentageText', value=value)
    if valueType == structures.SETTINGS_TYPE_BOOL:
        return bool(value)
    if valueType == structures.SETTINGS_TYPE_ISK:
        return FmtISK(value, showFractionsAlways=0)
    return value
