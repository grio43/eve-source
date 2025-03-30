#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\xmppchatuserentry2.py
import sys
import carbonui.const as uiconst
from carbon.common.script.util.commonutils import GetAttrs
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.shared.neocom.addressBook.contactsConst import COLOR_ONLINE, COLOR_OFFLINE
from eve.client.script.ui.shared.stateFlag import GetStateFlagFromData, AddAndSetFlagIcon, AddAndSetFlagIconFromData
from eve.client.script.ui.util.linkUtil import GetCharIDFromTextLink
from eve.common.script.sys import idCheckers
from eveservices.menu import GetMenuService
from eveservices.xmppchat import GetChatService
import evetypes
import localization
import telemetry
import uthread
import log
from carbonui.uicore import uicore
from xmppchatclient.xmppchannelmenu import XmppChannelMenu
ICON_ONLINESTATUS = 'res:/UI/Texture/Classes/Contacts/onlineIcon.png'
ICON_BLOCKED = 'res:/UI/Texture/Classes/Contacts/blockedWhite.png'
BUDDY_CONTAINER_PAD_LEFT = 3
BUDDY_CONTAINER_PAD_TOP = 1
STATUS_ICON_SIZE = 12
STATUS_ICON_PAD_LEFT = 2

class ChatUserEntryUnderlay(ListEntryUnderlay):
    default_padBottom = 0


