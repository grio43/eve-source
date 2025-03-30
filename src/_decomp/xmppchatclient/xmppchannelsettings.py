#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\xmppchannelsettings.py
import logging
from carbonui.control.combo import Combo
from xml.sax.saxutils import escape
import localization
from menu import MenuLabel
from carbon.common.script.sys import service
from carbonui.control.singlelineedits.singleLineEditPassword import SingleLineEditPassword
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.container import Container
from carbonui.util.sortUtil import SortListOfTuples
from chatutil import StripBreaks, GetChannelCategory
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
import carbonui.const as uiconst
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.userentry import User
from eveexceptions import UserError
from eveservices.xmppchat import GetChatService
from xmppchatclient.const import CATEGORY_SYSTEM, CATEGORY_PLAYER, PROXY_CONTROLLED_CATEGORIES
from xmppchatclient.pcownerpickerdialog import PCOwnerPickerDialog
logger = logging.getLogger('xmpp')
DUMMY_NO_CHANGE_PASSWORD = '__no_change__'

class ChannelAccessEntry(User):
    __guid__ = 'listentry.ChannelAccessEntry'

    def GetMenu(self, *args):
        if self.sr.node.canRemove:
            return [(MenuLabel('UI/Chat/RemoveSelected'), self._Remove), None]
        else:
            return [None]

    def _Remove(self, *args):
        scroll = self.sr.node.scroll
        if not scroll:
            return
        selected = [ each.info.ownerID for each in scroll.GetSelectedNodes(self.sr.node) ]
        if selected:
            self.sr.node.RemoveACL(selected)


def RequestOwnerId():
    dlg = PCOwnerPickerDialog.Open()
    dlg.ShowModal()
    ownerId = dlg.ownerID
    return ownerId


def GetFieldsFromConfig(config):
    if not config:
        return None
    qElem = config.find_child_with_tag('query')
    if not qElem:
        return None
    xElem = qElem.find_child_with_tag('x')
    if not xElem:
        return None
    fields = {}
    for child in xElem.children:
        if child.tag != 'field':
            continue
        fieldName = str(child.attributes.get('var'))
        fieldType = child.attributes.get('type')
        if fieldType == 'list-multi':
            value = []
            for grandchild in child.children:
                singleValue = GetElementValue(grandchild)
                if singleValue:
                    value.append(singleValue)

        else:
            valueElem = child.find_child_with_tag('value')
            value = GetElementValue(valueElem)
            if fieldType == 'boolean':
                value = not value == '0'
        if value:
            fields[fieldName] = value

    return fields


def GetElementValue(valueElem):
    if valueElem and valueElem.tag == 'value':
        value = unicode(valueElem.text)
    else:
        value = None
    return value


