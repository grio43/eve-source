#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\menuEntries.py
from carbon.common.script.util.format import FmtDist
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from localization import GetByLabel

def GetActionTextWithDistance(actionName, text):
    current = sm.GetService('menu').GetDefaultActionDistance(actionName)
    if current is not None:
        distString = FmtDist(current)
    else:
        distString = GetByLabel('UI/Menusvc/MenuHints/NoDistanceSet')
    return GetByLabel('UI/Menusvc/MenuHints/SelectedItemActionWithDist', actionName=text, distanceString=distString)


class DroneEngageTargetMenuEntryData(MenuEntryData):

    def __init__(self, text, func = None, subMenuData = None, texturePath = None, menuGroupID = None, menuEntryViewClass = None, internalName = '', typeID = None, droneIDs = None, **kwargs):
        super(DroneEngageTargetMenuEntryData, self).__init__(text, func, subMenuData, texturePath, menuGroupID, menuEntryViewClass, internalName, typeID, **kwargs)
        self.droneIDs = droneIDs


class OrbitMenuEntryData(MenuEntryData):

    def GetTextDescriptive(self):
        return GetActionTextWithDistance('Orbit', self.GetText())


class KeepAtRangeMenuEntryData(MenuEntryData):

    def GetTextDescriptive(self):
        return GetActionTextWithDistance('KeepAtRange', self.GetText())


class WarpToMenuEntryData(MenuEntryData):

    def GetTextDescriptive(self):
        return GetActionTextWithDistance('WarpTo', self.GetText())