class XmppChatUserEntry(SE_BaseClassCore):
    __guid__ = 'listentry.XmppChatUserEntry'
    __notifyevents__ = ['OnContactLoggedOn',
     'OnContactLoggedOff',
     'OnClientContactChange',
     'OnContactNoLongerContact',
     'OnStateSetupChange',
     'OnMyFleetInited',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'ProcessOnUIAllianceRelationshipChanged',
     'OnContactChange',
     'OnBlockContacts',
     'OnUnblockContacts',
     'OnCrimewatchEngagementUpdated',
     'OnSuspectsAndCriminalsUpdate',
     'OnDisapprovalUpdate',
     'OnCharStateChanged']
    default_highlightClass = ChatUserEntryUnderlay
    isDragObject = True
    charid = None
    selected = 0
    id = None
    groupID = None
    picloaded = 0
    label = None

    def Startup(self, *args):
        self._CreatePicture()
        self._CreateName()
        self.flagCont = None
        self._CreateBuddyContainer()
        self._CreateBottomRightContainer()
        sm.RegisterNotify(self)

    def _CreatePicture(self):
        self.sr.picture = Container(name='picture', parent=self, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, align=uiconst.RELATIVE)

    @telemetry.ZONE_METHOD
    def _CreateName(self):
        self.sr.namelabel = EveLabelMedium(name='nameLabel', parent=self, state=uiconst.UI_DISABLED, text='', idx=0)

    def _CreateBuddyContainer(self):
        self.sr.statusIconContainer = Container(name='statusIconContainer', parent=self, align=uiconst.TOPRIGHT, width=16, height=16, idx=0)
        self.sr.statusIcon = Sprite(name='statusIcon', parent=self.sr.statusIconContainer, align=uiconst.CENTER, width=STATUS_ICON_SIZE, height=STATUS_ICON_SIZE, texturePath=ICON_ONLINESTATUS)

    def _CreateBottomRightContainer(self):
        self.bottomRightCont = Container(name='bottomRightCont', parent=self, align=uiconst.BOTTOMRIGHT, width=16, height=16, idx=0)

    def PreLoad(node):
        data = node
        charinfo = data.Get('info', None) or cfg.eveowners.Get(data.charID)
        data.info = charinfo
        if data.GetLabel:
            data.label = data.GetLabel(data)
        elif not data.Get('label', None):
            label = charinfo.name
            data.label = label
        groupID = evetypes.GetGroupID(data.info.typeID)
        data.invtype = data.info.typeID
        data.IsCharacter = groupID == const.groupCharacter

    def Load(self, node):
        self.sr.node = node
        data = node
        self.channelID = data.Get('channelID', None)
        self.name = data.info.name
        self.sr.namelabel.text = data.label
        self.charid = self.id = data.itemID = data.charID
        self.picloaded = 0
        self.confirmOnDblClick = data.Get('dblconfirm', 1)
        self.data = {'Name': self.name,
         'charid': data.charID}
        self.inWatchlist = sm.GetService('addressbook').IsInWatchlist(data.charID)
        self.sr.namelabel.SetAlign(uiconst.CENTERLEFT)
        self.sr.namelabel.left = 40
        self.LoadPortrait()
        uthread.new(self.SetRelationship, data)
        self.sr.statusIconContainer.display = False
        if data.charID != session.charid and self.inWatchlist:
            try:
                self.SetOnline(sm.GetService('onlineStatus').GetOnlineStatus(data.charID, fetch=False))
            except IndexError:
                sys.exc_clear()

        if self.sr.node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        self.SetBlocked(1)
        if uicore.uilib.mouseOver is self:
            self.Select()

    def GetDynamicHeight(node, width):
        node.height = 32
        return node.height

    def OnContactLoggedOn(self, charID):
        self._OnContactsOnlineStateChanged(charID, isOnline=1)

    def OnContactLoggedOff(self, charID):
        self._OnContactsOnlineStateChanged(charID, isOnline=0)

    def _OnContactsOnlineStateChanged(self, charID, isOnline):
        if self._IsMeOrDestroyedEntry(charID):
            return
        if self.IsThisCharacter(charID):
            self.SetOnline(isOnline)

    def OnClientContactChange(self, charID, online):
        self._OnContactsOnlineStateChanged(charID, isOnline=bool(online))

    def OnContactNoLongerContact(self, charID):
        self._OnContactsOnlineStateChanged(charID, isOnline=None)

    def IsThisCharacter(self, charID):
        return charID == self.charid

    def _IsMeOrDestroyedEntry(self, charID):
        if not self:
            return True
        if self.destroyed:
            return True
        if charID == session.charid:
            return True
        if idCheckers.IsNPC(charID):
            return True
        return False

    def OnPortraitCreated(self, charID, _size):
        if self.destroyed:
            return
        if self.sr.node and charID == self.sr.node.charID and not self.picloaded:
            self.LoadPortrait(orderIfMissing=False)

    def OnContactChange(self, contactIDs, contactType = None):
        if self.destroyed:
            return
        self.SetRelationship(self.sr.node)
        if self.charid in contactIDs:
            addressbookSvc = sm.GetService('addressbook')
            self.inWatchlist = addressbookSvc.IsInWatchlist(self.charid)
            if self.inWatchlist:
                self.sr.statusIconContainer.display = True
            else:
                isBlocked = addressbookSvc.IsBlocked(self.charid)
                if isBlocked:
                    self.sr.statusIconContainer.display = True
                    self.sr.statusIcon.SetRGB(1.0, 1.0, 1.0)
                else:
                    self.sr.statusIconContainer.display = False

    def OnBlockContacts(self, contactIDs):
        if not self or self.destroyed:
            return
        if self.charid in contactIDs:
            self.SetBlocked(1)

    def OnUnblockContacts(self, contactIDs):
        if not self or self.destroyed:
            return
        if self.charid in contactIDs:
            self.SetBlocked(0)

    def OnStateSetupChange(self, what):
        if self.destroyed:
            return
        self.SetRelationship(self.sr.node)

    def ProcessOnUIAllianceRelationshipChanged(self, *args):
        if self.destroyed:
            return
        self.SetRelationship(self.sr.node)

    def OnFleetJoin_Local(self, memberInfo):
        thisCharID = self.GetCharIdFromNode()
        if thisCharID is None:
            return
        charID = memberInfo.charID
        if charID == thisCharID:
            uthread.new(self.SetRelationship, self.sr.node)

    def OnFleetLeave_Local(self, memberInfo):
        thisCharID = self.GetCharIdFromNode()
        if thisCharID is None:
            return
        charID = memberInfo.charID
        if charID == thisCharID or charID == session.charid:
            uthread.new(self.SetRelationship, self.sr.node)

    def OnMyFleetInited(self):
        if self.destroyed:
            return
        uthread.new(self.SetRelationship, self.sr.node)

    def SetOnline(self, online):
        if self.destroyed:
            return
        if online is None or not self.inWatchlist:
            if not sm.GetService('addressbook').IsBlocked(self.charid):
                self.sr.statusIconContainer.display = False
        else:
            color = COLOR_ONLINE if online else COLOR_OFFLINE
            self.sr.statusIcon.SetRGBA(*color)
            if online:
                hint = localization.GetByLabel('UI/Common/Online')
            else:
                hint = localization.GetByLabel('UI/Common/Offline')
            self.sr.statusIcon.hint = hint
            self.sr.statusIconContainer.display = True

    def SetBlocked(self, blocked):
        isBlocked = sm.GetService('addressbook').IsBlocked(self.charid)
        if blocked and isBlocked:
            self.sr.statusIcon.SetTexturePath(ICON_BLOCKED)
            self.sr.statusIconContainer.display = True
        elif self.inWatchlist:
            self.sr.statusIcon.SetTexturePath(ICON_ONLINESTATUS)
        else:
            self.sr.statusIconContainer.display = False

    def SetRelationship(self, data):
        if self.destroyed or not data:
            return
        flag = GetStateFlagFromData(data)
        if self.flagCont is None:
            self.flagCont = self.bottomRightCont
        AddAndSetFlagIcon(self.flagCont, align=uiconst.CENTER, flag=flag, width=12, height=12)
        self.flagCont.display = bool(flag is not None)

    def LoadPortrait(self, orderIfMissing = True):
        self.sr.picture.Flush()
        if self.sr.node is None:
            return
        if eveIcon.GetOwnerLogo(self.sr.picture, self.id, size=32, callback=True, orderIfMissing=orderIfMissing):
            self.picloaded = 1

    def GetMenu(self):
        if self.destroyed:
            return
        else:
            selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
            if len(selected) < 2:
                channelID = self.sr.node.Get('channelID', None)
                m = GetMenuService().GetMenuFromItemIDTypeID(self.id, self.sr.node.invtype, channelID=channelID)
                return m + [None] + XmppChannelMenu(channelID, self.sr.node.charID)
            charIDs = []
            for entry in selected:
                if entry.charID:
                    charIDs.append(entry.charID)

            return GetMenuService().CharacterMenu(charIDs)

    def ShowInfo(self, *args):
        if self.destroyed:
            return
        sm.GetService('info').ShowInfo(cfg.eveowners.Get(self.charid).typeID, self.charid)

    def OnClick(self, *args):
        if self.destroyed:
            return
        eve.Message('ListEntryClick')
        self.sr.node.scroll.SelectNode(self.sr.node)
        if self.sr.node.Get('OnClick', None):
            self.sr.node.OnClick(self)

    def OnDblClick(self, *args):
        if self.destroyed:
            return
        if self.sr.node.Get('OnDblClick', None):
            self.sr.node.OnDblClick(self)
            return
        onDblClick = settings.user.ui.Get('dblClickUser', 0)
        if onDblClick == 0:
            sm.GetService('info').ShowInfo(cfg.eveowners.Get(self.charid).typeID, self.charid)
        elif onDblClick == 1:
            GetChatService().Invite(self.charid)

    def GetDragData(self, *args):
        if self and not self.destroyed:
            return self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        else:
            return []

    def OnSuspectsAndCriminalsUpdate(self, criminalizedCharIDs, decriminalizedCharIDs):
        return self._UpdateOnSuspectCriminalAndDisapprovalChanges(criminalizedCharIDs, decriminalizedCharIDs)

    def OnDisapprovalUpdate(self, newCharIDs, removedCharIDs):
        return self._UpdateOnSuspectCriminalAndDisapprovalChanges(newCharIDs, removedCharIDs)

    def _UpdateOnSuspectCriminalAndDisapprovalChanges(self, newCharIDs, removedCharIDs):
        charID = self.GetCharIdFromNode()
        if charID is None:
            return
        if charID in newCharIDs or charID in removedCharIDs:
            uthread.new(self.SetRelationship, self.sr.node)

    def OnCrimewatchEngagementUpdated(self, otherCharId, timeout):
        charID = self.GetCharIdFromNode()
        if charID is None:
            return
        if charID == otherCharId:
            uthread.new(self.SetRelationship, self.sr.node)

    def OnCharStateChanged(self, otherCharID, newData):
        if self.destroyed:
            return
        charID = self.GetCharIdFromNode()
        if charID is None or charID != otherCharID:
            return
        currentData = self.sr.node
        try:
            currentData.corpID = newData['corpid']
            currentData.allianceID = newData['allianceid']
            currentData.warFactionID = newData['warfactionid']
        except KeyError:
            log.LogException()
        finally:
            self.SetRelationship(currentData)

    def GetCharIdFromNode(self):
        if self.destroyed:
            return None
        charID = GetAttrs(self, 'sr', 'node', 'charID')
        return charID

    def OnDropData(self, dragObj, nodes):
        nonCharNodes = []
        for eachNode in nodes:
            itemID = getattr(eachNode, 'itemID', None)
            if not itemID:
                itemID = GetCharIDFromTextLink(eachNode)
            if idCheckers.IsCharacter(itemID):
                continue
            nonCharNodes.append(eachNode)

        if nonCharNodes and self.charid:
            from eve.client.script.ui.station.pvptrade.tradeUtil import TryInitiateTrade
            TryInitiateTrade(self.charid, nonCharNodes)
        self.sr.node.scroll.GetContentContainer().OnDropData(dragObj, nodes)

    def _IsDisplayed(self, container):
        return container is not None and not container.destroyed and container.display

    def _OnResize(self, *args):
        self.UpdateComponentSizes()

    def UpdateComponentSizes(self):
        occupiedWidth = 4
        if self._IsDisplayed(self.sr.statusIconContainer):
            occupiedWidth += STATUS_ICON_SIZE + STATUS_ICON_PAD_LEFT
        if self._IsDisplayed(self.flagCont):
            occupiedWidth = max(occupiedWidth, self.flagCont.width + 5)
        spaceAvailableForNameLabel = self.width - self.sr.namelabel.left - occupiedWidth
        self.sr.namelabel.SetRightAlphaFade(fadeEnd=spaceAvailableForNameLabel, maxFadeWidth=3)

    @classmethod
    def GetCopyData(cls, node):
        return node.label


