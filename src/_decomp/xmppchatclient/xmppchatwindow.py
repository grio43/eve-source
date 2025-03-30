#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\xmppchatwindow.py
import logging
import random
import sys
from collections import deque
import blue
import carbonui.const as uiconst
import eveicon
import localization
import log
import telemetry
import threadutils
import uthread2
from caching.memoize import Memoize
from carbonui import AxisAlignment, TextColor
from carbonui.control.combo import Combo
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuDataFactory import CreateMenuDataFromRawTuples
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.services.setting import UserSettingBool, UserSettingEnum
from carbonui.text.settings import get_font_size_for_preset
from carbonui.uianimations import animations
from chatutil.filter import CleanText
from eve.client.script.ui.control.entries.util import GetFromClass
from menu import MenuLabel
from carbon.common.script.sys import service
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtDate, GetTimeParts
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.control.basicDynamicScroll import BasicDynamicScroll
from carbonui.control.scrollentries import ScrollEntryNode
from carbonui.primitives.container import Container
from carbonui.util.stringManip import SanitizeFilename
from chatutil import StripBreaks, IsChannelPrivate, ShouldHightlightBlink, CompleteAutoLinks, GetChannelCategory, MAX_TEXT_LEN, TruncateVeryLongText, GetChannelDifferentiator
from chatutil.spam import IsSpam
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from eve.client.script.ui.control.divider import Divider
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from carbonui.fontconst import EVE_SMALL_FONTSIZE
from eve.client.script.ui.util.linkUtil import GetCharIDFromTextLink
from eve.common.script.sys.idCheckers import IsCharacter, IsEvePlayerCharacter
from eveprefs import prefs
from eveservices.xmppchat import GetChatService
from globalConfig.getFunctions import GetMaxChatChannelIdleTime, GetUpdateChannelCountIntervalSeconds, IsContentComplianceControlSystemActive
from xmppchatclient.const import CATEGORY_PRIVATE, CATEGORY_PLAYER, CATEGORY_BOT, CATEGORY_SYSTEM, CATEGORY_FLEET, CATEGORY_CORP, CATEGORY_ALLIANCE, MESSAGEMODE_TEXTONLY, MESSAGEMODE_SMALLPORTRAIT, MESSAGEMODE_BIGPORTRAIT, SINGLE_WND_CATEGORIES, CATEGORY_WORMHOLE, CHANNELS_WITH_NO_PRESENCE_BROADCAST, CATEGORY_LOCAL, CATEGORY_LOCAL_SUPPRESSED, CATEGORY_NULLSEC, CATEGORY_TRIGLAVIAN
from xmppchatclient.xmppchannelsettings import ChannelSettingsDlg
from xmppchatclient.xmppchatchannels import XmppChatChannels
from xmppchatclient.xmppchatentry import XmppChatEntry
from eve.client.script.ui.shared.comtool.filterSettings import ChatFilterSettings
from bannedwords.client import bannedwords
from xmppchatclient.xmppchatuserentry2 import XmppChatSimpleUserEntry, XmppChatUserEntry
from chat.client.window import BaseChatWindow
from chat.client.const import AVAILABLE_FONT_SIZES, MAX_MESSAGES_IN_HISTORY, SLASH_EMOTE_STRING, SLASH_ME_STRING, CHATLOG_TEMPLATE
from chat.client.chat_settings import default_message_mode_setting, default_compact_member_entries_setting, default_show_member_list_setting, default_font_size_setting, global_font_size_setting, elevated_chat_highlighting_setting, show_message_timestamp_setting, highlight_my_messages_setting, ApplyFontSizeGloballySetting, EffectiveFontSizeSetting, auto_collapse_messages, auto_collapse_message_lines
from chat.client.util import should_hide_message, check_banned_message_in_new_player_channel
from chat.client.hide_messages import open_hide_message_settings, has_hide_message_setting
from chat.common.const import LOCAL_CHAT_CATEGORIES, ChatCategory
from chat.common.util import get_color_for_role
logger = logging.getLogger(__name__)
MESSAGEMODETEXTS = {MESSAGEMODE_TEXTONLY: 'UI/Chat/NoPortrait',
 MESSAGEMODE_SMALLPORTRAIT: 'UI/Chat/SmallPortrait',
 MESSAGEMODE_BIGPORTRAIT: 'UI/Chat/LargePortrait'}
ROLE_SLASH = service.ROLE_GML | service.ROLE_LEGIONEER
ACTION_ICON = 'res:/UI/Texture/classes/UtilMenu/BulletIcon.png'
MOTD_CHANNEL_TYPES = {CATEGORY_CORP,
 CATEGORY_ALLIANCE,
 CATEGORY_FLEET,
 CATEGORY_PLAYER,
 CATEGORY_SYSTEM}

