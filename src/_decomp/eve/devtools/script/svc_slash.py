#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_slash.py
import logging
import os
import random
import sys
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from collections import defaultdict
import blue
import dogma.data
import evetypes
import localization
import log
import trinity
import triui
import uiblinker
import uthread
import utillib
from avatardisplay.avatardisplay import AvatarDisplay as ad
from carbon.common.script.sys import sessions
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_ANY, ROLE_LOGIN, ROLE_PLAYER, ROLE_WORLDMOD, SERVICE_RUNNING, SERVICE_START_PENDING
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from controltowerresources.data import get_control_tower_resources
from eve.client.script.ui.control import eveEdit, eveLabel
from carbonui.button.group import ButtonGroup
from carbonui.control.window import Window
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from eve.common.script.sys import eveCfg
from eve.devtools.script import param
from eve.devtools.script.slashError import Error
from eveexceptions import UserError
from eveprefs import boot
from eveservices.menu import GetMenuService
from eveservices.xmppchat import GetChatService
from inventorycommon.const import typePlex
from inventorycommon.typeHelpers import GetAveragePrice
from uihighlighting.const import DIRECTION_STRING_TO_ID
from uihighlighting.ui.uiutil import UI_CLASS_BY_NAME
logger = logging.getLogger('svc_slash')
SERVICENAME = 'slash'
TOKEN = '$'
aliasFile = 'aliases.ini'
macroFile = 'macros.ini'
version = 2.4

def Message(title, body, icon = triui.INFO):
    sm.GetService('gameui').MessageBox(body, title, buttons=uiconst.OK, icon=icon)


def AsyncMessage(*args):
    uthread.new(Message, *args)


def Progress(title, text, current, total):
    sm.GetService('loading').ProgressWnd(title, text, current, total)


class InlineFunctionResolver():

    def __init__(self):
        pass

    def __getitem__(self, func):
        if ':' in func:
            func, args = func.split(':', 1)
        else:
            args = ()
        method = getattr(self, 'f_' + func.lower(), None)
        if func is None:
            raise Error("unknown inline function '%s'" % func)
        if args:
            args = args.split(',')
        return method(*args)

    def _getinvrow(self, *args):
        if len(args) == 1:
            containerID = eve.session.shipid
            flag = args[0]
        elif len(args) == 2:
            if args[0].lower() == 'me':
                containerID = eve.session.shipid
            else:
                containerID = int(args[0])
            flag = args[1]
        flag = getattr(const, 'flag' + flag.capitalize())
        for rec in sm.GetService('invCache').GetInventoryFromId(containerID).List():
            if rec.flag == flag:
                return rec

    def f_itemid(self, *args, **kw):
        return self._getinvrow(*args).itemID

    def f_typeid(self, *args):
        return self._getinvrow(*args).typeID


def GetCharacter(name, ignoreNotFound = False):
    result = sm.RemoteSvc('lookupSvc').LookupCharacters(name, 1)
    if result:
        cfg.eveowners.Prime([ each.characterID for each in result ])
        return result[0]
    try:
        return cfg.eveowners.Get(int(name))
    except:
        if ignoreNotFound:
            return None
        AsyncMessage('No such character', 'Character not found:<br>  %s' % name)
        raise UserError('IgnoreToTop')


def extract_prefix_from(prefix, original):
    if original.startswith(prefix):
        return original[len(prefix):]
    raise Error("Couldn't extract the prefix {} from {}".format(prefix, original))


def parse_params_for_gag_or_ban(p):
    try:
        channel_specifier, char, reason, durationInMinutes = p.Parse('sssi')
    except Error:
        channel_specifier, char, reason = p.Parse('sss')
        durationInMinutes = 30

    return (channel_specifier,
     char,
     reason,
     durationInMinutes)


def extract_arguments_for_gag_or_ban(p):
    channel_specifier, char, reason, durationInMinutes = parse_params_for_gag_or_ban(p)
    durationInSecs = durationInMinutes * 60
    channelName = extract_prefix_from('channelName=', channel_specifier)
    charID = GetCharacter(char).characterID
    return (channelName,
     charID,
     reason,
     durationInSecs)


def extract_arguments_for_ungag_or_unban(p):
    channel_specifier, char = p.Parse('ss')
    channelName = extract_prefix_from('channelName=', channel_specifier)
    charID = GetCharacter(char).characterID
    return (channelName, charID)


