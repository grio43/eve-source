#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\menuAction.py
import sys
import types
import uthread
import localization
import log
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.format import FmtDist
from carbonui import uiconst
from carbonui.control.contextMenu.menuUtil import ClearMenuLayer
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.crimewatch import crimewatchConst
from eve.client.script.ui.inflight.selectedItemConst import CLOSE_MENU_ACTIONS
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import SetDefaultDist, GetGlobalActiveItemKeyName
from eveservices.menu import GetMenuService
from menu import MenuLabel, CaptionIsInMultiFunctions

class Action(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.actionID = None
        self.disabled = attributes.get('disabled', False)
        self.Prepare_(icon=attributes.icon)

    def Prepare_(self, icon = None):
        opacity = 0.2 if self.disabled else 1.0
        self.icon = GlowSprite(parent=self, align=uiconst.TOALL, texturePath=icon, state=uiconst.UI_DISABLED, opacity=opacity, iconOpacity=1.0)
        self.sr.fill = Fill(parent=self, state=uiconst.UI_HIDDEN)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        shortcutString = None
        reasonString = None
        distString = None
        keywords = {}
        if isinstance(self.action[1], basestring):
            reasonString = self.action[1]
            if self.actionID in ('UI/Inflight/WarpToWithinDistance', 'UI/Inflight/WarpToMoonMiningPoint'):
                defaultWarpDist = GetMenuService().GetDefaultActionDistance('WarpTo')
                keywords['distance'] = FmtDist(float(defaultWarpDist))
        else:
            if isinstance(self.action[0], MenuLabel):
                actionNamePath, keywords = self.action[0]
            if self.actionID in ('UI/Inflight/OrbitObject', 'UI/Inflight/Submenus/KeepAtRange'):
                key = GetGlobalActiveItemKeyName(actionNamePath)
                current = GetMenuService().GetDefaultActionDistance(key)
                if current is not None:
                    distString = FmtDist(current)
                else:
                    distString = localization.GetByLabel('UI/Menusvc/MenuHints/NoDistanceSet')
        if hasattr(self, 'cmdName'):
            shortcutString = uicore.cmd.GetShortcutStringByFuncName(self.cmdName)
        actionName = localization.GetByLabel(self.actionID, **keywords)
        if distString:
            hint = localization.GetByLabel('UI/Menusvc/MenuHints/SelectedItemActionWithDist', actionName=actionName, distanceString=distString)
        else:
            hint = actionName
        tooltipPanel.AddLabelShortcut(hint, shortcutString)
        if reasonString:
            tooltipPanel.AddLabelMedium(text=reasonString, colSpan=tooltipPanel.columns)

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_2

    def GetMenu(self):
        m = []
        label = ''
        key = GetGlobalActiveItemKeyName(self.actionID)
        if key == 'Orbit':
            label = MenuLabel('UI/Inflight/SetDefaultOrbitDistance', {'typeName': self.actionID})
        elif key == 'KeepAtRange':
            label = MenuLabel('UI/Inflight/SetDefaultKeepAtRangeDistance', {'typeName': self.actionID})
        elif key == 'WarpTo':
            label = MenuLabel('UI/Inflight/SetDefaultWarpWithinDistance', {'typeName': self.actionID})
        if len(label) > 0:
            m.append((label, SetDefaultDist, (key,)))
        return m

    def OnMouseEnter(self, *args):
        if self.disabled:
            return
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if self.sr.Get('fill', None):
            if hasattr(self, 'action'):
                if 'EngageTarget' in self.action[0][0]:
                    crimewatchSvc = sm.GetService('crimewatchSvc')
                    droneInfo = self.action[2]
                    if len(self.itemIDs) > 1 and len(droneInfo) > 1 and isinstance(droneInfo[0], (types.MethodType, types.LambdaType, types.FunctionType)):
                        droneIDs = droneInfo[1]
                    else:
                        droneIDs = droneInfo
                    targetID = sm.GetService('target').GetActiveTargetID()
                    requiredSafetyLevel = crimewatchSvc.GetRequiredSafetyLevelForEngagingDrones(droneIDs, targetID)
                    if crimewatchSvc.CheckUnsafe(requiredSafetyLevel):
                        if requiredSafetyLevel == const.shipSafetyLevelNone:
                            color = crimewatchConst.Colors.Criminal.GetRGBA()
                        else:
                            color = crimewatchConst.Colors.Suspect.GetRGBA()
                        self.sr.fill.SetRGBA(*color[:3])
            self.sr.fill.state = uiconst.UI_DISABLED
            self.sr.fill.opacity = 0.25
            uicore.animations.MorphScalar(self.icon, 'glowAmount', self.icon.glowAmount, 1.0, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        if self.sr.Get('fill', None):
            self.sr.fill.SetRGBA(1, 1, 1, 1)
            self.sr.fill.state = uiconst.UI_HIDDEN
            uicore.animations.MorphScalar(self.icon, 'glowAmount', self.icon.glowAmount, 0.0, duration=uiconst.TIME_ENTRY)

    def OnMouseDown(self, *args):
        if self.sr.Get('fill', None):
            self.sr.fill.opacity = 0.5
            uicore.animations.MorphScalar(self.icon, 'glowAmount', self.icon.glowAmount, 1.3, duration=uiconst.TIME_ENTRY)

    def OnMouseUp(self, *args):
        if self.sr.Get('fill', None):
            self.sr.fill.opacity = 0.25
            uicore.animations.MorphScalar(self.icon, 'glowAmount', self.icon.glowAmount, 1.0, duration=uiconst.TIME_ENTRY)

    def OnClick(self, *args):
        sm.StartService('ui').StopBlink(self)
        if self.destroyed:
            ClearMenuLayer()
            return
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        if self.actionID in CLOSE_MENU_ACTIONS and isinstance(self.action[1], list):
            uthread.new(self.action[1][0][1], self.action[1][0][2][0])
            ClearMenuLayer()
            return
        if isinstance(self.action[1], basestring):
            ShowQuickMessage(self.action[1])
        else:
            try:
                actionMenuLabel = self.action[0]
                labelPath = actionMenuLabel[0]
                if len(self.action) > 2 and self.action[2]:
                    funcArgs = self.action[2]
                    if CaptionIsInMultiFunctions(labelPath) and not isinstance(funcArgs[0], (types.MethodType, types.FunctionType)):
                        funcArgs = (funcArgs,)
                else:
                    funcArgs = ()
                apply(self.action[1], funcArgs)
            except Exception as e:
                log.LogError(e, 'Failed executing action:', self.action)
                log.LogException()
                sys.exc_clear()

        ClearMenuLayer()
