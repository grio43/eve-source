#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\assets\assetSafetyControllers.py


class SafetyControllerCharacter(object):

    def GetItemsInSafety(self):
        return sm.GetService('assetSafety').GetItemsInSafetyForCharacter()


class SafetyControllerCorp(object):

    def GetItemsInSafety(self):
        return sm.GetService('assetSafety').GetItemsInSafetyForCorp()
