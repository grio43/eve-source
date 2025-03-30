#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\uilog.py
import os
import sys
import blue
import eveicon
import evetypes
import signals
import uthread
from actionLog.client.formatters import FormatBountyMessage, FormatModifiedBountyMessage, FormatMiningMessage, FormatMiningRewardsMessage, FormatOreDepositedMessage, FormatPirateKilledMessage
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_SERVICE
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuEntryData import MenuEntryDataCheckbox, MenuEntryDataRadioButton
from carbonui.control.window import Window
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.services.setting import UserSettingBool, UserSettingEnum
from carbonui.uicore import uicore
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.button.menu import MenuButtonIcon
from eve.client.script.ui.menuUtil import DESTRUCTIVEGROUP
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from carbon.common.script.util import timerstuff
from carbon.common.script.util.logUtil import LogError, LogException, LogInfo, LogWarn
from eve.client.script.ui.control import eveScroll
import localization
import telemetry
import trinity
import itertoolsext
import log
from eve.client.script.ui.control.message import CombatMessage
from eve.common.script.sys import idCheckers
from eveprefs import prefs
from menu import MenuLabel
MAX_MSGS = 256
COLORS_BY_TYPE = {'error': '<color=0xffeb3700>',
 'warning': '<color=0xffffd800>',
 'slash': '<color=0xffff5500>',
 'combat': '<color=0xffff0000>',
 'bounty': '<color=0xff00aa00>',
 'mining': '<color=0xffaaaa00>'}
ENERGY_WARFARE_MESSAGES = ['OnEnergyNeutDefender',
 'OnEnergyNeutAttacker',
 'OnEnergyNosDefender',
 'OnEnergyNosAttacker']
INCOMING_REMOTE_ASSISTANCE_MESSAGES = ['OnRemoteShieldBoostTarget',
 'OnRemoteArmorRepairTarget',
 'OnRemoteHullRepairTarget',
 'OnRemoteCapacitorTransmitterTarget']
OUTGOING_REMOTE_ASSISTANCE_MESSAGES = ['OnRemoteShieldBoostSource',
 'OnRemoteArmorRepairSource',
 'OnRemoteHullRepairSource',
 'OnRemoteCapacitorTransmitterSource']
REMOTE_ASSISTANCE_MESSAGES = INCOMING_REMOTE_ASSISTANCE_MESSAGES + OUTGOING_REMOTE_ASSISTANCE_MESSAGES
DAMAGE_TYPE_ICONS = {const.attributeKineticDamage: 'res:/UI/Texture/classes/DamageTypes/Kinetic.png',
 const.attributeThermalDamage: 'res:/UI/Texture/classes/DamageTypes/Thermal.png',
 const.attributeExplosiveDamage: 'res:/UI/Texture/classes/DamageTypes/Explosive.png',
 const.attributeEmDamage: 'res:/UI/Texture/classes/DamageTypes/Electromagnetic.png'}

