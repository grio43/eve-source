#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureSettings\controllers\settingController.py
from signals import Signal
import structures

class SettingController(object):

    def __init__(self, settingID, groupID, value = 0.0):
        self.settingInfo = structures.SETTING_OBJECT_BY_SETTINGID[settingID]
        self.settingType = self.settingInfo.valueType
        self.settingID = settingID
        self.groupID = groupID
        self.value = value
        self.on_profile_value_changed = Signal(signalName='on_profile_value_changed')

    def GetGroupID(self):
        return self.groupID

    def GetSettingID(self):
        return self.settingID

    def GetSettingType(self):
        return self.settingType

    def GetSettingInfo(self):
        return self.settingInfo

    def SetValue(self, value):
        self.on_profile_value_changed()
        self.value = value

    def GetValue(self):
        return self.value

    def SettingCanHaveGroups(self):
        return self.settingInfo.hasGroups
