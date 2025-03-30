#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\controls\mapViewSettingButton.py
from carbonui import const as uiconst
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.shared.mapView.mapViewSettings import GetMapViewSetting, ICON_MAP_BY_ID

class MapViewSettingButton(ButtonIcon):
    default_iconSize = 24
    default_width = 26
    default_height = 26
    settingGroupKey = None
    callback = None
    mapViewID = None

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        self.settingGroupKey = attributes.settingGroupKey
        self.mapViewID = attributes.mapViewID
        self.callback = attributes.callback
        self.ReloadSettingValue()

    def ReloadSettingValue(self):
        currentActive = GetMapViewSetting(self.settingGroupKey, self.mapViewID)
        self.SetTexturePath(ICON_MAP_BY_ID[currentActive])
        uicore.animations.BlinkOut(self.icon, startVal=1.0, endVal=0.0, duration=0.2, loops=2, curveType=uiconst.ANIM_BOUNCE)

    def Close(self, *args):
        ButtonIcon.Close(self, *args)
        self.callback = None

    def LoadTooltipPanel(self, tooltipPanel, *args):
        pass

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_1