class Logger(Service):
    __exportedcalls__ = {'AddMessage': [],
     'AddCombatMessage': [],
     'AddText': [],
     'AddBountyMessage': [],
     'AddMiningMessage': [],
     'GetLog': [ROLE_SERVICE]}
    __guid__ = 'svc.logger'
    __notifyevents__ = ['ProcessSessionChange']
    __servicename__ = 'logger'
    __displayname__ = 'Logger Client Service'
    __dependencies__ = []
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.LogInfo('Starting Logger')
        self.broken = 0
        self.Reset()
        self.newfileAttempts = 0
        self.addmsg = []
        self.persistInterval = 1000
        self.combatMessagePeriod = 10000L * prefs.GetValue('combatMessagePeriod', 200)
        self.lastCombatMessage = 0
        self.inMovingMode = False
        self.frameCounterAndWindow = (None, None)
        self.cachedHitQualityText = {}
        self.notificationFontSize = inflight_message_font_size_setting.get()
        uthread.new(self._PersistWorker)

    def Stop(self, memStream = None):
        self.DumpToLog()
        self.messages = []
        self.msglog = []
        self.addmsg = []

    def ProcessSessionChange(self, isremote, session, change):
        if 'charid' in change:
            self.Reset()
        if not session.charid:
            self.Stop()

    def GetTimePartsForLog(self, timestamp = None):
        if timestamp is None:
            timestamp = blue.os.GetWallclockTime()
        timestamp += localization.GetTimeDeltaSeconds() * const.SEC
        return blue.os.GetTimeParts(timestamp)

    def GetLog(self, maxsize = const.petitionMaxCombatLogSize, *args):
        LogInfo('Getting logfiles')
        self.DumpToLog()
        year, month, weekday, day, hour, minute, second, msec = self.GetTimePartsForLog()
        now = '%d%.2d%.2d' % (year, month, day)
        year, month, weekday, day, hour, minute, second, msec = self.GetTimePartsForLog(blue.os.GetWallclockTime() - const.DAY)
        yesterday = '%d%.2d%.2d' % (year, month, day)
        root = blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/logs/Gamelogs'
        logs = []
        for each in os.listdir(root):
            filename = os.path.join(root, each)
            fooname = filename[:-11]
            if fooname.endswith(now) or fooname.endswith(yesterday):
                logs.append((each, filename))

        logs.sort(reverse=True)
        ret = []
        bytesread = 0
        for k, filename in logs:
            f = None
            try:
                f = file(filename)
                tmp = f.read()
                f.close()
                line = '\n\n%s:\n%s' % (filename.encode('utf8', 'replace'), tmp)
                bytesread += len(line)
                ret.append(line)
                if bytesread > maxsize:
                    break
            except:
                LogException()
                sys.exc_clear()
                if f and not f.closed:
                    f.close()

        LogInfo('Getting logfiles done')
        ret.reverse()
        return ''.join(ret)[-maxsize:]

    def Reset(self):
        self.resettime = blue.os.GetWallclockTime()
        self.messages = []
        self.msglog = ['-' * 60 + '\n', '  %s\n' % localization.GetByLabel('UI/Accessories/Log/GameLog').encode('utf8', 'replace')]
        if eve.session.charid:
            self.msglog.append(('  %s: %s\n' % (localization.GetByLabel('UI/Accessories/Log/Listener'), cfg.eveowners.Get(eve.session.charid).name)).encode('utf8', 'replace'))
        self.msglog += [('  %s: %s\n' % (localization.GetByLabel('UI/Accessories/Log/SessionStarted'), FmtDate(self.resettime))).encode('utf8', 'replace'),
         '',
         '-' * 60 + '\n',
         '']
        self.DumpToLog()

    @telemetry.ZONE_METHOD
    def GetWnd(self):
        return LoggerWindow.GetIfOpen()

    @telemetry.ZONE_METHOD
    def GetWndWithFrameCounter(self, *args):
        frameCounter = trinity.GetCurrentFrameCounter()
        if frameCounter == self.frameCounterAndWindow[0]:
            return self.frameCounterAndWindow[1]
        wnd = self.GetWnd()
        self.frameCounterAndWindow = (frameCounter, wnd)
        return wnd

    def GetMessages(self):
        self.addmsg = []
        return self.messages

    def GetPendingMessages(self):
        retval = self.addmsg
        self.addmsg = []
        return retval

    def AddMessage(self, msg, msgtype = None):
        if msg.type == 'error' and not settings.user.ui.Get('logerrors', 0):
            return
        self.AddText(msg.text, msgtype or msg.type or 'notify', msg)

    def GetHitQualityMessage(self, hitQuality):
        try:
            hitQuality = int(hitQuality)
            label = {1: 'UI/Inflight/HitQuality1',
             2: 'UI/Inflight/HitQuality2',
             3: 'UI/Inflight/HitQuality3',
             4: 'UI/Inflight/HitQuality4',
             5: 'UI/Inflight/HitQuality5',
             6: 'UI/Inflight/HitQuality6'}[hitQuality]
        except (KeyError, ValueError):
            return 'No hit quality message for level %s' % hitQuality

        return localization.GetByLabel(label)

    def AddMiningMessage(self, oreTypeID, amount, hasRewards, amountWasted):
        if amount > 0:
            if show_inflight_mining_messages_setting.get():
                msgFormatter = FormatMiningRewardsMessage if hasRewards else FormatMiningMessage
                msg = msgFormatter(normalFontSize=self.notificationFontSize, oreTypeID=oreTypeID, amount=amount, amountWasted=amountWasted)
                self.SayMessage(msg, 'mining')

    def AddOreDepositedMessage(self, oreTypeID, amount, charID):
        if amount > 0:
            if show_inflight_mining_messages_setting.get():
                msg = FormatOreDepositedMessage(charID=charID, normalFontSize=self.notificationFontSize, oreTypeID=oreTypeID, amount=amount)
                self.SayMessage(msg, 'mining')

    def AddRwPirateKilledByCharacterMessage(self, killerID, killedShipItem):
        if show_inflight_damage_messages_setting.get():
            killerName = cfg.eveowners.Get(killerID).name
            killedName = sm.GetService('bracket').GetDisplayNameForBracket(killedShipItem)
            msg = FormatPirateKilledMessage(killerName=killerName, normalFontSize=self.notificationFontSize, killedName=killedName)
            self.SayMessage(msg, 'combat')

    def AddRwPirateKilledByNpcMessage(self, killerShipItem, killedShipItem):
        if show_inflight_damage_messages_setting.get():
            killerName = sm.GetService('bracket').GetDisplayNameForBracket(killerShipItem)
            killedName = sm.GetService('bracket').GetDisplayNameForBracket(killedShipItem)
            msg = FormatPirateKilledMessage(killerName=killerName, normalFontSize=self.notificationFontSize, killedName=killedName)
            self.SayMessage(msg, 'combat')

    def AddBountyMessage(self, bountyPayout, payoutTime, enemyTypeID, isModified):
        if bountyPayout > 0:
            if show_inflight_bounty_messages_setting.get():
                blue.synchro.Sleep(1000)
                if not isModified:
                    msg = FormatBountyMessage(normalFontSize=self.notificationFontSize, bounty=bountyPayout)
                    self.SayMessage(msg, 'bounty')
                else:
                    msg = FormatModifiedBountyMessage(normalFontSize=self.notificationFontSize, bounty=bountyPayout)
                    self.SayMessage(msg, 'bounty')

    def _ReadIconsFromMessageDict(self, damageMessagesArgs):
        icons = []
        if damageMessagesArgs.get('hitQuality', 0) == 0:
            return []
        damageAttributes = damageMessagesArgs.get('damageAttributes', {})
        for attr in damageAttributes:
            if attr in DAMAGE_TYPE_ICONS and damageAttributes[attr] > 0:
                icons.append(DAMAGE_TYPE_ICONS[attr])

        return icons

    @telemetry.ZONE_METHOD
    def AddCombatMessageFromDict(self, damageMessagesArgs):
        hitQuality = damageMessagesArgs['hitQuality']
        isBanked = damageMessagesArgs['isBanked']
        if hitQuality == 0:
            msgKey = 'AttackMiss'
        elif hitQuality > 0 and hitQuality <= 6:
            msgKey = 'AttackHits'
            try:
                hitQualityText = self.cachedHitQualityText[hitQuality]
            except KeyError:
                hitQualityText = self.GetHitQualityMessage(hitQuality)
                self.cachedHitQualityText[hitQuality] = hitQualityText

            damageMessagesArgs['hitQualityText'] = hitQualityText
        else:
            msgKey = 'AttackHits'
            hitQualityText = ''
            damageMessagesArgs['hitQualityText'] = hitQualityText
        attackType = damageMessagesArgs.get('attackType', 'me')
        if attackType == 'otherPlayer':
            msgKey += 'RD'
        elif attackType == 'otherPlayerWeapons':
            msgKey += 'R'
        elif attackType == 'me':
            if isBanked:
                msgKey += 'Banked'
        else:
            LogError('attackType not valid! attackType = ' + attackType)
            return
        for argName in ('source', 'target', 'owner'):
            if argName not in damageMessagesArgs:
                continue
            if argName == 'owner':
                ownerTypeID, ownerID = damageMessagesArgs[argName]
                if ownerTypeID != const.UE_OWNERID:
                    continue
                objectID = damageMessagesArgs.get('attackerID', None)
                if objectID is None:
                    continue
            else:
                objectID = damageMessagesArgs[argName]
            bracket = sm.GetService('bracket').GetBracket(objectID)
            if bracket:
                slimItem = bracket.slimItem
            else:
                ballpark = sm.GetService('michelle').GetBallpark()
                if ballpark is None:
                    self.LogWarn('OnDamageMessage: No ballpark, not showing damage message.')
                    return
                slimItem = ballpark.GetInvItem(objectID)
            if slimItem:
                if slimItem.corpID and not idCheckers.IsNPC(slimItem.corpID):
                    damageMessagesArgs['typeName'] = evetypes.GetName(slimItem.typeID)
                    tickerText = cfg.corptickernames.Get(slimItem.corpID).tickerName
                    damageMessagesArgs['tickerText'] = tickerText
            objectName = self._GetObjectName(slimItem, argName, damageMessagesArgs)
            if objectName is None:
                if argName == 'owner':
                    continue
                else:
                    return
            damageMessagesArgs[argName] = objectName
            damageMessagesArgs['%s_ID' % argName] = objectID

        self.AddCombatMessage(msgKey, damageMessagesArgs)

    def _GetObjectName(self, slimItem, argName, damageMessagesArgs):
        if slimItem:
            return uix.GetSlimItemName(slimItem) or 'Some object'
        if argName == 'owner':
            return
        if argName == 'source' and 'sourceCharID' in damageMessagesArgs:
            charID = damageMessagesArgs['sourceCharID']
            return cfg.eveowners.Get(charID).name
        if argName == 'target' and 'targetOwnerID' in damageMessagesArgs:
            targetOwnerID = damageMessagesArgs['targetOwnerID']
            return cfg.eveowners.Get(targetOwnerID).name
        self.LogError('Failed to display message', damageMessagesArgs)

    @telemetry.ZONE_METHOD
    def AddCombatMessage(self, msgKey, msgTextArgs):
        if msgKey in ENERGY_WARFARE_MESSAGES and not show_inflight_energy_warfare_messages_setting.get():
            return
        if msgKey in REMOTE_ASSISTANCE_MESSAGES:
            if not show_inflight_remote_assistance_messages_setting.get():
                return
            if msgKey in INCOMING_REMOTE_ASSISTANCE_MESSAGES and not show_inflight_remote_assistance_incoming_messages_setting.get():
                return
            if msgKey in OUTGOING_REMOTE_ASSISTANCE_MESSAGES and not show_inflight_remote_assistance_outgoing_messages_setting.get():
                return
        icons = self._ReadIconsFromMessageDict(msgTextArgs)
        smallFontsize = max(10, self.notificationFontSize - 2)
        msgTextArgs.update({'strongColor': '<color=0xff00ffff>',
         'faintColor': '<color=0x77ffffff>',
         'fontMarkUpStart': '<font size=%s>' % smallFontsize,
         'fontMarkUpEnd': '</font>'})
        showTicker = show_inflight_message_ticker_setting.get()
        showShip = show_inflight_message_ship_setting.get()
        showWeapon = show_inflight_message_weapon_setting.get()
        showQuality = show_inflight_message_quality_setting.get()
        doShowInspaceNotifications = show_inflight_messages_setting.get()
        notificationsExtraNameText = ''
        logExtraNameText = ''
        if msgTextArgs.get('tickerText', ''):
            extra = '[%s]' % msgTextArgs.get('tickerText', '')
            logExtraNameText += extra
            if showTicker:
                notificationsExtraNameText += extra
        if msgTextArgs.get('typeName', ''):
            extra = '(%s)' % msgTextArgs.get('typeName', '')
            logExtraNameText += extra
            if showShip:
                notificationsExtraNameText += extra
        deflectedDmg = msgTextArgs.get('deflectedDmg', None)
        if deflectedDmg:
            damage = msgTextArgs.get('damage', 0)
            msgTextArgs['damage'] = damage + deflectedDmg
        msgTextArgs['extraNameText'] = logExtraNameText
        msgFullText = cfg.GetMessageTypeAndText(msgKey, msgTextArgs)
        if msgFullText.type == 'error' and not settings.user.ui.Get('logerrors', 0):
            return
        if doShowInspaceNotifications:
            if logExtraNameText == notificationsExtraNameText:
                msgLimited = msgFullText
            else:
                msgTextArgs['extraNameText'] = notificationsExtraNameText
                msgLimited = cfg.GetMessageTypeAndText(msgKey, msgTextArgs)
        logPostText = ''
        notificationsPostText = ''
        if 'weapon' in msgTextArgs:
            extra = ' - %s' % evetypes.GetName(msgTextArgs['weapon'])
            logPostText += extra
            if showWeapon:
                notificationsPostText += extra
        if msgTextArgs.get('hitQualityText', ''):
            extra = ' - %s' % msgTextArgs['hitQualityText']
            logPostText += extra
            if showQuality:
                notificationsPostText += extra
        if deflectedDmg:
            notificationsPostText += ' (%s)' % localization.GetByLabel('UI/Accessories/Log/DeflectedDamage', damageDeflected=deflectedDmg)
            logPostText += notificationsPostText
        damage = msgTextArgs.get('damage', None)
        hitQuality = msgTextArgs.get('hitQuality', None)
        damageHtml = None
        if damage is not None and hitQuality > 0:
            rounded_damage = int(round(damage))
            red = '0xffcc0000'
            blue = '0xff00ffff'
            color = red if msgTextArgs.get('attackType', 'me') != 'me' else blue
            damageHtml = '<color={color}><b>{damage}</b>'.format(color=color, damage=rounded_damage)
        fullText = msgFullText.text + logPostText
        if damageHtml is not None:
            fullText = ' '.join((damageHtml, fullText))
        self.AddText(fullText, 'combat')
        if doShowInspaceNotifications:
            limitedText = msgLimited.text + notificationsPostText
            hitQuality = msgTextArgs.get('hitQuality', None)
            attackerID = msgTextArgs.get('attackerID', None)
            self.Say(limitedText, hitQuality, attackerID, icons, damageHtml)

    @telemetry.ZONE_METHOD
    def AddText(self, msgtext, msgtype = None, msg = None):
        timestamp = blue.os.GetWallclockTime()
        if not self.broken:
            formattedTime = self.GetFormattedTime(timestamp)
            formattedMessage = '[%20s ] (%s) %s\n' % (formattedTime, msgtype, msgtext)
            encodedMessage = formattedMessage.encode('utf8', 'replace')
            self.msglog.append(encodedMessage)
        if not self.ShowMessage(msgtype):
            return
        msgData = (msgtext, msgtype, timestamp)
        self.messages.append(msgData)
        maxlog = log_message_count_setting.get()
        if len(self.messages) > maxlog * 2:
            self.messages = self.messages[-maxlog:]
        wnd = self.GetWndWithFrameCounter()
        if wnd and not wnd.destroyed:
            self.addmsg.append(msgData)

    @telemetry.ZONE_METHOD
    def GetFormattedTime(self, timestamp, *args):
        year, month, wd, day, hour, min, sec, ms = self.GetTimePartsForLog(timestamp)
        return '%d.%.2d.%.2d %.2d:%.2d:%.2d' % (year,
         month,
         day,
         hour,
         min,
         sec)

    def SayMessage(self, text, msgType):
        message = self._MakeOrGetMessageUI()
        message.AddActionMessage(text)
        self.AddText(text, msgType)

    def Say(self, msgtext, hitQuality, attackerID, *args):
        message = self._MakeOrGetMessageUI()
        message.AddMessage(msgtext, hitQuality, attackerID, *args)

    def CloseMessageUI(self):
        message = getattr(uicore.layer.target, 'message', None)
        if message and not message.destroyed:
            message.Close()

    def _MakeOrGetMessageUI(self):
        message = getattr(uicore.layer.target, 'message', None)
        if not message or message.destroyed:
            message = CombatMessage(parent=uicore.layer.target, name='combatMessage', state=uiconst.UI_PICKCHILDREN)
            uicore.layer.target.message = message
        return message

    def ShowMessage(self, msgtype):
        setting = MESSAGE_FILTER_SETTING_BY_MESSAGE_TYPE.get(msgtype, None)
        if setting is not None:
            return setting.get()
        else:
            return True

    def DumpToLog(self):
        uthread.new(self.DumpToLogThread)

    @telemetry.ZONE_METHOD
    def DumpToLogThread(self):
        if self.broken or not self.msglog:
            return
        logfile = None
        try:
            filename = self.GetLogfileName()
            try:
                logfile = file(filename, 'a')
            except:
                if self.newfileAttempts < 3:
                    LogWarn('Failed to open the logfile %s, creating new logfile...' % filename)
                    filename = self.GetLogfileName(reset=True)
                    LogWarn('new logfile name is: ', filename)
                    self.newfileAttempts += 1
                    logfile = file(filename, 'a')
                else:
                    self.broken = 1
                    LogException(toAlertSvc=0)
                sys.exc_clear()

            if logfile:
                try:
                    logfile.writelines(self.msglog)
                    logfile.close()
                except IOError:
                    log.LogTraceback()
                    sys.exc_clear()

                self.msglog = []
        except:
            LogException(toAlertSvc=0)
            sys.exc_clear()

        if logfile and not logfile.closed:
            logfile.close()

    def CopyLog(self):
        self.DumpToLog()
        logfile = None
        try:
            filename = self.GetLogfileName()
            logfile = file(filename)
            ret = logfile.read()
            logfile.close()
            blue.pyos.SetClipboardData(ret)
        except:
            LogException()
            sys.exc_clear()

        if logfile and not logfile.closed:
            logfile.close()

    def GetLogfileName(self, reset = False):
        if reset:
            self.Reset()
        year, month, weekday, day, hour, minute, second, msec = self.GetTimePartsForLog(self.resettime)
        postFix = '_%s' % session.charid if session.charid else ''
        filename = '%d%.2d%.2d_%.2d%.2d%.2d%s' % (year,
         month,
         day,
         hour,
         minute,
         second,
         postFix)
        filename = blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/logs/Gamelogs/%s.txt' % filename
        return filename

    def _PersistWorker(self):
        while self.IsRunning():
            blue.pyos.synchro.SleepWallclock(self.persistInterval)
            self.DumpToLog()

    def MoveNotifications(self, enterMode, *args):
        self.SetDragModeState(state=enterMode)
        message = getattr(uicore.layer.target, 'message', None)
        if not message or message.destroyed:
            message = CombatMessage(parent=uicore.layer.target, name='combatMessage', state=uiconst.UI_PICKCHILDREN, width=400, height=60)
            uicore.layer.target.message = message
            message.SetSizeAndPosition()
        msg = None
        for each in uicore.layer.abovemain.children[:]:
            if each.name == 'message':
                msg = each
                break

        if msg is None:
            from eve.client.script.ui.control.message import QuickMessage
            msg = QuickMessage(parent=uicore.layer.abovemain, name='message', height=40, width=300, state=uiconst.UI_HIDDEN)
        if enterMode:
            msg.EnterDragMode()
            message.EnterDragMode()
        else:
            msg.ExitDragMode()
            message.ExitDragMode()

    def IsInDragMode(self, *args):
        return self.inMovingMode

    def SetDragModeState(self, state, *args):
        self.inMovingMode = state


