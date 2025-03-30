#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\xmppchatsvc.py
import json
import logging
import socket
from xml.sax.saxutils import escape, quoteattr
import stackless
from stackless_tracing.attributes import SERVICE_NAME, SERVICE_NAME_PREFIX
import yaml
from collections import OrderedDict
import gametime
import localization
import locks
import uthread2
import carbonui.const as uiconst
import monolithhoneycomb_events as mhe
from bannedwords.client import bannedwords
from carbon.common.script.util.format import FmtDate
from monolithhoneycomb_events.events import CHAT_CLIENT_LOGIN, CHAT_CLIENT_HANDLE_LOGGED_IN, CHAT_CLIENT_HANDLE_CONNECTION_LOST, CHAT_CLIENT_CONNECTION_OBJECT_CREATED
from carbon.common.script.sys import service
from chatutil import IsInvite, GetErrorCode, GetUsersFromResponse, GetChannelCategory, GetInviteReason, GetInviteSender, GetChannelDifferentiator, UpdateChatFilterVariables, IsDecline, GetDeclineReason, GetDeclineSender, GetInvitePassword, TruncateVeryLongText, GetCharacterBannnedExpiry, GetErrorType, GetErrorTextElement
from chatutil.channelnames import IsValidChannelName, GetSessionBasedChannelName
from eve.common.script.sys.idCheckers import IsNPC, IsCharacter, IsCorporation, IsAlliance
from eveexceptions import UserError
from eveexceptions.exceptionEater import ExceptionEater
from eveprefs import prefs
from uihighlighting import UiHighlightDirections
from xmpp import XmppConnection
import xmppchatclient.const as xmppchatConst
from xmppchatclient.chatinvitewindow import PresentChatInviteWindow
from xmppchatclient.xmppchatpassword import ChannelPasswordWindow
from xmppchatclient.xmppchatwindow import XmppChatWindow
from chat.common.util import is_local_chat_suppressed
from chat.common.const import MIGRATED_CHAT_CATEGORIES
from collections import defaultdict
from globalConfig import GetEjabberdAddress
logger = logging.getLogger('xmppchat')
SESSION_CHANGE_CATEGORIES = OrderedDict([('solarsystemid2', xmppchatConst.CATEGORY_LOCAL),
 ('allianceid', xmppchatConst.CATEGORY_ALLIANCE),
 ('corpid', xmppchatConst.CATEGORY_CORP),
 ('fleetid', xmppchatConst.CATEGORY_FLEET),
 ('warfactionid', xmppchatConst.CATEGORY_FACTION)])

