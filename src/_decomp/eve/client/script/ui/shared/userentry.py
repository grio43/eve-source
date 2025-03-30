#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\userentry.py
import sys
from carbon.common.script.util.commonutils import GetAttrs
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import TextColor, uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.base import ReverseScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.eveColor import SUCCESS_GREEN_HEX
from eve.client.script.ui.shared.neocom.addressBook.buddyOnlineIndicator import BuddyOnlineIndicator
from eve.client.script.ui.shared.stateFlag import GetStateFlagFromData, AddAndSetFlagIcon, GetFlagFromRelationShip, AddAndSetFlagIconFromData
from eve.client.script.ui.station.agents.agentConversationIcon import AgentConversationIcon
from eve.client.script.ui.station.agents.agentDialogueUtil import GetAgentNameAndLevel
from eve.client.script.ui.station.agents.agentUtil import GetAgentLocationText
from eve.client.script.ui.util.uix import GetTextHeight
from eve.common.script.sys import idCheckers
from eve.common.script.util.eveFormat import FmtISK
from eveservices.menu import GetMenuService
from eveservices.xmppchat import GetChatService
import evetypes
from gametime import GetWallclockTimeNow, HOUR, MIN
import localization
import telemetry
import uthread
from menu import MenuLabel
from npcs.divisions import get_division_name
HEIGHT = 40
BUDDY_CONTAINER_PAD_LEFT = 4
STATUS_ICON_SIZE = 12
STATUS_ICON_PAD_LEFT = 2