log_message_count_setting = UserSettingEnum(settings_key='logmessageamount', default_value=100, options=[100, 1000])
show_info_messages_setting = UserSettingBool(settings_key='showinfologmessages', default_value=True)
show_warning_messages_setting = UserSettingBool(settings_key='showwarninglogmessages', default_value=True)
show_error_messages_setting = UserSettingBool(settings_key='showerrorlogmessages', default_value=True)
show_combat_messages_setting = UserSettingBool(settings_key='showcombatlogmessages', default_value=True)
show_notify_messages_setting = UserSettingBool(settings_key='shownotifylogmessages', default_value=True)
show_question_messages_setting = UserSettingBool(settings_key='showquestionlogmessages', default_value=True)
show_mining_messages_setting = UserSettingBool(settings_key='showmininglogmessages', default_value=True)
show_bounty_messages_setting = UserSettingBool(settings_key='showbountylogmessages', default_value=True)
MESSAGE_FILTER_SETTING_BY_MESSAGE_TYPE = {'info': show_info_messages_setting,
 'warning': show_warning_messages_setting,
 'error': show_error_messages_setting,
 'combat': show_combat_messages_setting,
 'notify': show_notify_messages_setting,
 'question': show_question_messages_setting,
 'mining': show_mining_messages_setting,
 'bounty': show_bounty_messages_setting}