class SlashService(Service):
    __guid__ = 'svc.slash'
    __notifyevents__ = ['ProcessRestartUI', 'ProcessUIRefresh']
    __slashhook__ = True

    def __init__(self):
        Service.__init__(self)
        self.patched = False
        self.aliases = {}
        self.macros = {}
        self.typeIDsByName = None

    def Run(self, _memStream = None):
        self.state = SERVICE_START_PENDING
        try:
            self.wnd = None
            self.history = []
            self.historyPtr = -1
            self.lastslash = ''
            self.busy = self.aborted = False
            self.jobs = []
            self.LoadMacrosAndAliases()
            self.Clear()
        except:
            log.LogException()
            sys.exc_clear()

        self.state = SERVICE_RUNNING

    def GetMacros(self):
        self.LoadMacrosAndAliases()
        return self.macros.items()

    def LoadMacrosAndAliases(self):
        defaultMacros = {'GMH: Unload All': '/unload me all',
         'WM: Remove All Drones': '/unspawn range=500000 only=categoryDrone',
         'WM: Remove All Fighters': '/unspawn range=500000 only=categoryFighter',
         'WM: Remove All Wrecks': '/unspawn range=500000 only=groupWreck',
         'WM: Remove CargoContainers': '/unspawn range=500000 only=groupCargoContainer,groupFreightContainer',
         'WM: Remove SecureContainers': '/unspawn range=500000 only=groupSecureCargoContainer,groupAuditLogSecureContainer',
         'HEALSELF: Repair My Ship': '/heal',
         'HEALSELF: Repair My Modules': '/repairmodules',
         'GMH: Online My Modules': '/online me',
         'GML: Session Change 5sec': '/sessionchange 5'}
        self.aliases = self.LoadStuff(aliasFile)
        if len(self.aliases) == 0:
            self.aliases = {}
        self.macros = self.LoadStuff(macroFile)
        self.macros.update(defaultMacros)

    def LoadStuff(self, fileName):
        targetFile = os.path.join(sm.StartService('insider').GetInsiderDir(), fileName)
        if not os.path.exists(targetFile):
            return {}
        d = {}
        lines = blue.AtomicFileRead(targetFile).replace('\r', '').replace('\x00', '').split('\n')
        for line in lines:
            aliasName, comseq = line.split('=', 1)
            d[aliasName.strip()] = comseq.strip()

        return d

    def SaveStuff(self, thisDict, fileName):
        text = '\r\n'.join([ '%s=%s' % (aliasName, comseq) for aliasName, comseq in thisDict.iteritems() ])
        targetFile = os.path.join(sm.StartService('insider').GetInsiderDir(), fileName)
        blue.AtomicFileWrite(targetFile, text)

    def Stop(self, memStream = None):
        if self.wnd and not self.wnd.destroyed:
            self.Hide()
        Service.Stop(self, memStream)

    def ConstructLayout(self):
        self.wnd = wnd = Window.GetIfOpen(windowID='slashcon')
        if wnd:
            self.wnd.Maximize()
            return
        self.Layout()

    def Layout(self):
        self.wnd = wnd = Window.Open(windowID='slashcon')
        wnd.DoClose = self.Hide
        wnd.SetCaption('Slash')
        wnd.OnUIRefresh = None
        self.main = Container(name='con', parent=wnd.GetChild('main'))
        self.input_container = Container(name='input', parent=self.main, align=uiconst.TOBOTTOM, height=20)
        self.control_container = ContainerAutoSize(name='control', parent=self.main, align=uiconst.TOBOTTOM, padBottom=8, callback=self.ApplyWindowMinSize, only_use_callback_when_size_changes=True)
        self.output_container = Container(name='output', parent=self.main, align=uiconst.TOALL)
        self.ConstructCommandInput()
        self.ConstructButtonGroup()
        self.ConstructOutput()
        self.ApplyWindowMinSize()
        uicore.registry.SetFocus(self.input)

    def ConstructOutput(self):
        output = self.wnd.sr.output = eveEdit.Edit(setvalue=self.outputcontents, parent=self.output_container, readonly=1)
        output.autoScrollToBottom = 1

    def ConstructCommandInput(self):
        eveLabel.Label(text='Command: ', parent=self.input_container, align=uiconst.TOLEFT, color=None, state=uiconst.UI_DISABLED, singleline=1)
        self.input = self.wnd.sr.input = SingleLineEditText(name='slashCmd', parent=self.input_container, left=0, width=0, align=uiconst.TOALL)
        self.input.OnKeyDown = (self.InputKey, self.input)
        self.input.OnReturn = self.InputEnter

    def ConstructButtonGroup(self):
        buttons = ButtonGroup(parent=self.control_container, align=uiconst.CENTER)
        buttons.AddButton('Clear', self.Clear)
        buttons.AddButton('Exec Last', self.ExLast)
        buttons.AddButton('Exec Once', self.ExOnce)
        buttons.AddButton('Exec Loop', self.ExLoop)
        buttons.AddButton('Abort', self.ExAbort)

    def ApplyWindowMinSize(self):
        width, height = self.wnd.GetWindowSizeForContentSize(height=self.control_container.height, width=self.control_container.width)
        self.wnd.SetMinSize([width, 224])

    def Hide(self, *args):
        if self.wnd:
            self.slashcontents = self.wnd.sr.input.GetValue()
            self.wnd.Close()
        self.wnd = None

    def ProcessRestartUI(self):
        if self.wnd:
            self.Hide()
            self.ConstructLayout()

    def ProcessUIRefresh(self):
        if self.wnd:
            self.wnd.Close()
            self.ConstructLayout()

    def Clear(self, *args):
        cmds = []
        import svc
        for sname in svc.__dict__:
            s = getattr(svc, sname)
            if getattr(s, '__slashhook__', False):
                for m in dir(s):
                    if m.startswith('cmd_'):
                        cmds.append(m[4:])

        cmds.sort()
        self.outputcontents = 'Commands: <font color="#ffc000">%s</font><br>' % (', '.join(cmds) or 'None')
        if self.aliases:
            cmds = self.aliases.keys()
            cmds.sort()
            self.outputcontents += 'Aliases: <font color="#00ffc0">%s</font><br>' % ', '.join(cmds)
        self.outputcontents += 'Note: Slash commands, extended commands and user-defined aliases all work both in chat and in console. Commands that require a chat channel cannot be run in the console.<br>'
        if self.wnd:
            self.wnd.sr.output.SetText(self.outputcontents)

    def Echo(self, text):
        self.outputcontents = '%s%s' % (self.outputcontents, text)
        if self.wnd:
            self.wnd.sr.output.SetText(self.outputcontents)

    def InputKey(self, otherself, key, flag):
        CTRL = uicore.uilib.Key(uiconst.VK_CONTROL)
        if CTRL and key == uiconst.VK_UP:
            self.InputHistory(-1)
        elif CTRL and key == uiconst.VK_DOWN:
            self.InputHistory(1)
        else:
            SingleLineEditText.OnKeyDown(otherself, key, flag)

    def InputHistory(self, offset):
        if self.history:
            self.historyPtr += offset
            if self.historyPtr < -len(self.history):
                self.historyPtr = -len(self.history)
                return
            if self.historyPtr >= 0:
                self.historyPtr = 0
                self.wnd.sr.input.SetValue('')
                return
            self.wnd.sr.input.SetValue(self.history[self.historyPtr])

    def InputEnter(self, *_args):
        try:
            self.lastslash = self.wnd.sr.input.GetValue()
        except:
            return

        self.history.append(self.lastslash)
        self.historyPtr = 0
        self.wnd.sr.input.SetValue('')
        self.Ex(self.lastslash)

    def ExLoop(self, *_args):
        try:
            cmd = self.wnd.sr.input.GetValue().strip()
        except:
            return

        if len(cmd) > 1:
            result = uix.QtyPopup(maxvalue=50, minvalue=1, caption='Looped Execution', label='', hint='Specify number of times to execute:<br><br> %s<br><br>Note:<br>- Max. 50 iterations<br>- USE WITH CARE!' % cmd)
            if result:
                amount = result['qty']
                self.lastslash = cmd
                self.wnd.sr.input.SetValue('')
                self.Ex(cmd, amount)

    def ExLast(self, *_args):
        if self.lastslash:
            self.Ex(self.lastslash)

    def ExOnce(self, *_args):
        try:
            self.lastslash = self.wnd.sr.input.GetValue()
        except:
            return

        self.Ex(self.lastslash)

    def ExAbort(self, *_args):
        if self.busy and not self.aborted:
            self.Echo('<font color="#ffff00">*** Aborting...</font><br>')
        self.aborted = True
        self.busy = False

    def Ex(self, this, count = 1):
        if not this:
            return
        if this[0] != '/':
            this = '/' + this
        self.jobs.append((this, count))
        if self.busy:
            if count > 0:
                self.Echo('<font color="#ffff00">*** Queued(%d): %s</font><br>' % (count, this))
            else:
                self.Echo('<font color="#ffff00">*** Queued: %s</font><br>' % this)
            return
        self.JobHandler()

    def JobHandler(self):
        try:
            self.aborted = False
            while self.jobs and not self.aborted:
                this, count = self.jobs.pop(0)
                isLoop = count > 1
                try:
                    self.busy = True
                    self.aborted = False
                    if isLoop:
                        self.Echo('<font color="#ffff00">*** Loop started (%d iterations)</font><br>' % count)
                    while count and not self.aborted:
                        self.Echo('<font color="#00ffff">slash: %s</font><br>' % this)
                        try:
                            res = sm.GetService('slash').SlashCmd(this)
                            if res and len(str(res)) > 5000:
                                res = str(res)[:5000] + '...'
                            self.Echo('<font color="#00ff55">slash result: %s</font><br>' % res)
                        except UserError as e:
                            if e.args[0] in ('SlashError',):
                                self.Echo('<font color="#ff5500">slash error: %s</font><br>' % e.dict['reason'])
                                break
                            else:
                                self.Echo('<font color="#00ff55">slash result: None</font><br>')
                                raise UserError, e

                        count -= 1
                        blue.pyos.synchro.SleepWallclock(100)

                    if isLoop:
                        if self.aborted:
                            reason = 'Aborted by user'
                        elif count != 0:
                            reason = 'Error condition'
                        else:
                            reason = 'Batch completed'
                        self.Echo('<font color="#ffff00">*** Loop terminated (%s)</font><br>' % reason)
                finally:
                    self.busy = False

            else:
                if self.jobs:
                    self.Echo('<font color="#ffff00">*** Slash command queue flushed</font><br>')
                    self.jobs = []

        finally:
            self.aborted = False

    def FetchRemoteCommandList(self):
        if hasattr(self, 'remoteCommandList'):
            return
        try:
            sm.RemoteSvc('slash').SlashCmd('/')
        except UserError as e:
            try:
                msg = e.args[1]['reason']
                cmds = eval(msg.split(': ')[1])
                cmds.sort()
            except:
                cmds = []
                log.LogException()
                Message('Hmmm', "Unable to acquire server slash command list. Not particularly bad, just means command autocompletion won't work")
                sys.exc_clear()

            sys.exc_clear()

        self.remoteCommandList = cmds

    def MatchCmd(self, command):
        ret = []
        localMatch = False
        for cmd in self.aliases:
            if cmd.startswith(command):
                if cmd == command:
                    return ([cmd], True)
                if cmd not in ret:
                    ret.append(cmd)
                localMatch = True

        for cmd in self.remoteCommandList:
            if cmd.startswith(command):
                if cmd == command:
                    return ([cmd], False)
                ret.append(cmd)

        import svc
        for sname in svc.__dict__:
            s = getattr(svc, sname)
            if getattr(s, '__slashhook__', False):
                for f in s.__dict__:
                    if f.startswith('cmd_' + command):
                        cmd = f[4:]
                        if cmd == command:
                            return ([cmd], True)
                        if cmd not in ret:
                            ret.append(cmd)
                        localMatch = True

        return (ret, localMatch)

    def SlashCmd(self, command, fallThrough = True, isMacro = False):
        if command.startswith('//'):
            return sm.RemoteSvc('slash').SlashCmd(command[1:])
        return self._SlashCmd(command, fallThrough, isMacro)

    def _SlashCmd(self, txt, fallThrough, isMacro):
        if isMacro:
            self.FetchRemoteCommandList()
            command = None
        else:
            parts = txt.split(' ', 1)
            command = parts[0].strip().lower()
            if len(parts) == 2:
                args = parts[1].strip()
            else:
                args = ''
            if command[0] == '/':
                command = command[1:]
            self.FetchRemoteCommandList()
            if self.remoteCommandList is not None:
                matches, hasLocal = self.MatchCmd(command)
                if hasLocal:
                    if len(matches) == 1:
                        command = matches[0]
                    else:
                        raise Error('%s is ambiguous. It resolves to multiple commands or aliases: %s' % (command, matches))
        if self.aliases.has_key(command) or isMacro:
            if isMacro:
                sequence = txt
            else:
                sequence = self.aliases[command]
            sequence = sequence.split(';')
            for line in sequence:
                line = line.strip()
                if line:
                    newline = []
                    p = param.ParamObject(txt)
                    for part in line.split(TOKEN):
                        if newline:
                            if len(part) >= 1:
                                if part[0] in '0123456789':
                                    try:
                                        if len(part) >= 2 and part[1] == '-':
                                            part = p[int(part[0]):] + part[2:]
                                        else:
                                            part = p[int(part[0])] + part[1:]
                                    except param.Error:
                                        raise Error('Alias expected additional parameter(s)')

                                else:
                                    part = TOKEN + part
                        newline.append(part)

                    newline = ''.join(newline) % InlineFunctionResolver()
                    res = self.SlashCmd(newline)

            if len(sequence) == 1:
                return res
            return 'Ok'
        try:
            args = args % InlineFunctionResolver()
            commandLine = '/' + command + ' ' + args
        except Error:
            raise
        except:
            log.LogException()
            raise Error('unexpected error resolving inline function')

        import svc
        for raw_service_name in svc.__dict__:
            service_classobj = getattr(svc, raw_service_name)
            if getattr(service_classobj, '__slashhook__', False):
                command_name = 'cmd_' + command
                slash_func = getattr(service_classobj, command_name, None)
                if slash_func:
                    try:
                        service_name = service_classobj.__guid__[4:]
                        service_instance = sm.GetService(service_name)
                        function_to_call = getattr(service_instance, command_name)
                        ret = function_to_call(param.ParamObject(args))
                        if ret:
                            return ret
                        break
                    except param.Error as e:
                        if slash_func.__doc__:
                            raise Error('usage: /%s %s' % (command, slash_func.__doc__.replace('%s', command)))
                        else:
                            raise Error('/%s called with crap args and doesnt handle it properly' % command)

        if fallThrough:
            return sm.RemoteSvc('slash').SlashCmd(commandLine)

    def cmd_sethackingdifficulty(self, p):
        sm.GetService('hackingUI').SetDifficulty(p.Parse('i')[0])
        return 'Ok'

    def cmd_sethackingvirusstats(self, p):
        integers = p.Parse('iii')
        sm.GetService('hackingUI').SetVirusStats(integers[0], integers[1], integers[2])
        return 'Ok'

    def cmd_openhacking(self, p):
        sm.GetService('hackingUI').TriggerNewGame()

    def cmd_run(self, p):
        filename, = p.Parse('s')
        if not os.path.exists(filename):
            filename += '.txt'
            if not os.path.exists(filename):
                raise Error('file not found')
        for line in open(filename, 'r'):
            line = line.strip()
            if line.startswith('/'):
                self.SlashCmd(line)

        return 'Ok'

    def cmd_macromenu(self, p):
        return self.cmd_alias(p, True)

    def cmd_alias(self, p, isMacro = False):
        what, rest = p.Parse('s?r')
        what = what.lower()
        if isMacro:
            thing = 'Macro'
            catalog = self.macros
            file = macroFile
        else:
            thing = 'Alias'
            catalog = self.aliases
            file = aliasFile
        if what == 'add':
            what, aliasName, rest = p.Parse('ssr')
            for key in catalog.keys():
                if key.lower() == aliasName.lower():
                    action = 'modified'
                    break
            else:
                action = 'added'

            catalog[aliasName] = rest
            self.SaveStuff(catalog, file)
            return '%s %s %s' % (thing, aliasName, action)
        if what == 'del':
            if not rest:
                raise param.Error
            aliasName = rest.lower().strip('"')
            for key in catalog.keys():
                if key.lower() == aliasName:
                    del catalog[aliasName]
                    self.SaveStuff(catalog, file)
                    return '%s %s deleted' % (thing, aliasName)
            else:
                raise Error('No such %s: %s' % (thing, aliasName))

        elif what == 'list':
            cmds = catalog.keys()
            cmds.sort()
            return '%s: <font color="#00ffc0">%s</font><br>' % (thing, ', '.join(cmds))
        for key, item in catalog.iteritems():
            if key.lower() == what.lower():
                return '%s %s is defined as: %s' % (thing, what, item)

        raise param.Error

    def cmd_loop(self, p):
        count, rest = p.Parse('ir')
        if count >= 10:
            if count > 50:
                Message('Looped Execution', 'The number of iterations must be less than 50')
                return
            ret = sm.GetService('gameui').MessageBox(title='Looped Execution', text='You have specified %d iterations.<br>Slash commands looped this way cannot be aborted. Depending on the slash command, it can take a long time to complete or cause a high server load.<br>Continue?' % count, buttons=uiconst.OKCANCEL, icon=uiconst.WARNING)
            if ret:
                if ret[0] in (uiconst.ID_CANCEL, uiconst.ID_CLOSE):
                    return
        for i in xrange(count):
            self.SlashCmd(rest)

        return 'Ok'

    def cmd_chtgag(self, p):
        channelName, charID, reason, durationInSecs = extract_arguments_for_gag_or_ban(p)
        GetChatService().MuteUser(channelName, charID, reason, durationInSecs)
        return 'Ok'

    def cmd_chtungag(self, p):
        channelName, charID = extract_arguments_for_ungag_or_unban(p)
        GetChatService().UnmuteUser(channelName, charID)
        return 'Ok'

    def cmd_chtban(self, p):
        channelName, charID, reason, durationInSecs = extract_arguments_for_gag_or_ban(p)
        GetChatService().BanUserFromChannel(channelName, charID, reason, durationInSecs)
        return 'Ok'

    def cmd_chtunban(self, p):
        channelName, charID = extract_arguments_for_ungag_or_unban(p)
        GetChatService().UnbanUserFromChannel(channelName, charID)
        return 'Ok'

    def cmd_whoami(self, p):
        roles = []
        for k, v in globals().iteritems():
            if k.startswith('ROLE_'):
                if type(v) in (int, long):
                    if eve.session.role & v and v not in (ROLE_ANY, ROLE_PLAYER, ROLE_LOGIN):
                        roles.append(k[5:])

        text = ['character: %s (%s)' % (eve.session.charid, cfg.eveowners.Get(eve.session.charid).name), 'user: %s (type: %s)' % (eve.session.userid, eve.session.userType), 'role: 0x%08X (%s)' % (eve.session.role, ', '.join(roles))]
        AsyncMessage('Account Information', '<br>'.join(text))
        return 'Ok'

    def cmd_hop(self, p):
        if eve.session.role & ROLE_WORLDMOD:
            return
        dist, = p.Parse('i')
        if eve.session.stationid:
            raise Error("This obviously won't work in a station :)")
        bp = sm.GetService('michelle').GetBallpark()
        me = bp.GetBall(bp.ego)
        v = trinity.TriVector(me.vx, me.vy, me.vz)
        v.Normalize()
        v.Scale(dist)
        sm.RemoteSvc('slash').SlashCmd('/tr me me offset=%d,%d,%d' % (int(v.x), int(v.y), int(v.z)))
        GetMenuService().ClearAlignTargets()
        return 'Ok'

    def cmd_online(self, p):
        target, = p.Parse('s')
        activeShipID = eveCfg.GetActiveShip()
        if session.stationid is not None and (target == 'me' or int(target) == activeShipID):
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            for module in dogmaLocation.dogmaItems[activeShipID].GetFittedItems().itervalues():
                if const.effectOnline in (row.effectID for row in dogma.data.get_type_effects(module.typeID)):
                    try:
                        dogmaLocation.OnlineModule(module.itemID)
                    except UserError as e:
                        if e.msg.startswith('EffectAlreadyActive'):
                            continue
                        raise

        else:
            sm.RemoteSvc('slash').SlashCmd('/online %s' % target)
        return 'Ok'

    def cmd_super(self, p):
        target, = p.Parse('s')
        if target.lower() == 'me':
            victim = 'you'
            target = 'me'
        else:
            char = GetCharacter(target)
            victim = '"' + char.characterName + '"'
            target = char.characterID
        Progress('Making %s Leet' % victim, 'Please wait...', 0, 1)
        try:
            sm.RemoteSvc('slash').SlashCmd('/giveskill %s super 5' % target)
        finally:
            Progress('Making %s Leet' % victim, 'Done!', 1, 1)

        return 'Ok'

    def cmd_noob(self, p):
        target, = p.Parse('s')
        if target.lower() == 'me':
            victim = 'you'
            target = 'me'
        else:
            char = GetCharacter(target)
            victim = '"' + char.characterName + '"'
            target = char.characterID
        Progress('Making %s n00b' % victim, 'Please wait...', 0, 1)
        try:
            sm.RemoteSvc('slash').SlashCmd('/removeskill %s all' % target)
            sm.GetService('skillqueue').ReInitialize()
        finally:
            Progress('Making %s n00b' % victim, 'Done!', 1, 1)

        return 'Ok'

    def cmd_givestarterskills(self, p):
        try:
            target, = p.Parse('s')
            if target.lower() == 'me':
                victim = 'you'
                target = session.charid
            else:
                char = GetCharacter(target)
                victim = '"' + char.characterName + '"'
                target = char.characterID
        except param.Error:
            victim = 'you'
            target = session.charid

        Progress('Giving %s starter skills' % victim, 'Please wait...', 0, 1)
        try:
            sm.RemoteSvc('slash').SlashCmd('/givestarterskills %s' % target)
        finally:
            Progress('Giving %s starter skills' % victim, 'Done!', 1, 1)

        return 'Ok'

    def cmd_randomizeskills(self, p):
        Progress('Randomizing your skills,', 'Please wait...', 0, 1)
        try:
            sm.RemoteSvc('slash').SlashCmd('/randomizeskills')
        finally:
            Progress('Randomizing your skills,', 'Done!', 1, 1)

        return 'Ok'

    def cmd_bp(self, p):
        try:
            name, rest = p.Parse('s?r')
            if rest is None:
                rest = ''
        except param.Error:
            rest = ''
            try:
                name, = p.Parse('r')
            except param.Error:
                return

        typeID = self.AutoComplete(name, allowedCategories=[const.categoryBlueprint])
        if typeID:
            return sm.RemoteSvc('slash').SlashCmd('/bp %s %s' % (typeID, rest))
        else:
            return

    def cmd_createitem(self, p):
        qty = 1
        try:
            name, = p.Parse('s')
        except param.Error:
            try:
                name, qty = p.Parse('ss')
            except param.Error:
                try:
                    name, = p.Parse('r')
                except param.Error:
                    return

        typeID = self.AutoComplete(name)
        if typeID:
            return sm.RemoteSvc('slash').SlashCmd('/createitem %s %s' % (typeID, qty))
        else:
            return

    def cmd_unload(self, p):
        try:
            target, rest = p.Parse('s?r')
            if rest is None:
                rest = ''
            else:
                rest = rest.lower().strip('"')
        except param.Error:
            return

        if target.lower() != 'me' or rest == 'all' or rest.isdigit():
            return
        matches = {}
        for rec in sm.GetService('invCache').GetInventoryFromId(eve.session.shipid).List():
            if rec.categoryID != const.categoryOwner:
                typeName = evetypes.GetName(rec.typeID)
                if rest in typeName.lower():
                    matches[typeName] = rec.typeID

        if not matches:
            return
        matches = matches.items()
        matches.sort()
        if len(matches) > 1:
            ret = uix.ListWnd(matches, listtype='generic', caption='AutoComplete: %d types found' % len(matches))
        else:
            ret = matches[0]
        if ret:
            return sm.RemoteSvc('slash').SlashCmd('/unload me %s' % ret[1].typeID) or 'Ok'
        else:
            return

    def cmd_dogmaupdate(self, p):
        sm.RemoteSvc('slash').SlashCmd('/dogmaupdate')
        sm.GetService('clientEffectCompiler').effects.clear()
        eve.Message('CustomNotify', {'notify': 'Server has regenerated the expressions and yours have been cleared'})
        return 'Ok'

    def cmd_loadcontainer(self, p):
        return self.cmd_fit(p, cmd='load', categories=None)

    def cmd_fit(self, p, cmd = 'fit', categories = -1):
        if categories == -1:
            categories = [const.categoryModule, const.categoryDrone, const.categoryCharge]
        qty = ''
        try:
            target, name, qty = p.Parse('sss')
        except param.Error:
            try:
                target, name = p.Parse('ss')
            except param.Error:
                try:
                    target, name = p.Parse('sr')
                except param.Error:
                    return

        typeID = self.AutoComplete(name, allowedCategories=categories)
        if typeID:
            return sm.RemoteSvc('slash').SlashCmd('/%s "%s" %s %s' % (cmd,
             target,
             typeID,
             qty))
        else:
            return

    def cmd_entity(self, p):
        qty = 1
        try:
            action, qty, name = p.Parse('sir')
        except param.Error:
            try:
                action, name = p.Parse('sr')
            except param.Error:
                return

        if action.lower() != 'deploy':
            return
        else:
            typeID = self.AutoComplete(name, allowedCategories=[const.categoryEntity])
            if typeID:
                return sm.RemoteSvc('slash').SlashCmd('/entity deploy %s %s' % (qty, typeID)) or 'Ok'
            return

    def cmd_spawn(self, p):
        try:
            name, rest = p.Parse('sr')
        except param.Error:
            try:
                name, = p.Parse('r')
                rest = ''
            except param.Error:
                return

        typeID = self.AutoComplete(name, allowedCategories=[const.categoryShip, const.categoryAsteroid, const.categoryDrone], allowedGroups=[const.groupLargeCollidableObject,
         const.groupCargoContainer,
         const.groupBiomass,
         const.groupComet,
         const.groupCloud,
         const.groupSentryGun,
         const.groupInvisibleBeacon])
        if typeID:
            return sm.RemoteSvc('slash').SlashCmd('/spawn %s %s' % (typeID, rest))
        else:
            return

    def cmd_spawnn(self, p):
        try:
            qty, deviation, name = p.Parse('ifr')
        except param.Error:
            return

        typeID = self.AutoComplete(name, allowedCategories=[const.categoryShip, const.categoryAsteroid, const.categoryDrone], allowedGroups=[const.groupLargeCollidableObject,
         const.groupCargoContainer,
         const.groupBiomass,
         const.groupComet,
         const.groupCloud,
         const.groupInvisibleBeacon,
         const.groupSentryGun])
        if typeID:
            return sm.RemoteSvc('slash').SlashCmd('/spawnn %s %s %s' % (qty, deviation, typeID)) or 'Ok'
        else:
            return

    def cmd_giveskills(self, p):
        try:
            target, skillname, level = p.Parse('ssi')
        except param.Error:
            try:
                level = None
                target, skillname = p.Parse('sr')
            except param.Error:
                return

        skillname = skillname.strip('"')
        if skillname.lower() in ('all', 'super'):
            return
        else:
            typeID = self.AutoComplete(skillname, allowedCategories=[const.categorySkill])
            if typeID:
                if level is None:
                    level = 5
                return sm.RemoteSvc('slash').SlashCmd('/giveskill "%s" %s %s' % (target, typeID, level)) or 'Ok'
            return

    def cmd_removeskills(self, p):
        try:
            level = None
            target, skillname = p.Parse('sr')
        except param.Error:
            return

        skillname = skillname.strip('"')
        if skillname.lower() == 'all':
            return
        else:
            typeID = self.AutoComplete(skillname, allowedCategories=[const.categorySkill])
            if typeID:
                return sm.RemoteSvc('slash').SlashCmd('/removeskill "%s" %s' % (target, typeID)) or 'Ok'
            return

    def cmd_skillscopy(self, p):
        try:
            fromCharacter, toCharacter = p.Parse('sr')
        except param.Error:
            return

        Progress('Preparing Copy', 'Please wait...', 0, 1)
        try:
            sm.RemoteSvc('slash').SlashCmd('/skillscopy "%s" "%s"' % (fromCharacter, toCharacter))
        finally:
            Progress('Copying Skills', 'Done!', 1, 1)

        return 'Ok'

    def _extract_windowName_from_params(self, p):
        extracted_param = p.Parse('s')[0]
        prefix = 'windowID=chatchannel_'
        if extracted_param.startswith(prefix):
            windowName = extracted_param[len(prefix):]
        else:
            raise Error("Couldn't extract a windowName from the params")
        return windowName

    def cmd_massfleetinvite(self, p):
        fleetSvc = sm.StartService('fleet')
        fleetSvc.CheckIsInFleet()
        windowName = self._extract_windowName_from_params(p)
        candidates = sm.GetService('XmppChat').GetMemberIDsForNamedWindow(windowName)
        if eve.session.charid in candidates:
            candidates.remove(eve.session.charid)
        t = len(candidates)
        c = 0
        for charID in candidates:
            c += 1
            Progress('Inviting...', '[%d/%d] %s' % (c, t, cfg.eveowners.Get(charID).ownerName), c, t)
            try:
                fleetSvc.fleet.Invite(charID, None, None, None, True)
            except:
                pass

        Progress('Inviting...', 'Done!', 1, 1)
        return 'Ok'

    def cmd_masstransport(self, p):
        windowName = self._extract_windowName_from_params(p)
        memberIDs = sm.GetService('XmppChat').GetMemberIDsForNamedWindow(windowName)
        local_memberIDs = sm.GetService('XmppChat').GetMemberIDsForNamedWindow('local')
        candidates = [ charID for charID in memberIDs if charID not in local_memberIDs ]
        if eve.session.charid in candidates:
            candidates.remove(eve.session.charid)
        t = len(candidates)
        c = 0
        for charID in candidates:
            c += 1
            Progress('Transfering...', '[%d/%d] %s' % (c, t, cfg.eveowners.Get(charID).ownerName), c, t)
            sm.RemoteSvc('slash').SlashCmd('/tr %d me noblock' % charID)

        Progress('Transfering...', 'All commands sent to the server', 1, 1)
        return 'Ok'

    def cmd_massstanding(self, p):
        try:
            fromID, newStanding = p.Parse('sr')
        except:
            raise UserError('SlashError', {'reason': 'Provide from and the new standing value.'})
            sys.exc_clear()
            return

        local = (('solarsystemid2', eve.session.solarsystemid2),)
        c = self.GetChannel()
        if not c or c.channelID == local:
            return
        candidates = [ charID for charID in self.GetChannelUsers() ]
        if eve.session.charid in candidates:
            candidates.remove(eve.session.charid)
        t = len(candidates)
        c = 0
        reason = 'Mass standing change by %s' % cfg.eveowners.Get(eve.session.charid).name
        corps = sm.RemoteSvc('lookupSvc').LookupCorporations(fromID)
        corpIDs = [ each.corporationID for each in corps ]
        factions = sm.RemoteSvc('lookupSvc').LookupFactions(fromID)
        factionIDs = [ each.factionID for each in factions ]
        resultIDs = corpIDs + factionIDs
        resultList = [ (cfg.eveowners.Get(each).name, cfg.eveowners.Get(each).id, cfg.eveowners.Get(each).typeID) for each in resultIDs ]
        if not resultList:
            raise UserError('SlashError', {'reason': 'Unable to resolve corporation or faction name'})
            sys.exc_clear()
            return
        ret = uix.ListWnd(resultList, caption='AutoComplete: %d types found' % len(resultList), ordered=1)
        if ret:
            if eve.Message('CustomQuestion', {'header': 'Change standings?',
             'question': 'Do you really want to change the standings towards %s for the characters in this channel?' % ret[0]}, uiconst.YESNO) == uiconst.ID_YES:
                for charID in candidates:
                    c += 1
                    Progress('Setting standings...', '[%d/%d] %s' % (c, t, cfg.eveowners.Get(charID).ownerName), c, t)
                    sm.RemoteSvc('slash').SlashCmd('/setstanding "%s" %d %s "%s"' % (ret[1],
                     charID,
                     newStanding,
                     reason))

                txt = 'Standings to %s set to %s for %d characters' % (ret[0], newStanding, c)
            else:
                txt = 'Standings to %s left unmodified' % ret[0]
        else:
            txt = 'Standings left unmodified'
        Progress('Setting standings...', 'Done!', 1, 1)
        eve.Message('CustomNotify', {'notify': txt})
        return 'Ok'

    def cmd_avatar(self, p):
        b = u''
        try:
            a, b = p.Parse('sr')
        except param.Error:
            a = p.Parse('s')[0]

        if a.isdigit():
            if not b:
                ad.DisplayCharacter(a)
            else:
                b_params = b.split()
                dna_file = None
                anim_file = None
                audio_msg = None
                for par in b_params:
                    if '.prs' in par:
                        dna_file = par
                    elif '.gr2' in par or '.gsf' in par:
                        anim_file = par
                    else:
                        audio_msg = par

                ad.DisplayCharacter(a, dna_str=dna_file, anim_str=anim_file, audio_str=audio_msg)
        else:
            a_params = a.split()
            dna_file = None
            anim_file = None
            audio_msg = None
            for par in a_params:
                if '.prs' in par:
                    dna_file = par
                elif '.gr2' in par or '.gsf' in par:
                    anim_file = par
                else:
                    audio_msg = par

            if b:
                b_params = b.split()
                for par in b_params:
                    if '.prs' in par:
                        dna_file = par
                    elif '.gr2' in par or '.gsf' in par:
                        anim_file = par
                    else:
                        audio_msg = par

            ad.DisplayCharacter(0, dna_str=dna_file, anim_str=anim_file, audio_str=audio_msg)
        return 'Ok'

    def cmd_avatarscene(self, p):
        b = u''
        anim_strs = []
        audio_strs = []
        b = p.Parse('r')
        b_params = b[0].split()
        a = b_params.pop(0)
        n = None
        if b_params:
            for par in b_params:
                try:
                    n = int(par)
                except ValueError():
                    n = None
                except Exception as e:
                    raise e

                if '.gr2' in par or '.gsf' in par or par == 'no_anim':
                    anim_strs.append(par)
                else:
                    audio_strs.append(par)

        ad.DisplayPreparedScene(a, anim_strs=anim_strs, audio_strs=audio_strs, sub_char=n)
        return 'Ok'

    def cmd_avatarcommand(self, p):
        b = p.Parse('r')
        b_params = b[0].split()
        command = b_params.pop(0)
        if b_params:
            sm.ScatterEvent('OnAvatarCommand', command, *b_params)
        else:
            sm.ScatterEvent('OnAvatarCommand', command)
        return 'Ok'

    def cmd_pos(self, p):
        try:
            action, id = p.Parse('sr')
        except param.Error:
            try:
                action = p.Parse('s')
                bp = sm.GetService('michelle').GetBallpark()
                for ballID in bp.balls.keys():
                    try:
                        item = bp.GetInvItem(ballID)
                        if item.groupID in (const.groupControlTower,):
                            id = item.itemID
                            action = action[0]
                    except:
                        pass

            except:
                pass

        if not id:
            return
        elif action.lower() != 'fuel':
            return
        else:
            try:
                id = int(id)
            except ValueError:
                eve.Message('CustomInfo', {'info': "This must be called as either '/pos fuel' or '/pos fuel itemID'"})
                return 'ok'

            resourcesPerHour = []
            reinforcedResourcesPerHour = []
            totalFuelVolumePerCycle = float()
            starbaseCharters = []
            invCache = sm.GetService('invCache')
            chosenTower = invCache.GetInventoryFromId(id)
            secStatus = sm.GetService('map').GetSecurityStatus(eve.session.locationid)
            for typeID in evetypes.GetTypeIDsByGroup(const.groupLease):
                starbaseCharters.append(typeID)

            resources = get_control_tower_resources(chosenTower.typeID)
            for resource in resources:
                if resource.resourceTypeID == const.typeStrontiumClathrates:
                    reinforcedResourcesPerHour.append((resource.resourceTypeID, resource.quantity, evetypes.GetVolume(resource.resourceTypeID)))
                elif secStatus < 0.4:
                    if resource.resourceTypeID not in starbaseCharters:
                        resourcesPerHour.append((resource.resourceTypeID, resource.quantity, evetypes.GetVolume(resource.resourceTypeID)))
                else:
                    resourcesPerHour.append((resource.resourceTypeID, resource.quantity, evetypes.GetVolume(resource.resourceTypeID)))

            for resourceTypeID, amountPerCycle, resourceVolume in resourcesPerHour:
                totalFuelVolumePerCycle += int(amountPerCycle * resourceVolume)

            totalFuelVolumePerCycle += 1
            strontVolume = reinforcedResourcesPerHour[0][2]
            fuelBay = chosenTower.GetCapacity()
            strontBay = chosenTower.GetCapacity(flag=const.flagSecondaryStorage)
            fuelCycles = int(fuelBay.capacity / totalFuelVolumePerCycle)
            strontCycles = int(strontBay.capacity / strontVolume)
            if eve.session.role & ROLE_WORLDMOD:
                addList = []
                for commodity, amountPerCycle, resourceVolume in reinforcedResourcesPerHour:
                    sm.GetService('slash').SlashCmd('crea %d %s' % (commodity, strontCycles))
                    for cargo in invCache.GetInventoryFromId(eve.session.shipid).ListCargo():
                        if cargo.typeID == commodity:
                            addList.append(cargo.itemID)

                invCache.GetInventoryFromId(id).MultiAdd(addList, eve.session.shipid, flag=const.flagSecondaryStorage)
                addList = []
                for fuel, amountPerCycle, resourceVolume in resourcesPerHour:
                    sm.GetService('slash').SlashCmd('crea %d %s' % (fuel, int(fuelCycles * amountPerCycle)))
                    for cargo in invCache.GetInventoryFromId(eve.session.shipid).ListCargo():
                        if cargo.typeID == fuel and cargo.stacksize == fuelCycles * amountPerCycle:
                            addList.append(cargo.itemID)

                invCache.GetInventoryFromId(id).MultiAdd(addList, eve.session.shipid, flag=const.flagNone)
                return 'Ok'
            shipType = const.typeBHMegaCargoShip
            oldShipItemID = eve.session.shipid
            newShipItemID = int()
            if invCache.GetInventoryFromId(int(eve.session.shipid)).typeID != shipType:
                newShipItemID = sm.RemoteSvc('slash').SlashCmd('/spawn %d' % shipType)
                ship = sm.StartService('gameui').GetShipAccess()
                if ship:
                    sm.StartService('sessionMgr').PerformSessionChange('board', ship.Board, newShipItemID, oldShipItemID)
            blue.pyos.synchro.SleepSim(5000)
            addList = []
            for commodity, amountPerCycle, resourceVolume in reinforcedResourcesPerHour:
                sm.GetService('slash').SlashCmd('load me %d %s' % (commodity, strontCycles))
                for cargo in invCache.GetInventoryFromId(eve.session.shipid).ListCargo():
                    if cargo.typeID == commodity:
                        addList.append(cargo.itemID)

            invCache.GetInventoryFromId(id).MultiAdd(addList, eve.session.shipid, flag=const.flagSecondaryStorage)
            addList = []
            for fuel, amountPerCycle, resourceVolume in resourcesPerHour:
                sm.GetService('slash').SlashCmd('load me %d %s' % (fuel, int(fuelCycles * amountPerCycle)))
                for cargo in invCache.GetInventoryFromId(eve.session.shipid).ListCargo():
                    if cargo.typeID == fuel and cargo.stacksize == fuelCycles * amountPerCycle:
                        addList.append(cargo.itemID)

            invCache.GetInventoryFromId(id).MultiAdd(addList, eve.session.shipid, flag=const.flagNone)
            if blue.os.GetSimTime() <= eve.session.nextSessionChange:
                ms = 1000 + 1000L * (eve.session.nextSessionChange - blue.os.GetSimTime()) / 10000000L
                blue.pyos.synchro.SleepSim(ms)
                if newShipItemID:
                    ship = sm.StartService('gameui').GetShipAccess()
                    if ship:
                        sm.StartService('sessionMgr').PerformSessionChange('board', ship.Board, oldShipItemID, newShipItemID)
                        sm.GetService('slash').SlashCmd('heal %d 0' % newShipItemID)
                        blue.pyos.synchro.SleepSim(5000)
                        sm.GetService('insider').HealRemove(const.groupWreck)
            return 'Ok'

    def GetAmmoTypesForWeapon(self, itemID):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        dogmaItem = dogmaLocation.dogmaItems[itemID]
        ammoInfoByTypeID = defaultdict(lambda : utillib.KeyVal(singletons=[], nonSingletons=[]))
        validGroupIDs = dogmaLocation.dogmaStaticMgr.GetValidChargeGroupsForType(dogmaItem.typeID)
        GetTypeAttribute = dogmaLocation.dogmaStaticMgr.GetTypeAttribute
        preferredChargeSize = GetTypeAttribute(dogmaItem.typeID, const.attributeChargeSize)
        legalTypes = set()
        for typeID in evetypes.GetTypeIDsByGroups(validGroupIDs):
            if preferredChargeSize is not None and GetTypeAttribute(typeID, const.attributeChargeSize) != preferredChargeSize:
                continue
            legalTypes.add(typeID)

        return legalTypes

    def IsLegalAmmo(self, weaponItemID, chargeTypeID):
        if not chargeTypeID:
            return True
        for typeID in self.GetAmmoTypesForWeapon(weaponItemID):
            if typeID == chargeTypeID:
                return True

        return False

    def GetRandomAmmoForWeapon(self, weaponItemID):
        for typeID in self.GetAmmoTypesForWeapon(weaponItemID):
            return typeID

    def cmd_ammo(self, p):
        try:
            typeID = p.Parse('s')[0]
        except:
            raise UserError('SlashError', {'reason': 'Usage: /ammo [typeID]|random<br>Loads ammo of the specified type into all turrets or launchers that support this type.<br>If random is specified then all weapons are loaded with the first matching ammo found.'})

        if typeID == 'random':
            typeID = 0
        shipInv = sm.GetService('invCache').GetInventoryFromId(session.shipid)
        for row in shipInv.ListHardwareModules():
            if self.IsLegalAmmo(row.itemID, typeID):
                shipInv.ClearCharges(row.flagID)

        if typeID == 'clear':
            return 'Ok'
        typeID = int(typeID)
        blue.pyos.synchro.SleepSim(1000)
        cmds = []
        stateMgr = sm.GetService('godma').GetStateManager()
        for row in shipInv.ListHardwareModules():
            thisTypeID = typeID
            if not self.IsLegalAmmo(row.itemID, typeID):
                continue
            if not thisTypeID:
                thisTypeID = self.GetRandomAmmoForWeapon(row.itemID)
            if not thisTypeID:
                continue
            self.LogNotice('/ammo: Putting %s into %s' % (thisTypeID, row.itemID))
            ma = stateMgr.GetType(row.typeID)
            num = int(ma.capacity / evetypes.GetVolume(thisTypeID))
            if num > 0:
                cmds.append('/fit me %d %d flag=%d' % (thisTypeID, num, row.flagID))

        uthread.parallel([ (sm.GetService('slash').SlashCmd, (cmd,)) for cmd in cmds ])
        return 'Ok'

    def cmd_sessionchangetimer(self, p):
        oldVal = sessions.sessionChangeDelay
        try:
            secs = p.Parse('i')[0]
            sessions.sessionChangeDelay = min(max(5, secs), 60) * const.SEC
            session.nextSessionChange = None
        except:
            pass

        eve.Message('CustomNotify', {'notify': 'Session-Change Timer was changed from %ss to <b>%ss</b>.<br>This value will be reset next time you log in' % (oldVal / const.SEC, sessions.sessionChangeDelay / const.SEC)})
        return 'Ok'

    def cmd_recustomize(self, p):
        if sm.GetService('cc').NoExistingCustomization():
            return 1
        sm.GetService('gameui').GoCharacterCreationCurrentCharacter()
        return 1

    def cmd_buyorders(self, p):
        if session.stationid is None:
            raise UserError('SlashError', {'reason': 'You must be in a station to execute this command.'})
        qty = 1
        orderRange = 32767
        try:
            name, = p.Parse('s')
        except param.Error:
            try:
                name, qty = p.Parse('si')
            except param.Error:
                try:
                    name, qty, orderRange = p.Parse('sii')
                except param.Error:
                    return

        typeID = self.AutoComplete(name)
        typeName = evetypes.GetName(typeID)
        minVolume = 1
        duration = 0
        useCorp = False
        qtyDone = 0
        Progress('Buying %s %s' % (qty, typeName), 'Please wait...', 0, 1)
        try:
            while qty > qtyDone:
                order = sm.GetService('marketQuote').GetBestAskInRange(typeID, session.stationid, orderRange)
                if order is None:
                    break
                if order.volRemaining + qtyDone > qty:
                    buyQty = qty - qtyDone
                else:
                    buyQty = order.volRemaining
                sm.GetService('marketQuote').BuyStuff(session.stationid, typeID, order.price, buyQty, orderRange, minVolume, duration, useCorp)
                blue.pyos.synchro.SleepSim(800)
                qtyDone += buyQty

        finally:
            if qtyDone == qty:
                Progress('Done buying all the %s you asked me to.' % typeName, '', 1, 1)
            else:
                Progress('Done. Did not find as many %s as you asked for.' % typeName, '', 1, 1)

        return 'Ok'

    def cmd_sellorders(self, p):
        if session.stationid is None:
            raise UserError('SlashError', {'reason': 'You must be in a station to execute this command.'})
        qty = 1
        orderCount = 1
        priceFluct = 0
        try:
            theType, price = p.Parse('sf')
        except param.Error:
            try:
                theType, price, qty = p.Parse('sfi')
            except param.Error:
                try:
                    theType, price, qty, orderCount = p.Parse('sfii')
                except param.Error:
                    try:
                        theType, price, qty, orderCount, priceFluct = p.Parse('sfiif')
                    except param.Error:
                        raise UserError('SlashError', {'reason': 'Syntax error: should be /sellorders type price [qty] [ordercount] [price fluctuation in %]'})

        duration = 14
        useCorp = False
        officeID = None
        expectedBrokersFee = None
        if priceFluct != 0:
            p = priceFluct / 100.0
            minPriceCents = int(max(price - price * p, 1) * 100)
            maxPriceCents = int((price + price * p) * 100)
        Progress('Creating %s Market order(s)' % orderCount, 'Please wait...', 0, 1)
        try:
            validatedItems = []
            itemID = self.cmd_createitem(param.ParamObject(str(theType) + ' ' + unicode(orderCount * qty)))
            blue.pyos.synchro.SleepSim(1200)
            typeID = sm.GetService('invCache').FetchItem(itemID, session.stationid).typeID
            for x in xrange(orderCount):
                if priceFluct == 0:
                    orderPrice = price
                else:
                    orderPrice = random.randint(minPriceCents, maxPriceCents) / 100.0
                validatedItem = utillib.KeyVal(stationID=int(session.stationid), typeID=int(typeID), itemID=itemID, price=orderPrice, quantity=int(qty), officeID=officeID)
                sm.GetService('marketQuote').SellMulti([validatedItem], useCorp, duration, expectedBrokersFee)

        finally:
            Progress('Done creating market orders.', '', 1, 1)

        return 'Ok'

    def cmd_cancelallorders(self, p):
        orders = sm.GetService('marketQuote').GetMyOrders()
        if not orders:
            raise UserError('SlashError', {'reason': 'No market orders found.'})
        for order in orders:
            sm.GetService('marketQuote').CancelOrder(order.orderID, order.regionID)

        return 'Ok'

    def cmd_reimbursebounties(self, p):
        sm.GetService('bountySvc').GMReimburseBounties()
        return 'Ok'

    def cmd_clearbountycache(self, p):
        sm.GetService('bountySvc').GMClearBountyCache()
        return 'Ok'

    def cmd_killright(self, p):
        sm.RemoteSvc('slash').SlashCmd('/killright %s' % p.line)
        sm.GetService('bountySvc').ClearAllKillRightData()
        return 'Ok'

    def cmd_newscanner(self, p):
        cmd = p.Parse('s')
        if 'start' in cmd:
            sm.GetService('sensorSuite')
        elif 'stop' in cmd:
            sm.StopService('sensorSuite')
        elif 'show' in cmd:
            if session.solarsystemid is not None:
                sensorSuite = sm.GetService('sensorSuite')
                sensorSuite.EnableSensorOverlay()
        elif 'hide' in cmd:
            if session.solarsystemid is not None:
                sensorSuite = sm.GetService('sensorSuite')
                sensorSuite.EnableSensorOverlay()
        elif 'register' in cmd:
            if session.solarsystemid is not None:
                sensorSuite = sm.GetService('sensorSuite')
                sm.RemoteSvc('scanMgr').SignalTrackerRegister()
        elif 'scan' in cmd:
            if session.solarsystemid is not None:
                sensorSuite = sm.GetService('sensorSuite')
                sensorSuite.DisableSensorOverlay()
                sensorSuite.systemReadyTime = blue.os.GetSimTime() - const.SEC * 2
                sensorSuite.StartSensorSweep()
        return 'Ok'

    def cmd_dplay(self, p):
        coords = None
        try:
            dungeonID, godmode, x, y, z = p.Parse('i?i?f?f?f')
            coords = (x, y, z)
            if None in coords:
                coords = None
        except param.Error:
            raise Error('Use /dplay DUNGEONID [godmode:0|1]\n(godmode defaults to 1)')

        dungeonID = int(dungeonID)
        if godmode is None:
            godmode = 1
        self.leveleditor = player = eveMoniker.Moniker('keeper', session.userid)
        player.PlayDungeon(dungeonID, godmode=godmode, coords=coords)
        return 'Ok'

    def cmd_dgoto(self, p):
        roomID = int(p.Parse('i')[0])
        self.leveleditor = player = eveMoniker.Moniker('keeper', session.userid)
        player.GotoRoom(roomID)
        return 'Ok'

    def cmd_highlight(self, p):
        try:
            cmd_option, _ = p.Parse('s?r')
        except:
            self._cmd_highlightError()

        if cmd_option == 'ui':
            return self._cmd_highlightui(p)
        if cmd_option == 'menu':
            return self._cmd_highlightmenu(p)
        if cmd_option == 'object':
            return self._cmd_highlightobject(p)
        if cmd_option == 'item':
            return self._cmd_highlightitem(p)
        if cmd_option == 'entitygroup':
            return self._cmd_highlightentitygroup(p)
        if cmd_option == 'type':
            return self._cmd_highlighttype(p)
        if cmd_option == 'group':
            return self._cmd_highlightgroup(p)
        if cmd_option == 'spaceobject':
            return self._cmd_highlightspaceobject(p)
        if cmd_option == 'clear':
            return self._cmd_highlightclear(p)
        self._cmd_highlightError()

    def _cmd_highlightError(self):
        raise UserError('SlashError', {'reason': 'Available options:\n/highlight ui\n/highlight menu\n/highlight object\n/highlight item\n/highlight entitygroup\n/highlight type\n/highlight group\n/highlight spaceobject\n/highlight clear ui\n/highlight clear menu\n/highlight clear space\n/highlight clear all'})

    def _cmd_highlightui(self, p):
        relativePositionString = None
        style = None
        try:
            _, uiElementName, title, message, secondsTilFadeout, relativePositionString, style = p.Parse('ssssiss')
        except:
            try:
                _, uiElementName, title, message, secondsTilFadeout, relativePositionString = p.Parse('ssssis')
            except:
                try:
                    _, uiElementName, title, message, secondsTilFadeout = p.Parse('ssssi')
                    relativePositionString = None
                except:
                    try:
                        _, uiElementName, title, message, relativePositionString = p.Parse('sssss')
                        secondsTilFadeout = None
                    except:
                        try:
                            _, uiElementName, title, message = p.Parse('ssss')
                            relativePositionString = None
                            secondsTilFadeout = None
                        except:
                            raise UserError('SlashError', {'reason': 'Usage: /highlight ui uiElementName title message [secondsTilFadeout] [relativePosition] [style]'})

        if relativePositionString and relativePositionString not in DIRECTION_STRING_TO_ID:
            raise UserError('SlashError', {'reason': 'Available relative positions for UI highlight: left, up, right, down'})
        if style and style not in UI_CLASS_BY_NAME:
            raise UserError('SlashError', {'reason': 'Available styles for UI highlight: AuraBlue, RetroBlack'})
        sm.GetService('uiHighlightingService').highlight_ui_element_by_name(ui_element_name=uiElementName, message=message, fadeout_seconds=secondsTilFadeout, title=title, default_direction=DIRECTION_STRING_TO_ID[relativePositionString] if relativePositionString else None, ui_class=style)
        return 'Ok'

    def _cmd_highlightmenu(self, p):
        try:
            _, menu_name, type_id = p.Parse('ssi')
        except:
            try:
                _, menu_name = p.Parse('ss')
                type_id = None
            except:
                raise UserError('SlashError', {'reason': 'Usage: /highlight menu menuName'})

        type_ids = [type_id] if type_id else []
        sm.GetService('uiHighlightingService').highlight_menu_by_name(menu_name, type_ids)
        return 'Ok'

    def _cmd_highlightobject(self, p):
        try:
            __, objectID, message, hint, secondsTilFadeout = p.Parse('sissi')
            sm.GetService('uiHighlightingService').highlight_space_object_by_dungeon_object_id(objectID, message, hint, secondsTilFadeout)
        except:
            try:
                _, objectID, message, hint = p.Parse('siss')
                sm.GetService('uiHighlightingService').highlight_space_object_by_dungeon_object_id(objectID, message, hint)
            except:
                raise UserError('SlashError', {'reason': 'Usage: /highlight object objectID message, hint, [secondsTilFadeout]'})

        return 'Ok'

    def _cmd_highlightitem(self, p):
        try:
            __, itemID, message, hint, secondsTilFadeout = p.Parse('sissi')
            sm.GetService('uiHighlightingService').highlight_space_object_by_item_id(itemID, message, hint, secondsTilFadeout)
        except:
            try:
                _, itemID, message, hint = p.Parse('siss')
                sm.GetService('uiHighlightingService').highlight_space_object_by_item_id(itemID, message, hint)
            except:
                raise UserError('SlashError', {'reason': 'Usage: /highlight item itemID message, hint, [secondsTilFadeout]'})

        return 'Ok'

    def _cmd_highlightentitygroup(self, p):
        try:
            __, entityGroupID, message, hint, secondsTilFadeout = p.Parse('sissi')
            sm.GetService('uiHighlightingService').highlight_space_object_by_dungeon_entity_group_id(entityGroupID, message, hint, secondsTilFadeout)
        except:
            try:
                _, entityGroupID, message, hint = p.Parse('siss')
                sm.GetService('uiHighlightingService').highlight_space_object_by_dungeon_entity_group_id(entityGroupID, message, hint)
            except:
                raise UserError('SlashError', {'reason': 'Usage: /highlight entitygroup entityGroupID message, hint, [secondsTilFadeout]'})

        return 'Ok'

    def _cmd_highlighttype(self, p):
        try:
            __, typeID, message, hint, secondsTilFadeout = p.Parse('sissi')
            sm.GetService('uiHighlightingService').highlight_space_object_by_type(typeID, message, hint, secondsTilFadeout)
        except:
            try:
                _, typeID, message, hint = p.Parse('siss')
                sm.GetService('uiHighlightingService').highlight_space_object_by_type(typeID, message, hint)
            except:
                raise UserError('SlashError', {'reason': 'Usage: /highlight type typeID message, hint, [secondsTilFadeout]'})

        return 'Ok'

    def _cmd_highlightgroup(self, p):
        try:
            _, groupID, message, hint, secondsTilFadeout = p.Parse('sissi')
            sm.GetService('uiHighlightingService').highlight_space_object_by_group(groupID, message, hint, secondsTilFadeout)
        except:
            try:
                _, groupID, message, hint = p.Parse('siss')
                sm.GetService('uiHighlightingService').highlight_space_object_by_group(groupID, message, hint)
            except:
                raise UserError('SlashError', {'reason': 'Usage: /highlight group groupID message, hint, [secondsTilFadeout]'})

        return 'Ok'

    def _cmd_highlightspaceobject(self, p):
        try:
            _, highlight_id = p.Parse('si')
        except:
            raise UserError('SlashError', {'reason': 'Usage: /highlight spaceobject highlight_id'})

        sm.GetService('uiHighlightingService').highlight_space_object(highlight_id)
        return 'Ok'

    def _cmd_highlightclear(self, p):
        cmd_option, clear_option = p.Parse('ss')
        if clear_option == 'ui':
            return self._cmd_highlightclearui(p)
        if clear_option == 'menu':
            return self._cmd_highlightclearmenu(p)
        if clear_option == 'space':
            return self._cmd_highlightclearspace(p)
        if clear_option == 'all':
            return self._cmd_highlightclearall(p)
        self._cmd_highlightError()

    def _cmd_highlightclearui(self, p):
        sm.GetService('uiHighlightingService').clear_ui_element_highlighting()
        return 'Ok'

    def _cmd_highlightclearspace(self, p):
        sm.GetService('uiHighlightingService').clear_space_object_highlighting()
        return 'Ok'

    def _cmd_highlightclearmenu(self, p):
        sm.GetService('uiHighlightingService').clear_menu_highlighting()
        return 'Ok'

    def _cmd_highlightclearall(self, p):
        sm.GetService('uiHighlightingService').clear_all_highlighting()
        return 'Ok'

    def cmd_uiblink(self, p):
        try:
            cmd_option, _ = p.Parse('s?r')
        except:
            self._cmd_uiBlinkError()

        if cmd_option == 'start':
            return self._cmd_uiblinkBlink(p)
        if cmd_option == 'stop':
            return self._cmd_uiblinkClear(p)
        self._cmd_uiBlinkError()

    def _cmd_uiBlinkError(self):
        raise UserError('SlashError', {'reason': 'Available options:\n/uiblink start {path}\n/uiblink stop {path}\n/uiblink stop all\n'})

    def _cmd_uiblinkBlink(self, p):
        try:
            cmd_option, ui_element_path = p.Parse('ss')
        except Exception:
            self._cmd_uiBlinkError()
        else:
            uiblinker.get_service().start_blinker_by_path(ui_element_path)
            return 'OK'

    def _cmd_uiblinkClear(self, p):
        try:
            cmd_option, ui_element_path = p.Parse('ss')
        except Exception:
            self._cmd_uiBlinkError()
        else:
            if 'all' == ui_element_path:
                uiblinker.get_service().stop_all_blinkers()
            else:
                uiblinker.get_service().stop_blinker_by_path(ui_element_path)

        return 'OK'

    def cmd_networth(self, p):
        try:
            cmd_option, _ = p.Parse('s?r')
        except:
            self._cmd_networthError()

        resultString = None
        if cmd_option == 'total':
            resultString = self._cmd_networthtotal()
        elif cmd_option == 'wallet':
            resultString = self._cmd_networthwallet()
        elif cmd_option == 'assets':
            resultString = self._cmd_networthassets()
        elif cmd_option == 'contract':
            resultString = self._cmd_networthcontract()
        elif cmd_option == 'market':
            resultString = self._cmd_networthmarket()
        elif cmd_option == 'plex':
            resultString = self._cmd_networthplex()
        if resultString:
            self._cmd_networthResults(resultString)
            return 'Ok'
        self._cmd_networthError()

    def _cmd_networthError(self):
        raise UserError('SlashError', {'reason': 'Available options:\n/networth total\n/networth wallet\n/networth assets\n/networth plex\n/networth contract\n/networth market\n'})

    def _cmd_networthResults(self, string):
        Message('Net Worth Results', string)

    def _cmd_networthtotal(self):
        wallet = self._GetNetWorthWallet()
        iskInContractEscrow, itemsInContractEscrow = self._GetNetWorthContracts()
        iskInMarketEscrow, itemsInMarketEscrow = self._GetNetWorthMarket()
        assets, assetsPlex = self._GetNetWorthAssets()
        accountPlex = self._GetNetWorthAccountPlex()
        combinedAssets = itemsInContractEscrow + itemsInMarketEscrow + assets
        totalPlex = assetsPlex + accountPlex
        total = wallet + iskInMarketEscrow + iskInContractEscrow + combinedAssets + totalPlex
        return '<b>Total Net Worth:</b> {:0,.0f} ISK:<br/><b> - Wallet:</b> {:0,.0f} ISK<br/><b> - Combined assets:</b> {:0,.0f} ISK<br/><b> - PLEX:</b> {:0,.0f} ISK<br/><b> - Contracts:</b> {:0,.0f} ISK<br/><b> - Market orders:</b> {:0,.0f} ISK'.format(total, wallet, combinedAssets, totalPlex, iskInContractEscrow, iskInMarketEscrow)

    def _cmd_networthwallet(self):
        wallet = self._GetNetWorthWallet()
        return '<b>Wallet Balance:</b> {:0,.0f} ISK'.format(wallet)

    def _cmd_networthassets(self):
        _, itemsInContractEscrow = self._GetNetWorthContracts()
        _, itemsInMarketEscrow = self._GetNetWorthMarket()
        assets, _ = self._GetNetWorthAssets()
        total = itemsInContractEscrow + itemsInMarketEscrow + assets
        return '<b>Combined Asset Net Worth:</b> {:0,.0f} ISK:<br/><b> - Assets:</b> {:0,.0f} ISK<br/><b> - Contracts:</b> {:0,.0f} ISK<br/><b> - Market orders:</b> {:0,.0f} ISK'.format(total, assets, itemsInContractEscrow, itemsInMarketEscrow)

    def _cmd_networthcontract(self):
        iskInContractEscrow, _ = self._GetNetWorthContracts()
        return '<b>Contract Escrow:</b> {:0,.0f} ISK'.format(iskInContractEscrow)

    def _cmd_networthmarket(self):
        iskInMarketEscrow, _ = self._GetNetWorthMarket()
        return '<b>Market Escrow:</b> {:0,.0f} ISK'.format(iskInMarketEscrow)

    def _cmd_networthplex(self):
        _, assetsPlex = self._GetNetWorthAssets()
        accountPlex = self._GetNetWorthAccountPlex()
        totalPlex = assetsPlex + accountPlex
        return '<b>PLEX Estimated Value:</b> {:0,.0f} ISK<br/><b>- PLEX in assets:</b> {:0,.0f} ISK<br/><b>- PLEX in Plex Vault:</b> {:0,.0f} ISK'.format(totalPlex, assetsPlex, accountPlex)

    def _GetNetWorthWallet(self):
        return sm.GetService('wallet').GetWealth()

    def _GetNetWorthAssets(self):
        invContainer = sm.GetService('invCache').GetInventory(const.containerGlobal)
        assets, assetsPlex = invContainer.GetAssetWorth()
        return (assets, assetsPlex)

    def _GetNetWorthMarket(self):
        iskInMarketEscrow, itemsInMarketEscrow = sm.GetService('marketQuote').GetMyMarketEscrow()
        return (iskInMarketEscrow, itemsInMarketEscrow)

    def _GetNetWorthContracts(self):
        iskInContractEscrow, itemsInContractEscrow = sm.GetService('contracts').GetMyContractEscrow()
        return (iskInContractEscrow, itemsInContractEscrow)

    def _GetNetWorthAccountPlex(self):
        account = sm.GetService('vgsService').GetStore().GetAccount()
        plex_amount = account.GetAurumBalance() or 0.0
        plex_price = GetAveragePrice(typePlex) or 0.0
        plex_worth = plex_amount * plex_price
        return plex_worth

    def cmd_asteroid(self, p):
        try:
            cmd_option, _ = p.Parse('s?r')
        except:
            self._cmd_asteroidError()

        if cmd_option == 'highlight':
            return self._cmd_asteroid_highlight(p)
        if cmd_option == 'clear':
            return self._cmd_asteroid_clear_highlight(p)
        if cmd_option == 'rewards':
            return self._cmd_asteroid_list_rewards()
        self._cmd_asteroidError()

    def _cmd_asteroidError(self):
        raise UserError('SlashError', {'reason': 'Available options:\n/asteroid rewards\n/asteroid highlight {asteroidID}\n/asteroid clear {asteroidID}'})

    def _cmd_asteroid_list_rewards(self):
        sm.RemoteSvc('slash').SlashCmd('/asteroid rewards')
        return 'Ok'

    def _cmd_asteroid_highlight(self, p):
        try:
            __, asteroidID = p.Parse('si')
            sm.GetService('dungeonTracking').OnAsteroidRevealed(asteroidID)
        except:
            raise UserError('SlashError', {'reason': 'Usage: /asteroid highlight {asteroidID}'})

        return 'Ok'

    def _cmd_asteroid_clear_highlight(self, p):
        try:
            __, asteroidID = p.Parse('si')
            sm.GetService('dungeonTracking').OnAsteroidTerminated(asteroidID)
        except:
            raise UserError('SlashError', {'reason': 'Usage: /asteroid clear {asteroidID}'})

        return 'Ok'

    def cmd_intro(self, p):
        try:
            cmd_option, _ = p.Parse('s?r')
        except:
            self._cmd_introError()
            return

        if cmd_option in ('start', 'stop', 'terminate'):
            return
        self._cmd_introError()

    def _cmd_introError(self):
        raise UserError('SlashError', {'reason': 'Available options:\n/intro start\n/intro stop\n/intro terminate\n/intro free'})

    def MatchTypes(self, name, allowedCategories = None, allowedGroups = None, smart = True):
        name = name.strip('"')
        self._PopulateTypeDict()

        def _filter(typeID):
            if allowedCategories:
                if evetypes.GetCategoryID(typeID) in allowedCategories:
                    return True
                if allowedGroups:
                    if evetypes.GetGroupID(typeID) in allowedGroups:
                        return True
            elif allowedGroups:
                if evetypes.GetGroupID(typeID) in allowedGroups:
                    return True
            else:
                return True
            return False

        if smart and name.lower() in self.typeIDsByName:
            typeIDs = self.typeIDsByName[name.lower()]
            return [ (evetypes.GetName(typeID), typeID) for typeID in typeIDs ]
        if name.isdigit():
            typeName = evetypes.GetNameOrNone(int(name))
            if typeName:
                return [(typeName, int(name))]
        else:
            name = name.lower().strip('"')
        if len(name) < 3:
            raise UserError('SlashError', {'reason': 'Autocompletion requires 3 or more characters'})
        matches = []
        for typeName, typeIDs in self.typeIDsByName.iteritems():
            if name in typeName:
                for typeID in typeIDs:
                    if _filter(typeID):
                        matches.append((evetypes.GetName(typeID), typeID))

        return matches

    def _PopulateTypeDict(self):
        if self.typeIDsByName is not None:
            return
        d = defaultdict(list)
        noOfExceptions = 0
        optic_locale = localization.const.LOCALE_SHORT_CHINESE
        for typeID in evetypes.Iterate():
            blue.pyos.BeNice()
            try:
                if boot.region == 'optic':
                    if evetypes.GetNameID(typeID) is not None:
                        d[evetypes.GetName(typeID, optic_locale).lower()].append(typeID)
                else:
                    englishName = evetypes.GetEnglishName(typeID)
                    if englishName is not None:
                        d[englishName.lower()].append(typeID)
            except Exception:
                if noOfExceptions == 0:
                    log.LogException('Unexpected Exception in _PopulateTypeDict')
                noOfExceptions += 1
                sys.exc_clear()

        if noOfExceptions > 0:
            self.LogError('_PopulateTypeDict failed', noOfExceptions, 'times getting the typeName')
        self.typeIDsByName = d

    def AutoComplete(self, name, allowedCategories = None, allowedGroups = None):
        matches = self.MatchTypes(name, allowedCategories, allowedGroups)
        if not matches:
            return None
        if len(matches) == 1:
            ret = matches[0]
        else:
            matches.sort()
            ret = uix.ListWnd(matches, listtype='generic', caption='AutoComplete: %d types found' % len(matches))
        if not ret:
            raise Error('Cancelled')
        return ret[1]

    def GetChannel(self):
        log.LogTraceback('PAT: SlashService.GetChannel called')
        f = sys._getframe().f_back
        while f:
            logger.debug('PAT: f=%s', f)
            loc = f.f_locals
            logger.debug('PAT: loc=%s', loc)
            if loc.has_key('self'):
                target = loc['self']
                logger.debug('PAT: target=%s', target)
                from packages.xmppchatclient.xmppchatwindow import XmppChatWindow
                if isinstance(target, XmppChatWindow):
                    logger.debug('PAT: Found XmppChatWindow target instance: %s', target)
                    return target
            f = f.f_back

        raise Error('This function can only be used in a chat channel')

    def GetChannelUsers(self):
        c = self.GetChannel()
        return [ each.charID for each in c.userlist.sr.nodes ]


exports = {'slash.Error': Error}