class XmppChatService(service.Service):
    __guid__ = 'svc.XmppChat'
    __displayname__ = 'Xmpp Chat Service'
    __exportedcalls__ = {'AskYesNoQuestion': [service.ROLE_SERVICE]}
    __notifyevents__ = ['OnSessionChanged',
     'OnDisconnect',
     'OnCharacterPokedByGM',
     'ProcessSessionReset',
     'OnSessionReset',
     'OnCharacterPermanentlyBanned',
     'OnCharacterTemporarilyBanned',
     'OnCharacterUnbanned']

    def __init__(self):
        super(XmppChatService, self).__init__()
        self.verbose = prefs.GetValue('xmppChatVerbose', False)
        self._has_local_chat_migrated = None
        self.xmppConnection = None
        self.hostname = None
        self.ejabberd_address = None
        self.messageWindows = {}
        self.groupChatWindows = {}
        self.myName = None
        self.charsToPrime = set()
        self.myPendingPrivateChats = {}
        self.myPendingInvites = {}
        self.pendingJoins = []
        self.outstandingJoins = {}
        self.channelJoinsInProgress = set()
        self.isReconnecting = False
        self.chatFilters = None
        self.userData = {}
        self.translatedMsgText = localization.GetByLabel('UI/Common/Message')
        self.hasLoggedInOnce = False
        self.memberRolesByChannels = defaultdict(dict)
        self.isDoingLogoff = False
        self._threads = []
        self.banExpiry = xmppchatConst.BAN_EXPIRY_STATUS_NONE

    def Run(self, memStream = None):
        self.state = service.SERVICE_RUNNING

    def UpdateLocalChatMigrated(self, local_chat_migrated):
        if local_chat_migrated == self._has_local_chat_migrated:
            return
        self._has_local_chat_migrated = local_chat_migrated
        if not session.charid:
            return
        channelName = GetSessionBasedChannelName(xmppchatConst.CATEGORY_LOCAL, session.solarsystemid2)
        if self._has_local_chat_migrated:
            self.CloseChannelWindow(channelName)
        else:
            self.GetOrCreateGroupChatWindow(channelName)

    def _IsCategoryMigrated(self, category):
        return self._has_local_chat_migrated and category in MIGRATED_CHAT_CATEGORIES

    def HandleLoggingIn(self):
        uthread2.start_tasklet(self.Login)
        uthread2.start_tasklet(self.InitChatFilters)

    def IsCharacterBanned(self):
        return self.banExpiry == xmppchatConst.BAN_EXPIRY_STATUS_NEVER or gametime.GetWallclockTime() <= self.banExpiry

    def OnCharacterPermanentlyBanned(self):
        self._CharacterBanned(xmppchatConst.BAN_EXPIRY_STATUS_NEVER)

    def OnCharacterTemporarilyBanned(self, banExpiry):
        self._CharacterBanned(banExpiry)

    def _CharacterBanned(self, banExpiry):
        self._SetBanExpiry(banExpiry)
        for window in self.groupChatWindows.values():
            window.OnCharacterBannedNotify()

        eve.Message('CharacterBannedFromChat')

    def _SetBanExpiry(self, banExpiry):
        self.banExpiry = banExpiry

    def OnCharacterUnbanned(self):
        self._SetBanExpiry(xmppchatConst.BAN_EXPIRY_STATUS_NONE)

    def GetCharacterBannedMessage(self):
        if self.banExpiry == xmppchatConst.BAN_EXPIRY_STATUS_NEVER:
            return localization.GetByLabel('UI/Chat/ChatSvc/CharacterPermanentlyBanned')
        if self.banExpiry > 0:
            return localization.GetByLabel('UI/Chat/ChatSvc/CharacterTemporarilyBanned', datetime=FmtDate(self.banExpiry, 'll'))
        raise RuntimeError('Character is not banned')

    def OnSessionChanged(self, isremote, sess, changes):
        if 'charid' in changes and changes['charid'][1] is not None:
            self.HandleLoggingIn()
        channelsToLeave = []
        for category, prefix in SESSION_CHANGE_CATEGORIES.iteritems():
            if self._IsCategoryMigrated(category):
                continue
            if category in changes:
                old, _new = changes[category]
                if old:
                    channelName = GetSessionBasedChannelName(prefix, old)
                    channelsToLeave.append(channelName)

        uthread2.start_tasklet(self._LeaveChannels, channelsToLeave)
        uthread2.start_tasklet(self._HandleLocalSuppressedSessionChange, changes)

    def ProcessSessionReset(self):
        self.isDoingLogoff = True

    def OnSessionReset(self):
        self.xmppConnection.Disconnect()
        self.xmppConnection = None
        self.messageWindows = {}
        self.groupChatWindows = {}
        self.myName = None
        self.charsToPrime = set()
        self.myPendingPrivateChats = {}
        self.myPendingInvites = {}
        self.pendingJoins = []
        self.outstandingJoins = {}
        self.channelJoinsInProgress = set()
        self.chatFilters = None
        self.userData = {}
        self.memberRolesByChannels = defaultdict(dict)
        self.pendingJoins = []
        threads = self._threads[:]
        self._threads = []
        for t in threads:
            t.kill()

        self.isDoingLogoff = False
        self.banExpiry = xmppchatConst.BAN_EXPIRY_STATUS_NONE

    def _HandleLocalSuppressedSessionChange(self, changes):
        if 'solarsystemid2' in changes:
            newSolarSystemID = changes['solarsystemid2'][1]
            if is_local_chat_suppressed(newSolarSystemID):
                self.GetOrCreateGroupChatWindow(xmppchatConst.CATEGORY_LOCAL, setWindowsChannel=False)
                channelName = GetSessionBasedChannelName(xmppchatConst.CATEGORY_LOCAL_SUPPRESSED, newSolarSystemID)
                self.JoinChannel(channelName)

    def OnDisconnect(self, reason = 0, msg = ''):
        if self.xmppConnection:
            self.xmppConnection.Disconnect()

    def TryJoinPlayerChannelsFromOldSettings_Temp(self):
        if settings.char.ui.Get('chat_OldChannelsMigrated', False):
            return
        oldChannels = settings.char.ui.Get('lscengine_mychannels', [])
        channelsToAttemptToJoin = []
        for channelID in oldChannels:
            if not isinstance(channelID, int):
                continue
            if 0 <= channelID <= xmppchatConst.SYSTEM_CHANNEL_MAX_CHANNELID:
                continue
            newChannelID = '%s_%s' % (xmppchatConst.CATEGORY_PLAYER, channelID)
            channelsToAttemptToJoin.append(newChannelID)

        if channelsToAttemptToJoin:
            uthread2.start_tasklet(self._JoinChannels, channelsToAttemptToJoin)
        settings.char.ui.Set('chat_OldChannelsMigrated', True)

    def _LeaveChannels(self, channelsToLeave):
        for each in channelsToLeave:
            self.LeaveChannel(each)

    def _JoinChannels(self, channelsToJoin):
        for each in channelsToJoin:
            if not self.JoinChannel(each):
                self._RemoveWindowForChannel(each)

    def _RemoveWindowForChannel(self, each):
        window = self.groupChatWindows.pop(each, None)
        if window:
            window.access_lost = True
            window.Close()

    def Login(self):
        self._CreateConnection()
        self.myName = self.GetUserName()
        logger.info('Logging in as %s on %s', self.myName, self.xmppConnection.ejabberd_address)
        sm.GetService('settings').LoadCharSettingsIfNeeded()
        channelListInSettings = settings.char.ui.Get('chatchannels', [])
        self.CreateSessionChannelWindows()
        self._RestoreChannelList(channelListInSettings)
        while True:
            try:
                self.xmppConnection.Connect(self.myName, 'eveclient')
                self.hasLoggedInOnce = True
                self.send_honey_event(CHAT_CLIENT_LOGIN)
                break
            except socket.error as e:
                msg = 'Error connecting to {0}'.format(self.xmppConnection.ejabberd_address)
                logger.exception(msg)
                ret = eve.Message('RetryChatServerConnection', {'server': self.xmppConnection.ejabberd_address,
                 'port': self.xmppConnection.port}, uiconst.YESNO)
                if ret != uiconst.ID_YES:
                    self._DisableChat()
                    self.send_honey_event(CHAT_CLIENT_LOGIN, {'error': True,
                     'eve.xmpp.connection.retry': False})
                    return
                self.send_honey_event(CHAT_CLIENT_LOGIN, {'error': True,
                 'eve.xmpp.connection.retry': True})

    def _DisableChat(self):
        for window in self.groupChatWindows.values():
            try:
                msg = localization.GetByLabel('UI/Chat/ChatSvc/NoChatServer', server=self.xmppConnection.ejabberd_address, port=self.xmppConnection.port)
                window.Receive(const.ownerSystem, msg)
            except Exception:
                pass

    def _CreateConnection(self):
        self.hostname = self.XmppChatMgr.Hostname()
        self.ejabberd_address = self.get_ejabberd_address()
        if self.xmppConnection is not None:
            self.xmppConnection.hostname = self.hostname
            self.xmppConnection.ejabberd_address = self.ejabberd_address
            return
        if self.ejabberd_address is None:
            self.send_honey_event(CHAT_CLIENT_CONNECTION_OBJECT_CREATED, {'error': True})
            logger.exception('No ejabberd address configured for client.')
            return
        logger.info('xmppchatsvc._CreateConnection::ejabberd_address={}, hostname={}'.format(self.ejabberd_address, self.hostname))
        self.xmppConnection = XmppConnection(hostname=self.hostname, ejabberd_address=self.ejabberd_address)
        self.xmppConnection.handle_message = self.HandleXmppMessage
        self.xmppConnection.handle_logged_in = self.HandleXmppLoggedIn
        self.xmppConnection.handle_connection_lost = self.HandleXmppConnectionLost
        self.xmppConnection.handle_presence = self.HandleXmppPresence
        self.xmppConnection.handle_stream_error = self.HandleStreamError
        self.xmppConnection.get_password = self.GetAuthenticationToken
        self.xmppConnection.verbose = self.verbose
        self.send_honey_event(CHAT_CLIENT_CONNECTION_OBJECT_CREATED, {'eve.xmpp.connection.created.id': id(self.xmppConnection)})

    def get_ejabberd_address(self):
        address = GetEjabberdAddress(sm.GetService('machoNet'))
        if address is not None and len(address) > 0:
            return address
        return self.XmppChatMgr.GetDeprecatedPrefsFallback()

    def GetUserName(self):
        return self.GetUserNameFromCharId(session.charid)

    def GetAuthenticationToken(self):
        token = sm.RemoteSvc('chatAuthenticationService').GetAuthenticationToken()
        if token:
            return token
        else:
            logger.debug("Can't get token from authentication service - are you on a local server?")
            return 'ejabberd'

    def SendGroupChat(self, group, messageText):
        sm.ScatterEvent('OnClientEvent_ChatMessageSent')
        if not self.xmppConnection or not self.xmppConnection.IsConnected():
            self.Login()
        if not self.xmppConnection or not self.xmppConnection.IsConnected():
            logger.warning("Can't send message when not connected")
            return
        if group in self.myPendingPrivateChats:
            other, isInvited = self.myPendingPrivateChats[group]
            if not isInvited:
                self.myPendingPrivateChats[group] = (other, True)
                roomName = self.GetFullRoomName(group)
                self.xmppConnection.Invite(self.GetUserNameFromCharId(other), roomName, 'Private chat')
        receiver = self.GetFullRoomName(group)
        messageText = TruncateVeryLongText(messageText)
        return self.xmppConnection.GroupChat(receiver, messageText)

    def _JoinSystemChannels(self):
        channelsToJoin = None
        while channelsToJoin is None:
            if self.verbose:
                logger.debug('Calling ResyncSystemChannelAccess on proxy')
            channelsToJoin = self.XmppChatMgr.ResyncSystemChannelAccess()
            if not channelsToJoin:
                uthread2.sleep(5)

        categoriesToJoin = set()
        for each in channelsToJoin:
            self.JoinChannel(each)
            with ExceptionEater('_JoinSystemChannels'):
                category = GetChannelCategory(each)
                if category in (xmppchatConst.CATEGORY_LOCAL_SUPPRESSED,
                 xmppchatConst.CATEGORY_WORMHOLE,
                 xmppchatConst.CATEGORY_NULLSEC,
                 xmppchatConst.CATEGORY_TRIGLAVIAN):
                    category = xmppchatConst.CATEGORY_LOCAL
                categoriesToJoin.add(category)

        uthread2.start_tasklet(self._JoinChannels, channelsToJoin)
        windowsToClose = set(SESSION_CHANGE_CATEGORIES.values()) - categoriesToJoin
        for eachWindowName in windowsToClose:
            self._RemoveWindowForChannel(eachWindowName)

    def HandleXmppLoggedIn(self):
        self.send_honey_event(CHAT_CLIENT_HANDLE_LOGGED_IN)
        logger.info('Logged in to %s at %s as %s', self.xmppConnection.hostname, self.xmppConnection.ejabberd_address, self.xmppConnection.username)
        channelsToJoin = self.pendingJoins
        self.pendingJoins = []
        for window in self.groupChatWindows.values():
            uthread2.start_tasklet(window.SetCaptionAsDisplayName)
            channel = window.receiver
            category = GetChannelCategory(channel)
            if category in [xmppchatConst.CATEGORY_PRIVATE,
             xmppchatConst.CATEGORY_PLAYER,
             xmppchatConst.CATEGORY_BOT,
             xmppchatConst.CATEGORY_SYSTEM]:
                channelsToJoin.append(channel)

        self._threads.append(uthread2.start_tasklet(self._JoinChannels, channelsToJoin))
        self._threads.append(uthread2.start_tasklet(self._JoinSystemChannels))
        self._threads.append(uthread2.start_tasklet(self.TryJoinPlayerChannelsFromOldSettings_Temp))
        if session.role & service.ROLE_NEWBIE:
            self._threads.append(uthread2.start_tasklet(self.JoinRookieHelpChannel))
        if self.isReconnecting:
            for window in self.groupChatWindows.values():
                window.Receive(const.ownerSystem, localization.GetByLabel('UI/Chat/ChatSvc/ReconnectedToChatServer'))
                window.ResetAfterReconnect()

            self.isReconnecting = False
        sm.ScatterEvent('OnRefreshChannels')

    def HandleXmppConnectionLost(self):
        logger.warning('Connection to chat server lost\n%s\n%s\n%s', self.xmppConnection.hostname, self.xmppConnection.ejabberd_address, self.xmppConnection.username)
        self.send_honey_event(CHAT_CLIENT_HANDLE_CONNECTION_LOST)
        if self.isReconnecting or session.charid is None:
            return
        for window in self.groupChatWindows.values():
            try:
                window.Receive(const.ownerSystem, localization.GetByLabel('UI/Chat/ChatSvc/ConnectionChatServerLost'))
            except Exception:
                pass

        self.pendingJoins = []
        self.channelJoinsInProgress.clear()
        for each in self.outstandingJoins.itervalues():
            each.send(None)

        self.outstandingJoins.clear()
        self.isReconnecting = True

    def HandleXmppMessage(self, response):
        sender = response.attributes.getValue('from')
        what = response.attributes.get('type', '')
        if what == 'groupchat':
            self._HandleGroupchat(sender, response)
        elif what == 'error':
            self._HandleMessageError(sender, response)
        else:
            uthread2.start_tasklet(self._HandleMessage, sender, response)

    def _HandleMessageError(self, sender, response):
        errorType = GetErrorType(response)
        if errorType == xmppchatConst.ERROR_CHAT_BANNED:
            textElement = GetErrorTextElement(response)
            if textElement:
                values = textElement.text.split(' ', 2)
                if len(values) >= 2 and values[0] == 'mod_ban':
                    self._SetBanExpiry(GetCharacterBannnedExpiry(values[1]))
                    channelname, _ = sender.split('@', 1)
                    window = self.GetGroupChatWindow(channelname)
                    if window:
                        window.OnCharacterBannedNotify()
                    return
        errorCode = GetErrorCode(response)
        if errorCode == xmppchatConst.ERROR_CHANNEL_UNAVAILABLE:
            raise UserError('LSCCannotSendMessage', {'msg': localization.GetByLabel('UI/Chat/ChatEngine/YouAreNotAbleToSpeak')})
        elif errorCode == xmppchatConst.ERROR_LACKING_CONTROL_RIGHTS:
            if IsInvite(response):
                raise UserError('LSCCannotAccessControl', {'msg': (101, 'UI/Chat/ChatSvc/YouDontHavePriviledgeToAccessControl')})
        elif errorCode == xmppchatConst.ERROR_CONSTRAINED:
            text = 'Rate limited'
            errorElem = response.find_child_with_tag('error')
            if errorElem:
                textElem = errorElem.find_child_with_tag('text')
                text = textElem.text
            logger.warning(text)
            channelname, rest = sender.split('@', 1)
            window = self.GetGroupChatWindow(channelname)
            if window:
                window.HandleErrorResponse(response)
            return
        logger.warning('Error response: %s', response.toXml())

    def _HandleGroupchat(self, sender, response):
        group, rest = sender.split('@', 1)
        senderparts = rest.split('/')
        if len(senderparts) > 1:
            sender = senderparts[1]
        else:
            sender = 'admin'
        if GetChannelCategory(group) == xmppchatConst.CATEGORY_LOCAL:
            if GetChannelDifferentiator(group) != str(session.solarsystemid2):
                return
        window = self.GetOrCreateGroupChatWindow(group)
        if window is None or window.receiver != group:
            return
        body = response.find_child_with_tag('body')
        if body and body.text is not None:
            text = body.text
            if sender == 'admin':
                self._HandleMessageFromAdmin(text, window)
            else:
                senderID = int(sender)
                userdata = self.GetUserData(senderID)
                addressBookSvc = sm.GetService('addressbook')
                isBlocked = addressBookSvc.IsBlocked(senderID) or addressBookSvc.IsBlocked(userdata.get('corpid')) or addressBookSvc.IsBlocked(userdata.get('allianceid'))
                if not isBlocked:
                    isBlocked = sm.GetService('chat').is_reported_spammer(senderID)
                if not isBlocked:
                    msg_id = response.attributes.get('id')
                    text = TruncateVeryLongText(text)
                    window.Receive(senderID, text, msg_id=msg_id)
        subject = response.find_child_with_tag('subject')
        if subject:
            if self.verbose:
                logger.debug("PAT: _HandleGroupchat 'subject' (motd) change with sender=%s, response=%s", sender, response)
            if sender == 'admin':
                sender = None
            text = subject.text
            window.SetMotd(sender, text)
        x = response.find_child_with_tag('x')
        if x:
            status = x.find_child_with_tag('status')
            if status:
                if status.attributes.get('code', 0) == '104':
                    if self.verbose:
                        logger.debug('Config changed for %s', group)
                    window.SetCaptionAsDisplayName()
                    msg = localization.GetByLabel('UI/Chat/ChannelConfigChanged')
                    window.Receive(const.ownerSystem, msg)

    def _HandleMessageFromAdmin(self, text, window):
        try:
            data = json.loads(text)
            if self.verbose:
                logger.debug('Message from admin:\n{0}'.format(data))
            cmd = data['cmd']
            who = data['charid']
            if cmd == 'join':
                userdata = data['userdata']
                infoLine = userdata.get('info')
                if infoLine:
                    self._PopulateEveownersFromInfo(who, infoLine)
                    del userdata['info']
                self.userData[who] = userdata
                window.CharacterJoinedChannel(who)
            elif cmd == 'leave':
                window.CharacterLeftChannel(who)
            elif cmd == 'speak':
                messageText = data['messageText']
                window.Receive(who, messageText)
            elif cmd == 'refresh_char':
                charID = data['charid']
                logger.debug('info on char %s is stale', charID)
                if charID == session.charid:
                    sm.GetService('stateSvc').NotifyOnStateSetupChange('flagState')
                else:
                    sm.ScatterEvent('OnCharStateChanged', charID, data)
        except ValueError:
            logger.warning('Invalid message from admin: %s', text)

    def _HandleMessage(self, sender, response):
        channel_name = sender.split('@')[0]
        if IsInvite(response):
            self._HandleInvite(channel_name, response)
        elif IsDecline(response):
            self._HandleDecline(channel_name, response)

    def _HandleInvite(self, channel_name, response):
        inviteDetails = GetInviteReason(response)
        sender = GetInviteSender(response)
        if self.verbose:
            logger.debug('Channel invite from %s to %s: %s', sender, channel_name, inviteDetails)
        if sender == 'admin':
            uthread2.start_tasklet(self.JoinChannel, channel_name)
        else:
            uthread2.start_tasklet(self._HandleOptionalInvite, sender, channel_name, response)

    def _HandleOptionalInvite(self, sender, channel_name, response):
        if self._AcceptInvitation(sender, channel_name):
            password = GetInvitePassword(response)
            if password:
                settings.user.ui.Set('%sPassword' % channel_name, password)
            self.JoinChannel(channel_name)

    def _AcceptInvitation(self, sender, channel_name):
        try:
            senderId = int(sender)
        except ValueError:
            logger.warning('Not a valid user id: %s', sender)
            return False

        if sm.GetService('addressbook').IsBlocked(senderId):
            if self.verbose:
                logger.debug('%s is blocked', senderId)
            self.RejectInvite(sender, channel_name, 'blocked')
            return False
        if settings.user.ui.Get('autoRejectInvitations', 0):
            if self.verbose:
                logger.debug('Auto-reject invitations enabled')
            self.RejectInvite(sender, channel_name, 'rejected')
            return False
        if sm.GetService('addressbook').IsInAddressBook(senderId, 'contact'):
            if self.verbose:
                logger.debug('%s is in address book - accepting', senderId)
            return True
        if self.IsJoined(channel_name):
            if self.verbose:
                logger.debug('Already in channel %s', channel_name)
            return False
        sm.GetService('logger').AddText(localization.GetByLabel('UI/Chat/InvitedToConversation', inviter=senderId))
        accepted, extra = PresentChatInviteWindow(senderId)
        if not accepted:
            if extra == 'block':
                self.RejectInvite(sender, channel_name, 'rejected_and_blocked')
            else:
                self.RejectInvite(sender, channel_name, 'rejected')
        return accepted

    def _HandleDecline(self, channel_name, response):
        who = GetDeclineSender(response)
        try:
            who = int(who)
        except ValueError:
            pass

        if who not in self.myPendingInvites:
            return
        del self.myPendingInvites[who]
        if channel_name in self.myPendingPrivateChats:
            self.CloseChannelWindow(channel_name)
        reason = GetDeclineReason(response)
        if self.verbose:
            logger.debug('Invite from %s was declined: %s', who, reason)
        if reason == 'rejected':
            raise UserError('ChtRejected', {'char': who})
        elif reason == 'blocked':
            raise UserError('ChtCharNotReachable', {'char': who})
        elif reason == 'rejected_and_blocked':
            raise UserError('ChtBlockedNow', {'char': who})

    def HandleXmppPresence(self, response):
        if self.isDoingLogoff:
            return
        self._HandleXmppPresence(response)

    def _HandleXmppPresence(self, response):
        if 'id' in response.attributes:
            response_id = response.attributes['id']
            if response_id in self.outstandingJoins:
                channel = self.outstandingJoins[response_id]
                del self.outstandingJoins[response_id]
                channel.send(response)
        who = response.attributes['from']
        user, domain = who.split('@', 1)
        if domain.startswith('conference.'):
            channel = user
            category = GetChannelCategory(channel)
            character = domain.split('/')[1]
            try:
                charid = int(character)
            except ValueError:
                charid = character

            if charid == 'admin':
                return
            if category in [xmppchatConst.CATEGORY_WORMHOLE, xmppchatConst.CATEGORY_NULLSEC, xmppchatConst.CATEGORY_TRIGLAVIAN]:
                if charid == session.charid:
                    return
            if charid == 'viking':
                self._UnpackVikingPresence(channel, response)
                return
            other, isInvited = self.myPendingPrivateChats.get(channel, (None, False))
            if other == charid:
                del self.myPendingPrivateChats[channel]
            channelForPendingInvite = self.myPendingInvites.get(charid)
            if channelForPendingInvite and channelForPendingInvite == channel:
                del self.myPendingInvites[charid]
                window = self.GetGroupChatWindow(channel)
            presenceType = response.attributes.get('type', None)
            if self.verbose:
                logger.debug('Presence type: %s', presenceType)
            if presenceType in ('unavailable', 'leave'):
                if charid != session.charid:
                    if category in xmppchatConst.CHANNELS_WITH_SPECIAL_PRESENCE_HANDLING:
                        return
                    window = self.GetGroupChatWindow(channel)
                    if window and window.receiver == channel:
                        window.CharacterLeftChannel(charid)
                else:
                    category = GetChannelCategory(channel)
                    if category not in xmppchatConst.UNCLOSABLE_CHAT_WNDS:
                        self.CloseChannelWindow(channel)
                self.memberRolesByChannels[channel].pop(charid, None)
            elif presenceType is None:
                userData = self._GetPresenceUserData(charid, response)
                if userData:
                    self.userData[charid] = userData
                if self.verbose:
                    logger.debug('User data for %s: %s', charid, userData)
                self._HandleRoleChange(channel, charid, response)
                window = self.GetOrCreateGroupChatWindow(channel)
                if window and window.receiver == channel:
                    self._AddCharacterToChannelWindow(window, charid)
                memberRole = self.GetRoleFromResponse(response)
                if memberRole:
                    self.memberRolesByChannels[channel][charid] = memberRole
                else:
                    self.memberRolesByChannels[channel].pop(charid, None)
            elif presenceType == 'error':
                errorCode = GetErrorCode(response)
                if errorCode == xmppchatConst.ERROR_CHANNEL_UNAVAILABLE:
                    eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Chat/ChatSvc/ChannelUnavailable')})
            else:
                raise RuntimeError('Unhandled presence type')

    def _UnpackVikingPresence(self, channel, packet):
        window = self.GetOrCreateGroupChatWindow(channel)
        if window is None or window.receiver != channel:
            return
        for vp in packet.children:
            userData = {}
            for key in ['corpid',
             'allianceid',
             'warfactionid',
             'typeid']:
                try:
                    value = int(vp.attributes.get(key, 0))
                except ValueError:
                    value = 0

                userData[key] = value

            try:
                value = long(vp.attributes.get('role', 0L))
            except ValueError:
                value = 0L

            userData['role'] = value
            try:
                infoLine = vp.attributes.get('info')
                charid = json.loads(infoLine)[0]
                self._PopulateEveownersFromInfo(charid, infoLine)
            except (TypeError, IndexError):
                logger.warning('Skipping a bad chat viking presence record. Channel: %s', channel)
                continue

            if userData:
                self.userData[charid] = userData
            self._AddCharacterToChannelWindow(window, charid)
            self.memberRolesByChannels[channel][charid] = 'participant'

    def _AddCharacterToChannelWindow(self, window, charID):
        charID = int(charID)
        if cfg.eveowners.GetIfExists(charID):
            self._DoAddCharToWindow(charID, window)
            return
        self.charsToPrime.add(charID)
        with locks.TempLock('xmppChatPrimingCharForChannel'):
            isPrimed = cfg.eveowners.GetIfExists(charID)
            if not isPrimed:
                charsToPrime = self.charsToPrime.copy()
                self.charsToPrime.clear()
                cfg.eveowners.Prime(charsToPrime)
                uthread2.sleep(0.1)
        self._DoAddCharToWindow(charID, window)

    def _DoAddCharToWindow(self, charID, window):
        if window and not window.destroyed:
            window.CharacterJoinedChannel(charID)

    def _HandleRoleChange(self, channel, charid, response):
        presenceItem = self._GetPresenceItem(response)
        if presenceItem:
            window = self.GetOrCreateGroupChatWindow(channel)
            if window is None:
                return
            reason = self._GetPresenceReason(presenceItem)
            user = self._GetUserFromJidAttribute(presenceItem)
            if not user:
                user = charid
            role = presenceItem.attributes.get('role', None)
            if role == 'visitor':
                if not window.IsCharacterMuted(user):
                    if self.verbose:
                        logger.debug('User is being muted\n%s', response.toXml())
                    window.SetCharacterMuted(user, reason)
            elif role == 'participant':
                if window.IsCharacterMuted(user):
                    if self.verbose:
                        logger.debug('User is no longer muted\n%s', response.toXml())
                    window.SetCharacterUnmuted(user)

    def _GetPresenceUserData(self, charid, presenceItem):
        userDataElem = presenceItem.find_child_with_tag('eve_user_data')
        userData = {}
        if userDataElem:
            for key in ['corpid',
             'allianceid',
             'warfactionid',
             'typeid']:
                try:
                    value = int(userDataElem.attributes.get(key, 0))
                except ValueError:
                    value = 0

                userData[key] = value

            try:
                value = long(userDataElem.attributes.get('role', 0L))
            except ValueError:
                value = 0L

            userData['role'] = value
            infoLine = userDataElem.attributes.get('info')
            self._PopulateEveownersFromInfo(charid, infoLine)
        return userData

    def _PopulateEveownersFromInfo(self, charid, infoLine):
        if charid not in cfg.eveowners:
            if infoLine:
                info = json.loads(infoLine)
                cfg.eveowners.Hint(charid, info)

    def _GetPresenceReason(self, presenceItem):
        reasonElem = presenceItem.find_child_with_tag('reason')
        if reasonElem:
            reason = reasonElem.text
        else:
            reason = None
        return reason

    def GetRoleFromResponse(self, response):
        presenceItem = self._GetPresenceItem(response)
        return presenceItem.attributes.get('role', None)

    def _GetPresenceItem(self, response):
        presenceItem = None
        x = response.find_child_with_tag('x')
        if x:
            xmlns = x.attributes['xmlns']
            if xmlns == 'http://jabber.org/protocol/muc#user':
                item = x.find_child_with_tag('item')
                if item:
                    presenceItem = item
        return presenceItem

    def _GetUserFromJidAttribute(self, item):
        user = None
        jid = item.attributes.get('jid', None)
        if jid:
            user = jid.split('@')[0]
            try:
                user = int(user)
            except ValueError:
                pass

        return user

    def HandleStreamError(self, state, response):
        child = response.children[0]
        if child.tag == 'host-unknown':
            logger.error('Virtual host has not been set up for %s', self.hostname)
            self.xmppConnection.Disconnect()

    def GetOrCreateGroupChatWindow(self, channel, setWindowsChannel = True):
        window = self.GetGroupChatWindow(channel)
        if not window:
            windowName = self.GetWindowNameForGroup(channel)
            if self._IsCategoryMigrated(windowName):
                return
            stackless_channel = stackless.channel()
            self.groupChatWindows[windowName] = stackless_channel
            try:
                if self.verbose:
                    logger.debug('Creating window for %s', channel)
                displayName = self.GetDisplayName(channel)
                windowId = 'chatchannel_%s' % windowName
                window = XmppChatWindow(receiver=channel, isGroupChat=True, channel=channel, name=windowName, caption=displayName, windowID=windowId, check_open_minimized=True)
                window.verbose = self.verbose
                self.groupChatWindows[windowName] = window
            finally:
                if self.verbose:
                    logger.debug('Window for %s has been created', channel)
                while stackless_channel.balance < 0:
                    stackless_channel.send(window)

                if self.verbose:
                    logger.debug('Channels waiting for %s have been notified', channel)

            uthread2.start_tasklet(self.StoreChannelList)
        if setWindowsChannel:
            window.SetChannel(channel)
        return window

    def GetGroupChatWindow(self, group):
        windowName = self.GetWindowNameForGroup(group)
        window = self.groupChatWindows.get(windowName, None)
        if type(window) == stackless.channel:
            if self.verbose:
                logger.debug('Waiting for window for %s', group)
            window = window.receive()
        if window and window.destroyed:
            del self.groupChatWindows[windowName]
            window = None
        return window

    def GetWindowNameForGroup(self, group):
        parts = group.split('_')
        try:
            windowName = parts[0]
        except IndexError:
            windowName = group

        if windowName in [xmppchatConst.CATEGORY_PRIVATE,
         xmppchatConst.CATEGORY_PLAYER,
         xmppchatConst.CATEGORY_BOT,
         xmppchatConst.CATEGORY_SYSTEM]:
            windowName = group
        if windowName in [xmppchatConst.CATEGORY_LOCAL_SUPPRESSED,
         xmppchatConst.CATEGORY_WORMHOLE,
         xmppchatConst.CATEGORY_NULLSEC,
         xmppchatConst.CATEGORY_TRIGLAVIAN]:
            windowName = xmppchatConst.CATEGORY_LOCAL
        return windowName

    def GetChannels(self):
        if not self.xmppConnection:
            return []
        channels = []
        playerChannels = set()
        to = 'conference.{0}'.format(self.hostname)
        queryTemplate = "<query xmlns='http://jabber.org/protocol/disco#items' node='forme'></query>"
        initialQuery = queryTemplate.format('')
        response = self.xmppConnection.IssueRequest(initialQuery, 'get', to=to, method_tag='get_channels')
        response_channels = []
        try:
            queryNode = response.children[0]
            response_channels = queryNode.children
        except AttributeError:
            logger.error('GetChannel request returned nothing')

        for item in response_channels:
            jid = item.attributes.get('jid', None)
            if jid is None:
                logger.error('Error with getting jid')
                continue
            if item.tag == 'item':
                channel = jid.split('@')[0]
                name = item.attributes.get('name', '')
                affiliation = item.attributes.get('node')
                channels.append((channel, name, affiliation))
                category = GetChannelCategory(channel)
                if category == xmppchatConst.CATEGORY_PLAYER:
                    playerChannels.add(channel)

        playerChannelsJoined = settings.user.ui.Get('chatPlayerChannelsJoined', {})
        for pc, displayName in playerChannelsJoined.iteritems():
            if pc not in playerChannels and displayName:
                channels.append((pc, displayName))

        return channels

    def GetNumChannelOccupants(self, channelName):
        if not self.xmppConnection:
            return 0
        query = "<query xmlns='http://jabber.org/protocol/disco#info'/>"
        roomName = self.GetFullRoomName(channelName)
        response = self.xmppConnection.IssueRequest(query, 'get', to=roomName, method_tag='get_num_channel_occupants')
        if response and response.attributes.get('type') == 'result':
            num_occupants = self._GetNumOccupantsFromInfoQuery(response)
        else:
            num_occupants = 0
        return num_occupants

    def GetChannelByDisplayName(self, displayName):
        channels = []
        if not self.xmppConnection:
            return channels
        to = 'conference.{0}'.format(self.hostname)
        queryTemplate = "<query xmlns='http://jabber.org/protocol/disco#items' node={0}></query>"
        node = 'byname/' + escape(displayName).encode('utf-8')
        quoted_node = quoteattr(node)
        initialQuery = queryTemplate.format(quoted_node)
        response = self.xmppConnection.IssueRequest(initialQuery, 'get', to=to, method_tag='get_channel_by_display_name')
        queryNode = response.children[0]
        for item in queryNode.children:
            if item.tag == 'item':
                channel = item.attributes['jid'].split('@')[0]
                name = item.attributes['name']
                channels.append((channel, name))

        return channels

    def GetMembersWithNoRole(self, channel):
        query = "<query xmlns='http://jabber.org/protocol/disco#items' node='norole'></query>"
        roomName = self.GetFullRoomName(channel)
        response = self.xmppConnection.IssueRequest(query, 'get', to=roomName, method_tag='get_members_with_no_role')
        queryNode = response.children[0]
        chars = []
        for item in queryNode.children:
            if item.tag == 'item':
                name = item.attributes['name']
                try:
                    name = int(name)
                except ValueError:
                    pass

                chars.append(name)

        return chars

    def JoinRookieHelpChannel(self):
        self.JoinChannel(self.XmppChatMgr.GetRookieChannel())

    def JoinHelpChannelForLanguage(self, languageID):
        self.JoinChannel(self.XmppChatMgr.GetHelpChannel(languageID))

    def JoinHelpChannels(self):
        normal_help_channel = self.XmppChatMgr.GetHelpChannel()
        self.JoinChannel(normal_help_channel)
        if session.role & service.ROLE_NEWBIE:
            rookie_help_channel = self.XmppChatMgr.GetRookieChannel()
            if rookie_help_channel != normal_help_channel:
                self.JoinChannel(rookie_help_channel)

    def JoinChannel(self, channelName, password = '', suppressMessage = False, isConnectionCheck = False, historySeconds = 0):
        if not IsValidChannelName(channelName):
            raise RuntimeError('Invalid channel name')
        if channelName in self.channelJoinsInProgress:
            if self.verbose:
                logger.debug('Joining channel %s already in progress', channelName)
            return
        channelCategory = GetChannelCategory(channelName)
        if self._IsCategoryMigrated(channelCategory):
            return
        self.channelJoinsInProgress.add(channelName)
        if channelCategory == xmppchatConst.CATEGORY_PLAYER and not suppressMessage:
            eve.Message('ChannelTryingToJoin')
        try:
            result = self._JoinChannelInternal(channelName, password=password, isConnectionCheck=isConnectionCheck, historySeconds=historySeconds)
        finally:
            self.channelJoinsInProgress.discard(channelName)

        return result

    def _JoinChannelInternal(self, channelName, password = '', isConnectionCheck = False, historySeconds = 0):
        if self.xmppConnection and self.xmppConnection.disconnectRequested:
            if self.verbose:
                logger.debug("Can't join channel %s because we're disconnecting...")
            self.pendingJoins = []
            return
        if not self.xmppConnection or not self.xmppConnection.IsConnected():
            if self.verbose:
                logger.debug("Can't join channel %s until logged in to chat server - adding to pending list", channelName)
            self.pendingJoins.append(channelName)
            return
        if self.verbose:
            logger.debug('Joining channel %s', channelName)
        category = GetChannelCategory(channelName)
        if category == xmppchatConst.CATEGORY_LOCAL_SUPPRESSED:
            if not isConnectionCheck:
                sm.ScatterEvent('OnChannelJoined', channelName)
            self.GetOrCreateGroupChatWindow(channelName)
            return True
        if not password:
            password = settings.user.ui.Get('%sPassword' % channelName)
        retriesRemaining = 4
        isRetry = False
        while retriesRemaining > 0:
            retriesRemaining -= 1
            response = self._JoinChannelHelper(channelName, password, historySeconds)
            if not response:
                return False
            responseType = response.attributes.get('type', None)
            if responseType == 'error':
                errorCode = GetErrorCode(response)
                if self.verbose:
                    logger.debug('Error response while attempting to join channel %s: %s', channelName, str(response))
                if errorCode == xmppchatConst.ERROR_WRONG_PASSWORD:
                    displayName = self.GetDisplayName(channelName)
                    if retriesRemaining == 0:
                        eve.Message('LSCWrongPassword', {'channelName': displayName})
                        return False
                    password = self._GetPasswordHelper(channelName, displayName, isRetry)
                    if not password:
                        break
                    isRetry = True
                else:
                    if errorCode == xmppchatConst.ERROR_CHANNEL_UNAVAILABLE:
                        return False
                    if errorCode == xmppchatConst.ERROR_CANT_JOIN_CHANNEL:
                        if category in [xmppchatConst.CATEGORY_PLAYER] and session.role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GML):
                            self.XmppChatMgr.GrantChannelOwnership(channelName)
                        elif category in xmppchatConst.PROXY_CONTROLLED_CATEGORIES:
                            if retriesRemaining == 0:
                                gotSomething = self._ResyncWithRetries()
                                if gotSomething:
                                    logger.warning("Can't join channel %s, waiting for proxy to resync" % channelName)
                                else:
                                    logger.exception("Can't join channel that proxy should have given us access to")
                                return False
                            logger.warning("Can't join channel %s, retrying" % channelName)
                            uthread2.sleep(3)
                        else:
                            displayName = self.GetDisplayName(channelName)
                            eve.Message('LSCCannotJoin', {'msg': (const.UE_LOC, 'UI/Chat/ChatSvc/YouHaveBeenBanned', {'channelName': displayName})})
                            return False
                    elif errorCode == xmppchatConst.ERROR_CONSTRAINED:
                        eve.Message('LSCCannotCreate', {'msg': (const.UE_LOC, 'UI/Chat/ChatSvc/YouHaveTooManyChannels', {'maxChannels': 10})})
                        return False
                    else:
                        logger.debug("Can't join channel %s", channelName)
                        return False

            else:
                if category == xmppchatConst.CATEGORY_PLAYER:
                    playerChannelsJoined = settings.user.ui.Get('chatPlayerChannelsJoined', {})
                    if channelName not in playerChannelsJoined:
                        displayName = self.GetDisplayName(channelName)
                        playerChannelsJoined[channelName] = displayName
                        settings.user.ui.Set('chatPlayerChannelsJoined', playerChannelsJoined)
                if not isConnectionCheck:
                    sm.ScatterEvent('OnChannelJoined', channelName)
                return True

        return False

    def _ResyncWithRetries(self):
        resyncRetriesRemaining = 5
        gotSomething = False
        while resyncRetriesRemaining > 0 and not gotSomething:
            resyncRetriesRemaining -= 1
            channelsToJoin = self.XmppChatMgr.ResyncSystemChannelAccess()
            if not channelsToJoin:
                logger.warning('ResyncSystemChannelAccess returned None, retrying')
                uthread2.sleep(3)
            else:
                gotSomething = True

        return gotSomething

    def _GetPasswordHelper(self, channelName, displayName, isRetry):
        if session.role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GML):
            self.XmppChatMgr.GrantChannelOwnership(channelName)
            return 'bypass_with_roles'
        else:
            title = localization.GetByLabel('UI/Chat/PasswordRequired', channelName=displayName)
            dlg = ChannelPasswordWindow.Open(channel=channelName, title=title, retry=isRetry)
            dlg.ShowDialog()
            password = dlg.password
            return password

    def _JoinChannelHelper(self, channelName, password, historySeconds):
        roomName = self.GetFullRoomName(channelName)
        response_id = self.xmppConnection.JoinRoom(roomName, password=password, historySeconds=historySeconds)
        stackless_channel = stackless.channel()
        self.outstandingJoins[response_id] = stackless_channel
        response = stackless_channel.receive()
        return response

    def LeaveChannel(self, channelName):
        if self.verbose:
            logger.debug('LeaveChannel %s', channelName)
        if channelName in self.pendingJoins:
            self.pendingJoins.remove(channelName)
            return
        roomName = self.GetFullRoomName(channelName)
        self.xmppConnection.LeaveRoom(roomName)
        category = GetChannelCategory(channelName)
        if category not in xmppchatConst.UNCLOSABLE_CHAT_WNDS:
            self.CloseChannelWindow(channelName)
        self.memberRolesByChannels.pop(channelName, None)

    def CloseChannelWindow(self, channelName):
        if self.verbose:
            logger.debug('Scattering OnChannelLeft for %s', channelName)
        sm.ScatterEvent('OnChannelLeft', channelName)
        if channelName in self.myPendingPrivateChats:
            other, isInvited = self.myPendingPrivateChats[channelName]
            del self.myPendingPrivateChats[channelName]
            if other in self.myPendingInvites:
                del self.myPendingInvites[other]
        window = self.GetGroupChatWindow(channelName)
        if window:
            window.access_lost = True
            window.Close()
            windowName = self.GetWindowNameForGroup(channelName)
            del self.groupChatWindows[windowName]
            self.StoreChannelList()

    def IsJoined(self, channelName):
        return channelName in self.groupChatWindows

    def GetFullRoomName(self, channelName):
        roomName = '{0}@conference.{1}'.format(channelName, self.hostname)
        return roomName

    def GetUserNameFromCharId(self, charid):
        return self.xmppConnection.GetFullUsername(charid)

    def CreatePrivateChannel(self, charid):
        channelName = self.XmppChatMgr.CreatePrivateChannel(charid)
        self.myPendingPrivateChats[channelName] = (charid, False)
        self.JoinChannel(channelName)
        return channelName

    def CreateChannel(self, name):
        return self.XmppChatMgr.CreatePlayerOwnedChannel(name)

    def DeleteChannel(self, channelName):
        query = "<query xmlns='http://jabber.org/protocol/muc#owner'><destroy/></query>"
        roomName = self.GetFullRoomName(channelName)
        displayName = self.GetDisplayName(channelName)
        isElevatedPlayer = session.role & service.ROLEMASK_ELEVATEDPLAYER
        if isElevatedPlayer:
            msgName = 'LSCConfirmDestroyChannelElevatedPlayer'
        else:
            msgName = 'LSCConfirmDestroyChannel'
        if eve.Message(msgName, {'displayName': displayName}, uiconst.YESNO) != uiconst.ID_YES:
            return
        response = self.xmppConnection.IssueRequest(query, 'set', to=roomName, method_tag='delete_channel')
        if response.attributes.getValue('type') == 'result':
            playerChannelsJoined = settings.user.ui.Get('chatPlayerChannelsJoined', {})
            try:
                del playerChannelsJoined[channelName]
            except KeyError:
                pass

            settings.user.ui.Set('chatPlayerChannelsJoined', playerChannelsJoined)
            sm.ScatterEvent('OnChannelDeleted', channelName)
        else:
            logger.warn('DeleteChannel: Incorrect response')

    def ForgetChannel(self, channelName):
        playerChannelsJoined = settings.user.ui.Get('chatPlayerChannelsJoined', {})
        if channelName in playerChannelsJoined:
            del playerChannelsJoined[channelName]
        settings.user.ui.Set('chatPlayerChannelsJoined', playerChannelsJoined)
        sm.ScatterEvent('OnRefreshChannels')

    def Invite(self, charid, channelName = None, isRecruiting = None):
        if charid == session.charid:
            raise UserError('ChtCannotInviteSelf', {'char': charid,
             'channel': channelName})
        if IsNPC(charid) or not IsCharacter(charid):
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Chat/ErrorNotAPlayerCharacter')})
            return
        reason = ''
        isPrivate = False
        if channelName is None:
            if charid in self.myPendingInvites:
                raise UserError('ChtAlreadyInvited', {'char': charid})
            channelName = self.CreatePrivateChannel(charid)
            if not channelName:
                raise RuntimeError('Could not create channel for private chat')
            reason = 'Private chat'
            isPrivate = True
            self.myPendingInvites[charid] = channelName
        if session.role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GML | service.ROLE_LEGIONEER):
            self.XmppChatMgr.AddCharacterToChannel(channelName, charid, 'Added by %s' % session.charid)
        elif not isPrivate:
            roomName = self.GetFullRoomName(channelName)
            self.xmppConnection.Invite(self.GetUserNameFromCharId(charid), roomName, reason)

    def RejectInvite(self, charid, channelName, reason):
        roomName = self.GetFullRoomName(channelName)
        self.xmppConnection.RejectInvite(self.GetUserNameFromCharId(charid), roomName, reason)

    def GetChannelsAvailableForInvite(self, charid):
        channels = []
        for each in self.groupChatWindows.itervalues():
            if each.CanInvite(charid):
                channels.append(each.GetChannelId())

        return channels

    def GetDisplayName(self, channelName):
        if self.verbose:
            logger.debug('GetDisplayName %s', channelName)
        k = GetChannelCategory(channelName)
        if k in ('incursion', 'spreadingIncursion'):
            try:
                v = int(GetChannelDifferentiator(channelName))
            except ValueError:
                return channelName

        if k == 'global':
            return localization.GetByLabel('UI/Common/Global')
        if k == xmppchatConst.CATEGORY_FLEET:
            return localization.GetByLabel('UI/Fleet/Fleet')
        if k == 'squad':
            return localization.GetByLabel('UI/Fleet/Squad')
        if k == 'wing':
            return localization.GetByLabel('UI/Fleet/Wing')
        if k == xmppchatConst.CATEGORY_CORP:
            return localization.GetByLabel('UI/Common/Corp')
        if k == xmppchatConst.CATEGORY_FACTION:
            return localization.GetByLabel('UI/Common/Militia')
        if k == xmppchatConst.CATEGORY_ALLIANCE:
            return localization.GetByLabel('UI/Common/Alliance')
        if k in (xmppchatConst.CATEGORY_LOCAL,
         xmppchatConst.CATEGORY_LOCAL_SUPPRESSED,
         xmppchatConst.CATEGORY_WORMHOLE,
         xmppchatConst.CATEGORY_NULLSEC,
         xmppchatConst.CATEGORY_TRIGLAVIAN):
            return localization.GetByLabel('UI/Chat/Local')
        if k == 'solarsystem':
            return localization.GetByLabel('UI/Common/LocationTypes/System')
        if k == 'constellation':
            return localization.GetByLabel('UI/Common/LocationTypes/Constellation')
        if k == 'region':
            return localization.GetByLabel('UI/Common/LocationTypes/Region')
        if k == xmppchatConst.CATEGORY_RW:
            return sm.GetService('rwService').get_site_name()
        if k.startswith('incursion'):
            incursionSvc = sm.GetService('incursion')
            distributionName = incursionSvc.GetDistributionName(v)
            constellationName = incursionSvc.GetConstellationNameFromTaleIDForIncursionChat(v)
            return localization.GetByLabel('UI/Chat/IncursionConstellationChannel', constellationName=constellationName, distributionName=distributionName)
        if k.startswith('spreadingIncursion'):
            incursionSvc = sm.GetService('incursion')
            distributionName = incursionSvc.GetDistributionName(v)
            return distributionName
        if k.startswith('team'):
            return localization.GetByLabel('UI/Chat/District')
        if k == xmppchatConst.CATEGORY_SYSTEM:
            _, groupMessageId, channelMessageId = channelName.split('_', 3)
            return localization.GetByMessageID(int(channelMessageId))
        roomName = self.GetFullRoomName(channelName)
        if k == xmppchatConst.CATEGORY_PRIVATE:
            query = "<query xmlns='http://jabber.org/protocol/disco#info'/>"
            response = self.xmppConnection.IssueRequest(query, 'get', to=roomName, method_tag='get_private_display_name')
            if not response.attributes.getValue('type') == 'result':
                return None
            num_occupants = self._GetNumOccupantsFromInfoQuery(response)
            if num_occupants < 2:
                return localization.GetByLabel('UI/Chat/PrivateChatAlone')
            elif channelName in self.groupChatWindows and hasattr(self.groupChatWindows[channelName], 'GetMembers'):
                return self.GetPrivateChannelDisplayName(channelName)
            else:
                return localization.GetByLabel('UI/Chat/PrivateChat', title=num_occupants)
        if k == xmppchatConst.CATEGORY_PLAYER:
            query = "<query xmlns='http://jabber.org/protocol/disco#info' node='{0}'/>".format(channelName)
            response = self.xmppConnection.IssueRequest(query, 'get', to='conference.' + self.hostname, method_tag='get_player_display_name')
            return self._GetNameFromInfoQuery(response)
        return channelName

    def GetPrivateChannelDisplayName(self, channelName):
        window = self.groupChatWindows[channelName]
        if not window:
            return localization.GetByLabel('UI/Chat/PrivateChatAlone')
        members = window.GetMembers()
        if not members:
            return localization.GetByLabel('UI/Chat/PrivateChatAlone')
        member_names = []
        for each in members:
            if each == session.charid:
                continue
            name = cfg.eveowners.Get(each).name
            member_names.append(name)

        if len(member_names) == 0:
            if channelName in self.myPendingPrivateChats:
                other, isInvited = self.myPendingPrivateChats[channelName]
                name = cfg.eveowners.Get(other).name
                member_names.append(name)
        if len(member_names) == 0:
            return localization.GetByLabel('UI/Chat/PrivateChatAlone')
        if len(member_names) == 1:
            return localization.GetByLabel('UI/Chat/PrivateChat', title=member_names[0])
        return localization.GetByLabel('UI/Chat/GroupChat', title=', '.join(member_names))

    def GetMemberIDsForNamedWindow(self, windowName):
        window = self.groupChatWindows[windowName]
        memberIDs = window.GetMembers()
        return memberIDs

    def _GetNameFromInfoQuery(self, response):
        displayName = None
        if response:
            queryElement = response.find_child_with_tag('query')
            if queryElement:
                identityElement = queryElement.find_child_with_tag('identity')
                if identityElement:
                    displayName = identityElement.attributes.get('name', None)
        return displayName

    def _GetNumOccupantsFromInfoQuery(self, response):
        num_occupants = 0
        queryElement = response.find_child_with_tag('query')
        if queryElement:
            xElement = queryElement.find_child_with_tag('x')
            if xElement:
                for child in xElement.children:
                    var = child.attributes.get('var', None)
                    if var == 'muc#roominfo_occupants':
                        valueElement = child.find_child_with_tag('value')
                        if valueElement:
                            occupants = valueElement.text
                            try:
                                num_occupants = int(occupants)
                            except ValueError:
                                pass

        return num_occupants

    def GetDetailedDisplayName(self, channelName):
        k = GetChannelCategory(channelName)
        try:
            v = int(GetChannelDifferentiator(channelName))
        except ValueError:
            return self.GetDisplayName(channelName)

        if k == xmppchatConst.CATEGORY_CORP:
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/Corp'), featureName=cfg.eveowners.Get(v).name)
        if k == xmppchatConst.CATEGORY_WARFACTION:
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/Militia'), featureName=cfg.eveowners.Get(v).name)
        if k == xmppchatConst.CATEGORY_ALLIANCE:
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/Alliance'), featureName=cfg.eveowners.Get(v).name)
        if k == xmppchatConst.CATEGORY_LOCAL_SUPPRESSED:
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Chat/Local'), featureName=localization.GetByLabel('UI/Chat/Unknown'))
        if k in (xmppchatConst.CATEGORY_LOCAL,
         xmppchatConst.CATEGORY_WORMHOLE,
         xmppchatConst.CATEGORY_NULLSEC,
         xmppchatConst.CATEGORY_TRIGLAVIAN):
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Chat/Local'), featureName=cfg.evelocations.Get(v).name)
        if k == 'solarsystem':
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/LocationTypes/System'), featureName=cfg.evelocations.Get(v).name)
        if k == 'constellation':
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/LocationTypes/Constellation'), featureName=cfg.evelocations.Get(v).name)
        if k == 'region':
            return localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Common/LocationTypes/Region'), featureName=cfg.evelocations.Get(v).name)
        if k == xmppchatConst.CATEGORY_SYSTEM:
            _, groupMessageId, channelMessageId = channelName.split('_', 3)
            return localization.GetByMessageID(int(channelMessageId))
        return self.GetDisplayName(channelName)

    def IsOwnerOrOperatorOfChannel(self, channelName, ignoreRole = False):
        if not ignoreRole:
            if session.role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GML):
                category = GetChannelCategory(channelName)
                if category in [xmppchatConst.CATEGORY_PLAYER, xmppchatConst.CATEGORY_SYSTEM]:
                    return True
        for affiliationType in ('owner', 'admin'):
            try:
                users = self.GetUsersWithAffiliation(channelName, affiliationType)
            except AttributeError:
                logger.exception('Error when getting users with %s affiliation' % affiliationType)
                users = []

            if session.charid in users:
                return True
            if session.corpid in users:
                return True
            if session.allianceid in users:
                return True

        return False

    def IsOwnerOfChannel(self, channelName):
        try:
            users = self.GetUsersWithAffiliation(channelName, 'owner')
        except AttributeError:
            logger.exception('Error when getting users with owner affiliation')
            users = []

        if session.charid in users:
            return True
        return False

    def IsOperatorOfChannel(self, channelName):
        try:
            users = self.GetUsersWithAffiliation(channelName, 'admin')
        except AttributeError:
            logger.exception('Error when getting users with operator affiliation')
            users = []

        if session.charid in users:
            return True
        return False

    def SetMotd(self, channelName, motd):
        bannedwords.check_words_allowed(motd)
        if self.verbose:
            logger.debug('SetMotd for %s: %s', channelName, motd)
        roomName = self.GetFullRoomName(channelName)
        channelCategory = GetChannelCategory(channelName)
        if channelCategory == xmppchatConst.CATEGORY_FLEET:
            sm.GetService('fleet').SetRemoteMotd(motd)
            return
        if channelCategory in [xmppchatConst.CATEGORY_CORP, xmppchatConst.CATEGORY_ALLIANCE]:
            return self.XmppChatMgr.SetMotd(roomName, motd)
        self.xmppConnection.SendXmppSubject(roomName, motd)

    def GetMotd(self, channelName):
        window = self.GetGroupChatWindow(channelName)
        return window.GetMotd()

    def ConfigureChannel(self, channelName, roomconfig):
        form = "<field var='FORM_TYPE'><value>http://jabber.org/protocol/muc#roomconfig</value></field>\n"
        for key, value in roomconfig.items():
            field = "<field var='{0}'><value>{1}</value></field>\n".format(key, value)
            form += field

        query = "\n<query xmlns='http://jabber.org/protocol/muc#owner'>\n<x xmlns='jabber:x:data' type='submit'>\n"
        query += form
        query += '</x>\n</query>'
        roomName = self.GetFullRoomName(channelName)
        response = self.xmppConnection.IssueRequest(query, 'set', to=roomName, method_tag='configure_channel')
        if not response.attributes.getValue('type') == 'result':
            logger.warn('ConfigureChannel: Incorrect response')
            return False
        return True

    def BanUserFromChannel(self, channelName, charid, reason, durationInSecs):
        self.SetAffiliation(channelName, charid, 'outcast')
        self._RegisterTemporaryRestriction('ban', channelName, charid, durationInSecs)
        if durationInSecs:
            self.SetAffiliation(channelName, charid, 'none')

    def UnbanUserFromChannel(self, channelName, charid):
        if self.verbose:
            logger.debug('UnbanUserFromChannel(%s, %s)', channelName, charid)
        self.SetAffiliation(channelName, charid, 'none')
        if str(charid).startswith('set_'):
            prefix, charid = charid.split('_', 1)
            self.SetAffiliation(channelName, charid, 'none')
        self._UnregisterTemporaryRestriction('ban', channelName, charid)

    def MuteUser(self, channelName, charid, reason, durationInSecs = 0):
        self.SetRole(channelName, charid, 'visitor', reason)
        if durationInSecs <= 0:
            durationInSecs = 315360000
        self._RegisterTemporaryRestriction('mute', channelName, charid, durationInSecs)

    def UnmuteUser(self, channelName, charid):
        self.SetRole(channelName, charid, 'participant')
        self._UnregisterTemporaryRestriction('mute', channelName, charid)

    def _RegisterTemporaryRestriction(self, category, channelName, charid, durationInSecs):
        roomName = self.GetFullRoomName(channelName)
        jid = self.GetUserNameFromCharId(charid)
        self.xmppConnection.RegisterTemporaryRestriction(category, roomName, jid, durationInSecs)

    def _UnregisterTemporaryRestriction(self, category, channelName, charID):
        roomName = self.GetFullRoomName(channelName)
        jid = self.GetUserNameFromCharId(charID)
        self.xmppConnection.UnregisterTemporaryRestriction(category, roomName, jid)

    def IsMuted(self, channelID, charID):
        muted = self.GetUsersWithRole(channelID, 'visitor')
        if self.verbose:
            logger.debug('IsGagged(%s, %s): %s', channelID, charID, muted)
        return charID in muted

    def IsOperator(self, channelID, charID):
        memberRole = self.memberRolesByChannels[channelID].get(charID, None)
        if memberRole:
            return memberRole == 'moderator'
        else:
            moderators = self.GetUsersWithRole(channelID, 'moderator')
            return charID in moderators

    def SetAffiliation(self, channelName, charid, affiliation):
        if self.verbose:
            logger.debug('SetAffiliation(%s, %s, %s)', channelName, charid, affiliation)
        roomName = self.GetFullRoomName(channelName)
        idtype = 'character'
        if IsCorporation(charid):
            idtype = 'corporation'
        elif IsAlliance(charid):
            idtype = 'alliance'
        template = "<query xmlns='http://jabber.org/protocol/muc#admin'><item affiliation='{1}' jid='{0}'><reason>{2}</reason></item></query>"
        query = template.format(self.GetUserNameFromCharId(charid), affiliation, idtype)
        response = self.xmppConnection.IssueRequest(query, 'set', to=roomName, method_tag='set_affiliation')
        if not response.attributes.getValue('type') == 'result':
            logger.warn('SetAffiliation: Incorrect response')

    def GetUsersWithAffiliation(self, channelName, affiliation):
        if GetChannelCategory(channelName) == xmppchatConst.CATEGORY_LOCAL_SUPPRESSED:
            return []
        roomName = self.GetFullRoomName(channelName)
        template = "<query xmlns='http://jabber.org/protocol/muc#admin'><item affiliation='{0}'/></query>"
        query = template.format(affiliation)
        response = self.xmppConnection.IssueRequest(query, 'get', to=roomName, method_tag='get_users_with_affiliation')
        if response.attributes.getValue('type') == 'result':
            return GetUsersFromResponse(response)
        else:
            return []

    def SetRole(self, channelName, charId, role, reason = None):
        roomName = self.GetFullRoomName(channelName)
        self.xmppConnection.SetRole(roomName, charId, role, reason)

    def GetUsersWithRole(self, channelName, role):
        if GetChannelCategory(channelName) == xmppchatConst.CATEGORY_LOCAL_SUPPRESSED:
            return []
        roomName = self.GetFullRoomName(channelName)
        template = "<query xmlns='http://jabber.org/protocol/muc#admin'><item role='{0}'/></query>"
        query = template.format(role)
        response = self.xmppConnection.IssueRequest(query, 'get', to=roomName, method_tag='get_users_with_role')
        if response.attributes.getValue('type') == 'result':
            return GetUsersFromResponse(response)
        else:
            return []

    def GetUsersWithTemporaryRestriction(self, channelName, category):
        roomName = self.GetFullRoomName(channelName)
        template = "<query xmlns='urn:xmpp:expiring_record#search' room='{0}' category='{1}'/>"
        query = template.format(roomName, category)
        response = self.xmppConnection.IssueRequest(query, 'get', to=self.hostname, method_tag='get_users_with_temporary_restriction')
        if response.attributes.getValue('type') == 'result':
            return GetUsersFromResponse(response)
        else:
            return []

    def GetChannelConfig(self, channel):
        roomName = self.GetFullRoomName(channel)
        query = "<query xmlns='http://jabber.org/protocol/muc#owner'/>"
        response = self.xmppConnection.IssueRequest(query, 'get', to=roomName, method_tag='get_channel_config')
        if response.attributes.getValue('type') == 'result':
            return response
        else:
            return None

    def LocalEchoAll(self, msg, charid):
        window = self.GetGroupChatWindow(xmppchatConst.CATEGORY_LOCAL)
        if window:
            if charid is None:
                charid = localization.GetByLabel('UI/Common/Message')
            window.Receive(charid, msg)

    def StoreChannelList(self):
        channelList = []
        for windowName, window in self.groupChatWindows.items():
            if type(window) == stackless.channel:
                continue
            displayName = window.displayName
            channel = window.GetChannelId()
            channelList.append((windowName, channel, displayName))

        settings.char.ui.Set('chatchannels', channelList)

    def RemoveChannelFromCurrentChannelsSettings(self, windowName):
        allChannels = settings.char.ui.Get('chatchannels', [])
        allChannelsNew = []
        for eachChannel in allChannels:
            if eachChannel[0] != windowName:
                allChannelsNew.append(eachChannel)

        settings.char.ui.Set('chatchannels', allChannelsNew)

    def CreateSessionChannelWindows(self):
        for sessionVariable, groupName in SESSION_CHANGE_CATEGORIES.iteritems():
            if getattr(session, sessionVariable) and not self._IsCategoryMigrated(groupName):
                self.GetOrCreateGroupChatWindow(groupName, False)

    def _RestoreChannelList(self, channelListInSettings):
        if self.verbose:
            logger.debug('Restoring channels from settings')
        for windowName, channel, caption in channelListInSettings:
            if not self.ShouldChannelBeRestoredFromSettings(windowName, channel):
                continue
            w = self.groupChatWindows.get(windowName, None)
            if w is None or w.destroyed:
                if self.verbose:
                    logger.debug('Creating window %s for channel %s (%s)', windowName, channel, caption)
                windowId = 'chatchannel_%s' % windowName
                window = XmppChatWindow(receiver=channel, isGroupChat=True, channel=channel, name=windowName, caption=caption, windowID=windowId, check_open_minimized=True)
                window.verbose = self.verbose
                self.groupChatWindows[windowName] = window

    def ShouldChannelBeRestoredFromSettings(self, windowName, channel):
        if windowName in SESSION_CHANGE_CATEGORIES:
            return False
        try:
            if GetChannelCategory(channel) in (xmppchatConst.CATEGORY_PLAYER, xmppchatConst.CATEGORY_SYSTEM):
                return True
        except IndexError:
            logger.warn('ShouldChannelBeRestoredFromSettings: Could not find channel category: %s' % channel)

        return False

    def InitChatFilters(self):
        self.characterSettings = sm.GetService('characterSettings')
        chatFilters = self.GetChatFilters()
        UpdateChatFilterVariables(chatFilters.get('bannedWords', []), chatFilters.get('highlightWords', []))

    def GetChatFilters(self):
        if session.charid is None:
            return
        if self.chatFilters is None:
            self.chatFilters = self.FetchFiltersFromServer()
        return self.chatFilters

    def FetchFiltersFromServer(self):
        chatFilters = {}
        yamlStr = self.characterSettings.Get('chatFilters')
        if yamlStr is not None:
            chatFilters = yaml.load(yamlStr, Loader=yaml.CLoader)
        return chatFilters

    def SaveChatFiltersOnServer(self, bannedWords, highlightWords, blinkOnHighlightWords):
        currentFilters = self.GetChatFilters()
        if currentFilters:
            currentBanned = currentFilters.get('bannedWords', [])
            currentHighlight = currentFilters.get('highlightWords')
            currentBlink = currentFilters.get('blinkOnHighlightWords')
            if currentBanned == bannedWords and currentHighlight == highlightWords and currentBlink == blinkOnHighlightWords:
                return
        self.chatFilters = {'bannedWords': bannedWords,
         'highlightWords': highlightWords,
         'blinkOnHighlightWords': blinkOnHighlightWords}
        yamlFilters = yaml.safe_dump(self.chatFilters)
        self.characterSettings.Save('chatFilters', yamlFilters)
        UpdateChatFilterVariables(bannedWords, highlightWords)

    def GetChannelMessages(self):
        messageText = ''
        for window in self.groupChatWindows.itervalues():
            messageText += window.GetMessages()

        return messageText

    def AskYesNoQuestion(self, question, props, defaultChoice = 1):
        if defaultChoice:
            defaultChoice = uiconst.ID_YES
        else:
            defaultChoice = uiconst.ID_NO
        return eve.Message(question, props, uiconst.YESNO, defaultChoice) == uiconst.ID_YES

    def ReloadChannel(self, channelID):
        window = self.GetGroupChatWindow(channelID)
        if window:
            window.LoadMessages()

    def GetUserData(self, charid):
        userData = self.userData.get(charid)
        if userData and userData.get('corpid', 0) != 0:
            return userData
        user = self.GetUserNameFromCharId(charid)
        retries = 3
        while retries > 0:
            response = self.xmppConnection.GetEveUserData(user)
            if response:
                userData = self._GetPresenceUserData(charid, response)
                if userData and userData.get('corpid', 0) != 0:
                    self.userData[charid] = userData
                    return userData
                if userData:
                    logger.warning('User data has no corp for %s', charid)
                else:
                    logger.warning('Empty user data for %s', charid)
            else:
                logger.warning('Fetching user data failed for %s', charid)
            retries -= 1
            uthread2.sleep(0.1)

        logger.warning('Returning empty user data for %s', charid)
        return {}

    def IsPrivateChatPending(self, channelName):
        return channelName in self.myPendingPrivateChats

    def IsSenderMessage(self, sender):
        return sender == self.translatedMsgText

    def GetNumPilotsInSystem(self):
        window = self.GetGroupChatWindow('local')
        if window:
            return len(window.GetMembers())

    def PokePlayerAboutChatMsgGm(self, charID, channelName):
        sm.RemoteSvc('mailMgr').PokePlayerAboutChatMsgGm(charID, channelName)

    def OnCharacterPokedByGM(self, gmCharID, channelName):
        text = localization.GetByLabel('UI/Chat/ChatSvc/GmIsTryingToReachYou', charID=session.charid, gmCharID=gmCharID)
        elelmentName = 'chatchannel_%s' % channelName
        sm.GetService('uiHighlightingService').highlight_ui_element_by_name(elelmentName, text, 7, default_direction=UiHighlightDirections.UP)

    def send_honey_event(self, event_name, extra_fields = None):
        event_fields = {'eve.xmpp.connection.has_logged_in': self.hasLoggedInOnce,
         'eve.xmpp.connection.address': self.xmppConnection.hostname,
         'enduser.id': self.xmppConnection.username,
         'eve.xmpp.connection.reconnecting': self.isReconnecting,
         'eve.xmpp.connection.id': id(self.xmppConnection),
         SERVICE_NAME: SERVICE_NAME_PREFIX + 'xmppchatsvc'}
        if extra_fields is not None:
            event_fields.update(extra_fields)
        mhe.send(event_name, event_fields)

    @property
    def XmppChatMgr(self):
        return sm.ProxySvc('XmppChatMgr')
