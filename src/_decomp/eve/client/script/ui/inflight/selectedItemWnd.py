#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\selectedItemWnd.py
from collections import OrderedDict
import blue
import telemetry
import eveformat.client
import eveicon
import evetypes
import localization
import structures
import uthread
import uthread2
import utillib
from brennivin import itertoolsext
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.uiconst import PickState
from eve.common.script.sys.idCheckers import IsSkyhook
from eveservices.xmppchat import GetChatService
from localization import GetByLabel
import orbitalSkyhook.const as skyhookConst
from shipcaster.shipcasterUtil import GetShipcasterText
from carbon.common.script.util.format import FmtDate, FmtDist
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import TextColor, uiconst, Align
from carbonui.control.contextMenu import menuDataFactory
from carbonui.control.contextMenu.menuConst import DISABLED_ENTRY0
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.dragdrop.dragdata import ShipDragData
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.window.header.small import SmallWindowHeader
from carbonui.window.segment.underlay import WindowSegmentUnderlay
from carbonui.window.widget import WidgetWindow
from eve.client.script.parklife import states as state
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.inflight import actionPanelDefaults, selectedItemConst, actionConst
from eve.client.script.ui.inflight.actionConst import CMD_BY_ACTIONID
from eve.client.script.ui.inflight.selectedItemButton import SelectedItemButton
from eve.client.script.ui.inflight.selectedItemConst import ACTIONS_ALWAYS_VISIBLE, ACTIONS_BY_CATEGORYID, ACTIONS_BY_GROUPID, ACTIONS_BY_TYPEID, SUB_MENU_ACTIONS, TOGGLE_ACTIONS
from eve.client.script.ui.shared import killRights
from eve.client.script.ui.shared.pointerTool import pointerToolConst
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eve.common.script.util import eveFormat
from eveservices.menu import GetMenuService, StartMenuService
from menu import MenuLabel
from npcs.client.components.entity_bounty import get_entity_bounty
from spacecomponents.client.components import cargobay
from spacecomponents.common.helper import HasCargoBayComponent, HasShipcasterComponent, HasUnderConstructionComponent, HasTowGameObjectiveComponent, HasFilamentSpoolupComponent
from spacecomponents.common.helper import HasItemTrader
from uihider import UiHiderMixin
ITEM_ICON_SIZE_LARGE = 64
ITEM_ICON_SIZE_SMALL = 32
BUTTON_SIZE_LARGE = 32
BUTTON_SIZE_SMALL = 16
HEIGHTSTATE_SMALL = 1
HEIGHTSTATE_MEDIUM = 2
HEIGHTSTATE_LARGE = 3

class CharIcon(Container):
    isDragObject = True

    def ApplyAttributes(self, attributes):
        super(CharIcon, self).ApplyAttributes(attributes)
        self.typeID = None
        self.itemID = None
        self.chatIcon = ButtonIcon(name='chatIcon', parent=self, align=Align.BOTTOMRIGHT, texturePath=eveicon.chat_bubble, pos=(0, 0, 16, 16), iconSize=16, func=self.OnChatButton, hint=GetByLabel('UI/Chat/StartConversation'))
        self.icon = eveIcon.Icon(name='iconSprite', align=Align.TOALL, pickState=PickState.OFF, parent=self)

    def OnChatButton(self, *args):
        GetChatService().Invite(self.itemID)

    def SetID(self, typeID, itemID):
        self.typeID = typeID
        self.itemID = itemID
        self.icon.LoadIconByTypeID(typeID, itemID=itemID, ignoreSize=True)

    def GetMenu(self):
        return sm.GetService('menu').GetMenuForOwner(self.itemID)

    def GetDragData(self, *args):
        charID = self.itemID
        if not charID:
            return []
        fakeNode = utillib.KeyVal()
        fakeNode.charID = charID
        fakeNode.typeID = self.typeID
        fakeNode.itemID = charID
        fakeNode.info = cfg.eveowners.Get(charID)
        fakeNode.__guid__ = 'listentry.User'
        return [fakeNode]

    def OnClick(self, *args):
        sm.GetService('info').ShowInfo(self.typeID, self.itemID)