LABEL_BY_MESSAGE_TYPE = {'error': 'UI/Accessories/Log/LogError',
 'warning': 'UI/Accessories/Log/LogWarn',
 'slash': 'UI/Accessories/Log/LogSlash',
 'combat': 'UI/Accessories/Log/LogCombat',
 'notify': 'UI/Accessories/Log/LogNotify',
 'question': 'UI/Accessories/Log/LogQuestion',
 'info': 'UI/Accessories/Log/LogInfo',
 'hint': 'UI/Accessories/Log/LogHint',
 'mining': 'UI/Accessories/Log/LogMining',
 'bounty': 'UI/Accessories/Log/LogBounty'}
LABEL_BY_MESSAGE_FILTER_SETTING = {show_info_messages_setting: 'UI/Accessories/Log/ShowInfo',
 show_warning_messages_setting: 'UI/Accessories/Log/ShowWarn',
 show_error_messages_setting: 'UI/Accessories/Log/ShowError',
 show_combat_messages_setting: 'UI/Accessories/Log/ShowCombat',
 show_notify_messages_setting: 'UI/Accessories/Log/ShowNotify',
 show_question_messages_setting: 'UI/Accessories/Log/ShowQuestion',
 show_mining_messages_setting: 'UI/Accessories/Log/ShowMining',
 show_bounty_messages_setting: 'UI/Accessories/Log/ShowBounty'}