class XmppChatSimpleUserEntry(XmppChatUserEntry):
    __guid__ = 'listentry.XmppChatSimpleUserEntry'
    ENTRYHEIGHT = 16

    def Startup(self, *args):
        XmppChatUserEntry.Startup(self, *args)
        self.iconCont = Container(name='iconCont', parent=self, align=uiconst.TOLEFT, width=12)

    def _CreatePicture(self):
        pass

    def _CreateBottomRightContainer(self):
        pass

    def Load(self, node):
        XmppChatUserEntry.Load(self, node)
        self.sr.namelabel.left = 16

    def SetRelationship(self, data):
        if self.destroyed or not data:
            return
        AddAndSetFlagIconFromData(parentCont=self.iconCont, data=data, align=uiconst.CENTER, top=-1, left=0, width=12, height=12)

    def LoadPortrait(self, orderIfMissing = True):
        pass

    def _CreateBuddyContainer(self):
        self.sr.statusIconContainer = Container(name='statusIconContainer', parent=self, align=uiconst.TORIGHT, width=16, height=16)
        self.sr.statusIcon = Sprite(name='statusIcon', parent=self.sr.statusIconContainer, align=uiconst.CENTERRIGHT, width=STATUS_ICON_SIZE, height=STATUS_ICON_SIZE, texturePath=ICON_ONLINESTATUS)
