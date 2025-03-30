#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\controls\mapViewMarkersSettingButton.py
import evetypes
import localization
from carbonui import const as uiconst
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.mapViewConst import VIEWMODE_MARKERS_SETTINGS, VIEWMODE_MARKERS_OPTIONS, VIEWMODE_MARKERS_OPTIONS_CUSTOM, VIEWMODE_MARKERS_CUSTOM_LABELS, MARKERS_OPTION_SOV_HUBS
from eve.client.script.ui.shared.mapView.mapViewSettings import ICON_ROOT, GetMapViewSetting, SetMapViewSetting
from eve.client.script.ui.shared.mapView.workforce import CanSeeSovHubs

class MapViewMarkersSettingButton(ButtonIcon):
    default_iconSize = 24
    default_width = 26
    default_height = 26
    settingGroupKey = None
    mapViewID = None
    callback = None

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        self.settingGroupKey = VIEWMODE_MARKERS_SETTINGS
        self.mapViewID = attributes.Get('mapViewID', mapViewConst.MAPVIEW_PRIMARY_ID)
        self.callback = attributes.callback
        self.SetTexturePath(ICON_ROOT + 'markersIcon.png')

    def Close(self, *args):
        ButtonIcon.Close(self, *args)
        self.callback = None

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.uilib.leftbtn:
            return
        tooltipPanel.columns = 2
        tooltipPanel.AddLabelSmall(text=localization.GetByLabel('UI/Map/Markers'), bold=True, cellPadding=(8, 4, 4, 2), colSpan=tooltipPanel.columns)
        divider = LineThemeColored(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=1, padding=(1, 1, 1, 0), opacity=0.3)
        tooltipPanel.AddCell(divider, cellPadding=(0, 0, 0, 2), colSpan=tooltipPanel.columns)
        currentActive = GetMapViewSetting(self.settingGroupKey, self.mapViewID)
        sortList = []
        for groupID in VIEWMODE_MARKERS_OPTIONS:
            sortList.append((evetypes.GetGroupNameByGroup(groupID), groupID))

        customOptions = VIEWMODE_MARKERS_OPTIONS_CUSTOM[:]
        if CanSeeSovHubs():
            customOptions.append(MARKERS_OPTION_SOV_HUBS)
        for customID in customOptions:
            sortList.append((localization.GetByLabel(VIEWMODE_MARKERS_CUSTOM_LABELS[customID]), customID))

        for optionName, optionID in sorted(sortList):
            checkBox = Checkbox(align=uiconst.TOPLEFT, text=optionName, checked=optionID in currentActive, wrapLabel=False, callback=self.OnSettingButtonCheckBoxChange, settingsKey=optionID, settingsPath=None)
            tooltipPanel.AddCell(cellObject=checkBox, colSpan=tooltipPanel.columns, cellPadding=(5, 0, 5, 0))

        tooltipPanel.AddSpacer(width=2, height=2, colSpan=tooltipPanel.columns)
        tooltipPanel.state = uiconst.UI_NORMAL

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_1

    def GetTooltipDelay(self):
        return 5

    def OnSettingButtonCheckBoxChange(self, checkbox, *args, **kwds):
        currentActive = set(GetMapViewSetting(self.settingGroupKey, self.mapViewID))
        active = checkbox.GetValue()
        settingsKey = checkbox.GetSettingsKey()
        if active:
            currentActive.add(settingsKey)
        else:
            try:
                currentActive.remove(settingsKey)
            except KeyError:
                pass

        SetMapViewSetting(self.settingGroupKey, list(currentActive), self.mapViewID)
        if self.callback:
            self.callback(self.settingGroupKey, list(currentActive))