class ShowDamageMessageSetting(UserSettingBool):
    _on_available_changed = None

    def __init__(self, settings_key, default_value, caption_label, hint_label = None, depends_on = None):
        self._caption = caption_label
        self._hint = hint_label
        self._dependency = depends_on
        super(ShowDamageMessageSetting, self).__init__(settings_key=settings_key, default_value=default_value)
        if self._dependency:
            self._dependency.on_change.connect(self._on_dependency_changed)

    @property
    def available(self):
        if self._dependency is not None:
            return self._dependency.get()
        return True

    @property
    def on_available_changed(self):
        if self._on_available_changed is None:
            self._on_available_changed = signals.Signal('{}.on_available_changed'.format(self.__class__.__name__))
        return self._on_available_changed

    @property
    def caption(self):
        return localization.GetByLabel(self._caption)

    @property
    def hint(self):
        return localization.GetByLabel(self._hint)

    def _on_dependency_changed(self, value):
        if self._on_available_changed is not None:
            self._on_available_changed(self)


show_inflight_notify_messages_setting = ShowDamageMessageSetting(settings_key='notifyMessagesEnabled', default_value=True, caption_label='UI/SystemMenu/GeneralSettings/Inflight/ShowTacticalNotifications', hint_label='UI/SystemMenu/GeneralSettings/Inflight/ShowTacticalNotificationTooltip')
show_inflight_damage_messages_setting = ShowDamageMessageSetting(settings_key='damageMessages', default_value=True, caption_label='UI/SystemMenu/GeneralSettings/Inflight/DamageNotifications')
show_inflight_energy_warfare_messages_setting = ShowDamageMessageSetting(settings_key='energyWarfareMessages', default_value=True, caption_label='UI/SystemMenu/GeneralSettings/Inflight/ShowEnergyWarfareNotifications')
show_inflight_remote_assistance_messages_setting = ShowDamageMessageSetting(settings_key='remoteAssistanceMessages', default_value=True, caption_label='UI/SystemMenu/GeneralSettings/Inflight/ShowRemoteAssistanceNotifications')
show_inflight_bounty_messages_setting = ShowDamageMessageSetting(settings_key='actionMessagesBounty', default_value=True, caption_label='UI/SystemMenu/GeneralSettings/Inflight/ShowBountyNotifications')
show_inflight_mining_messages_setting = ShowDamageMessageSetting(settings_key='actionMessagesMining', default_value=True, caption_label='UI/SystemMenu/GeneralSettings/Inflight/ShowMiningNotification')
show_inflight_damage_miss_messages_setting = ShowDamageMessageSetting(settings_key='damageMessagesNoDamage', default_value=True, caption_label='UI/SystemMenu/GeneralSettings/Inflight/MissedHitNotifications', depends_on=show_inflight_damage_messages_setting)
show_inflight_damage_incoming_messages_setting = ShowDamageMessageSetting(settings_key='damageMessagesMine', default_value=True, caption_label='UI/SystemMenu/GeneralSettings/Inflight/ShowInflictedDamageNotifications', depends_on=show_inflight_damage_messages_setting)
show_inflight_damage_outgoing_messages_setting = ShowDamageMessageSetting(settings_key='damageMessagesEnemy', default_value=True, caption_label='UI/SystemMenu/GeneralSettings/Inflight/ShowIncurredDamageNotification', depends_on=show_inflight_damage_messages_setting)
show_inflight_remote_assistance_incoming_messages_setting = ShowDamageMessageSetting(settings_key='remoteAssistanceMessagesMine', default_value=True, caption_label='UI/SystemMenu/GeneralSettings/Inflight/ShowIncomingRemoteAssistanceNotifications', depends_on=show_inflight_remote_assistance_messages_setting)
show_inflight_remote_assistance_outgoing_messages_setting = ShowDamageMessageSetting(settings_key='remoteAssistanceMessagesOthers', default_value=True, caption_label='UI/SystemMenu/GeneralSettings/Inflight/ShowOutgoingRemoteAssistanceNotifications', depends_on=show_inflight_remote_assistance_messages_setting)
SHOW_INFLIGHT_MESSAGE_SETTINGS = (show_inflight_notify_messages_setting,
 show_inflight_damage_messages_setting,
 show_inflight_energy_warfare_messages_setting,
 show_inflight_remote_assistance_messages_setting,
 show_inflight_bounty_messages_setting,
 show_inflight_mining_messages_setting,
 show_inflight_damage_miss_messages_setting,
 show_inflight_damage_incoming_messages_setting,
 show_inflight_damage_outgoing_messages_setting,
 show_inflight_remote_assistance_incoming_messages_setting,
 show_inflight_remote_assistance_outgoing_messages_setting)