class User(SE_BaseClassCore):
    __guid__ = 'listentry.User'
    __params__ = ['charID']
    __notifyevents__ = ['OnContactLoggedOn',
     'OnContactLoggedOff',
     'OnClientContactChange',
     'OnPortraitCreated',
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
     'OnDisapprovalUpdate']
    isDragObject = True
    charid = None
    selected = 0
    big = 0
    id = None
    groupID = None
    picloaded = 0
    fleetCandidate = 0
    label = None
    slimuser = False

    def Startup(self, *args):
        self._CreatePicture()
        self._CreateName()
        self.sr.voiceIcon = None
        self.sr.eveGateIcon = None
        self.contactLabel = None
        self.rightCont = ContainerAutoSize(parent=self, align=uiconst.CENTERRIGHT, height=16, left=4)
        self.flagCont = None
        self._CreateOnlineStatusIcon()
        self._CreateStandingLabel()
        self._CreateCorpApplicationLabel()
        sm.RegisterNotify(self)

    def _CreatePicture(self):
        self.sr.picture = Container(parent=self, name='picture', state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, pos=(2, 0, 32, 32))
        self.sr.extraIconCont = Container(name='extraIconCont', parent=self, idx=0, pos=(0, 0, 16, 16), align=uiconst.BOTTOMLEFT, state=uiconst.UI_HIDDEN)

    @telemetry.ZONE_METHOD
    def _CreateName(self):
        self.sr.namelabel = EveLabelLarge(name='nameLabel', parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, idx=0)

    def _CreateContactLabels(self):
        self.contactLabel = EveLabelMedium(text='', name='contactLabels', parent=self, state=uiconst.UI_DISABLED, idx=0, align=uiconst.BOTTOMLEFT, left=40, top=4, color=TextColor.SECONDARY)

    @telemetry.ZONE_METHOD
    def _CreateStandingLabel(self):
        self.sr.standingLabel = EveLabelMedium(text='', name='standingLabel', parent=self.rightCont, state=uiconst.UI_DISABLED, align=uiconst.TORIGHT)

    def _CreateOnlineStatusIcon(self):
        self.onlineStatusIcon = BuddyOnlineIndicator(parent=self.rightCont, align=uiconst.TORIGHT, width=16)

    @telemetry.ZONE_METHOD
    def _CreateCorpApplicationLabel(self):
        self.sr.corpApplicationLabel = EveLabelMedium(text='corpApplicationLabel', name='corpApplicationLabel', parent=self, state=uiconst.UI_DISABLED, idx=0, align=uiconst.CENTERRIGHT)
        self.sr.corpApplicationLabel.left = 16

    def PreLoad(node):
        data = node
        charinfo = data.Get('info', None) or cfg.eveowners.Get(data.charID)
        data.info = charinfo
        if data.GetLabel:
            data.label = data.GetLabel(data)
        elif not data.Get('label', None):
            label = charinfo.name
            if data.bounty:
                label += '<br>'
                label += localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=FmtISK(data.bounty.bounty, 0))
            elif data.killTime:
                label += '<br>' + localization.GetByLabel('UI/PeopleAndPlaces/ExpiresTime', expires=data.killTime)
            data.label = label
        groupID = evetypes.GetGroupID(data.info.typeID)
        data.invtype = data.info.typeID
        data.IsCharacter = groupID == const.groupCharacter
        data.IsCorporation = groupID == const.groupCorporation
        data.IsFaction = groupID == const.groupFaction
        data.IsAlliance = groupID == const.groupAlliance
        if data.IsCorporation and not idCheckers.IsNPC(data.charID):
            logoData = cfg.corptickernames.Get(data.charID)

    def Load(self, node):
        self.sr.node = node
        data = node
        self.name = data.info.name
        self.sr.namelabel.text = data.label
        self.charid = self.id = data.itemID = data.charID
        self.picloaded = 0
        self.sr.parwnd = data.Get('dad', None)
        self.fleetCandidate = data.Get('fleetster', 1) and not data.info.IsNPC()
        self.confirmOnDblClick = data.Get('dblconfirm', 1)
        self.leaveDadAlone = data.Get('leavedad', 0)
        self.slimuser = data.Get('slimuser', False)
        self.data = {'Name': self.name,
         'charid': data.charID}
        self.inWatchlist = sm.GetService('addressbook').IsInWatchlist(data.charID)
        self.isContactList = data.Get('contactType', None)
        self.applicationDate = data.Get('applicationDate', None)
        self.contactLevel = None
        if self.isContactList:
            self.contactLevel = data.contactLevel
            self.SetLabelText()
        self.isCorpOrAllianceContact = data.contactType and data.contactType != 'contact'
        data.listvalue = [data.info.name, data.charID]
        level = self.sr.node.Get('sublevel', 0)
        subLevelOffset = 16
        self.sr.picture.left = 2 + max(0, subLevelOffset * level)
        self.LoadPortrait()
        if data.IsCharacter:
            uthread.new(self.SetRelationship, data)
            self.onlineStatusIcon.Hide()
            if data.charID != session.charid:
                if not idCheckers.IsNPC(data.charID) and not self.isCorpOrAllianceContact and self.inWatchlist:
                    try:
                        self.SetOnline(sm.GetService('onlineStatus').GetOnlineStatus(data.charID, fetch=False))
                    except IndexError:
                        sys.exc_clear()

        else:
            self.onlineStatusIcon.Hide()
            if data.charID != session.charid:
                uthread.new(self.SetRelationship, data)
        self.sr.namelabel.left = 40 + max(0, subLevelOffset * level)
        if self.sr.node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        if not self.isCorpOrAllianceContact:
            self.contactLevel = sm.GetService('addressbook').GetStandingsLevel(self.charid, 'contact')
            self.SetBlocked(1)
        else:
            self.SetBlocked(0)
        if self.isCorpOrAllianceContact:
            self.SetStandingText(self.contactLevel)
        if self.applicationDate:
            self.sr.corpApplicationLabel.SetText(localization.GetByLabel('UI/Corporations/Applied', applydate=self.applicationDate))
            self.sr.corpApplicationLabel.Show()
            data.Set('sort_' + localization.GetByLabel('UI/Common/Date'), self.applicationDate)
            data.Set('sort_' + localization.GetByLabel('UI/Common/Name'), data.info.name)
        else:
            self.sr.corpApplicationLabel.SetText('')
            self.sr.corpApplicationLabel.Hide()

    def GetValue(self):
        return [self.name, self.id]

    def GetDynamicHeight(node, width):
        if '<br>' in node.label:
            node.height = max(HEIGHT, GetTextHeight(node.label, linespace=11))
        else:
            node.height = HEIGHT
        return node.height

    def OnContactLoggedOn(self, charID):
        if self and not self.destroyed and charID == self.charid and charID != session.charid and not idCheckers.IsNPC(charID):
            self.SetOnline(1)

    def OnContactLoggedOff(self, charID):
        if self and not self.destroyed and charID == self.charid and charID != session.charid and not idCheckers.IsNPC(charID):
            self.SetOnline(0)

    def OnClientContactChange(self, charID, online):
        if online:
            self.OnContactLoggedOn(charID)
        else:
            self.OnContactLoggedOff(charID)

    def OnContactNoLongerContact(self, charID):
        if self and not self.destroyed and charID == self.charid and charID != session.charid:
            self.SetOnline(None)

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
            if sm.GetService('addressbook').IsInAddressBook(self.charid, contactType):
                if not self.isContactList:
                    self.isContactList = contactType
            else:
                self.isContactList = None
            self.inWatchlist = sm.GetService('addressbook').IsInWatchlist(self.charid)
            if not self.inWatchlist:
                isBlocked = sm.GetService('addressbook').IsBlocked(self.charid)
                if isBlocked:
                    self.onlineStatusIcon.SetBlocked()
                else:
                    self.onlineStatusIcon.Hide()

    def OnBlockContacts(self, contactIDs):
        if not self or self.destroyed:
            return
        if self.charid in contactIDs:
            self.SetBlocked(1)
        self.UpdateComponentSizes()

    def OnUnblockContacts(self, contactIDs):
        if not self or self.destroyed:
            return
        if self.charid in contactIDs:
            self.SetBlocked(0)
        self.UpdateComponentSizes()

    def OnStateSetupChange(self, what):
        if self.destroyed:
            return
        self.SetRelationship(self.sr.node)

    def ProcessOnUIAllianceRelationshipChanged(self, *args):
        if self.destroyed:
            return
        self.SetRelationship(self.sr.node)

    def OnFleetJoin_Local(self, memberInfo, state = 'Active'):
        if self.destroyed:
            return
        myID = GetAttrs(self, 'sr', 'node', 'charID')
        charID = memberInfo.charID
        if myID is not None and charID == myID:
            uthread.new(self.SetRelationship, self.sr.node)

    def OnFleetLeave_Local(self, memberInfo):
        if self.destroyed:
            return
        myID = GetAttrs(self, 'sr', 'node', 'charID')
        charID = memberInfo.charID
        if myID is not None and charID == myID or charID == session.charid:
            uthread.new(self.SetRelationship, self.sr.node)

    def OnMyFleetInited(self):
        if self.destroyed:
            return
        uthread.new(self.SetRelationship, self.sr.node)

    def SetOnline(self, online):
        if self.destroyed:
            return
        if self.slimuser:
            return
        if online is None or not self.inWatchlist or self.isCorpOrAllianceContact:
            self.onlineStatusIcon.Hide()
        elif online:
            self.onlineStatusIcon.SetOnline()
        else:
            self.onlineStatusIcon.SetOffline()

    def SetBlocked(self, blocked):
        isBlocked = sm.GetService('addressbook').IsBlocked(self.charid)
        if blocked and isBlocked and not self.isCorpOrAllianceContact:
            self.onlineStatusIcon.SetBlocked()
        elif self.inWatchlist:
            self.onlineStatusIcon.SetNotBlocked()
        else:
            self.onlineStatusIcon.Hide()

    @telemetry.ZONE_METHOD
    def SetLabelText(self):
        labelMask = sm.GetService('addressbook').GetLabelMask(self.charid)
        self.sr.node.labelMask = labelMask
        labeltext = sm.GetService('addressbook').GetLabelText(labelMask, self.isContactList)
        if labeltext:
            self.SetContactLabelText(labeltext)

    def SetContactLabelText(self, labeltext):
        if not self.contactLabel:
            self._CreateContactLabels()
        self.sr.namelabel.SetAlign(uiconst.TOPLEFT)
        self.sr.namelabel.top = 3
        self.contactLabel.text = labeltext

    def SetStandingText(self, standing):
        self.sr.standingLabel.text = standing

    def SetRelationship(self, data, debugFlag = None):
        if self.destroyed:
            return
        if self.slimuser:
            return
        if not data:
            return
        flag = None
        if data.Get('contactType', None):
            if self.contactLevel is None:
                return
            flag = GetFlagFromRelationShip(self.contactLevel)
        else:
            flag = GetStateFlagFromData(data)
        if flag:
            self._ConstructFlagCont(flag)

    def _ConstructFlagCont(self, flag):
        if self.flagCont is None:
            self.flagCont = Container(name='flagCont', parent=self.rightCont, pos=(0, 0, 16, 16), align=uiconst.TORIGHT, idx=0)
        AddAndSetFlagIcon(self.flagCont, flag=flag, top=0, left=0, width=12, height=12, align=uiconst.CENTER)

    def LoadPortrait(self, orderIfMissing = True):
        self.sr.picture.Flush()
        if self.sr.node is None:
            return
        if eveIcon.GetOwnerLogo(self.sr.picture, self.id, size=32, callback=True, orderIfMissing=orderIfMissing):
            self.picloaded = 1

    def RemoveFromListGroup(self, listGroupIDs, charIDs, listname):
        if self.destroyed:
            return
        if listGroupIDs:
            for listGroupID, charID in listGroupIDs:
                uicore.registry.RemoveFromListGroup(listGroupID, charID)

            sm.GetService('addressbook').RefreshWindow()
        if charIDs and listname:
            name = [localization.GetByLabel('UI/AddressBook/RemoveAddressBook1'), cfg.eveowners.Get(charIDs[0]).name][len(charIDs) == 1]
            if eve.Message('WarnDeleteFromAddressbook', {'name': name,
             'type': listname}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return
            sm.GetService('addressbook').DeleteEntryMulti(charIDs, None)

    def GetMenu(self):
        if self.destroyed:
            return
        m = []
        selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        multi = len(selected) > 1
        if multi:
            return self._GetMultiMenu(selected)
        channelID = self.sr.node.Get('channelID', None)
        m = GetMenuService().GetMenuFromItemIDTypeID(self.id, self.sr.node.invtype, channelID=channelID)
        if self.sr.node.Get('GetMenu', None) is not None:
            m += self.sr.node.GetMenu(self.sr.node)
        listGroupID = self.sr.node.Get('listGroupID', None)
        if listGroupID is not None:
            group = uicore.registry.GetListGroup(listGroupID)
            if group:
                if listGroupID not in [('buddygroups', 'all'), ('buddygroups', 'allcorps')]:
                    m.append(None)
                    m.append((MenuLabel('UI/Common/RemoveFromGroup', {'groupname': group['label']}), self.RemoveFromListGroup, ([(listGroupID, self.charid)], [], '')))
        if self.sr.node.Get('MenuFunction', None):
            cm = [None]
            cm += self.sr.node.MenuFunction([self.sr.node])
            m += cm
        if self.isContactList is not None:
            if sm.GetService('addressbook').ShowLabelMenuAndManageBtn(self.isContactList):
                m.append(None)
                assignLabelMenu = sm.StartService('addressbook').GetAssignLabelMenu(selected, [self.charid], self.isContactList)
                if len(assignLabelMenu) > 0:
                    m.append((MenuLabel('UI/Mail/AssignLabel'), assignLabelMenu))
                removeLabelMenu = sm.StartService('addressbook').GetRemoveLabelMenu(selected, [self.charid], self.isContactList)
                if len(removeLabelMenu) > 0:
                    m.append((MenuLabel('UI/Mail/LabelRemove'), removeLabelMenu))
        return m

    def _GetMultiMenu(self, selected):
        m = []
        charIDs = []
        multiCharIDs = []
        multiEveCharIDs = []
        listGroupIDs = {}
        listGroupID_charIDs = []
        onlyCharacters = True
        for entry in selected:
            listGroupID = entry.listGroupID
            if listGroupID:
                listGroupIDs[listGroupID] = 0
                listGroupID_charIDs.append((listGroupID, entry.charID))
            if entry.charID:
                charIDs.append(entry.charID)
                multiCharIDs.append(entry.charID)
                if not idCheckers.IsCharacter(entry.charID):
                    onlyCharacters = False

        if self.isContactList is None:
            if onlyCharacters:
                m += GetMenuService().CharacterMenu(charIDs)
            if listGroupIDs:
                listname = ''
                delCharIDs = []
                rem = []
                for listGroupID, charID in listGroupID_charIDs:
                    if listGroupID in [('buddygroups', 'all'), ('buddygroups', 'allcorps')]:
                        if onlyCharacters:
                            return m
                        uicore.registry.GetListGroup(listGroupID)
                        listname = [localization.GetByLabel('UI/Generic/BuddyList')][listGroupID == ('buddygroups', 'all')]
                        delCharIDs.append(charID)
                        rem.append((listGroupID, charID))

                for each in rem:
                    listGroupID_charIDs.remove(each)

                foldername = 'folders'
                if len(listGroupIDs) == 1:
                    group = uicore.registry.GetListGroup(listGroupIDs.keys()[0])
                    if group:
                        foldername = group['label']
                label = ''
                if delCharIDs and listname:
                    label = localization.GetByLabel('UI/PeopleAndPlaces/RemoveMultipleFromAddressbook', removecount=len(delCharIDs))
                    if listGroupID_charIDs:
                        label += [', ']
                if listGroupID_charIDs:
                    label += localization.GetByLabel('UI/PeopleAndPlaces/RemoveFromFolder', foldername=foldername, removecount=len(listGroupID_charIDs))
                m.append((label, self.RemoveFromListGroup, (listGroupID_charIDs, delCharIDs, listname)))
        else:
            addressBookSvc = sm.GetService('addressbook')
            counter = len(selected)
            blocked = 0
            if self.isContactList == 'contact':
                editLabel = localization.GetByLabel('UI/PeopleAndPlaces/EditContacts', contactcount=counter)
                m.append((editLabel, addressBookSvc.EditContacts, [multiCharIDs, 'contact']))
                deleteLabel = localization.GetByLabel('UI/PeopleAndPlaces/RemoveContacts', contactcount=counter)
                m.append((deleteLabel, addressBookSvc.DeleteEntryMulti, [multiCharIDs, 'contact']))
                for charid in multiCharIDs:
                    if sm.GetService('addressbook').IsBlocked(charid):
                        blocked += 1

                if blocked == counter:
                    unblockLabel = localization.GetByLabel('UI/PeopleAndPlaces/UnblockContacts', contactcount=blocked)
                    m.append((unblockLabel, addressBookSvc.UnblockOwner, [multiCharIDs]))
            elif self.isContactList == 'corpcontact':
                editLabel = localization.GetByLabel('UI/PeopleAndPlaces/EditCorpContacts', contactcount=counter)
                m.append((editLabel, addressBookSvc.EditContacts, [multiCharIDs, 'corpcontact']))
                deleteLabel = localization.GetByLabel('UI/PeopleAndPlaces/RemoveCorpContacts', contactcount=counter)
                m.append((deleteLabel, addressBookSvc.DeleteEntryMulti, [multiCharIDs, 'corpcontact']))
            elif self.isContactList == 'alliancecontact':
                editLabel = localization.GetByLabel('UI/PeopleAndPlaces/EditAllianceContacts', contactcount=counter)
                m.append((editLabel, addressBookSvc.EditContacts, [multiCharIDs, 'alliancecontact']))
                deleteLabel = localization.GetByLabel('UI/PeopleAndPlaces/RemoveAllianceContacts', contactcount=counter)
                m.append((deleteLabel, addressBookSvc.DeleteEntryMulti, [multiCharIDs, 'alliancecontact']))
            m.append(None)
            assignLabelMenu = sm.StartService('addressbook').GetAssignLabelMenu(selected, multiCharIDs, self.isContactList)
            if len(assignLabelMenu) > 0:
                m.append((MenuLabel('UI/PeopleAndPlaces/AddContactLabel'), assignLabelMenu))
            removeLabelMenu = sm.StartService('addressbook').GetRemoveLabelMenu(selected, multiCharIDs, self.isContactList)
            if len(removeLabelMenu) > 0:
                m.append((MenuLabel('UI/PeopleAndPlaces/RemoveContactLabel'), removeLabelMenu))
            m.append(None)
            m.append((MenuLabel('UI/Commands/CapturePortrait'), sm.StartService('photo').SavePortraits, [multiEveCharIDs]))
        if self.sr.node.Get('MenuFunction', None):
            cm = [None]
            cm += self.sr.node.MenuFunction(selected)
            m += cm
        return m

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
        if self.sr.parwnd and hasattr(self.sr.parwnd, 'Select') and self.confirmOnDblClick:
            self.sr.parwnd.Select(self)
            self.sr.parwnd.Confirm()
            return
        if not self.leaveDadAlone and self.sr.parwnd and uicore.registry.GetModalWindow() == self.sr.parwnd:
            self.sr.parwnd.SetModalResult(uiconst.ID_OK)
            return
        onDblClick = settings.user.ui.Get('dblClickUser', 0)
        if onDblClick == 0:
            sm.GetService('info').ShowInfo(cfg.eveowners.Get(self.charid).typeID, self.charid)
        elif onDblClick == 1:
            GetChatService().Invite(self.charid)

    def GetDragData(self, *args):
        if self and not self.destroyed and not self.slimuser:
            return self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        else:
            return []

    @classmethod
    def GetCopyData(cls, node):
        return node.label

    def OnSuspectsAndCriminalsUpdate(self, criminalizedCharIDs, decriminalizedCharIDs):
        return self._UpdateOnSuspectCriminalAndDisapprovalChanges(criminalizedCharIDs, decriminalizedCharIDs)

    def OnDisapprovalUpdate(self, newCharIDs, removedCharIDs):
        return self._UpdateOnSuspectCriminalAndDisapprovalChanges(newCharIDs, removedCharIDs)

    def _UpdateOnSuspectCriminalAndDisapprovalChanges(self, newCharIDs, removedCharIDs):
        if self.destroyed:
            return
        charID = GetAttrs(self, 'sr', 'node', 'charID')
        if charID is not None and (charID in newCharIDs or charID in removedCharIDs):
            uthread.new(self.SetRelationship, self.sr.node)

    def OnCrimewatchEngagementUpdated(self, otherCharId, timeout):
        if self.destroyed:
            return
        charID = GetAttrs(self, 'sr', 'node', 'charID')
        if charID is not None and charID == otherCharId:
            uthread.new(self.SetRelationship, self.sr.node)

    def OnDropData(self, dragObj, nodes):
        nonCharNodes = []
        for eachNode in nodes:
            itemID = getattr(eachNode, 'itemID', None)
            if idCheckers.IsCharacter(itemID):
                continue
            nonCharNodes.append(eachNode)

        if not nonCharNodes or not self.charid or not idCheckers.IsCharacter(self.charid):
            return
        from eve.client.script.ui.station.pvptrade.tradeUtil import TryInitiateTrade
        TryInitiateTrade(self.charid, nonCharNodes)

    def _IsDisplayed(self, container):
        return container is not None and not container.destroyed and container.display

    def _OnResize(self, *args):
        super(User, self)._OnResize(args)
        self.UpdateComponentSizes()

    def UpdateComponentSizes(self):
        occupiedWidth = BUDDY_CONTAINER_PAD_LEFT
        if self._IsDisplayed(self.onlineStatusIcon):
            occupiedWidth += STATUS_ICON_SIZE + STATUS_ICON_PAD_LEFT
        if self._IsDisplayed(self.flagCont):
            occupiedWidth += self.flagCont.width + 1
        spaceAvailableForNameLabel = self.width - self.sr.namelabel.left - occupiedWidth
        self.sr.namelabel.SetRightAlphaFade(fadeEnd=spaceAvailableForNameLabel, maxFadeWidth=3)


class UserSimple(User):
    __guid__ = 'listentry.UserSimple'
    ENTRYHEIGHT = 18

    def Startup(self, *args):
        User.Startup(self, *args)
        self.iconCont = Container(parent=self, align=uiconst.TOLEFT, width=16)

    def Load(self, node, *args):
        User.Load(self, node, *args)
        self.sr.namelabel.left = 16
        self.sr.label = self.sr.namelabel
        self.sr.label.maxLines = 1

    def SetRelationship(self, data, *args, **kwargs):
        if self.destroyed:
            return
        if not data:
            return
        AddAndSetFlagIconFromData(parentCont=self.iconCont, data=data, top=4, left=4)

    def LoadPortrait(self, orderIfMissing = True):
        pass

    def GetDynamicHeight(node, width):
        node.height = UserSimple.ENTRYHEIGHT
        return node.height


class AgentEntry(SE_BaseClassCore):
    __guid__ = 'listentry.AgentEntry'
    default_name = 'AgentEntry'
    isDragObject = True

    def Startup(self, *args):
        self.divisionName = ''
        self.agentName = ''
        self.levelName = ''
        self.agentType = ''
        self.agentLocation = ''
        self.missionState = ''
        self.locationLabel = None
        self.agentChatBtn = None
        self.timer = None
        self._timerUpdatesThread = None
        picCont = Container(parent=self, pos=(1, 0, 50, 0), name='pictureContainer', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT)
        self.sr.pic = Sprite(parent=picCont, name='picture', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        textCont = Container(parent=self, name='textCont', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOALL, padLeft=6, padTop=2, padRight=6)
        self.textCont = Container(parent=textCont, name='text', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOALL, clipChildren=True, padTop=2)
        self.sr.namelabel = EveLabelMedium(name='nameLabel', text='', parent=self.textCont)
        self.sr.timerLabel = EveLabelMedium(name='timerLabel', text='', align=uiconst.TOPLEFT, parent=self.textCont, top=14)
        self.sr.levelLabel = EveLabelMedium(name='levelLabel', text='', align=uiconst.TOPLEFT, parent=self.textCont, top=14)
        self.sr.missionLabel = EveLabelMedium(name='missionLabel', text='', parent=self.textCont, align=uiconst.TOPRIGHT)
        self.agentChatBtn = AgentConversationIcon(name='agentChatBtn', parent=self, align=uiconst.BOTTOMRIGHT, left=0, top=0)
        buttonIconOnMouseEnter = self.agentChatBtn.OnMouseEnter
        self.agentChatBtn.OnMouseEnter = (self.OnChatButtonMouseEnter, self.agentChatBtn, buttonIconOnMouseEnter)

    def PreLoad(node):
        data = node
        charinfo = data.Get('info', None) or cfg.eveowners.Get(data.charID)
        data.info = charinfo
        data.itemID = data.charID
        data.invtype = data.info.typeID

    def GetAgentInfo(self, data):
        charID = data.charID
        self.UpdateMissionStateText(charID)
        agentInfo = sm.GetService('agents').GetAgentByID(charID)
        self.agentName = GetAgentNameAndLevel(charID, agentInfo.level)
        if agentInfo:
            self.agentChatBtn.SetAgentID(charID)
            agentDivision = get_division_name(agentInfo.divisionID).replace('&', '&amp;')
            if charID in const.rookieAgentList:
                self.agentType = localization.GetByLabel('UI/AgentFinder/TutorialAgentDivision', divisionName=agentDivision)
            elif agentInfo.agentTypeID == const.agentTypeEpicArcAgent:
                self.agentType = localization.GetByLabel('UI/AgentFinder/EpicArcAgentDivision', divisionName=agentDivision)
            elif agentInfo.agentTypeID in (const.agentTypeGenericStorylineMissionAgent, const.agentTypeStorylineMissionAgent):
                self.agentType = localization.GetByLabel('UI/AgentFinder/StorylineAgentDivision', divisionName=agentDivision)
            elif agentInfo.agentTypeID == const.agentTypeEventMissionAgent:
                self.agentType = localization.GetByLabel('UI/AgentFinder/EventAgentDivision', divisionName=agentDivision)
            elif agentInfo.agentTypeID == const.agentTypeCareerAgent:
                self.agentType = localization.GetByLabel('UI/AgentFinder/CareerAgentDivision', divisionName=agentDivision)
            elif agentInfo.agentTypeID == const.agentTypeHeraldry:
                self.agentType = localization.GetByLabel('UI/AgentFinder/HeraldryAgent')
            elif agentInfo.agentTypeID == const.agentTypeAura:
                self.agentType = ''
            else:
                self.agentType = agentDivision
            if agentInfo.stationID and session.stationid != agentInfo.stationID:
                agentInfo = sm.GetService('agents').GetAgentByID(data.charID)
                solarSystemID = sm.GetService('contracts').GetSolarSystemIDForStationOrStructure(agentInfo.stationID)
                pathfinder = sm.GetService('clientPathfinderService')
                numJumps = pathfinder.GetAutopilotJumpCount(session.solarsystemid2, solarSystemID)
                self.agentLocation = GetAgentLocationText(solarSystemID)
        else:
            self.agentChatBtn.display = False

    def UpdateMissionStateText(self, charID):
        activeMission = sm.GetService('journal').GetActiveMissionForAgent(charID)
        if activeMission:
            self.missionState = activeMission.GetMissionStateTextColored()

    def Load(self, node):
        self.sr.node = node
        data = node
        if self.sr.node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        self.timer = getattr(data, 'timer', None)
        self.GetAgentInfo(data)
        extraTop = 0
        if self.agentLocation != '':
            if not self.locationLabel:
                self.locationLabel = EveLabelMedium(name='locationLabel', parent=self.textCont, text=self.agentLocation, top=14)
            extraTop = 14
        self.name = data.info.name
        self.sr.namelabel.text = self.agentName
        self.sr.missionLabel.text = self.missionState
        if self.timer:
            extraTop += 14
            self._StartTimerUpdates()
            self.sr.timerLabel.top = extraTop
        else:
            self._StopTimerUpdates()
            self.sr.timerLabel.top = extraTop
        extraTop += 14
        if self.levelName == '':
            levelText = self.agentType
        else:
            levelText = self.levelName
        self.sr.levelLabel.text = levelText
        self.sr.levelLabel.top = extraTop
        self.charID = data.charID
        sm.GetService('photo').GetPortrait(self.charID, 64, self.sr.pic)

    def _StartTimerUpdates(self):
        self._UpdateTimer()
        if not self._timerUpdatesThread:
            self._timerUpdatesThread = AutoTimer(interval=500, method=self._UpdateTimer)

    def _GetTimerText(self, timeLeft):
        if timeLeft >= 12 * HOUR:
            showTo = 'hour'
        elif timeLeft >= HOUR:
            showTo = 'minute'
        elif timeLeft >= 10 * MIN:
            showTo = 'minute'
        else:
            showTo = 'second'
        formatter = localization.formatters.FormatTimeIntervalShortWritten
        formattedTime = formatter(timeLeft, showFrom='hour', showTo=showTo)
        text = localization.GetByLabel('UI/Agents/AgentEntry/Timer', timeLeft=formattedTime, color=SUCCESS_GREEN_HEX)
        return text

    def _UpdateTimer(self):
        if self.destroyed or not self.sr.timerLabel or not self.timer:
            self._StopTimerUpdates()
            return
        now = GetWallclockTimeNow()
        timeLeft = max(self.timer - now, 0)
        text = self._GetTimerText(timeLeft)
        self.sr.timerLabel.SetText(text)
        if timeLeft == 0:
            self._StopTimerUpdates()

    def _StopTimerUpdates(self):
        if self._timerUpdatesThread:
            self._timerUpdatesThread.KillTimer()
            if not self.destroyed and self.sr.timerLabel:
                self.sr.timerLabel.text = ''
                self.sr.levelLabel.top = self.sr.timerLabel.top

    def GetMenu(self):
        if self.destroyed:
            return
        m = []
        selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        multi = len(selected) > 1
        if multi:
            return self._GetMultiMenu(selected)
        m = GetMenuService().GetMenuFromItemIDTypeID(self.charID, self.sr.node.invtype)
        if self.sr.node.Get('GetMenu', None) is not None:
            m += self.sr.node.GetMenu(self.sr.node)
        listGroupID = self.sr.node.Get('listGroupID', None)
        if listGroupID is not None:
            group = uicore.registry.GetListGroup(listGroupID)
            if group:
                if not listGroupID == ('agentgroups', 'all'):
                    m.append(None)
                    m.append((MenuLabel('UI/Common/RemoveFromGroup', {'groupname': group['label']}), self.RemoveFromListGroup, ([(listGroupID, self.charID)], [], '')))
        if self.sr.node.Get('MenuFunction', None):
            cm = [None]
            cm += self.sr.node.MenuFunction([self.sr.node])
            m += cm
        return m

    def _GetMultiMenu(self, selected):
        m = []
        charIDs = []
        multiCharIDs = []
        listGroupIDs = {}
        listGroupID_charIDs = []
        onlyCharacters = True
        for entry in selected:
            listGroupID = entry.listGroupID
            if listGroupID:
                listGroupIDs[listGroupID] = 0
                listGroupID_charIDs.append((listGroupID, entry.charID))
            if entry.charID:
                charIDs.append(entry.charID)
                multiCharIDs.append(entry.charID)
                if not idCheckers.IsCharacter(entry.charID):
                    onlyCharacters = False

        if onlyCharacters:
            m += GetMenuService().CharacterMenu(charIDs)
        if listGroupIDs:
            listname = ''
            delCharIDs = []
            rem = []
            for listGroupID, charID in listGroupID_charIDs:
                if listGroupID == ('agentgroups', 'all'):
                    if onlyCharacters:
                        return m
                    group = uicore.registry.GetListGroup(listGroupID)
                    listname = [localization.GetByLabel('UI/Agents/AgentList'), localization.GetByLabel('UI/Generic/BuddyList')][listGroupID == ('buddygroups', 'all')]
                    delCharIDs.append(charID)
                    rem.append((listGroupID, charID))

            for each in rem:
                listGroupID_charIDs.remove(each)

            foldername = 'folders'
            if len(listGroupIDs) == 1:
                group = uicore.registry.GetListGroup(listGroupIDs.keys()[0])
                if group:
                    foldername = group['label']
            label = ''
            if delCharIDs and listname:
                label = localization.GetByLabel('UI/PeopleAndPlaces/RemoveMultipleFromAddressbook', removecount=len(delCharIDs))
                if listGroupID_charIDs:
                    label += [', ']
            if listGroupID_charIDs:
                label += localization.GetByLabel('UI/PeopleAndPlaces/RemoveFromFolder', foldername=foldername, removecount=len(listGroupID_charIDs))
            m.append((label, self.RemoveFromListGroup, (listGroupID_charIDs, delCharIDs, listname)))
        if self.sr.node.Get('MenuFunction', None):
            cm = [None]
            cm += self.sr.node.MenuFunction(selected)
            m += cm
        return m

    def ShowInfo(self, *args):
        if self.destroyed:
            return
        sm.GetService('info').ShowInfo(cfg.eveowners.Get(self.charID).typeID, self.charID)

    def GetDragData(self, *args):
        if self and not self.destroyed:
            return self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        else:
            return []

    def OnClick(self, *args):
        if self.destroyed:
            return
        eve.Message('ListEntryClick')
        self.sr.node.scroll.SelectNode(self.sr.node)
        if self.sr.node.Get('OnClick', None):
            self.sr.node.OnClick(self)

    @telemetry.ZONE_METHOD
    def OnDblClick(self, *args):
        if self.destroyed:
            return
        if self.sr.node.Get('OnDblClick', None):
            self.sr.node.OnDblClick(self)
            return
        agentInfo = sm.GetService('agents').GetAgentByID(self.charID)
        if session.stationid and agentInfo:
            sm.GetService('agents').OpenDialogueWindow(self.charID)
            return
        self.ShowInfo()

    def GetHeight(self, *args):
        node, width = args
        node.height = 51
        return node.height

    def RemoveFromListGroup(self, listGroupIDs, charIDs, listname):
        if self.destroyed:
            return
        if listGroupIDs:
            for listGroupID, charID in listGroupIDs:
                uicore.registry.RemoveFromListGroup(listGroupID, charID)

            sm.GetService('addressbook').RefreshWindow()
        if charIDs and listname:
            name = [localization.GetByLabel('UI/AddressBook/RemoveAddressBook1'), cfg.eveowners.Get(charIDs[0]).name][len(charIDs) == 1]
            if eve.Message('WarnDeleteFromAddressbook', {'name': name,
             'type': listname}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return
            sm.GetService('addressbook').DeleteEntryMulti(charIDs, None)

    def OnChatButtonMouseEnter(self, btn, buttonIconOnMouseEnter, *args):
        self.OnMouseEnter()
        buttonIconOnMouseEnter()

    def UpdateAlignment(self, *args, **kwargs):
        alignment = super(AgentEntry, self).UpdateAlignment(*args, **kwargs)
        self.UpdateLabelRightFade()
        return alignment

    def UpdateLabelRightFade(self):
        availableWidth = ReverseScaleDpi(self.displayWidth) - 64 - ReverseScaleDpi(self.sr.missionLabel.displayWidth)
        self.sr.namelabel.SetRightAlphaFade(fadeEnd=availableWidth, maxFadeWidth=20)
        if self.agentChatBtn and self.agentChatBtn.display:
            availableWidth = ReverseScaleDpi(self.displayWidth) - 64 - self.agentChatBtn.width
            self.sr.levelLabel.SetRightAlphaFade(fadeEnd=availableWidth, maxFadeWidth=20)
        else:
            self.sr.levelLabel.SetRightAlphaFade(fadeEnd=0, maxFadeWidth=0)