class SelectedItemWnd(UiHiderMixin, WidgetWindow):
    uniqueUiName = pointerToolConst.UNIQUE_NAME_SELECTED_ITEM_VIEW
    __notifyevents__ = ['ProcessSessionChange',
     'OnStateChange',
     'DoBallRemove',
     'OnDistSettingsChange',
     'OnPlanetViewChanged',
     'DoBallsRemove',
     'OnActiveTrackingChange']
    default_minSize = (256, 0)
    default_windowID = 'selecteditemview'
    default_open = True
    default_isKillable = False
    default_captionLabelPath = 'UI/Inflight/ActiveItem/SelectedItem'
    default_scope = uiconst.SCOPE_INFLIGHT
    default_apply_content_padding = False

    @staticmethod
    def default_left(*args):
        return actionPanelDefaults.GetActiveItemLeft()

    @staticmethod
    def default_top(*args):
        return actionPanelDefaults.GetActiveItemTop()

    @staticmethod
    def default_width():
        return actionPanelDefaults.GetActiveItemWidth()

    @staticmethod
    def default_height():
        return actionPanelDefaults.GetActiveItemHeight()

    def ApplyAttributes(self, attributes):
        super(SelectedItemWnd, self).ApplyAttributes(attributes)
        panelname = attributes.panelname
        self.inited = False
        self.canAnchorToOthers = 0
        self.lastActionSerial = None
        self.lastSessionChange = None
        self.lastIcon = None
        self.lastBountyCheck = None
        self.bountyText = None
        self.buttonCont = None
        self.updateAutoTimer = None
        self.itemID = None
        self.panelname = panelname
        self.lastActionDist = None
        self.lastCloakingStatus = False
        self.noContentHint = None
        self.bountySvc = sm.GetService('bountySvc')
        self._last_button_size = None
        self._update_extend_content_into_header()
        self.ConstructLayout()
        stateSvc = sm.GetServiceIfRunning('stateSvc')
        if stateSvc:
            self.itemID = stateSvc.GetExclState(state.selected)
        self.topCont._OnSizeChange_NoBlock = self._on_top_cont_size_changed
        self.on_compact_mode_changed.connect(self._on_compact_mode_changed)
        self.on_content_padding_changed.connect(self._on_content_padding_changed)
        self.on_header_inset_changed.connect(self._on_window_header_inset_changed)
        self.on_end_scale.connect(self._on_end_scale)
        self.inited = True
        uthread2.start_tasklet(self.UpdateAll)

    def _UpdateMinSize(self):
        _, text_height = eveLabel.EveLabelMedium.MeasureTextSize('A')
        top_height = text_height + self.topCont.padTop + self.topCont.padBottom
        _, bottom_height = self.bottomCont.GetAbsoluteSize()
        content_height = top_height + bottom_height
        _, height_min = self.GetWindowSizeForContentSize(height=content_height)
        if self.compact:
            width_min = 200
        else:
            width_min = self.default_minSize[0]
        self.SetMinSize((width_min, height_min))

    def ConstructLayout(self):
        self._ConstructButtonCont()
        self.topCont = Container(name='topCont', parent=self.content, align=uiconst.TOALL, clipChildren=True)
        self._ConstructIconsAndLabel()
        self._update_padding_of_content()

    def _on_top_cont_size_changed(self, *args, **kwargs):
        self.ReconstructItemIcons()
        self.UpdateAll()

    def _on_end_scale(self, window):
        self._UpdateMinSize()

    def _ConstructIconsAndLabel(self):
        self.killRightsUtilMenuCont = Container(name='utilMenuCont', align=uiconst.TORIGHT, parent=self.topCont, width=16, state=uiconst.UI_HIDDEN, padLeft=4)
        self.killRightsUtilMenu = killRights.KillRightsUtilMenu(menuAlign=uiconst.TOPRIGHT, parent=self.killRightsUtilMenuCont, width=16, height=16, align=uiconst.TOPRIGHT)
        self.iconCont = ContainerAutoSize(name='iconCont', parent=self.topCont, align=uiconst.TOLEFT, padTop=2, padRight=8)
        self.ReconstructItemIcons()
        labelCont = ScrollContainer(name='labelCont', parent=self.topCont, state=uiconst.UI_PICKCHILDREN)
        labelCont.mainCont.state = uiconst.UI_PICKCHILDREN
        self.mainLabel = eveLabel.EveLabelMedium(parent=labelCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, color=TextColor.HIGHLIGHT)

    def _OnResize(self, *args, **kw):
        self._UpdateButtonSize()
        super(SelectedItemWnd, self)._OnResize(*args, **kw)

    def _UpdateIconContVisibility(self):
        self.iconCont.SetSizeAutomatically()
        heightState = self.GetHeightState()
        if heightState == HEIGHTSTATE_SMALL:
            self.iconCont.Hide()
        else:
            self.iconCont.Show()
            iconSize = ITEM_ICON_SIZE_LARGE if heightState == HEIGHTSTATE_LARGE else ITEM_ICON_SIZE_SMALL
            self.iconSprite.SetSize(iconSize, iconSize)
            self.charIcon.SetSize(iconSize, iconSize)
            self.charIcon.left = iconSize + 4

    def GetHeightState(self):
        _, h = self.topCont.GetAbsoluteSize()
        if h > ITEM_ICON_SIZE_LARGE:
            return HEIGHTSTATE_LARGE
        elif h > ITEM_ICON_SIZE_SMALL:
            return HEIGHTSTATE_MEDIUM
        else:
            return HEIGHTSTATE_SMALL

    def _UpdateButtonSize(self):
        iconSize = self.GetButtonSize()
        buttonSize = iconSize
        if iconSize == BUTTON_SIZE_SMALL:
            buttonSize += 4
        self.buttonCont.height = buttonSize
        for button in self.buttonCont.children:
            self._ApplyButtonSize(button, iconSize, buttonSize)

        if self._last_button_size is None or buttonSize != self._last_button_size:
            self._last_button_size = buttonSize
            self._UpdateMinSize()

    def _ApplyButtonSize(self, button, iconSize, buttonSize):
        button.width = buttonSize
        button.SetIconSize(iconSize)
        button.SetTexturePath(actionConst.ICON_BY_ACTIONID[button.GetActionID()].resolve(iconSize))

    def GetButtonSize(self):
        width, _ = self.GetCurrentAbsoluteSize()
        if width > 300:
            return BUTTON_SIZE_LARGE
        else:
            return BUTTON_SIZE_SMALL

    def _ConstructButtonCont(self):
        self.bottomCont = ContainerAutoSize(name='bottomCont', parent=self.content, align=uiconst.TOBOTTOM)
        self.buttonCont = Container(name='buttonCont', parent=self.bottomCont, align=uiconst.TOTOP, clipChildren=True)
        self.buttonCont.isTabStop = 1
        self.bottomContUnderlay = WindowSegmentUnderlay(bgParent=self.bottomCont)

    def ReconstructItemIcons(self):
        self.lastIcon = None
        self.iconCont.Flush()
        self.iconSprite = eveIcon.Icon(name='iconSprite', align=uiconst.TOPLEFT, parent=self.iconCont, state=uiconst.UI_HIDDEN)
        self.iconSprite.OnClick = (self.ShowInfo, self.iconSprite)
        self.iconSprite.GetMenu = (self.GetIconMenu, self.iconSprite)
        self.iconSprite.GetDragData = self.GetShipDragData
        self.charIcon = CharIcon(name='charIconSprite', align=uiconst.TOPLEFT, parent=self.iconCont, state=uiconst.UI_HIDDEN)
        self._UpdateIconContVisibility()

    def _on_compact_mode_changed(self, window):
        self.header.show_caption = not self.compact
        self._update_extend_content_into_header()
        self._UpdateMinSize()

    def _on_window_header_inset_changed(self, window):
        self._update_padding_of_content()

    def _on_content_padding_changed(self, window):
        self._update_padding_of_content()

    def _update_extend_content_into_header(self):
        self.extend_content_into_header = self.compact

    def _update_padding_of_content(self):
        pad_left, pad_top, pad_right, pad_bottom = self.content_padding
        _, inset_right = self.header_inset
        self.topCont.padding = (pad_left,
         pad_top,
         inset_right if self.compact else pad_right,
         0)
        self.buttonCont.padding = (pad_left,
         pad_bottom,
         pad_right,
         pad_bottom)

    def Prepare_Header_(self):
        self._SetHeader(SmallWindowHeader(show_caption=not self.compact))

    def OnActiveTrackingChange(self, isActivelyTracking):
        self.AdjustUIToActiveTrackingStatus(isActivelyTracking)

    def AdjustUIToActiveTrackingStatus(self, isTracking):
        caption = localization.GetByLabel('UI/Inflight/ActiveItem/SelectedItem')
        if isTracking:
            caption += ' - ' + localization.GetByLabel('UI/Inflight/ActiveItem/Tracking')
        self.SetCaption(caption)

    def _OnClose(self, *args):
        self.updateAutoTimer = None

    def ProcessSessionChange(self, isRemote, session, change):
        self.lastActionSerial = None
        self.lastActionDist = None
        self.lastCloakingStatus = None
        self.lastSessionChange = blue.os.GetWallclockTime()

    def OnItemIDSelected(self, itemID):
        self.itemID = itemID
        self.lastActionSerial = None
        self.lastActionDist = None
        self.lastBountyCheck = None
        self.bountyText = None
        uthread2.start_tasklet(self.UpdateAll, True)

    def OnStateChange(self, itemID, flag, true, *args):
        if itemID != session.shipid and not self.destroyed:
            uthread.new(self._OnStateChange, itemID, flag, true)

    @telemetry.ZONE_METHOD
    def _OnStateChange(self, itemID, flag, true):
        if flag == state.selected and true:
            self.OnItemIDSelected(itemID)
        if itemID == self.itemID and flag not in (state.selected, state.mouseOver):
            self.lastActionSerial = None
            self.lastActionDist = None
            self.UpdateAll()

    def OnDistSettingsChange(self):
        uthread.new(self._OnDistSettingsChange)

    @telemetry.ZONE_METHOD
    def _OnDistSettingsChange(self):
        self.ResetLastActionAndCloakingAndUpdateAll()

    def ResetLastActionAndCloakingAndUpdateAll(self):
        self.lastActionSerial = None
        self.lastCloakingStatus = None
        self.UpdateAll(True)

    def TryGetInvItem(self, itemID):
        if session.shipid is None:
            return
        ship = sm.GetService('invCache').GetInventoryFromId(session.shipid)
        if ship:
            for invItem in ship.List():
                if invItem.itemID == itemID:
                    return invItem

    def OnExpanded(self, *args):
        if not self.inited:
            return
        super(SelectedItemWnd, self).OnExpanded(*args)
        self.ResetLastActionAndCloakingAndUpdateAll()

    def OnEndMaximize_(self, *args):
        if not self.inited:
            return
        self.ResetLastActionAndCloakingAndUpdateAll()

    def FadeInSelf(self):
        self.opacity = 0.001
        super(SelectedItemWnd, self).FadeInSelf()
        if not self.inited:
            return
        self.ResetLastActionAndCloakingAndUpdateAll()

    def SetNoContentHint(self, hint = None):
        if self.noContentHint is None and hint:
            self.noContentHint = eveLabel.EveCaptionMedium(text=hint, parent=self.sr.main, align=uiconst.RELATIVE, left=16, top=18, width=256, color=TextColor.SECONDARY)
        elif self.noContentHint:
            if hint:
                self.noContentHint.text = hint
                self.noContentHint.state = uiconst.UI_DISABLED
            else:
                self.noContentHint.state = uiconst.UI_HIDDEN

    def FlushContent(self):
        self.mainLabel.text = ''
        self.SetNoContentHint(localization.GetByLabel('UI/Inflight/ActiveItem/NoObjectSelected'))
        self.buttonCont.Flush()
        self.iconSprite.state = uiconst.UI_HIDDEN
        self.charIcon.state = uiconst.UI_HIDDEN

    @telemetry.ZONE_METHOD
    def UpdateAll(self, reconstructButtons = False):
        if self.destroyed:
            return
        if self.itemID == session.shipid:
            self.itemID = None
        bp = sm.GetService('michelle').GetBallpark()
        if self.IsWindowVisible() and bp and self.itemID:
            slimItem = uix.GetBallparkRecord(self.itemID)
            if slimItem:
                ball = bp.GetBall(self.itemID)
                if ball:
                    self._UpdateSlimItem(slimItem, reconstructButtons)
                    return
            invItem = self.TryGetInvItem(self.itemID)
            if invItem:
                self._UpdateInvItem(invItem, reconstructButtons)
                return
        self.lastActionSerial = None
        self.lastActionDist = None
        self.FlushContent()

    def _UpdateSlimItem(self, slimItem, reconstructButtons):
        self.mainLabel.text = self._GetSlimItemText(slimItem, density=self.GetHeightState())
        self.SetNoContentHint(None)
        self._CheckUpdateIcons(slimItem, slimItem.typeID)
        self.UpdateKillRightsIconVisibility(slimItem)
        if reconstructButtons or self._CheckDistanceChanged() or self._RequiresRegularUpdates(slimItem):
            actions = GetMenuService().UnmergedCelestialMenu(slimItem)
            self.ReconstructButtons(slimItem, None, actions)
        if not self.updateAutoTimer:
            self.updateAutoTimer = AutoTimer(500, self.UpdateAll)

    def _GetSlimItemText(self, slimItem, density):
        text = uix.GetSlimItemName(slimItem)
        jumpExtraText = self._GetJumpExtraText(slimItem)
        if jumpExtraText:
            text += jumpExtraText
        distanceText = self._GetDistanceText()
        securityText = self._GetSecurityStatusTex(slimItem)
        if density == HEIGHTSTATE_LARGE:
            if distanceText:
                text += '<br>%s' % distanceText
            if securityText:
                text += '<br>%s' % securityText
        else:
            if distanceText:
                text = '%s - %s' % (text, distanceText)
            if securityText:
                text += ' (%s)' % securityText
        if self._HasStructureTimer(slimItem):
            structureTimerText = self._GetStructureTimerText(slimItem)
            text += '<br>' + structureTimerText
        if self._HasSkyhookTimer(slimItem):
            skyhookTimerText = self._GetSkyhookTimerText(slimItem)
            text += '<br>' + skyhookTimerText
        bountyText = self.GetBountyText(slimItem)
        if bountyText:
            if density == HEIGHTSTATE_SMALL:
                text += ' (%s)' % bountyText
            else:
                text += '<br>' + bountyText
        return text

    def _UpdateInvItem(self, invItem, reconstructButtons):
        self._CheckUpdateIcons(None, invItem.typeID)
        self.UpdateKillRightsIconVisibility()
        text = uix.GetItemName(invItem)
        bountyText = self.GetBountyText()
        text += bountyText
        self.mainLabel.text = text
        self.SetNoContentHint(None)
        self.UpdateKillRightsIconVisibility()
        if reconstructButtons:
            data = [(invItem, 0, None)]
            actions = StartMenuService().InvItemMenu(data)
            self.ReconstructButtons(None, invItem, actions)

    def _CheckDistanceChanged(self):
        bp = sm.GetService('michelle').GetBallpark()
        ball = bp.GetBall(self.itemID)
        distanceToItem = getattr(ball, 'surfaceDist', None)
        reconstructButtons = False
        if distanceToItem is not None:
            myBallMode = None
            myball = bp.GetBall(session.shipid)
            if myball:
                myBallMode = myball.mode
                if self.lastCloakingStatus is None or self.lastCloakingStatus != myball.isCloaked:
                    reconstructButtons = True
                self.lastCloakingStatus = myball.isCloaked
            if not self.lastActionDist or myBallMode != self.lastActionDist[1] or self.CheckDistanceUpdate(self.lastActionDist[0], distanceToItem):
                self.lastActionDist = (distanceToItem, myBallMode)
                reconstructButtons = True
        return reconstructButtons

    def _GetDistanceText(self):
        bp = sm.GetService('michelle').GetBallpark()
        ball = bp.GetBall(self.itemID)
        distanceToItem = getattr(ball, 'surfaceDist', None)
        if distanceToItem is not None:
            return FmtDist(distanceToItem, maxdemicals=1)

    def _GetSecurityStatusTex(self, slimItem):
        securityStatusText = ''
        sec = slimItem.securityStatus
        if sec:
            securityStatusText = localization.GetByLabel('UI/Inflight/ActiveItem/SelectedItemSecurity', secStatus=sec)
        return securityStatusText

    def _GetJumpExtraText(self, slimItem):
        if slimItem.groupID == const.groupStargate:
            return self._GetStargateSecurityText(slimItem)
        if HasShipcasterComponent(slimItem.typeID):
            shipcasterText = GetShipcasterText(slimItem)
            if shipcasterText:
                return '<br>%s' % shipcasterText
            return ''
        return ''

    def _GetStargateSecurityText(self, slimItem):
        return u' ({security_status})'.format(security_status=eveformat.solar_system_security_status(slimItem.jumps[0].locationID))

    def GetBountyText(self, slimItem = None):
        bountyItemID = None
        bountyTypeID = None
        bountySlim = None
        if slimItem:
            if slimItem.categoryID == const.categoryEntity:
                bountyTypeID = slimItem.typeID
                bountySlim = slimItem
            elif slimItem.charID:
                bountyItemID = slimItem.charID
                bountySlim = slimItem
        if (bountyItemID, bountyTypeID) != self.lastBountyCheck:
            bounty = self._GetBountyAmount(bountyTypeID, bountySlim)
            if bounty:
                self.bountyText = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bounty, 0))
            else:
                self.bountyText = None
            self.lastBountyCheck = (bountyItemID, bountyTypeID)
        bountyText = ''
        if self.bountyText:
            bountyText += self.bountyText
        return bountyText

    def UpdateKillRightsIconVisibility(self, slimItem = None):
        displayUtilMenu = False
        if slimItem:
            killRightID, price = self.bountySvc.GetBestKillRight(slimItem.charID)
            self.killRightsUtilMenu.UpdateKillRightInfo(killRightID, price, slimItem.charID, slimItem.itemID)
            stateSvc = sm.GetService('stateSvc')
            if killRightID is not None and not (stateSvc.CheckSuspect(slimItem) or stateSvc.CheckCriminal(slimItem)) and slimItem.categoryID != const.categoryStructure:
                displayUtilMenu = True
        self.killRightsUtilMenuCont.display = displayUtilMenu

    def _CheckUpdateIcons(self, slimItem, typeID):
        charID = None
        categoryID = None
        if slimItem:
            if slimItem.categoryID == const.categoryShip:
                if idCheckers.IsCharacter(slimItem.charID):
                    charID = slimItem.charID
                    categoryID = slimItem.categoryID
        if self.lastIcon != (typeID, self.itemID, charID):
            uthread2.start_tasklet(self.UpdateIcons, typeID, charID)
            self.lastIcon = (typeID, self.itemID, charID)
        else:
            self.iconSprite.state = uiconst.UI_NORMAL
            if categoryID == const.categoryShip and charID:
                self.charIcon.state = uiconst.UI_NORMAL

    def _RequiresRegularUpdates(self, slimItem):
        if self._HasStructureTimer(slimItem) or self._HasSkyhookTimer(slimItem):
            return True
        if HasShipcasterComponent(slimItem.typeID):
            return True
        if HasTowGameObjectiveComponent(slimItem.typeID):
            return True
        if HasFilamentSpoolupComponent(slimItem.typeID):
            return True
        return False

    def _HasStructureTimer(self, slimItem):
        if slimItem.categoryID != const.categoryStructure:
            return False
        return self._HasReinforceTimer(slimItem.timer, slimItem.state, structures.STATE_VULNERABILITY)

    def _HasSkyhookTimer(self, slimItem):
        if not IsSkyhook(slimItem.typeID):
            return False
        return self._HasReinforceTimer(slimItem.skyhook_timer, slimItem.skyhook_state, skyhookConst.STATE_VULNERABILITY)

    def _HasReinforceTimer(self, timer, structureState, vulnerableStates):
        isVulnerable = vulnerableStates.get(structureState, None)
        if isVulnerable is not False:
            return False
        if not timer:
            return False
        return True

    def _GetStructureTimerText(self, slimItem):
        return self._GetReinforceStructureTimerText(slimItem.timer, slimItem.state, structures.STATE_LABELS)

    def _GetSkyhookTimerText(self, slimItem):
        return self._GetReinforceStructureTimerText(slimItem.skyhook_timer, slimItem.skyhook_state, skyhookConst.STATE_LABELS)

    def _GetReinforceStructureTimerText(self, timer, structureState, labelDict):
        start, end, paused = timer
        if paused:
            end = end + blue.os.GetWallclockTime() - paused
        stateText = localization.GetByLabel(labelDict[structureState])
        return localization.GetByLabel('UI/Inflight/ActiveItem/InStateUntil', structureState=stateText, timestamp=FmtDate(end))

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if self.IsWindowVisible() and ball and ball.id == self.itemID:
            uthread.pool('ActiveItem::UpdateAll', self.UpdateAll, True)

    def UpdateIcons(self, typeID, charID):
        self.iconSprite.LoadIconByTypeID(typeID, itemID=self.itemID, ignoreSize=True)
        self.iconSprite.typeID = typeID
        self.iconSprite.itemID = self.itemID
        categoryID = evetypes.GetCategoryID(typeID)
        self.iconSprite.categoryID = categoryID
        self.iconSprite.state = uiconst.UI_NORMAL
        if categoryID == const.categoryShip and charID:
            typeID = cfg.eveowners.Get(charID).typeID
            self.charIcon.SetID(typeID, charID)
            self.charIcon.state = uiconst.UI_NORMAL
        else:
            self.charIcon.state = uiconst.UI_HIDDEN

    def GetShipDragData(self):
        categoryID = self.iconSprite.categoryID
        if categoryID != const.categoryShip:
            return []
        return ShipDragData(self.iconSprite.typeID, self.iconSprite.itemID, self.charIcon.itemID)

    def _GetBountyAmount(self, bountyTypeID, slimItem):
        bounty = None
        if bountyTypeID:
            bounty = get_entity_bounty(bountyTypeID, slimItem.itemID)
        elif slimItem:
            if self.bountySvc.CanHaveBounty(slimItem):
                bounty = self.bountySvc.GetBounty(slimItem.charID, slimItem.corpID, slimItem.allianceID)
        return bounty

    def GetNpcBounty(self, bountyAmount):
        return (bountyAmount, None, None)

    def ShowInfo(self, btn, *args):
        if btn and btn.typeID:
            sm.GetService('info').ShowInfo(btn.typeID, btn.itemID)

    def GetIconMenu(self, btn, *args):
        if btn and btn.typeID:
            return GetMenuService().GetMenuFromItemIDTypeID(getattr(btn, 'itemID', None), btn.typeID)

    def CheckDistanceUpdate(self, lastdist, dist):
        diff = abs(lastdist - dist)
        if not diff:
            return False
        elif dist:
            return bool(diff / dist > 0.01)
        else:
            return bool(lastdist != dist)

    def IsWindowVisible(self):
        return bool(not self.IsCollapsed() and not self.IsMinimized() and self.opacity > 0 and self.display)

    @telemetry.ZONE_METHOD
    def ReconstructButtons(self, slimItem, invItem, actions):
        if self.destroyed:
            return
        if not self.IsWindowVisible():
            self.updateAutoTimer = None
            return
        menuData = menuDataFactory.CreateMenuDataFromRawTuples(actions)
        if menuData is None:
            menuData = MenuData()
        actionNamesSerial, validActionsByName = self._GetValidActionsByName(menuData)
        if actionNamesSerial == self.lastActionSerial:
            return
        self.buttonCont.Flush()
        visibleActionNames = self._GetVisibleActionNamesOrdered(invItem, slimItem, validActionsByName)
        reasonsWhyNotAvailable = getattr(actions, 'reasonsWhyNotAvailable', {})
        for actionName in visibleActionNames:
            if actionName is None:
                continue
            menuEntryData = self._GetMenuEntryData(actionName, validActionsByName)
            disabledHint = None
            if not menuEntryData:
                menuEntryData = MenuEntryData(text=self._GetDisabledMenuLabel(actionName))
                disabledHint = reasonsWhyNotAvailable.get(actionName, localization.GetByLabel('UI/Menusvc/MenuHints/NoReasonGiven'))
            self._ConstructButton(menuEntryData, disabledHint)

        self._UpdateButtonSize()
        self.lastActionSerial = actionNamesSerial

    def _GetDisabledMenuLabel(self, actionName):
        if actionName in ('UI/Inflight/WarpToWithinDistance', 'UI/Inflight/WarpToMoonMiningPoint'):
            return MenuLabel(actionName, {'distance': 0})
        elif actionName == 'UI/Inflight/JumpByShipcaster':
            return MenuLabel(actionName, {'text': localization.GetByLabel('UI/Inflight/Jump')})
        else:
            return MenuLabel(actionName)

    def _GetMenuEntryData(self, actionName, validActionsByName):
        menuEntryData = validActionsByName.get(actionName, None)
        if not menuEntryData and actionName in TOGGLE_ACTIONS:
            menuEntryData = validActionsByName.get(TOGGLE_ACTIONS[actionName], None)
        return menuEntryData

    def _GetNotAvailableHint(self, actionName, reasonsWhyNotAvailable, validActionsByName):
        if actionName not in validActionsByName:
            return reasonsWhyNotAvailable.get(actionName, localization.GetByLabel('UI/Menusvc/MenuHints/NoReasonGiven'))

    def _GetVisibleActionNamesOrdered(self, invItem = None, slimItem = None, validActionsByName = None):
        if slimItem:
            typeID = slimItem.typeID
            groupID = slimItem.groupID
            categoryID = slimItem.categoryID
        elif invItem:
            typeID = invItem.typeID
            groupID = invItem.groupID
            categoryID = invItem.categoryID
        else:
            typeID = None
            groupID = None
            categoryID = None
        actions = []
        if 'UI/Inflight/AlignTo' not in validActionsByName:
            approachLabelPath = 'UI/Inflight/ApproachObject'
        else:
            approachLabelPath = 'UI/Inflight/AlignTo'
        actions += [approachLabelPath, 'UI/Inflight/Submenus/WarpToWithin']
        if typeID and typeID in ACTIONS_BY_TYPEID:
            actions += ACTIONS_BY_TYPEID[typeID]
        elif groupID and groupID in ACTIONS_BY_GROUPID:
            actions += ACTIONS_BY_GROUPID[groupID]
        elif categoryID and categoryID in ACTIONS_BY_CATEGORYID:
            actions += ACTIONS_BY_CATEGORYID[categoryID]
        item = slimItem or invItem
        if item:
            if HasCargoBayComponent(typeID) and not HasItemTrader(typeID):
                if HasUnderConstructionComponent(typeID):
                    actions.append('UI/Inflight/SpaceComponents/UnderConstruction/Access')
                elif cargobay.IsAccessibleByCharacter(item, session.charid):
                    actions.append('UI/Commands/OpenCargo')
            if HasItemTrader(typeID):
                actions.append('UI/Inflight/SpaceComponents/ItemTrader/Access')
        actions = itertoolsext.remove_duplicates_and_preserve_order(actions)
        actions += ACTIONS_ALWAYS_VISIBLE
        return actions

    def _GetValidActionsByName(self, menuData):
        menuEntries = self.GetAllActionsFromMenus(menuData)
        actionNamesSerial = ''
        validActionsByName = {}
        for menuEntryData in menuEntries:
            labelPath = menuEntryData.GetLabelPath()
            if labelPath in selectedItemConst.ICON_ID_AND_CMD_BY_ACTIONID:
                validActionsByName[labelPath] = menuEntryData
                if labelPath:
                    actionNamesSerial += '%s_' % labelPath

        return (actionNamesSerial, validActionsByName)

    def _ConstructButton(self, menuEntryData, disabledHint):
        actionObject = selectedItemConst.ICON_ID_AND_CMD_BY_ACTIONID[menuEntryData.GetLabelPath()]
        SelectedItemButton(name=actionObject.uniqueUiName or menuEntryData.GetLabelPath(), parent=self.buttonCont, align=uiconst.TOLEFT, uniqueUiName=actionObject.uniqueUiName, menuEntryData=menuEntryData, func=menuEntryData.func, cmdName=CMD_BY_ACTIONID.get(menuEntryData.GetLabelPath(), ''), disabledHint=disabledHint, enabled=not bool(disabledHint), padRight=4)

    def GetAllActionsFromMenus(self, menuData):
        allActionsDict = OrderedDict()
        subMenuActions = []
        for menuEntryData in menuData.GetEntries():
            if not menuEntryData or not menuEntryData.IsEnabled():
                continue
            allActionsDict[menuEntryData.GetLabelPath()] = menuEntryData
            if menuEntryData.GetLabelPath() in SUB_MENU_ACTIONS:
                for eachSubOption in menuEntryData.GetSubMenuData() or []:
                    if eachSubOption is not None:
                        subMenuActions.append(eachSubOption)

        for menuEntryData in subMenuActions:
            if menuEntryData.GetLabelPath() not in allActionsDict:
                allActionsDict[menuEntryData.GetLabelPath()] = menuEntryData

        return allActionsDict.values()

    def _IsDisabledEntry(self, each):
        if isinstance(each, MenuEntryData):
            return not each.IsEnabled()
        else:
            return each[1] == DISABLED_ENTRY0

    def OnPlanetViewChanged(self, newPlanetID, oldPlanetID):
        for planetID in (newPlanetID, oldPlanetID):
            if planetID == self.itemID:
                self.OnItemIDSelected(self.itemID)

    def GetMenuMoreOptions(self):
        menu = super(SelectedItemWnd, self).GetMenuMoreOptions()
        menu += self.GetMenu()
        return menu

    def GetMenu(self, *args):
        menu = super(SelectedItemWnd, self).GetMenu(*args)
        menu.AddEntry(MenuLabel('UI/Generic/Copy'), self._CopyText)
        if self.charIcon.display:
            menu.AddSeparator()
            menu.AddEntry(MenuLabel('UI/Common/Pilot', {'character': self.charIcon.itemID}), subMenuData=lambda : self.charIcon.GetMenu(), texturePath=eveicon.person)
        return menu

    def _CopyText(self):
        text = self._GetTextCopyContent()
        text = eveformat.strip_tags(text, tags=['localized'])
        if text is not None:
            blue.pyos.SetClipboardData(text)

    def _GetTextCopyContent(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None or self.itemID is None:
            return
        slim_item = uix.GetBallparkRecord(self.itemID)
        if slim_item is None:
            return
        ball = ballpark.GetBall(self.itemID)
        if ball:
            text = self._GetSlimItemText(slim_item, density=HEIGHTSTATE_LARGE)
            return text.replace(u'<br>', '\n')
        item = self.TryGetInvItem(self.itemID)
        if item:
            return u'{name}\n{bounty}'.format(name=uix.GetItemName(item), bounty=self.GetBountyText())