class ShowInflightMessageCheckboxMenuEntryData(MenuEntryDataCheckbox):

    def __init__(self, setting):
        super(ShowInflightMessageCheckboxMenuEntryData, self).__init__(text=setting.caption, setting=setting, isEnabled=setting.available)
        setting.on_available_changed.connect(self._on_available_changed)

    def _on_available_changed(self, setting):
        self.isEnabled = setting.available


class DependentCheckboxMenuEntryData(MenuEntryDataCheckbox):

    def __init__(self, text, setting, dependencies):
        self._dependencies = dependencies
        super(DependentCheckboxMenuEntryData, self).__init__(text=text, setting=setting, isEnabled=self._are_all_dependencies_enabled())
        for dependency in self._dependencies:
            dependency.on_change.connect(self._on_dependency_changed)

    def _on_dependency_changed(self, value):
        self.isEnabled = self._are_all_dependencies_enabled()

    def _are_all_dependencies_enabled(self):
        return all((dependency.get() for dependency in self._dependencies))


show_inflight_messages_setting = UserSettingBool(settings_key='damageMessageShowInspaceNotifications', default_value=True)
show_inflight_message_ship_setting = UserSettingBool(settings_key='damageMessagesShowShip', default_value=False)
show_inflight_message_ticker_setting = UserSettingBool(settings_key='damageMessagesShowTicker', default_value=False)
show_inflight_message_weapon_setting = UserSettingBool(settings_key='damageMessagesShowWeapon', default_value=False)
show_inflight_message_quality_setting = UserSettingBool(settings_key='damageMessagesShowQuality', default_value=True)
inflight_message_font_size_setting = UserSettingEnum(settings_key='dmgnotifictions_fontsize', options=[10, 12, 14], default_value=12)
inflight_messages_alignment_setting = UserSettingEnum(settings_key='dmgnotifictions_alignment', options=['auto',
 'left',
 'right',
 'center'], default_value='auto')
CAPTION_LABEL_BY_INFLIGHT_MESSAGE_ALIGNMENT = {'auto': 'UI/Accessories/Log/AlignmentAuto',
 'left': 'UI/Accessories/Log/AlignmentLeft',
 'right': 'UI/Accessories/Log/AlignmentRight',
 'center': 'UI/Accessories/Log/AlignmentCenter'}

