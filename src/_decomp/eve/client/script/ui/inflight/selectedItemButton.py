#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\selectedItemButton.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuUtil import ClearMenuLayer
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.crimewatch import crimewatchConst
from eve.client.script.ui.inflight.selectedItemConst import RESET_ACTIONS
from eve.client.script.ui.services.menuEntries import DroneEngageTargetMenuEntryData
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import SetDefaultDist, GetGlobalActiveItemKeyName
from menu import MenuLabel

class SelectedItemButton(ButtonIcon):

    def ApplyAttributes(self, attributes):
        self.menuEntryData = attributes.menuEntryData
        self.cmdName = attributes.cmdName
        self.disabledHint = attributes.disabledHint
        self.iconHoverColor = None
        super(SelectedItemButton, self).ApplyAttributes(attributes)
        if self.menuEntryData.GetLabelPath() in RESET_ACTIONS:
            Sprite(texturePath='res:/UI/Texture/icons/44_32_8.png', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, idx=0)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        shortcutString = uicore.cmd.GetShortcutStringByFuncName(self.cmdName)
        tooltipPanel.AddLabelShortcut(self._GetActionLabel(), shortcutString)
        if self.disabledHint:
            tooltipPanel.AddLabelMedium(text=self.disabledHint, colSpan=tooltipPanel.columns)

    def _GetActionLabel(self):
        return self.menuEntryData.GetTextDescriptive()

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_2

    def GetMenu(self):
        m = []
        label = ''
        key = GetGlobalActiveItemKeyName(self.menuEntryData.GetLabelPath())
        if key == 'Orbit':
            label = MenuLabel('UI/Inflight/SetDefaultOrbitDistance', {'typeName': self.menuEntryData.GetLabelPath()})
        elif key == 'KeepAtRange':
            label = MenuLabel('UI/Inflight/SetDefaultKeepAtRangeDistance', {'typeName': self.menuEntryData.GetLabelPath()})
        elif key == 'WarpTo':
            label = MenuLabel('UI/Inflight/SetDefaultWarpWithinDistance', {'typeName': self.menuEntryData.GetLabelPath()})
        if len(label) > 0:
            m.append((label, SetDefaultDist, (key,)))
        return m

    def OnMouseEnter(self, *args):
        if not self.IsEnabled():
            return
        super(SelectedItemButton, self).OnMouseEnter(*args)
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self._GetCrimewatchIconColor()

    def _GetCrimewatchIconColor(self):
        if isinstance(self.menuEntryData, DroneEngageTargetMenuEntryData):
            crimewatchSvc = sm.GetService('crimewatchSvc')
            targetID = sm.GetService('target').GetActiveTargetID()
            requiredSafetyLevel = crimewatchSvc.GetRequiredSafetyLevelForEngagingDrones(self.menuEntryData.droneIDs, targetID)
            if crimewatchSvc.CheckUnsafe(requiredSafetyLevel):
                if requiredSafetyLevel == const.shipSafetyLevelNone:
                    return crimewatchConst.Colors.Criminal.GetRGBA()
                else:
                    return crimewatchConst.Colors.Suspect.GetRGBA()

    def _GetIconHoverColor(self):
        if self.iconHoverColor is None:
            self.iconHoverColor = self._GetCrimewatchIconColor() or super(SelectedItemButton, self)._GetIconHoverColor()
        return self.iconHoverColor

    def _ExecuteFunction(self):
        if self.uniqueUiName:
            sm.ScatterEvent('OnSelectedItemButtonClicked', self.uniqueUiName)
        super(SelectedItemButton, self)._ExecuteFunction()
        sm.StartService('ui').StopBlink(self)
        ClearMenuLayer()

    def GetActionID(self):
        return self.menuEntryData.GetLabelPath()
