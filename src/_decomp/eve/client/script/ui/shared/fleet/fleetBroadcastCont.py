#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetBroadcastCont.py
import math
import evefleet
import localization
from carbonui import const as uiconst, TextColor
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.window.segment.underlay import WindowSegmentUnderlay
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.shared.fleet import fleetBroadcastConst, fleetbroadcastexports
from eve.client.script.ui.shared.fleet.fleetBroadcastConst import broadcastButtonIDs
from eve.client.script.ui.shared.fleet.fleetConst import FLEET_BROADCASTS_VISIBLE_SETTING
from eve.client.script.ui.shared.pointerTool import pointerToolConst as pConst
from eve.common.script.sys.idCheckers import IsUniverseCelestial
ICONS_BY_SCOPE = {evefleet.BROADCAST_DOWN: 'res:/UI/Texture/Icons/73_16_28.png',
 evefleet.BROADCAST_UP: 'res:/UI/Texture/Icons/73_16_27.png',
 evefleet.BROADCAST_ALL: 'res:/UI/Texture/Icons/73_16_29.png'}
uniqueUINameByBroadcastID = {evefleet.BROADCAST_HEAL_ARMOR: pConst.UNIQUE_NAME_BROADCAST_ARMOR,
 evefleet.BROADCAST_HEAL_SHIELD: pConst.UNIQUE_NAME_BROADCAST_SHIELD}
ICONSIZE_SMALL = 16
ICONSIZE_LARGE = 32
THRESHOLD_WIDTH = 330