class ChannelSettingsDlg(Window):
    default_windowID = 'ChannelSettingsDlg'
    default_iconNum = 'res:/UI/Texture/WindowIcons/chatchannel.png'
    default_captionLabelPath = 'UI/Chat/ChannelConfiguration'
    default_minSize = (400, 480)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.channel = attributes.channel
        self.current_config = None
        self.current_displayName = None
        self.generalTab = self._CreateTab()
        self.generalTabInitialized = False
        self.operatorOnly = True
        if not GetChatService().IsOwnerOrOperatorOfChannel(self.channel, ignoreRole=True):
            if eve.session.role & service.ROLE_GML:
                sm.ProxySvc('XmppChatMgr').GrantChannelOwnership(self.channel)
        self.allowedTab = self._CreateTab()
        self.allowedTabInitialized = False
        self.blockedTab = self._CreateTab()
        self.blockedTabInitialized = False
        self.mutedTab = self._CreateTab()
        self.mutedTabInitialized = False
        self.operatorsTab = self._CreateTab()
        self.operatorsTabInitialized = False
        self.ownersTab = self._CreateTab()
        self.ownersTabInitialized = False
        self.standardBtns = ButtonGroup(parent=self.GetMainArea(), btns=[[localization.GetByLabel('UI/Common/Buttons/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.OnCancel,
          (),
          81]], idx=0)
        index = 0
        self.maintabs = TabGroup(name='tabparent', parent=self.GetMainArea(), idx=index)
        propertyPages = [[localization.GetByLabel('UI/Generic/General'),
          self.generalTab,
          self,
          'general']]
        if GetChannelCategory(self.channel) in [CATEGORY_PLAYER, CATEGORY_SYSTEM]:
            propertyPages += [[localization.GetByLabel('UI/Chat/Allowed'),
              self.allowedTab,
              self,
              'allowed'],
             [localization.GetByLabel('UI/Chat/Blocked'),
              self.blockedTab,
              self,
              'blocked'],
             [localization.GetByLabel('UI/Chat/Muted'),
              self.mutedTab,
              self,
              'muted'],
             [localization.GetByLabel('UI/Chat/Operators'),
              self.operatorsTab,
              self,
              'operators'],
             [localization.GetByLabel('UI/Chat/Owners'),
              self.ownersTab,
              self,
              'owners']]
        self.OnGeneralTab()
        self.maintabs.Startup(propertyPages, 'channelconfigurationpanel', autoselecttab=1)
        self.tabHandlers = {'general': (self.generalTab, self.OnGeneralTab),
         'allowed': (self.allowedTab, self.OnAllowedTab),
         'blocked': (self.blockedTab, self.OnBlockedTab),
         'muted': (self.mutedTab, self.OnMutedTab),
         'operators': (self.operatorsTab, self.OnOperatorsTab),
         'owners': (self.ownersTab, self.OnOwnersTab)}

    def _CreateTab(self):
        return Container(name='tab', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, padding=(0, 0, 0, 8))

    def ValidateOK(self):
        if self.generalTabInitialized:
            self.newMotd = StripBreaks(self.motd.GetValue())
            if self.operatorOnly:
                self.newDisplayName = None
                self.newPassword = None
                self.newAccessType = None
                self.newDisplayName = None
            else:
                self.newDisplayName = self.channelName.GetValue().strip()
                self.channelName.SetValue(self.newDisplayName)
                if not self.newDisplayName:
                    eve.Message('ChannelNameEmpty')
                    return False
                if self.newDisplayName == self.current_displayName:
                    self.newDisplayName = None
                self.newPassword = self.password.GetValue(raw=1) or ''
                retypedPassword = self.retyped.GetValue(raw=1) or ''
                if self.newPassword:
                    if self.newPassword != retypedPassword:
                        eve.Message('ChtPasswordMismatch')
                        return False
                    if self.newPassword != self.newPassword.strip():
                        eve.Message('ChtNewPasswordInvalid')
                        return False
                    if len(self.newPassword) < 3 and len(self.newPassword):
                        eve.Message('ChtNewPasswordInvalid')
                        return False
                    if self.newPassword == DUMMY_NO_CHANGE_PASSWORD:
                        self.newPassword = None
                self.newAccessType = self.accessTypeCombo.GetValue()
        else:
            self.newMotd = None
            self.newPassword = None
            self.newAccessType = None
            self.newDisplayName = None
        return True

    def OnOK(self):
        if not self.ValidateOK():
            return
        if self.newMotd is not None:
            GetChatService().SetMotd(self.channel, self.newMotd)
        if not self.operatorOnly:
            config = {}
            if self.newDisplayName is not None:
                config['muc#roomconfig_roomname'] = escape(self.newDisplayName).encode('utf-8')
            if self.newPassword is not None:
                if self.newPassword:
                    config['muc#roomconfig_passwordprotectedroom'] = 1
                    config['muc#roomconfig_roomsecret'] = escape(self.newPassword).encode('utf-8')
                else:
                    config['muc#roomconfig_passwordprotectedroom'] = 0
            if self.newAccessType is not None:
                config['muc#roomconfig_moderatedroom'] = 1
                if self.newAccessType == 'allowed':
                    config['muc#roomconfig_membersonly'] = 0
                    config['muc#roomconfig_allowinvites'] = 1
                    config['members_by_default'] = 1
                elif self.newAccessType == 'moderated':
                    config['muc#roomconfig_membersonly'] = 0
                    config['muc#roomconfig_allowinvites'] = 1
                    config['members_by_default'] = 0
                elif self.newAccessType == 'blocked':
                    config['muc#roomconfig_membersonly'] = 1
                    config['muc#roomconfig_allowinvites'] = 0
                    config['members_by_default'] = 1
            if config:
                self.current_config = config
                if GetChatService().ConfigureChannel(self.channel, config):
                    sm.ScatterEvent('OnRefreshChannels')
                elif self.newDisplayName is not None:
                    raise UserError('LSCCannotRename', {'msg': (const.UE_LOC, 'UI/Chat/ChatSvc/ChannelAlreadyExists')})
                else:
                    raise RuntimeError('ConfigureChannel failed')
            elif self.current_config:
                GetChatService().ConfigureChannel(self.channel, self.current_config)
        self.CloseByUser()

    def OnCancel(self):
        self.CloseByUser()

    def Load(self, tabName):
        tab, handler = self.tabHandlers.get(tabName, (None, None))
        if handler:
            handler()
        for eachTab, eachHandler in self.tabHandlers.itervalues():
            if eachTab is not tab:
                eachTab.state = uiconst.UI_HIDDEN
            else:
                eachTab.state = uiconst.UI_NORMAL

    def OnGeneralTab(self):
        if self.generalTabInitialized:
            return
        config = GetChatService().GetChannelConfig(self.channel)
        features = GetFieldsFromConfig(config)
        if features:
            self.operatorOnly = False
        else:
            self.operatorOnly = True
        self.current_displayName = GetChatService().GetDisplayName(self.channel)
        container = Container(name='container', align=uiconst.TOTOP, parent=self.generalTab, height=18, top=const.defaultPadding)
        EveLabelSmall(text=localization.GetByLabel('UI/Chat/ChannelName'), parent=container, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        channelNameReadonly = not features or GetChannelCategory(self.channel) in PROXY_CONTROLLED_CATEGORIES
        self.channelName = SingleLineEditText(name='channelName', parent=container, setvalue=self.current_displayName, pos=(0, 0, 150, 0), align=uiconst.TORIGHT, maxLength=50, readonly=channelNameReadonly)
        if features:
            if features.get('muc#roomconfig_passwordprotectedroom'):
                password = DUMMY_NO_CHANGE_PASSWORD
            else:
                password = ''
            container = Container(name='container', align=uiconst.TOTOP, parent=self.generalTab, height=18, top=const.defaultPadding)
            EveLabelSmall(text=localization.GetByLabel('UI/Chat/Password'), parent=container, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
            self.password = SingleLineEditPassword(name='password', parent=container, setvalue=password, pos=(0, 0, 150, 0), align=uiconst.TORIGHT, maxLength=20, passwordCharacter=u'\u2022')
            container = Container(name='container', align=uiconst.TOTOP, parent=self.generalTab, height=18, top=const.defaultPadding)
            EveLabelSmall(text=localization.GetByLabel('UI/Chat/RetypePassword'), parent=container, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
            self.retyped = SingleLineEditPassword(name='retyped', parent=container, setvalue=password, pos=(0, 0, 150, 0), align=uiconst.TORIGHT, maxLength=20, passwordCharacter=u'\u2022')
            container = Container(name='container', align=uiconst.TOTOP, parent=self.generalTab, height=18, top=const.defaultPadding)
            EveLabelSmall(text=localization.GetByLabel('UI/Chat/DefaultAccess'), parent=container, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
            modes = [(localization.GetByLabel('UI/Chat/Allowed'), 'allowed'), (localization.GetByLabel('UI/Chat/Moderated'), 'moderated'), (localization.GetByLabel('UI/Chat/Blocked'), 'blocked')]
            self.accessTypeCombo = Combo(label='', parent=container, options=modes, name='combo', align=uiconst.TORIGHT, width=150)
            self.accessTypeCombo.Startup(modes)
            if features.get('muc#roomconfig_membersonly'):
                accessType = 'blocked'
            elif features.get('members_by_default'):
                accessType = 'allowed'
            else:
                accessType = 'moderated'
            self.accessTypeCombo.SelectItemByValue(accessType)
            self.accessTypeCombo.state = uiconst.UI_NORMAL
        container = Container(name='container', align=uiconst.TOALL, parent=self.generalTab, pos=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        EveLabelSmall(text=localization.GetByLabel('UI/Chat/Motd'), parent=container, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        currentMotd = GetChatService().GetMotd(self.channel)
        self.motd = EditPlainText(parent=container, showattributepanel=1, maxLength=4000, setvalue=currentMotd or '', padTop=20)
        self.generalTabInitialized = True

    def OnAllowedTab(self):
        if not self.allowedTabInitialized:
            self.allow = Button(parent=ContainerAutoSize(parent=self.allowedTab, align=uiconst.TOTOP, padBottom=8), label=localization.GetByLabel('UI/Chat/AddToAllowedList'), func=self._Allow, align=uiconst.CENTER)
            self.allowedlist = Scroll(parent=self.allowedTab)
            self.allowedTabInitialized = True
        self.PopulateAllowedList()

    def PopulateAllowedList(self):
        self.allowedlist.Clear()
        allowed = GetChatService().GetUsersWithAffiliation(self.channel, 'member')
        self._PrimeOwners(allowed)
        listentries = []
        for each in allowed:
            charid = int(each)
            info = self._GetOwnerInfo(charid)
            if not info:
                continue
            entry = GetFromClass(ChannelAccessEntry, {'charID': info.ownerID,
             'canRemove': True,
             'info': info,
             'RemoveACL': self._RemoveAllowed})
            listentries.append((info.name.lower(), entry))

        listentries = SortListOfTuples(listentries)
        self.allowedlist.Load(24, listentries)

    def _Allow(self, *args):
        ownerId = RequestOwnerId()
        if ownerId:
            GetChatService().SetAffiliation(self.channel, ownerId, 'member')
            self.PopulateAllowedList()

    def _RemoveAllowed(self, ownerIds):
        for charid in ownerIds:
            GetChatService().SetAffiliation(self.channel, charid, 'none')

        self.PopulateAllowedList()

    def OnBlockedTab(self):
        if not self.blockedTabInitialized:
            self.block = Button(parent=ContainerAutoSize(parent=self.blockedTab, align=uiconst.TOTOP, padBottom=8), label=localization.GetByLabel('UI/Chat/AddToBlockedList'), func=self._Block, align=uiconst.CENTER)
            self.blockedlist = Scroll(parent=self.blockedTab)
            self.blockedTabInitialized = True
        self.PopulateBannedList()

    def PopulateBannedList(self):
        self.blockedlist.Clear()
        OUTCAST = 'outcast'
        BAN = 'ban'
        banned = GetChatService().GetUsersWithAffiliation(self.channel, OUTCAST)
        temporaryBanned = GetChatService().GetUsersWithTemporaryRestriction(self.channel, BAN)
        toPrime = banned + temporaryBanned
        self._PrimeOwners(toPrime)
        listentries = []
        bannedLists = [(OUTCAST, banned), (BAN, temporaryBanned)]
        temporaryBanText = '<color=grey> - %s</color>' % localization.GetByLabel('UI/Chat/TemporaryBan')
        for bannedType, bannedOwners in bannedLists:
            for eachOwnerID in bannedOwners:
                info = self._GetOwnerInfo(eachOwnerID)
                if not info:
                    continue
                label = info.name
                if bannedType == BAN:
                    label += temporaryBanText
                entry = GetFromClass(ChannelAccessEntry, {'label': label,
                 'charID': info.ownerID,
                 'info': info,
                 'canRemove': True,
                 'RemoveACL': self._RemoveBlocked})
                listentries.append((info.name.lower(), entry))

        toLoad = SortListOfTuples(listentries)
        self.blockedlist.Load(24, toLoad)

    def _GetOwnerInfo(self, charID):
        try:
            charID = int(charID)
        except ValueError:
            return

        try:
            return cfg.eveowners.Get(charID)
        except KeyError:
            return

    def _Block(self, *args):
        ownerId = RequestOwnerId()
        if ownerId:
            GetChatService().SetAffiliation(self.channel, ownerId, 'outcast')
            self.PopulateBannedList()

    def _RemoveBlocked(self, ownerIds):
        for char in ownerIds:
            GetChatService().UnbanUserFromChannel(self.channel, char)

        self.PopulateBannedList()

    def OnMutedTab(self):
        if not self.mutedTabInitialized:
            textContainer = Container(name='scroll', parent=self.mutedTab, left=const.defaultPadding, top=const.defaultPadding, align=uiconst.TOTOP, height=22, width=300)
            text = EveLabelSmall(text=localization.GetByLabel('UI/Chat/HowtoMuteHint'), parent=textContainer, align=uiconst.TOALL)
            textContainer.height = text.textheight
            self.mutedlist = Scroll(parent=self.mutedTab)
            self.mutedTabInitialized = True
        self.PopulateMutedList()

    def _RemoveMuted(self, ownerIds):
        for char in ownerIds:
            GetChatService().UnmuteUser(self.channel, char)

        self.PopulateMutedList()

    def PopulateMutedList(self):
        self.mutedlist.Clear()
        listentries = []
        temporaryMuted = GetChatService().GetUsersWithTemporaryRestriction(self.channel, 'mute')
        self._PrimeOwners(temporaryMuted)
        for each in temporaryMuted:
            info = self._GetOwnerInfo(each)
            if not info:
                continue
            entry = GetFromClass(ChannelAccessEntry, {'charID': info.ownerID,
             'info': info,
             'canRemove': True,
             'RemoveACL': self._RemoveMuted})
            listentries.append((info.name.lower, entry))

        listentries = SortListOfTuples(listentries)
        self.mutedlist.Load(24, listentries)

    def _PrimeOwners(self, ownersToPrime):

        def CanPrime(ownerID):
            try:
                int(ownerID)
                return True
            except ValueError:
                return False

        toPrime = filter(CanPrime, ownersToPrime)
        cfg.eveowners.Prime(toPrime)

    def OnOperatorsTab(self):
        if not self.operatorsTabInitialized:
            if not self.operatorOnly:
                self.addOperator = Button(parent=ContainerAutoSize(parent=self.operatorsTab, align=uiconst.TOTOP, padBottom=8), label=localization.GetByLabel('UI/Chat/AddToOperatorList'), func=self._Op, align=uiconst.CENTER)
            self.operatorslist = Scroll(parent=self.operatorsTab)
            self.operatorsTabInitialized = True
        self.PopulateOperatorsList()

    def PopulateOperatorsList(self):
        self.operatorslist.Clear()
        ops = GetChatService().GetUsersWithAffiliation(self.channel, 'admin')
        listentries = []
        self._PrimeOwners(ops)
        for each in ops:
            info = self._GetOwnerInfo(each)
            if not info:
                continue
            entry = GetFromClass(ChannelAccessEntry, {'charID': info.ownerID,
             'info': info,
             'canRemove': not self.operatorOnly,
             'RemoveACL': self._RemoveOp})
            listentries.append((info.name.lower(), entry))

        listentries = SortListOfTuples(listentries)
        self.operatorslist.Load(24, listentries)

    def _Op(self, *args):
        ownerId = RequestOwnerId()
        if ownerId:
            GetChatService().SetAffiliation(self.channel, ownerId, 'admin')
            self.PopulateOperatorsList()

    def _RemoveOp(self, ownerIds):
        for char in ownerIds:
            GetChatService().SetAffiliation(self.channel, char, 'member')

        self.PopulateOperatorsList()

    def OnOwnersTab(self):
        if not self.ownersTabInitialized:
            if not self.operatorOnly:
                self.addOwner = Button(parent=ContainerAutoSize(parent=self.ownersTab, align=uiconst.TOTOP, padBottom=8), label=localization.GetByLabel('UI/Chat/AddToOwnerList'), func=self._Owner, align=uiconst.CENTER)
            self.ownerslist = Scroll(parent=self.ownersTab)
            self.ownersTabInitialized = True
        self.PopulateOwnersList()

    def PopulateOwnersList(self):
        self.ownerslist.Clear()
        owners = GetChatService().GetUsersWithAffiliation(self.channel, 'owner')
        listentries = []
        self._PrimeOwners(owners)
        for each in owners:
            info = self._GetOwnerInfo(each)
            if not info:
                continue
            entry = GetFromClass(ChannelAccessEntry, {'charID': info.ownerID,
             'info': info,
             'canRemove': not self.operatorOnly,
             'RemoveACL': self._RemoveOwner})
            listentries.append((info.name.lower(), entry))

        listentries = SortListOfTuples(listentries)
        self.ownerslist.Load(24, listentries)

    def _Owner(self, *args):
        ownerId = RequestOwnerId()
        if ownerId:
            GetChatService().SetAffiliation(self.channel, ownerId, 'owner')
            self.PopulateOwnersList()

    def _RemoveOwner(self, ownerIds):
        for char in ownerIds:
            GetChatService().SetAffiliation(self.channel, char, 'member')

        self.PopulateOwnersList()