class LoggerWindow(Window):
    __guid__ = 'form.Logger'
    default_windowID = 'logger'
    default_captionLabelPath = 'UI/Accessories/Log/Log'
    default_iconNum = 'res:/ui/Texture/WindowIcons/log.png'
    default_minSize = (256, 136)
    default_width = 400
    default_height = 200
    default_isCompactable = True
    _actions = None
    _toolbar = None

    def __init__(self, **kwargs):
        super(LoggerWindow, self).__init__(**kwargs)
        self._toolbar = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, padLeft=-4)
        self._actions = ContainerAutoSize(parent=self._get_actions_parent(), align=self._get_actions_alignment(), height=24, alignMode=uiconst.TOLEFT)
        scroll = eveScroll.Scroll(parent=self.content, align=uiconst.TOALL, padLeft=-8)
        scroll.Load(contentList=[], headers=[localization.GetByLabel('UI/Common/DateWords/Time'), localization.GetByLabel('UI/Accessories/Log/Type'), localization.GetByLabel('UI/Accessories/Log/Message')])
        scroll.sr.id = 'logScroll'
        self.sr.scroll = scroll
        MenuButtonIcon(parent=ContainerAutoSize(parent=self._actions, align=uiconst.TOLEFT), align=uiconst.TOPLEFT, width=24, height=24, iconSize=16, texturePath=eveicon.filter, get_menu_func=self._get_log_filter_menu, hint=localization.GetByLabel('UI/Generic/Filters'))
        MenuButtonIcon(parent=ContainerAutoSize(parent=self._actions, align=uiconst.TOLEFT), align=uiconst.TOPLEFT, width=24, height=24, iconSize=16, texturePath=eveicon.settings, get_menu_func=self._get_combat_message_menu, hint=localization.GetByLabel('UI/Accessories/Log/CombatSettings'))
        self.LoadAllMessages()
        self.timer = timerstuff.AutoTimer(1000, self.CheckMessages)
        log_message_count_setting.on_change.connect(self._on_log_message_count_setting_changed)
        show_inflight_messages_setting.on_change.connect(self._on_show_inflight_messages_setting_changed)
        inflight_message_font_size_setting.on_change.connect(self._on_inflight_message_font_size_setting_changed)
        inflight_messages_alignment_setting.on_change.connect(self._on_inflight_messages_alignment_setting_changed)
        for setting in MESSAGE_FILTER_SETTING_BY_MESSAGE_TYPE.values():
            setting.on_change.connect(self._on_message_filter_setting_changed)

        self.on_compact_mode_changed.connect(self._on_window_compact_mode_changed)
        self.on_stacked_changed.connect(self._on_window_stacked_changed)

    def _get_actions_parent(self):
        if self.compact and not self.stacked:
            return self.header.extra_content
        else:
            return self._toolbar

    def _get_actions_alignment(self):
        if self.compact and not self.stacked:
            return uiconst.CENTERRIGHT
        else:
            return uiconst.TOPLEFT

    def _update_actions(self):
        self._actions.SetParent(None)
        self._actions.align = self._get_actions_alignment()
        self._actions.SetParent(self._get_actions_parent())

    def _on_window_compact_mode_changed(self, window):
        self._update_actions()

    def _on_window_stacked_changed(self, window):
        self._update_actions()

    def _PrepareListEntries(self, messages):
        showmsgs = []
        dateSortKey = 'sort_%s' % localization.GetByLabel('UI/Common/DateWords/Time')
        openMsgTitle = localization.GetByLabel('UI/Accessories/Log/LogMessage')
        for msg in messages:
            msgtext, msgtype, timestamp = msg
            if not self.ShowMessage(msgtype):
                continue
            color = COLORS_BY_TYPE.get(msgtype, '<color=0xffffffff>')
            if msgtype:
                if msgtype in LABEL_BY_MESSAGE_TYPE:
                    label = localization.GetByLabel(LABEL_BY_MESSAGE_TYPE[msgtype])
                else:
                    label = msgtype
            else:
                label = localization.GetByLabel('UI/Accessories/Log/Generic')
            text = localization.GetByLabel('UI/Accessories/Log/MessageOutput', logtime=timestamp, color=color, label=label, message=StripTags(msgtext, stripOnly=['t']))
            entry = GetFromClass(Generic, {'label': text,
             'canOpen': openMsgTitle,
             dateSortKey: timestamp,
             'line': 1})
            showmsgs.append(entry)

        return showmsgs

    @telemetry.ZONE_METHOD
    def LoadAllMessages(self):
        maxlog = log_message_count_setting.get()
        messages = sm.GetService('logger').GetMessages()
        if len(messages) > maxlog:
            messages = messages[-maxlog:]
        showmsgs = self._PrepareListEntries(messages)
        self.sr.scroll.Load(contentList=showmsgs, headers=[localization.GetByLabel('UI/Common/DateWords/Time'), localization.GetByLabel('UI/Accessories/Log/Type'), localization.GetByLabel('UI/Accessories/Log/Message')])

    @telemetry.ZONE_METHOD
    def CheckMessages(self):
        if self.sr.scroll.IsVisible():
            dateSortKey = 'sort_%s' % localization.GetByLabel('UI/Common/DateWords/Time')
            messages = sm.GetService('logger').GetPendingMessages()
            if messages:
                entryList = self._PrepareListEntries(messages)
                maxlog = log_message_count_setting.get()
                self.sr.scroll.AddEntries(0, entryList)
                revSorting = self.sr.scroll.GetSortDirection() or self.sr.scroll.GetSortBy() is None
                if revSorting:
                    self.sr.scroll.RemoveEntries(self.sr.scroll.GetNodes()[maxlog:])
                else:
                    self.sr.scroll.RemoveEntries(self.sr.scroll.GetNodes()[:-maxlog])

    def GetMenu(self, *args):
        m = super(LoggerWindow, self).GetMenu(*args)
        return m

    def GetMenuMoreOptions(self):
        menu = super(LoggerWindow, self).GetMenuMoreOptions()
        menu.AddEntry(text=MenuLabel('UI/Accessories/Log/CaptureLog'), func=sm.GetService('logger').DumpToLog)
        menu.AddEntry(text=MenuLabel('UI/Accessories/Log/CopyLog'), func=sm.GetService('logger').CopyLog, texturePath=eveicon.copy)
        return menu

    def _get_log_filter_menu(self):
        menu = MenuData()
        menu.AddCaption(localization.GetByLabel('UI/Accessories/Log/MessageTypesToLog'))
        for setting, label in LABEL_BY_MESSAGE_FILTER_SETTING.items():
            menu.AddCheckbox(text=localization.GetByLabel(label), setting=setting)

        menu.AddCaption(localization.GetByLabel('UI/Accessories/Log/NumMessagesInLogView'))
        for message_count in log_message_count_setting.options:
            menu.AddRadioButton(text=unicode(message_count), setting=log_message_count_setting, value=message_count)

        return menu

    def ResetDmgNotificationAlignment(self, *args):
        settings.char.ui.Delete('damageMessages_config')
        inflight_messages_alignment_setting.reset()
        message = getattr(uicore.layer.target, 'message', None)
        if message:
            message.ResetAlignment()
        message = itertoolsext.first_or_default(uicore.layer.abovemain.children, predicate=lambda each: each.name == 'message')
        if message:
            message.ResetAlignment()

    def _get_combat_message_menu(self):
        menu = MenuData()
        menu.AddEntry(text=localization.GetByLabel('UI/Accessories/Log/CombatMessagesToDisplay'), subMenuData=[ ShowInflightMessageCheckboxMenuEntryData(setting) for setting in SHOW_INFLIGHT_MESSAGE_SETTINGS ])
        inflight_message_sub_menu = MenuData()
        inflight_message_sub_menu.AppendMenuEntryData(DependentCheckboxMenuEntryData(text=localization.GetByLabel('UI/Accessories/Log/ShowInspaceNotifications'), setting=show_inflight_messages_setting, dependencies=[show_inflight_damage_messages_setting]))
        inflight_message_sub_menu.AddSeparator()
        inflight_message_sub_menu.AppendMenuEntryData(DependentCheckboxMenuEntryData(text=localization.GetByLabel('UI/Accessories/Log/DmgNotificationsShowShip'), setting=show_inflight_message_ship_setting, dependencies=[show_inflight_messages_setting, show_inflight_damage_messages_setting]))
        inflight_message_sub_menu.AppendMenuEntryData(DependentCheckboxMenuEntryData(text=localization.GetByLabel('UI/Accessories/Log/DmgNotificationsShowTicker'), setting=show_inflight_message_ticker_setting, dependencies=[show_inflight_messages_setting, show_inflight_damage_messages_setting]))
        inflight_message_sub_menu.AppendMenuEntryData(DependentCheckboxMenuEntryData(text=localization.GetByLabel('UI/Accessories/Log/DmgNotificationsShowWeapon'), setting=show_inflight_message_weapon_setting, dependencies=[show_inflight_messages_setting, show_inflight_damage_messages_setting]))
        inflight_message_sub_menu.AppendMenuEntryData(DependentCheckboxMenuEntryData(text=localization.GetByLabel('UI/Accessories/Log/DmgNotificationsShowQuality'), setting=show_inflight_message_quality_setting, dependencies=[show_inflight_messages_setting, show_inflight_damage_messages_setting]))
        inflight_message_sub_menu.AddSeparator()
        drag_mode_active = sm.GetService('logger').IsInDragMode()
        inflight_message_sub_menu.AddEntry(text=localization.GetByLabel('UI/Accessories/Log/ExitMessageMovingMode') if drag_mode_active else localization.GetByLabel('UI/Accessories/Log/EnterMessageMovingMode'), func=lambda : sm.GetService('logger').MoveNotifications(not drag_mode_active), texturePath=eveicon.caret_up_down_left_right)
        menu.AddEntry(text=localization.GetByLabel('UI/Accessories/Log/ExtraInfoHeader'), subMenuData=inflight_message_sub_menu)
        menu.AddEntry(text=localization.GetByLabel('UI/Accessories/Log/FontSize'), subMenuData=[ MenuEntryDataRadioButton(text=unicode(font_size), setting=inflight_message_font_size_setting, value=font_size) for font_size in inflight_message_font_size_setting.options ])
        alignment_sub_menu = MenuData(entryList=[ MenuEntryDataRadioButton(text=localization.GetByLabel(CAPTION_LABEL_BY_INFLIGHT_MESSAGE_ALIGNMENT.get(alignment)), setting=inflight_messages_alignment_setting, value=alignment) for alignment in inflight_messages_alignment_setting.options ])
        alignment_sub_menu.AddSeparator()
        alignment_sub_menu.AddEntry(text=localization.GetByLabel('UI/Accessories/Log/ResetAlignment'), func=self.ResetDmgNotificationAlignment, menuGroupID=DESTRUCTIVEGROUP)
        menu.AddEntry(text=localization.GetByLabel('UI/Accessories/Log/InspaceNotificationFontAlignment'), subMenuData=alignment_sub_menu)
        return menu

    def OnEndMaximize(self, *args):
        self.LoadAllMessages()

    def _OnClose(self, *args):
        self.timer = None

    def ShowMessage(self, msgtype):
        return sm.GetService('logger').ShowMessage(msgtype)

    def _on_log_message_count_setting_changed(self, value):
        self.LoadAllMessages()

    def _on_message_filter_setting_changed(self, value):
        self.LoadAllMessages()

    @staticmethod
    def _on_show_inflight_messages_setting_changed(value):
        message_box = getattr(uicore.layer.target, 'message', None)
        if message_box and not message_box.destroyed:
            message_box.Close()

    @staticmethod
    def _on_inflight_message_font_size_setting_changed(value):
        sm.GetService('logger').notificationFontSize = value
        message = getattr(uicore.layer.target, 'message', None)
        if message:
            message.ChangeFontSize()

    @staticmethod
    def _on_inflight_messages_alignment_setting_changed(value):
        message = getattr(uicore.layer.target, 'message', None)
        if message:
            message.ChangeAlignment()
