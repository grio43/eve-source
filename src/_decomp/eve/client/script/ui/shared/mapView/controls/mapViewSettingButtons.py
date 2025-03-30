#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\controls\mapViewSettingButtons.py
import localization
from carbonui import const as uiconst
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.shared.mapView.colorModeSettingsButton import MapViewColorModeSettingButton
from eve.client.script.ui.shared.mapView.controls.mapViewCheckboxOptionButton import MapViewCheckboxOptionButton
from eve.client.script.ui.shared.mapView.mapViewConst import VIEWMODE_LAYOUT_SETTINGS, VIEWMODE_LINES_SETTINGS, VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS, VIEWMODE_COLOR_SETTINGS, VIEWMODE_FOCUS_SELF, VIEWMODE_LINES_SHOW_JUMP_BRIDGES_SETTINGS
from eve.client.script.ui.shared.mapView.controls.mapViewMarkersSettingButton import MapViewMarkersSettingButton
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst

class MapViewSettingButtons(LayoutGrid):
    onSettingsChangedCallback = None

    def ApplyAttributes(self, attributes):
        LayoutGrid.ApplyAttributes(self, attributes)
        self.columns = 4
        self.buttonIconByGroupKey = {}
        self.onSettingsChangedCallback = attributes.onSettingsChangedCallback
        self.mapViewID = attributes.mapViewID
        MapViewCheckboxOptionButton(parent=self, settingGroupKeys=(VIEWMODE_LAYOUT_SETTINGS,
         VIEWMODE_LINES_SETTINGS,
         VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS,
         VIEWMODE_LINES_SHOW_JUMP_BRIDGES_SETTINGS), callback=self.OnSettingsChanged, mapViewID=self.mapViewID)
        MapViewColorModeSettingButton(parent=self, settingGroupKey=VIEWMODE_COLOR_SETTINGS, callback=self.OnSettingsChanged, mapViewID=self.mapViewID, uniqueUiName=pConst.UNIQUE_NAME_MAP_COLOR_SETTINGS)
        MapViewMarkersSettingButton(parent=self, callback=self.OnSettingsChanged, mapViewID=self.mapViewID)
        focusSelf = ButtonIcon(parent=self, width=26, height=26, iconSize=16, func=self.FocusSelf, hint=localization.GetByLabel('UI/Map/FocusCurrentLocation'), texturePath='res:/UI/Texture/classes/MapView/focusIcon.png')
        focusSelf.tooltipPointer = uiconst.POINT_TOP_1

    def Close(self, *args):
        LayoutGrid.Close(self, *args)
        self.buttonIconByGroupKey = None
        self.onSettingsChangedCallback = None

    def FocusSelf(self, *args):
        if self.onSettingsChangedCallback:
            self.onSettingsChangedCallback(VIEWMODE_FOCUS_SELF, session.charid)

    def OnSettingsChanged(self, settingGroupKey, settingValue, mapViewID = None):
        button = self.buttonIconByGroupKey.get(settingGroupKey, None)
        if button:
            button.ReloadSettingValue()
        if self.onSettingsChangedCallback:
            self.onSettingsChangedCallback(settingGroupKey, settingValue)

    def UpdateButtons(self):
        for groupID, button in self.buttonIconByGroupKey.iteritems():
            button.ReloadSettingValue()
