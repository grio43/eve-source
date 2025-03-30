#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\controls\mapViewCheckboxOptionButton.py
import localization
from carbonui import const as uiconst
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.client.script.ui.shared.mapView.mapViewSettings import ICON_ROOT, MV_GROUPS_BY_ID, GetMapViewSetting, LABEL_MAP_BY_ID, SetMapViewSetting

class MapViewCheckboxOptionButton(ButtonIcon):
    default_iconSize = 24
    default_width = 26
    default_height = 26
    settingGroupKeys = None
    callback = None

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        self.settingGroupKeys = attributes.settingGroupKeys
        self.mapViewID = attributes.mapViewID
        self.callback = attributes.callback
        self.SetTexturePath(ICON_ROOT + 'icon_const_group.png')

    def Close(self, *args):
        ButtonIcon.Close(self, *args)
        self.callback = None

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.uilib.leftbtn:
            return
        tooltipPanel.columns = 2
        tooltipPanel.AddLabelSmall(text=localization.GetByLabel('UI/Map/Layout'), bold=True, cellPadding=(8, 4, 4, 2), colSpan=tooltipPanel.columns)
        for settingsGroupKey in self.settingGroupKeys:
            if len(tooltipPanel.children):
                divider = LineThemeColored(align=uiconst.TOTOP, height=1, padding=(1, 1, 1, 0), opacity=0.3)
                tooltipPanel.AddCell(cellObject=divider, colSpan=tooltipPanel.columns)
            if settingsGroupKey in MV_GROUPS_BY_ID:
                for settingsID in MV_GROUPS_BY_ID[settingsGroupKey]:
                    checked = settingsID == GetMapViewSetting(settingsGroupKey, self.mapViewID)
                    textKey = (settingsGroupKey, settingsID)
                    checkBox = RadioButton(align=uiconst.TOPLEFT, text=LABEL_MAP_BY_ID[textKey], groupname=settingsGroupKey, checked=checked, wrapLabel=False, callback=self.OnRadioButtonChange, settingsKey=settingsGroupKey, retval=settingsID, settingsPath=None)
                    tooltipPanel.AddCell(cellObject=checkBox, colSpan=tooltipPanel.columns, cellPadding=(5, 0, 5, 0))

            else:
                checked = bool(GetMapViewSetting(settingsGroupKey, self.mapViewID))
                checkBox = Checkbox(align=uiconst.TOPLEFT, text=LABEL_MAP_BY_ID[settingsGroupKey], checked=checked, wrapLabel=False, callback=self.OnCheckBoxChange, settingsKey=settingsGroupKey, settingsPath=None)
                tooltipPanel.AddCell(cellObject=checkBox, colSpan=tooltipPanel.columns, cellPadding=(5, 0, 5, 0))

        tooltipPanel.state = uiconst.UI_NORMAL

    def OnCheckBoxChange(self, checkbox):
        key = checkbox.GetSettingsKey()
        val = checkbox.checked
        SetMapViewSetting(key, val, self.mapViewID)
        if self.callback:
            self.callback(key, val)

    def OnRadioButtonChange(self, checkbox):
        key = checkbox.GetSettingsKey()
        val = checkbox.GetReturnValue()
        SetMapViewSetting(key, val, self.mapViewID)
        if self.callback:
            self.callback(key, val)

    def _LocalCallback(self, *args, **kwds):
        if self.callback:
            self.callback(*args, **kwds)

    def GetTooltipDelay(self):
        return 5

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_1

    def GetTooltipPositionFallbacks(self):
        return [uiconst.POINT_TOP_2,
         uiconst.POINT_TOP_1,
         uiconst.POINT_TOP_3,
         uiconst.POINT_BOTTOM_2,
         uiconst.POINT_BOTTOM_1,
         uiconst.POINT_BOTTOM_3]