class XmppChatWindow(BaseChatWindow):
    __notifyevents__ = ['OnPortraitCreated']
    default_caption = 'Xmpp Chat'
    default_windowID = 'XmppChat'
    default_open = True
    _has_left_channel = False

    def OnUIRefresh(self):
        pass

    def ApplyAttributes(self, attributes):
        self.throttleFunc = None
        self._user_list_cont = None
        self._user_list_underlay = None
        BaseChatWindow.ApplyAttributes(self, attributes)
        self.verbose = False
        self.inputs = ['']
        self.inputIndex = None
        self.receiver = attributes.receiver
        self.displayName = StripTags(attributes.caption)
        self.channelName = attributes.channel
        self.channelCategory = GetChannelCategory(self.receiver)
        self.hasStartedUpdateApproximateCount = False
        self.approximateMemberCount = 0
        self.userlistNodesByName = {}
        self.messages = []
        self.myPendingMessages = {}
        self.motd = None
        self.motd_set = False
        self.access_lost = False
        self.members = {}
        self.muted_members = set()
        self._message_style_setting = UserSettingEnum(settings_key='%s_mode' % self.name, default_value=lambda : default_message_mode_setting.get(), options=default_message_mode_setting.options)
        self._font_size_setting = UserSettingEnum(settings_key='chatfontsize_%s' % self.name, default_value=lambda : default_font_size_setting.get(), options=AVAILABLE_FONT_SIZES)
        self._apply_font_size_globally_setting = ApplyFontSizeGloballySetting(font_size_setting=self._font_size_setting)
        self._effective_font_size_setting = EffectiveFontSizeSetting(font_size_setting=self._font_size_setting)
        self._chat_notifications_enabled_setting = UserSettingBool(settings_key='chatWindowBlink_%s' % self.name, default_value=True)
        self._show_member_list_setting = UserSettingBool(settings_key='%s_usermode' % self.name, default_value=lambda : default_show_member_list_setting.get())
        self._compact_member_entries_setting = UserSettingBool(settings_key=self._get_compact_member_entries_setting_key(), default_value=lambda : default_compact_member_entries_setting.get())
        self.removeIdleCharactersTasklet = None
        self._ResetTrackActivityPerMember()
        self.pendingPortraitReloads = set()
        self.GetMainArea().clipChildren = True
        input_cont = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOBOTTOM, alignMode=uiconst.TOBOTTOM, padTop=-3)
        bottom_divider = Divider(name='bottom_divider', parent=input_cont, align=uiconst.TOTOP_NOPUSH, state=uiconst.UI_NORMAL, height=8)
        self.input = EditPlainText(parent=input_cont, align=uiconst.TOBOTTOM, height=settings.user.ui.Get('chatinputsize_%s' % self.name, 64), innerPadding=(8, 8, 8, 8), padding=(-1, 3, -1, -1), pushContent=True, maxLength=MAX_TEXT_LEN)
        self.input.ValidatePaste = self.ValidatePaste
        self.input.OnReturn = self._HandleInputOnReturn
        self.input.CtrlUp = self._HandleInputCtrlUp
        self.input.CtrlDown = self._HandleInputCtrlDown
        self.input.RegisterFocus = self._RegisterFocus
        bottom_divider.Startup(self.input, 'height', 'y', 30, 96)
        bottom_divider.OnSizeChanged = self.OnInputSizeChanged
        self._user_list_cont = Container(parent=self.GetMainArea(), align=uiconst.TORIGHT, width=settings.user.ui.Get('%s_userlistwidth' % self.name, 128))
        DividerLine(parent=self._user_list_cont, align=uiconst.TOLEFT_NOPUSH)
        self._user_list_underlay = Fill(bgParent=self._user_list_cont, align=uiconst.TOALL, padLeft=1, color=(1.0, 1.0, 1.0, 0.05))
        divider = Divider(name='user_list_divider', parent=self._user_list_cont, align=uiconst.TOLEFT_NOPUSH, state=uiconst.UI_NORMAL, width=8, cross_axis_alignment=AxisAlignment.START)
        divider.Startup(victim=self._user_list_cont, attribute='width', xory='x', minValue=50, maxValue=200)
        divider.OnSizeChanged = self.UserlistEndScale
        self.numMembersCont = Container(name='numMembersCont', parent=self._user_list_cont, align=uiconst.TOTOP, height=16, padding=(8, 8, 8, 0))
        self.numMembersCont.display = False
        if self.channelCategory in CHANNELS_WITH_NO_PRESENCE_BROADCAST:
            memberHint = localization.GetByLabel('UI/Chat/CombinedCounterHint')
        else:
            memberHint = localization.GetByLabel('UI/Chat/CapsuleerCounterHint')
        Sprite(name='numMembersSprite', parent=self.numMembersCont, align=uiconst.CENTERLEFT, width=16, height=16, texturePath=eveicon.person, color=TextColor.NORMAL, hint=memberHint)
        self.numMembersLabel = EveLabelSmall(name='numMembersLabel', parent=self.numMembersCont, align=uiconst.CENTERLEFT, left=20, text='', hint=memberHint)
        self.userlist = BasicDynamicScroll(name='userlist', parent=self._user_list_cont, align=uiconst.TOALL, padding=(8, 8, 8, 0), entry_spacing=self._get_user_list_entry_spacing(), pushContent=True)
        self.userlist.isCondensed = self._compact_member_entries_setting.is_enabled()
        self.userlist.GetContentContainer().OnDropData = self.OnDropCharacter
        self.output = BasicDynamicScroll(parent=self.GetMainArea(), align=uiconst.TOALL, innerPadding=(8, 8, 8, 8), entry_spacing=4, pushContent=False, stickToBottom=True)
        self.output.sr.content.GetMenu = self.GetOutputMenu
        self._UpdateMinSize()
        if elevated_chat_highlighting_setting.is_enabled():
            self.input.OnKeyUp = self.OnOutputOrInputKeyUp
            self.output.OnKeyUp = self.OnOutputOrInputKeyUp
        self.SetupUserlist()
        self.output.Load(contentList=[], fixedEntryHeight=18)
        if self.CanKillChannel():
            self.MakeKillable()
        self.lastActivityTime = blue.os.GetWallclockTime()
        self.checkConnectionStatusTasklet = uthread2.start_tasklet(self._CheckConnectionStatus)
        self.logfile = None
        if settings.user.ui.Get('logchat', 1):
            uthread2.start_tasklet(self._SetupLogfile)
        if self.channelCategory == CATEGORY_PRIVATE and GetChatService().IsPrivateChatPending(self.receiver):
            self.AddPrivateConvoHint()
        self._message_style_setting.on_change.connect(self._on_message_style_setting_changed)
        self._font_size_setting.on_change.connect(self._on_font_size_setting_changed)
        self._apply_font_size_globally_setting.on_change.connect(self._on_apply_font_size_globally_setting_changed)
        global_font_size_setting.on_change.connect(self._on_global_font_size_setting_changed)
        elevated_chat_highlighting_setting.on_change.connect(self._on_elevated_chat_highlighting_setting_changed)
        self._show_member_list_setting.on_change.connect(self._on_show_member_list_setting_changed)
        self._compact_member_entries_setting.on_change.connect(self._on_compact_member_entries_setting_changed)

    @property
    def _user_entry_type(self):
        if self._compact_member_entries_setting.is_enabled():
            return XmppChatSimpleUserEntry
        else:
            return XmppChatUserEntry

    def OnSetActive_(self, *args):
        if self._user_list_underlay is not None:
            animations.FadeTo(self._user_list_underlay, startVal=self._user_list_underlay.opacity, endVal=0.05, duration=0.1)

    def OnSetInactive(self, *args):
        super(XmppChatWindow, self).OnSetInactive()
        if self._user_list_underlay is not None:
            animations.FadeOut(self._user_list_underlay, duration=0.3)

    def _ResetTrackActivityPerMember(self):
        self.activityTimestampPerMember = {}
        self.activityQueue = deque()
        if self.channelCategory in CHANNELS_WITH_NO_PRESENCE_BROADCAST:
            if not self.removeIdleCharactersTasklet:
                self.removeIdleCharactersTasklet = uthread2.start_tasklet(self._RemoveIdleCharactersLoop)
        elif self.removeIdleCharactersTasklet:
            self.removeIdleCharactersTasklet.kill()
            self.removeIdleCharactersTasklet = None

    def _AddActivity(self, sender, timestamp):
        self.activityTimestampPerMember[sender] = timestamp
        self.activityQueue.append((timestamp, sender))

    def _RemoveIdleCharactersLoop(self):
        while not self.destroyed:
            now = blue.os.GetWallclockTime()
            toRemove = []
            characterIdlePeriodSeconds = prefs.GetValue('chat_idle_character_removal_period', 900)
            logger.debug('_RemoveIdleCharactersLoop, idle period is %s', characterIdlePeriodSeconds)
            sleepDuration = characterIdlePeriodSeconds
            while len(self.activityQueue) > 0:
                timestamp, sender = self.activityQueue[0]
                ageInSec = blue.os.TimeDiffInMs(timestamp, now) / 1000
                if ageInSec > characterIdlePeriodSeconds:
                    self.activityQueue.popleft()
                    timestampForSender = self.activityTimestampPerMember[sender]
                    ageForSenderInSec = blue.os.TimeDiffInMs(timestampForSender, now) / 1000
                    if ageForSenderInSec > characterIdlePeriodSeconds:
                        toRemove.append(sender)
                else:
                    sleepDuration = characterIdlePeriodSeconds - ageInSec + 1
                    break

            for charid in toRemove:
                logger.debug('Removing idle character %s', charid)
                self.CharacterLeftChannel(charid)

            uthread2.sleep(sleepDuration)

    def UserlistEndScale(self, *args):
        settings.user.ui.Set('%s_userlistwidth' % self.name, self._user_list_cont.width)
        self._UpdateMinSize()

    def _UpdateMinSize(self):
        if self._user_list_cont is None:
            return
        default_min_width, default_min_height = self.default_minSize
        user_list_width, _ = self.GetWindowSizeForContentSize(width=self._user_list_cont.width)
        min_width = max(default_min_width, user_list_width)
        self.SetMinSize((min_width, default_min_height))

    def OnInputSizeChanged(self):
        settings.user.ui.Set('chatinputsize_%s' % self.name, self.input.height)

    def _SetupLogfile(self):
        if eve.session.charid:
            charName = cfg.eveowners.Get(eve.session.charid).name
        else:
            logger.warning('_SetupLogfile %s: No charid in session. Listener will be unknown character in chatlog' % self.displayName)
            charName = 'unknown_character'
        chatlog = CHATLOG_TEMPLATE % (self.receiver,
         self.displayName,
         charName,
         FmtDate(blue.os.GetWallclockTime()))
        year, month, weekday, day, hour, minute, second, msec = blue.os.GetTimeParts(blue.os.GetWallclockTime())
        timeStamp = '%d%.2d%.2d_%.2d%.2d%.2d' % (year,
         month,
         day,
         hour,
         minute,
         second)
        filename = '%s_%s' % (self.displayName, timeStamp)
        filename = SanitizeFilename(filename)
        postFix = '_%s' % session.charid if session.charid else ''
        filename = blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/logs/Chatlogs/%s%s.txt' % (filename, postFix)
        try:
            self.logfile = blue.classes.CreateInstance('blue.ResFile')
            if not self.logfile.Open(filename, 0):
                self.logfile.Create(filename)
            self.logfile.Write(chatlog.encode('utf-16'))
        except Exception:
            self.logfile = None
            logger.exception('Failed to instantiate log file')
            sys.exc_clear()

    def ResetAfterReconnect(self):
        self.myPendingMessages = {}

    def Receive(self, sender, text, msg_id = None, stripFormatting = True):
        try:
            isMessage = False
            senderId = int(sender)
        except ValueError:
            isMessage = GetChatService().IsSenderMessage(sender)
            senderId = 0

        strippedText = self._GetStrippedText(text, isMessage)
        if self.logfile is not None and self.logfile.size > 0:
            timestamp = blue.os.GetWallclockTime()
            self._WriteToLogfile(sender, strippedText, timestamp)
        if senderId == eve.session.charid:
            if not msg_id:
                logger.warning('No message id in message from self')
            try:
                del self.myPendingMessages[msg_id]
                if self.verbose:
                    logger.debug('Deleted pending message %s', msg_id)
            except KeyError:
                logger.warning('Unexpected message from self: %s', msg_id)

            return
        if stripFormatting:
            text = strippedText
        self._Output(sender, text)

    def HandleErrorResponse(self, response):
        msg_id = response.attributes.getValue('id')
        if self.verbose:
            logger.debug('HandleErrorResponse %s', msg_id)
        try:
            node, timestamp = self.myPendingMessages[msg_id]
            del self.myPendingMessages[msg_id]
            if self.verbose:
                logger.debug('Deleted pending message %s', msg_id)
        except KeyError:
            logger.warning('Unexpected error response: %s', msg_id)
            return

        XmppChatEntry.MarkMessageUndelivered(node)

    def _GetStrippedText(self, text, isMessage = False):
        ignoredTags = ['b',
         'i',
         'u',
         'url',
         'br']
        if isMessage:
            ignoredTags.append('color')
        text = StripTags(text, ignoredTags=ignoredTags)
        return text

    def _Output(self, sender, text):
        if self.verbose:
            logger.debug('_Output: %s', text)
        timestamp = blue.os.GetWallclockTime()
        self.lastActivityTime = timestamp
        if IsSpam(text):
            return
        if IsEvePlayerCharacter(sender):
            self._AddActivity(sender, timestamp)
            if sender not in self.members:
                self.CharacterJoinedChannel(sender)
                if self.channelCategory == CATEGORY_LOCAL:
                    logger.warning('Got a message in local from someone who is not a member')
            if sender != session.charid and should_hide_message(self.receiver, self.channelCategory, text):
                return
        text = CompleteAutoLinks(text)
        colorkey = self.GetColorKeyForSender(sender)
        self.messages.append((sender,
         text,
         timestamp,
         colorkey))
        if len(self.messages) >= MAX_MESSAGES_IN_HISTORY:
            self.messages.pop(0)
            if self.output.GetNodes():
                self.output.RemoveNodes([self.output.GetNodes()[0]])
        node = self._GetChatEntry(sender, text, timestamp, colorkey)
        self.output.AddNodes(-1, [node])
        self._BlinkIfNeeded(sender, text)
        return node

    def _BlinkIfNeeded(self, sender, text):
        if sender in (eve.session.charid, const.ownerSystem):
            return
        blink_enabled = self._chat_notifications_enabled_setting.is_enabled()
        if blink_enabled or ShouldHightlightBlink(text):
            self.Blink()
            if self.state == uiconst.UI_HIDDEN or self.IsMinimized():
                self.SetBlinking()

    def SetBlinking(self):
        super(XmppChatWindow, self).SetBlinking()
        sm.ScatterEvent('OnChatWindowStartBlinking', self)

    def SetNotBlinking(self):
        super(XmppChatWindow, self).SetNotBlinking()
        sm.ScatterEvent('OnChatWindowStopBlinking', self)

    def _WriteToLogfile(self, sender, text, timestamp):
        textWithoutTags = StripTags(text).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        try:
            if sender is None:
                who = localization.GetByLabel('UI/Common/Message')
            else:
                who = cfg.eveowners.Get(int(sender)).name
        except ValueError:
            who = sender

        line = '[%20s ] %s > %s\r\n' % (FmtDate(timestamp), who, textWithoutTags)
        try:
            self.logfile.Write(line.encode('utf-16'))
        except IOError:
            log.LogException(toAlertSvc=0)
            sys.exc_clear()

    def GetMessages(self):
        messageText = 'Channel: %s\n' % self.displayName
        for sender, text, timestamp, colorkey in self.messages:
            messageText += '[%s] %s> %s\n' % (FmtDate(timestamp), sender, text)

        return messageText

    def SetMotd(self, sender, text):
        if self.channelCategory == CATEGORY_FLEET:
            text = sm.GetService('fleet').GetMotd()
            if not text and self.motd is None:
                return
        if self.verbose:
            logger.debug('SetMotd: sender=%s, text=%s', sender, text)
        self.lastActivityTime = blue.os.GetWallclockTime()
        if text == self.motd:
            return
        self.motd = text
        if self.motd:
            if sender and self.motd_set:
                msg = localization.GetByLabel('UI/Chat/ChannelMotdChanged', newMotd=self.motd, admin=sender)
            else:
                msg = localization.GetByLabel('UI/Chat/ChannelMotd', motd=text)
        elif sender in (None, 'admin'):
            msg = localization.GetByLabel('UI/Chat/ChannelMotdClearedByAdmin')
        else:
            msg = localization.GetByLabel('UI/Chat/ChannelMotdCleared', admin=sender)
        self.motd_set = True
        self.Receive(const.ownerSystem, msg, stripFormatting=False)

    def AddPrivateConvoHint(self):
        msg = localization.GetByLabel('UI/Chat/BeingTalkingToOpenRequest')
        self._Output(const.ownerSystem, unicode(msg))

    def GetMotd(self):
        return self.motd

    def GetMembers(self):
        return self.members.keys()

    def IsCharacterMember(self, char):
        return char in self.members

    def SetCharacterMuted(self, char, reason):
        if char in self.muted_members:
            return
        if char == session.charid:
            muteMsg = localization.GetByLabel('UI/Chat/MuteMessage', muted=char, admin=const.ownerSystem, reason=reason)
            self._Output(const.ownerSystem, muteMsg)
        self.muted_members.add(char)

    def SetCharacterUnmuted(self, char):
        if char in self.muted_members:
            if char == session.charid:
                muteMsg = localization.GetByLabel('UI/Chat/UnmuteMessage', unmuted=char, admin=const.ownerSystem)
                self._Output(const.ownerSystem, muteMsg)
            self.muted_members.remove(char)

    def IsCharacterMuted(self, char):
        return char in self.muted_members

    def CharacterJoinedChannel(self, char):
        if self.verbose:
            logger.debug('%s joined channel %s', char, self.receiver)
        self.lastActivityTime = blue.os.GetWallclockTime()
        userdata = GetChatService().GetUserData(char)
        self.members[char] = userdata
        if self.verbose:
            logger.debug('userdata for %s: %s', char, userdata)
        if char not in self.userlistNodesByName:
            if self.verbose:
                logger.debug('%s added to channel %s', char, self.receiver)
            role = userdata.get('role', 0L)
            if role & service.ROLE_CHTINVISIBLE:
                if self.verbose:
                    logger.debug('Ignoring charID %s because role %s includes ROLE_CHTINVISIBLE', char, role)
                return
            ownerInfo = cfg.eveowners.Get(char)
            if char in self.userlistNodesByName:
                return
            node = self._GetUserEntryNode(char, ownerInfo, userdata)
            idx = self.GetIdxForUser_WithBinarySearch(node.charIndex)
            self.userlistNodesByName[char] = node
            updateScroll = False
            self.userlist.AddNodes(idx, [node], updateScroll=updateScroll)
            node.positionFromTop = idx * node.height
            throttleFunc = self.GetThrottleFunc()
            throttleFunc()
        elif self.verbose:
            logger.debug('%s is already in channel %s', char, self.receiver)
        self.UpdateCaption()

    def GetThrottleFunc(self):
        if getattr(self, 'throttleFunc', None):
            return self.throttleFunc

        @threadutils.throttled(0.5)
        def UpdateScrollAfterNodeAddition_throttled():
            clipperWidth, clipperHeight = self.userlist.sr.clipper.GetAbsoluteSize()
            with self.userlist.KillUpdateThreadAndBlock():
                self.userlist.UpdateNodesWidthAndPosition(clipperWidth)
                self.userlist.UpdatePosition(fromWhere='AddNodes')

        self.throttleFunc = UpdateScrollAfterNodeAddition_throttled
        return self.throttleFunc

    @telemetry.ZONE_METHOD
    def GetIdxForUser(self, ownerName):
        idx = 0
        for each in self.userlist.GetNodes():
            if each.charIndex > ownerName:
                break
            idx += 1

        return idx

    @telemetry.ZONE_METHOD
    def GetIdxForUser_WithBinarySearch(self, ownerName):
        a = self.userlist.GetNodes()
        x = ownerName
        lo = 0
        hi = len(a)
        while lo < hi:
            mid = (lo + hi) // 2
            if x < a[mid].charIndex:
                hi = mid
            else:
                lo = mid + 1

        return lo

    def _GetUserEntryNode(self, charID, ownerInfo, userdata):
        node = GetFromClass(self._user_entry_type, {'channelID': self.receiver,
         'charID': charID,
         'info': ownerInfo,
         'corpID': userdata.get('corpid', None),
         'allianceID': userdata.get('allianceid', None),
         'warFactionID': userdata.get('warfactionid', None),
         'color': get_color_for_role(userdata.get('role', None)),
         'showChatBubble': not self._compact_member_entries_setting.is_enabled(),
         'charIndex': ownerInfo.name.lower()})
        return node

    def CharacterLeftChannel(self, char):
        self.lastActivityTime = blue.os.GetWallclockTime()
        if char in self.members:
            if self.verbose:
                logger.debug('%s left channel %s', char, self.receiver)
            try:
                userdata = self.members.pop(char, {})
                node = self.userlistNodesByName[char]
                del self.userlistNodesByName[char]
                self.userlist.RemoveNodes([node])
            except KeyError:
                if userdata and userdata.get('role', 0L) & service.ROLE_CHTINVISIBLE:
                    pass
                else:
                    logger.exception('Error removing character from channel')

            self.UpdateCaption()
        elif self.verbose:
            logger.debug('%s already left channel %s', char, self.receiver)
        if char in self.userlistNodesByName:
            try:
                channelId = self.receiver
                raise RuntimeError('Userlist node still exists for character after leaving channel')
            except RuntimeError:
                logger.exception('Userlist node still exists for character after leaving channel')

    def CanInvite(self, charid):
        channelName = self.receiver
        if not IsChannelPrivate(channelName):
            return False
        if charid in self.members:
            return False
        return True

    def CanKillChannel(self):
        if self.channelCategory in [CATEGORY_PRIVATE,
         CATEGORY_PLAYER,
         CATEGORY_BOT,
         CATEGORY_SYSTEM]:
            return True
        return False

    def SetChannel(self, channel):
        if channel == self.receiver:
            return
        logger.info('Switching %s from %s to %s', self.name, self.receiver, channel)
        self.receiver = channel
        self.userlist.Clear()
        self.userlistNodesByName = {}
        self.members = {}
        self.SetCaptionAsDisplayName()
        self.Receive(const.ownerSystem, localization.GetByLabel('UI/Chat/ChannelWindow/ChannelChangedToChannelName', channelName=GetChatService().GetDetailedDisplayName(channel)))
        if GetChannelCategory(channel) != self.channelCategory:
            logger.warning('Channel category changes from %s to %s', self.channelCategory, GetChannelCategory(channel))
        self.channelCategory = GetChannelCategory(channel)
        if self.channelCategory in (CATEGORY_LOCAL,
         CATEGORY_LOCAL_SUPPRESSED,
         CATEGORY_WORMHOLE,
         CATEGORY_NULLSEC,
         CATEGORY_TRIGLAVIAN):
            solarsystem = int(GetChannelDifferentiator(channel))
            if solarsystem != session.solarsystemid2:
                logger.warning('Switching local channel to %s while current system is %s', solarsystem, session.solarsystemid2)
        if not self.hasStartedUpdateApproximateCount:
            if self.channelCategory in CHANNELS_WITH_NO_PRESENCE_BROADCAST:
                self.hasStartedUpdateApproximateCount = True
                uthread2.start_tasklet(self._UpdateApproximateCount)
        self._ResetTrackActivityPerMember()
        if self.channelCategory == CATEGORY_LOCAL_SUPPRESSED:
            self.CharacterJoinedChannel(session.charid)

    def SetCaptionAsDisplayName(self):
        name = StripTags(GetChatService().GetDisplayName(self.receiver))
        if name is None:
            if self.displayName is None:
                logger.error('GetDisplayName returned None and display name is not currently set')
                self.displayName = self.receiver
        else:
            self.displayName = name
        self.SetCaption(self.displayName)
        if self.verbose:
            logger.debug('Caption set as %s', self.displayName)
        uthread2.start_tasklet(GetChatService().StoreChannelList)
        self.UpdateCaption()

    def UpdateChannelCaptionCounter(self):
        if not self.displayName:
            self.displayName = StripTags(GetChatService().GetDisplayName(self.receiver))
        caption = self.displayName or ''
        if self.channelCategory in [CATEGORY_WORMHOLE, CATEGORY_NULLSEC, CATEGORY_TRIGLAVIAN]:
            count = 0
        elif self.channelCategory in CHANNELS_WITH_NO_PRESENCE_BROADCAST:
            count = self.approximateMemberCount
        elif len(self.members) > 1:
            count = len(self.members)
            caption += ' [%d]' % count
        else:
            count = 0
        self.SetCaption(caption)
        self.SetMemberCountDisplay(count)

    def _UpdateApproximateCount(self):
        logger.debug('Starting update loop for approximate member count for %s', self.receiver)
        while not self.destroyed:
            interval = GetUpdateChannelCountIntervalSeconds(sm.GetService('machoNet'))
            if interval > 0:
                logger.debug('Getting member count for %s', self.receiver)
                self.approximateMemberCount = GetChatService().GetNumChannelOccupants(self.receiver)
                self.SetMemberCountDisplay(self.approximateMemberCount)
                uthread2.sleep(interval)
            else:
                uthread2.sleep(300)

    def UpdatePrivateChannelCaption(self):
        caption = GetChatService().GetPrivateChannelDisplayName(self.receiver)
        self.SetCaption(caption)

    def SetMemberCountDisplay(self, count):
        if self.channelCategory in (CATEGORY_PRIVATE,
         CATEGORY_WORMHOLE,
         CATEGORY_NULLSEC,
         CATEGORY_TRIGLAVIAN) or not count:
            self.numMembersCont.display = False
            self.numMembersLabel.countDisplayed = count
            return
        self.numMembersCont.display = True
        countDisplayed = getattr(self.numMembersLabel, 'memberCount', None)
        if count != countDisplayed:
            self.numMembersLabel.text = count
            self.numMembersLabel.countDisplayed = count

    def GetChannelId(self):
        return self.receiver

    def GetMenu(self, *args):
        menu = MenuData()
        menu.AddCaption(self.caption)
        menu.AddSeparator()
        self._AddChannelMenu(menu)
        tab_menu = CreateMenuDataFromRawTuples(super(XmppChatWindow, self).GetMenu(*args))
        if tab_menu is not None and tab_menu.GetEntries():
            menu += tab_menu
            menu.AddSeparator()
        return menu

    def _AddChannelMenu(self, menu):
        gm_options = MenuData()
        if session.role & service.ROLE_GML:
            gm_options.AddEntry(text='channel id: ' + self.receiver, func=lambda : blue.pyos.SetClipboardData(self.receiver))
            gm_options.AddEntry(text='category id: ' + self.channelCategory, func=lambda : blue.pyos.SetClipboardData(self.channelCategory))
            gm_options.AddEntry(text='window id: ' + self.windowID, func=lambda : blue.pyos.SetClipboardData(self.windowID))
        pokeRoles = service.ROLE_LEGIONEER | service.ROLE_CENTURION | service.ROLE_GMH | service.ROLE_GMS | service.ROLE_GML | service.ROLE_WORLDMOD
        if session.role & pokeRoles and GetChannelCategory(self.receiver) == CATEGORY_PRIVATE:
            for memberID in self.GetMembers():
                if memberID != session.charid:
                    gm_options.AddEntry(text='Poke %s' % cfg.eveowners.Get(memberID).name, func=lambda _member_id = memberID: GetChatService().PokePlayerAboutChatMsgGm(_member_id, self.receiver))
                    break

        if gm_options.GetEntries():
            menu.AddEntry(text='GM / WM Extras', subMenuData=gm_options)
        self._add_elevated_options(menu)
        menu.AddLabel(localization.GetByLabel('UI/Chat/ChannelSettingsSection'))
        if self._should_show_channel_settings_option():
            menu.AddEntry(text=localization.GetByLabel('UI/Chat/Configuration'), texturePath=eveicon.settings, func=self._OpenSettingsWindow)
        member_list_options = MenuData()
        member_list_options.AddCheckbox(text=localization.GetByLabel('UI/Chat/ShowMemberList'), setting=self._show_member_list_setting)
        member_list_options.AddSeparator()
        member_list_options.AddCheckbox(text=localization.GetByLabel('UI/Chat/ShowCompactMemberList'), setting=self._compact_member_entries_setting)
        menu.AddEntry(text=localization.GetByLabel('UI/Chat/MemberList'), texturePath=eveicon.people, subMenuData=member_list_options)
        menu.AddEntry(text=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/FontSize'), texturePath=eveicon.font_size, subMenuData=self._get_font_size_menu)
        menu.AddEntry(text=localization.GetByLabel('UI/Chat/MessagePortraits'), texturePath=eveicon.person, subMenuData=self._get_message_style_menu)
        if has_hide_message_setting(self.channelCategory):
            menu.AddEntry(text=localization.GetByLabel('UI/Chat/MessageFilterContextMenu'), texturePath=eveicon.filter, func=self._OpenHideMessageSettings)
        menu.AddCheckbox(text=localization.GetByLabel('UI/Chat/BlinkOnNewActivity'), setting=self._chat_notifications_enabled_setting)
        category = self.receiver.split('_')[0]
        if category in MOTD_CHANNEL_TYPES:
            menu.AddEntry(text=localization.GetByLabel('UI/Chat/ReloadChannelMOTD'), func=self.ShowMotdFromMenu)
        menu.AddEntry(text=localization.GetByLabel('UI/Chat/ClearAllContent'), func=self.ClearContent)
        menu.AddSeparator()
        menu.AddLabel(localization.GetByLabel('UI/Chat/GlobalSettingsSection'))
        autoCollapseMenu = MenuData()
        autoCollapseMenu.AddCheckbox(localization.GetByLabel('UI/Chat/AutoCollapseMessagesEnabled'), hint=localization.GetByLabel('UI/Chat/AutoCollapseMessagesHint'), setting=auto_collapse_messages)
        autoCollapseMenu.AddSlider(localization.GetByLabel('UI/Chat/AutoCollapseMessagesLines'), setting=auto_collapse_message_lines, isInteger=True)
        menu.AddEntry(text=localization.GetByLabel('UI/Chat/AutoCollapseMessages'), hint=localization.GetByLabel('UI/Chat/AutoCollapseMessagesHint'), texturePath=eveicon.collapse, subMenuData=autoCollapseMenu)
        menu.AddCheckbox(text=localization.GetByLabel('UI/Chat/HighlightMyMessages'), setting=highlight_my_messages_setting)
        menu.AddCheckbox(text=localization.GetByLabel('UI/Chat/ShowTimestamp'), setting=show_message_timestamp_setting)
        menu.AddEntry(text=localization.GetByLabel('UI/Chat/ConfigureWordFiltersAndHighlights'), func=self.SetWordAndHightlightFilters)

    def _HandleInputOnReturn(self):
        txt = self.input.GetValue(html=0)
        txt = StripBreaks(txt)
        txt = self._GetStrippedText(txt)
        if not txt:
            return
        bannedwords.check_chat_character_allowed(session.charid)
        bannedwords.check_chat_words_allowed(txt)
        self._FlushTimedOutPendingMessages()
        if len(self.myPendingMessages) > 4:
            logger.warning('Too many pending messages')
            eve.Message('uiwarning03')
            return
        self.input.SetValue('')
        if self.inputs[-1] != txt:
            self.inputs.append(txt)
        self.inputIndex = None
        if txt.startswith(SLASH_ME_STRING):
            txt = txt.replace(SLASH_ME_STRING, SLASH_EMOTE_STRING, 1)
        if GetChatService().IsCharacterBanned():
            self.OnCharacterBannedNotify()
            return
        if txt.startswith('/') and not (txt.startswith(SLASH_EMOTE_STRING) or txt == '/'):
            self._HandleSlashCommand(txt)
        else:
            txt = TruncateVeryLongText(txt)
            check_banned_message_in_new_player_channel(self.channelCategory, txt)
            node = self._Output(eve.session.charid, txt)
            if self.channelCategory == CATEGORY_LOCAL_SUPPRESSED:
                return
            msg_id = self._Send(txt)
            timestamp = blue.os.GetWallclockTime()
            self.myPendingMessages[msg_id] = (node, timestamp)

    def _FlushTimedOutPendingMessages(self):
        now = blue.os.GetWallclockTime()
        stillPending = {}
        for k, v in self.myPendingMessages.iteritems():
            node, timestamp = v
            if blue.os.TimeDiffInMs(timestamp, now) > 60000:
                XmppChatEntry.MarkMessageUndelivered(node)
            else:
                stillPending[k] = v

        self.myPendingMessages = stillPending

    def _HandleInputCtrlDown(self, editctrl):
        self._BrowseInputs(1)

    def _HandleInputCtrlUp(self, editctrl):
        self._BrowseInputs(-1)

    def _BrowseInputs(self, updown):
        if self.inputIndex is None:
            self.inputIndex = len(self.inputs) - 1
        else:
            self.inputIndex += updown
        if self.inputIndex < 0:
            self.inputIndex = len(self.inputs) - 1
        elif self.inputIndex >= len(self.inputs):
            self.inputIndex = 0
        self.input.SetValue(self.inputs[self.inputIndex], cursorPos=-1)

    def _RegisterFocus(self, edit, *args):
        sm.GetService('focus').SetFocusChannel(self)

    def SetCharFocus(self, char):
        uicore.registry.SetFocus(self.input)
        uicore.layer.menu.Flush()
        if char is not None:
            self.input.OnChar(char, 0)

    def OnTabSelect(self):
        uicore.registry.SetFocus(self.input)
        if self.pendingPortraitReloads:
            if self.verbose:
                logger.debug('Triggering reload of %d portraits', len(self.pendingPortraitReloads))
            self._ReloadPendingPortraits()

    def _HandleSlashCommand(self, txt):
        for commandLine in StripTags(txt, ignoredTags=('br',)).split('<br>'):
            try:
                slashRes = uicore.cmd.Execute(commandLine)
                if slashRes is not None:
                    sm.GetService('logger').AddText('slash result: %s' % slashRes, 'slash')
                elif txt.startswith('/tutorial') and eve.session and eve.session.role & service.ROLE_GML:
                    sm.GetService('tutorial').SlashCmd(commandLine)
                elif txt.startswith('/advantage') and session and session.role & service.ROLE_GML:
                    sm.GetService('fwAdvantageSvc').HandleSlashCmd(commandLine)
                elif sm.GetService('publicQaToolsClient').CommandAllowed(commandLine):
                    sm.GetService('publicQaToolsClient').SlashCmd(commandLine)
                elif eve.session and eve.session.role & ROLE_SLASH:
                    if commandLine.lower().startswith('/mark'):
                        sm.StartService('logger').LogError('SLASHMARKER: ', (eve.session.userid, eve.session.charid), ': ', commandLine)
                    commandLine = self._adjust_commandLine(commandLine)
                    slashRes = sm.GetService('slash').SlashCmd(commandLine)
                    if slashRes is not None:
                        sm.GetService('logger').AddText('slash result: %s' % slashRes, 'slash')
                self._Output(eve.session.charid, '/slash: ' + commandLine)
            except:
                self._Output(eve.session.charid, '/slash failed: ' + commandLine)
                raise

    def _adjust_commandLine(self, commandLine):
        COMMANDS_NEEDING_EXTRA_PARAMS = ('/chtban', '/chtunban', '/chtgag', '/chtungag', '/massfleetinvite', '/masstransport')
        parts = commandLine.split(' ', 1)
        command = parts[0].strip().lower()
        if command in COMMANDS_NEEDING_EXTRA_PARAMS:
            if command in ('/massfleetinvite', '/masstransport'):
                extra_params = 'windowID={}'.format(self.windowID)
            else:
                extra_params = 'channelName={}'.format(self.channelName)
            parts.insert(1, extra_params)
            commandLine = ' '.join(parts)
        return commandLine

    def _Send(self, text):
        if text == '':
            return
        if IsSpam(text):
            return
        return GetChatService().SendGroupChat(self.receiver, text)

    def LoadMessages(self):
        portion = self.output.GetScrollProportion()
        self.output.Clear()
        nodes = []
        for sender, text, timestamp, colorkey in self.messages:
            node = self._GetChatEntry(sender, text, timestamp, colorkey)
            nodes.append(node)

        self.output.AddNodes(-1, nodes)
        if portion:
            self.output.ScrollToProportion(portion)

    def OnOutputOrInputKeyUp(self, key, *args):
        if elevated_chat_highlighting_setting.is_enabled():
            self.TurnHighlightOff()

    def IsHilighting(self, *args):
        return elevated_chat_highlighting_setting.is_enabled() and uicore.uilib.Key(uiconst.VK_CONTROL)

    def HighlightTextInOutput(self, findText = '', *args):
        if not self.IsHilighting():
            return
        if len(findText.strip().replace('(', '').replace(')', '')) < 2:
            return
        if getattr(self, 'highlightedText', '') and self.highlightedText != findText:
            self.TurnHighlightOff()
        self.highlightedText = findText
        nodes = self.output.GetNodes()
        for eachNode in nodes:
            if eachNode.panel:
                eachNode.panel.LoadHighlightedText(findText)

    def TurnHighlightOff(self, *args):
        highlightedText = getattr(self, 'highlightedText', '')
        if not highlightedText:
            return
        for eachNode in self.output.GetNodes():
            if eachNode.panel:
                eachNode.panel.RemoveHighlightedText()

        self.highlightedText = None

    def _GetChatEntry(self, sender, text, timestamp, colorkey):
        try:
            charid = int(sender)
        except ValueError:
            charid = sender

        if elevated_chat_highlighting_setting.is_enabled():
            highlightFunc = self.HighlightTextInOutput
            collectWordsInStack = True
        else:
            highlightFunc = None
            collectWordsInStack = False
        if auto_collapse_messages.get() and charid and charid != session.charid and IsEvePlayerCharacter(charid):
            maxLines = int(auto_collapse_message_lines.get())
        else:
            maxLines = None
        node = ScrollEntryNode(decoClass=XmppChatEntry, text=text, timestamp=timestamp, fontsize=self._get_font_size(), letterspace=self._get_letter_space(), sender=sender, charid=charid, mode=self._message_style_setting.get(), colorkey=colorkey, channelMenu=self.GetOutputMenu, mouseOverWordCallback=highlightFunc, collectWordsInStack=collectWordsInStack, channelid=self.receiver, maxLines=maxLines, showExpander=False)
        return node

    def GetColorKeyForSender(self, sender):
        try:
            charid = int(sender)
        except ValueError:
            charid = sender

        if charid == session.charid:
            colorkey = session.role
        elif charid == const.ownerSystem:
            colorkey = service.ROLE_ADMIN
        else:
            userdata = self.members.get(charid, {})
            colorkey = userdata.get('role', None)
        return colorkey

    def _OnClose(self, *args, **kw):
        if self.verbose:
            logger.debug('_OnClose %s', self.receiver)
        if self == sm.GetService('focus').GetFocusChannel():
            sm.GetService('focus').SetFocusChannel()
        if self.checkConnectionStatusTasklet:
            self.checkConnectionStatusTasklet.kill()
            self.checkConnectionStatusTasklet = None
        if self.removeIdleCharactersTasklet:
            self.removeIdleCharactersTasklet.kill()
            self.removeIdleCharactersTasklet = None
        if not self._has_left_channel:
            self._has_left_channel = True
            if self.logfile is not None:
                self.logfile.Close()
                self.logfile = None
            if not self.access_lost:
                if sm.IsServiceRunning('XmppChat'):
                    xmppSvc = sm.GetService('XmppChat')
                    xmppSvc.LeaveChannel(self.receiver)
                    if xmppSvc.isDoingLogoff is False:
                        windowName = self.name.replace('chatchannel_', '')
                        xmppSvc.RemoveChannelFromCurrentChannelsSettings(windowName)

    def MaybeAddSettingsOptionsToMenuParent(self, mParent):
        if self._should_show_channel_settings_option():
            mParent.AddIconEntry(icon=ACTION_ICON, text=localization.GetByLabel('UI/Chat/OpenChannelSettingsWnd'), callback=self._OpenSettingsWindow)

    def _should_show_channel_settings_option(self):
        channel_category = GetChannelCategory(self.receiver)
        if channel_category in (CATEGORY_CORP, CATEGORY_ALLIANCE):
            if IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
                return False
            else:
                return self._HasSuitableCorpRolesForChatManagement(channel_category)
        else:
            is_owner_or_operator = self._IsOwnerOrOperatorOfChannel_Memoized(self.receiver)
            if not is_owner_or_operator and channel_category == CATEGORY_FLEET:
                if sm.GetService('fleet').IsBoss():
                    return True
            return is_owner_or_operator

    @Memoize(0.2)
    def _HasSuitableCorpRolesForChatManagement(self, channelCategory):
        if session.corprole & const.corpRoleChatManager != const.corpRoleChatManager:
            return False
        if channelCategory == CATEGORY_ALLIANCE:
            allianceInfo = sm.GetService('alliance').GetAlliance()
            if not allianceInfo or allianceInfo.executorCorpID != session.corpid:
                return False
        return True

    @Memoize(0.2)
    def _IsOwnerOrOperatorOfChannel_Memoized(self, channelName):
        return GetChatService().IsOwnerOrOperatorOfChannel(channelName)

    def _OpenSettingsWindow(self):
        ChannelSettingsDlg.Open(channel=self.receiver, windowID='ChannelSettingsDlg_%s' % self.receiver)

    def GetUserEntry(self, charID):
        for each in self.userlist.GetNodes():
            if each.charID == charID:
                return each

    def SetWordAndHightlightFilters(self):
        ChatFilterSettings.Open()

    def _OpenHideMessageSettings(self):
        categoryID = self.channelCategory
        if categoryID in LOCAL_CHAT_CATEGORIES:
            categoryID = ChatCategory.LOCAL
        open_hide_message_settings(category_id=categoryID, channel_id=self.receiver, channel_name=GetChatService().GetDetailedDisplayName(self.receiver))

    def SetPictureMode(self, pictureMode):
        self._message_style_setting.set(pictureMode)

    def GetMenuMoreOptions(self):
        menu = super(XmppChatWindow, self).GetMenuMoreOptions()
        self._AddChannelMenu(menu)
        return menu

    def _get_message_style_menu(self):
        menu = MenuData()
        for mode in self._message_style_setting.options:
            menu.AddRadioButton(text=localization.GetByLabel(MESSAGEMODETEXTS[mode]), value=mode, setting=self._message_style_setting)

        return menu

    def _get_font_size_menu(self):
        menu = MenuData()
        menu.AddCheckbox(text=localization.GetByLabel('UI/Chat/UseFontSizeInAllChannels'), setting=self._apply_font_size_globally_setting)
        menu.AddSeparator()
        for font_size in self._effective_font_size_setting.options:
            menu.AddRadioButton(text=str(font_size), value=font_size, setting=self._effective_font_size_setting)

        return menu

    @staticmethod
    def _add_elevated_options(menu):
        role_mask = service.ROLE_CENTURION | service.ROLE_LEGIONEER | service.ROLEMASK_ELEVATEDPLAYER
        if session.role & role_mask:
            menu.AddCheckbox(text='Special chat highlighting', setting=elevated_chat_highlighting_setting)
            menu.AddSeparator()

    def SettingMenu(self, menuParent):
        category = self.receiver.split('_')[0]
        if category in MOTD_CHANNEL_TYPES:
            menuParent.AddIconEntry(icon=ACTION_ICON, text=localization.GetByLabel('UI/Chat/ReloadMOTD'), callback=self.ShowMotdFromMenu)
        self.MaybeAddSettingsOptionsToMenuParent(menuParent)
        menuParent.AddDivider()
        menuParent.AddIconEntry(icon=ACTION_ICON, text=localization.GetByLabel('UI/Chat/ChannelWindow/SetWordFilters'), callback=self.SetWordAndHightlightFilters)
        menuParent.AddDivider()
        message_style = self._message_style_setting.get()
        menuParent.AddRadioButton(text=localization.GetByLabel(MESSAGEMODETEXTS[MESSAGEMODE_TEXTONLY]), checked=message_style == MESSAGEMODE_TEXTONLY, callback=(self.SetPictureMode, MESSAGEMODE_TEXTONLY))
        menuParent.AddRadioButton(text=localization.GetByLabel(MESSAGEMODETEXTS[MESSAGEMODE_SMALLPORTRAIT]), checked=message_style == MESSAGEMODE_SMALLPORTRAIT, callback=(self.SetPictureMode, MESSAGEMODE_SMALLPORTRAIT))
        menuParent.AddRadioButton(text=localization.GetByLabel(MESSAGEMODETEXTS[MESSAGEMODE_BIGPORTRAIT]), checked=message_style == MESSAGEMODE_BIGPORTRAIT, callback=(self.SetPictureMode, MESSAGEMODE_BIGPORTRAIT))
        menuParent.AddDivider()
        cont = menuParent.AddContainer(padding=(6, 15, 6, 4), height=18)
        Combo(name='fontSizeCombo', parent=cont, align=uiconst.TOTOP, label=localization.GetByLabel('/Carbon/UI/Controls/EditRichText/FontSize'), options=[ (str(size), size) for size in self._font_size_setting.options ], callback=self.OnFontSizeCombo, select=self._get_font_size())
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Chat/ApplyFontsizeToAllWnds'), checked=self._apply_font_size_globally_setting.is_enabled(), callback=self._apply_font_size_globally_setting.toggle)
        menuParent.AddDivider()
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Chat/BlinkOn'), checked=self._chat_notifications_enabled_setting.is_enabled(), callback=self._chat_notifications_enabled_setting.toggle)
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Chat/HighlightMyMessages'), checked=highlight_my_messages_setting.is_enabled(), callback=highlight_my_messages_setting.toggle)
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Chat/ShowTimestamp'), checked=show_message_timestamp_setting.is_enabled(), callback=show_message_timestamp_setting.toggle)
        menuParent.AddDivider()
        menuParent.AddIconEntry(icon=ACTION_ICON, text=localization.GetByLabel('UI/Chat/ClearAllContent'), callback=self.ClearContent)
        menuParent.AddDivider()
        roleMask = service.ROLE_CENTURION | service.ROLE_LEGIONEER | service.ROLEMASK_ELEVATEDPLAYER
        if session.role & roleMask:
            chatHightlighting = elevated_chat_highlighting_setting.is_enabled()
            if chatHightlighting:
                text = 'Turn chat highlighting off'
            else:
                text = 'Turn chat highlighting on'
            menuParent.AddIconEntry(icon=ACTION_ICON, text=text, callback=elevated_chat_highlighting_setting.toggle)

    def UserListMenu(self, menuParent):
        if self.channelCategory in CHANNELS_WITH_NO_PRESENCE_BROADCAST:
            memberText = localization.GetByLabel('UI/Chat/MemberListRecentText')
            hint = localization.GetByLabel('UI/Chat/MemberListRecentSpeakers')
        else:
            memberText = localization.GetByLabel('UI/Chat/ShowMemberList')
            hint = None
        menuParent.AddCheckBox(text=memberText, checked=self._show_member_list_setting.is_enabled(), callback=self._show_member_list_setting.toggle, hint=hint)
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Chat/ShowCompactMemberList'), checked=self._compact_member_entries_setting.is_enabled(), callback=self._compact_member_entries_setting.toggle)

    def _get_compact_member_entries_setting_key(self):
        if self.channelCategory in SINGLE_WND_CATEGORIES:
            name_part = self.channelCategory
        else:
            name_part = self.name
        return 'chatCondensedUserList_%s' % name_part

    def SetupUserlist(self):
        if self.destroyed:
            return
        if not self._show_member_list_setting.is_enabled():
            self._user_list_cont.state = uiconst.UI_HIDDEN
        else:
            minW = 50
            maxW = 200
            self._user_list_cont.width = min(maxW, max(minW, self._user_list_cont.width))
            self._user_list_cont.state = uiconst.UI_PICKCHILDREN
            condensed = self._compact_member_entries_setting.is_enabled()
            if condensed != getattr(self.userlist, 'isCondensed', False):
                self.InitUsers()

    def InitUsers(self):
        self.userlist.Clear()
        nodeListToSort = []
        for char, userdata in self.members.iteritems():
            role = userdata.get('role', 0L)
            if role & service.ROLE_CHTINVISIBLE:
                logger.debug('Ignoring charID %s because role %s includes ROLE_CHTINVISIBLE', char, role)
                continue
            ownerInfo = cfg.eveowners.Get(char)
            node = self._GetUserEntryNode(char, ownerInfo, userdata)
            nodeListToSort.append(node)
            self.userlistNodesByName[char] = node

        nodeList = sorted(nodeListToSort, key=lambda x: x.charIndex)
        self.userlist.AddNodes(-1, nodeList)

    def OpenChannelWindow(self):
        XmppChatChannels.Open()

    def ShowMotdFromMenu(self):
        if self.motd:
            msg = localization.GetByLabel('UI/Chat/ChannelMotd', motd=self.motd)
            self._Output(const.ownerSystem, msg)

    def GetOutputMenu(self, *args):
        m = [(MenuLabel('UI/Common/CopyAll'), self.CopyAll)]
        return m

    def CopyAll(self):
        t = ''
        for node in self.output.GetNodes():
            timestr = ''
            if show_message_timestamp_setting.is_enabled():
                year, month, wd, day, hour, min, sec, ms = GetTimeParts(node.timestamp)
                timestr = '[%02d:%02d:%02d] ' % (hour, min, sec)
            who = node.sender
            try:
                who = cfg.eveowners.Get(who).name
            except ValueError:
                pass

            text = node.text.replace('&gt;', '>').replace('&amp;', '&')
            text = CleanText(text)
            t += '%s%s > %s\r\n' % (timestr, who, text)

        blue.pyos.SetClipboardData(t)

    def ClearContent(self):
        if self.output:
            self.output.Clear()
            self.messages = []

    def OnFontSizeCombo(self, combo, label, value):
        self._font_size_setting.set(value)

    def OnDropCharacter(self, dragObj, nodes):
        for node in nodes[:5]:
            charID = GetCharIDFromTextLink(node)
            if not charID:
                guid = getattr(node, '__guid__', None)
                if guid not in AllUserEntries():
                    return
                charID = node.charID
            if IsCharacter(charID):
                GetChatService().Invite(charID, self.receiver)

    def OnPortraitCreated(self, charID, _size):
        if self.destroyed or self.output is None:
            return
        if self.verbose:
            logger.debug('OnPortraitCreated %s', charID)
        self.pendingPortraitReloads.add(charID)
        if self.state == uiconst.UI_HIDDEN:
            return
        self._ReloadPendingPortraits()

    def _ReloadPendingPortraits(self):
        if not self.pendingPortraitReloads:
            return
        for node in self.output.GetNodes():
            if not node.panel or node.panel.state == uiconst.UI_HIDDEN:
                continue
            if node.charid in self.pendingPortraitReloads and not node.panel.picloaded:
                node.panel.LoadPortrait(orderIfMissing=False)

        if self.userlist.state != uiconst.UI_HIDDEN:
            for charid in self.pendingPortraitReloads:
                userNode = self.GetUserEntry(charid)
                if userNode and userNode.panel:
                    if not userNode.panel.picloaded:
                        userNode.panel.LoadPortrait(orderIfMissing=False)

        self.pendingPortraitReloads = set()

    def _on_elevated_chat_highlighting_setting_changed(self, value):
        if elevated_chat_highlighting_setting.is_enabled():
            if self.input and not self.input.destroyed:
                self.input.OnKeyUp = self.OnOutputOrInputKeyUp
            if self.output and not self.output.destroyed:
                self.output.OnKeyUp = self.OnOutputOrInputKeyUp
        else:
            if self.input and not self.input.destroyed:
                self.input.OnKeyUp = None
            if self.output and not self.output.destroyed:
                self.output.OnKeyUp = None
        self.TurnHighlightOff()
        self.LoadMessages()

    def _CheckConnectionStatus(self):
        while not self.destroyed:
            sleepPeriod = GetMaxChatChannelIdleTime(sm.GetService('machoNet'))
            if sleepPeriod == 0:
                uthread2.Sleep(300)
                continue
            sleepPeriod += random.random() * 3.0
            uthread2.Sleep(sleepPeriod)
            if self.destroyed:
                break
            now = blue.os.GetWallclockTime()
            deltaInSec = blue.os.TimeDiffInMs(self.lastActivityTime, now) / 1000.0
            if deltaInSec > sleepPeriod:
                if self.verbose:
                    logger.debug('No activity on %s for %s seconds', self.receiver, deltaInSec)
                GetChatService().JoinChannel(self.receiver, suppressMessage=True, isConnectionCheck=True, historySeconds=deltaInSec - 2)

    def OnMouseUp(self, _):
        uthread2.start_tasklet(self.StackSelf)

    def StackSelf(self):
        if self.stacked:
            self.stack.Check()
        elif self.FindWindowToStackTo():
            pass
        else:
            self._ConstructStack([(self, 1)], [])

    def ValidatePaste(self, text):
        return sm.GetService('chat').validate_paste(text)

    def _GetExtraIgnoredTags(self, text):
        return sm.GetService('helpPointer').FindTagToIgnore(text)

    def UpdateCaption(self):
        if self.channelCategory == CATEGORY_PRIVATE:
            self.UpdatePrivateChannelCaption()
        else:
            self.UpdateChannelCaptionCounter()

    def GetRecentEntriesFromCharID(self, charID):
        all_entries = self.output.GetNodes()
        selected_entries = []
        for e in all_entries:
            if e.charid == charID:
                who = e.sender
                try:
                    who = cfg.eveowners.Get(who).name
                except ValueError:
                    pass

                text = e.text.replace('&gt;', '>').replace('&amp;', '&')
                time = e.timestamp
                selected_entries.append('[%s] %s > %s' % (FmtDate(time, 'nl'), who, text))

        selected_entries = selected_entries[-10:]
        selected_entries.reverse()
        return selected_entries

    def OnCharacterBannedNotify(self):
        self.Receive(const.ownerSystem, GetChatService().GetCharacterBannedMessage())

    def _get_font_size(self):
        font_size = global_font_size_setting.get()
        if font_size is None:
            font_size = self._font_size_setting.get()
        return font_size

    def _get_letter_space(self):
        font_size = self._get_font_size()
        small_font_size = get_font_size_for_preset(EVE_SMALL_FONTSIZE)
        if font_size <= small_font_size:
            return 1
        else:
            return 0

    def _update_font_size(self):
        self.LoadMessages()
        self.input.SetDefaultFontSize(self._get_font_size())

    def _on_font_size_setting_changed(self, value):
        if self._apply_font_size_globally_setting.is_enabled():
            global_font_size_setting.set(self._font_size_setting.get())
        else:
            self._update_font_size()

    def _on_apply_font_size_globally_setting_changed(self, value):
        if self._apply_font_size_globally_setting.is_enabled():
            global_font_size_setting.set(self._font_size_setting.get())

    def _on_global_font_size_setting_changed(self, value):
        self._update_font_size()

    def _on_message_style_setting_changed(self, value):
        self._update_message_style()

    def _update_message_style(self):
        self.LoadMessages()
        uicore.registry.SetFocus(self)

    def _on_show_member_list_setting_changed(self, value):
        self.SetupUserlist()

    def _on_compact_member_entries_setting_changed(self, value):
        is_compact = self._compact_member_entries_setting.is_enabled()
        if self._show_member_list_setting.is_enabled():
            self.userlist.entry_spacing = self._get_user_list_entry_spacing()
            self.InitUsers()
        self.userlist.isCondensed = is_compact if self.userlist.display else -1

    def _get_user_list_entry_spacing(self):
        if self._compact_member_entries_setting.is_enabled():
            return 1
        else:
            return 4