class FleetBroadcastCont(ContainerAutoSize):
    __notifyevents__ = ['OnFleetBroadcast_Local', 'OnBroadcastScopeChange']

    def ApplyAttributes(self, attributes):
        super(FleetBroadcastCont, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        innerPadding = attributes.innerPadding
        self.lastBroadcast = None
        self.iconSize = None
        WindowSegmentUnderlay(name='bgFill', bgParent=self)
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self, align=uiconst.TOTOP)
        self.lastBroadcastCont = Container(name='lastBroadcastCont', parent=self.mainCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=18)
        self.buttonCont = Container(name='broadcastButtonCont', parent=self.mainCont, align=uiconst.TOTOP, padTop=4, uniqueUiName=pConst.UNIQUE_NAME_FLEET_BROADCAST_ICONS)
        self.toggleButton = ButtonIcon(name='broadcastExpanderIcon', parent=self.lastBroadcastCont, align=uiconst.CENTERRIGHT, pos=(0, 0, 16, 16), iconSize=7, texturePath='res:/UI/Texture/classes/Neocom/arrowUp.png', func=self.ToggleBroadcasts, uniqueUiName=pConst.UNIQUE_NAME_FLEET_SHOW_BROADCASTS)
        self.ConstructLastBroadcastBanner()
        self.UpdateBroadcastButtonState()
        self.SetInnerPadding(innerPadding)

    def ReconstructBroadcastButtons(self):
        self.buttonCont.Flush()
        self.buttonCont.height = self.iconSize
        self.scopeBtn = ButtonIcon(parent=self.buttonCont, align=uiconst.CENTERRIGHT, pos=(0, 0, 16, 16), iconSize=16, uniqueUiName=pConst.UNIQUE_NAME_FLEET_BROADCAST_SCOPE, func=self.CycleBroadcastScope)
        self.UpdateScopeButton()
        for i, broadcastID in enumerate(broadcastButtonIDs):
            self.ConstructBroadcastButton(broadcastID, i)

    def _GetButtonIconSize(self, width):
        if width > THRESHOLD_WIDTH:
            return ICONSIZE_LARGE
        else:
            return ICONSIZE_SMALL

    def ConstructBroadcastButton(self, broadcastID, i):
        BroadcastButton(parent=self.buttonCont, align=uiconst.TOLEFT, padRight=4 if self.iconSize == ICONSIZE_LARGE else 8, width=self.iconSize, iconSize=self.iconSize, height=0, hint=fleetbroadcastexports.GetBroadcastName(broadcastID), broadcastID=broadcastID, texturePath=self._GetBroadcastIcon(broadcastID), func=lambda *args: sm.GetService('fleet').SendBroadcast(broadcastID), uniqueUiName=uniqueUINameByBroadcastID.get(broadcastID, None))

    def _GetBroadcastIcon(self, broadcastID):
        if self.iconSize == ICONSIZE_SMALL:
            return fleetBroadcastConst.iconsByBroadcastType[broadcastID]
        else:
            return fleetBroadcastConst.iconsLargeByBroadcastType[broadcastID]

    def ToggleBroadcasts(self, *args):
        FLEET_BROADCASTS_VISIBLE_SETTING.toggle()
        self.UpdateBroadcastButtonState()

    def UpdateBroadcastButtonState(self):
        if FLEET_BROADCASTS_VISIBLE_SETTING.is_enabled():
            self.buttonCont.Hide()
            self.toggleButton.SetRotation(0)
        else:
            self.buttonCont.Show()
            self.toggleButton.SetRotation(math.pi)

    def SetInnerPadding(self, padding):
        self.mainCont.padding = padding

    def ConstructLastBroadcastBanner(self):
        lastBroadcastBanner = Container(name='lastBroadcastBanner', parent=self.lastBroadcastCont, state=uiconst.UI_NORMAL)
        lastBroadcastBanner.GetMenu = self.GetLastBroadcastMenu
        lastBroadcastBanner.OnClick = self.OnLastBroadcastClick
        lastBroadcastBanner.GetHint = self.GetLastBroadcastHint
        self.bannerIcon = eveIcon.Sprite(name='bannerIcon', parent=lastBroadcastBanner, align=uiconst.CENTERLEFT, pos=(4, 0, 16, 16), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Icons/44_32_29.png', color=TextColor.NORMAL)
        self.bannerLabel = eveLabel.EveLabelMedium(name='bannerLabel', text=localization.GetByLabel('UI/Fleet/FleetBroadcast/NoBroadcasts'), parent=lastBroadcastBanner, align=uiconst.CENTERLEFT, left=26, autoFadeSides=32)

    def GetLastBroadcastHint(self):
        if not self.lastBroadcast:
            return None
        member = sm.GetService('fleet').GetMemberInfo(int(self.lastBroadcast.charID))
        if member:
            rank_name = fleetbroadcastexports.GetRankName(member)
        else:
            rank_name = localization.GetByLabel('UI/Fleet/Ranks/FleetMember')
        scope_name = fleetbroadcastexports.GetBroadcastScopeName(self.lastBroadcast.scope, self.lastBroadcast.where)
        return localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastNotificationHint', eventLabel=self.lastBroadcast.broadcastLabel, time=self.lastBroadcast.time, charID=self.lastBroadcast.charID, range=scope_name, role=rank_name)

    def CycleBroadcastScope(self, *args):
        sm.GetService('fleet').CycleBroadcastScope()

    def GetLastBroadcastMenu(self):
        if not self.lastBroadcast:
            return
        m = []
        func = fleetbroadcastexports.GetMenuFunc(self.lastBroadcast.name)
        if func:
            args = (self.lastBroadcast.charID, self.lastBroadcast.solarSystemID, self.lastBroadcast.itemID)
            if getattr(self.lastBroadcast, 'typeID', None):
                args += (self.lastBroadcast.typeID,)
            m = func(*args)
            m += [None]
        m += fleetbroadcastexports.GetMenu_Member(self.lastBroadcast.charID)
        m += [None]
        m += fleetbroadcastexports.GetMenu_Ignore(self.lastBroadcast.name)
        return m

    def UpdateScopeButton(self):
        scope = sm.GetService('fleet').broadcastScope
        self.scopeBtn.hint = localization.GetByLabel('UI/Fleet/FleetBroadcast/CycleBroadcastScope', scope=fleetbroadcastexports.GetBroadcastScopeName(scope))
        texturePath = ICONS_BY_SCOPE.get(scope, 'res:/UI/Texture/Icons/73_16_28.png')
        self.scopeBtn.icon.SetTexturePath(texturePath)

    def OnLastBroadcastClick(self):
        if not uicore.uilib.Key(uiconst.VK_CONTROL) or self.lastBroadcast.itemID == session.shipid or session.shipid is None or self.lastBroadcast.itemID is None or IsUniverseCelestial(self.lastBroadcast.itemID):
            return
        itemID = self.lastBroadcast.itemID
        if sm.GetService('target').IsInTargetingRange(itemID):
            sm.GetService('target').TryLockTarget(itemID)

    def OnFleetBroadcast_Local(self, broadcast):
        self.lastBroadcast = broadcast
        self.bannerLabel.text = self.lastBroadcast.broadcastLabel
        texturePath = fleetBroadcastConst.iconsByBroadcastType.get(self.lastBroadcast.name, 'res:/UI/Texture/Icons/44_32_29.png')
        self.bannerIcon.SetTexturePath(texturePath)
        animations.FadeTo(self.bannerIcon, 1.0, 0.0, duration=0.7, loops=3, curveType=uiconst.ANIM_WAVE)

    def OnBroadcastScopeChange(self):
        self.UpdateScopeButton()

    def _OnSizeChange_NoBlock(self, width, height):
        oldIconSize = self.iconSize
        self.iconSize = self._GetButtonIconSize(width)
        if self.iconSize != oldIconSize:
            self.ReconstructBroadcastButtons()


class BroadcastButton(ButtonIcon):

    def ApplyAttributes(self, attributes):
        super(BroadcastButton, self).ApplyAttributes(attributes)
        self.broadcastID = attributes.broadcastID

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if not self.broadcastID:
            return
        cmdName = 'CmdFleetBroadcast_%s' % self.broadcastID
        cmd = uicore.cmd.commandMap.GetCommandByName(cmdName)
        shortcutStr = cmd.GetShortcutAsString()
        tooltipPanel.LoadGeneric3ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=self.hint, cellPadding=(0, 0, 7, 0), colSpan=tooltipPanel.columns - 1, width=200, autoFitToText=True)
        if shortcutStr:
            tooltipPanel.AddShortcutCell(shortcutStr)
        else:
            tooltipPanel.AddCell()
