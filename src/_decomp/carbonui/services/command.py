#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\services\command.py
import sys
import blue
import bluepy
import carbon.client.script.sys.appUtils as appUtils
import carbonui.const as uiconst
import localization
import log
import trinity
import uthread
from carbon.common.script.sys.service import Service
from carbonui.control.contextMenu.menuUtil import CloseContextMenus
from carbonui.control.window import Window
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetClipboardData
from eve.devtools.script.enginetools import EngineToolsLauncher
from eveprefs import boot
from jobboard.client import job_board_signals
from threadutils import throttled
NUMPAD_KEYS = []
for num in range(0, 10):
    NUMPAD_KEYS.append(getattr(uiconst, 'VK_NUMPAD%s' % num, num + 96))

VK_KEYS = [ key for key in dir(uiconst) if key.startswith('VK_') ]
RENAMEMAP = {'CONTROL': 'CTRL',
 'MENU': 'ALT',
 'MBUTTON': 'MOUSE3',
 'XBUTTON1': 'MOUSE4',
 'XBUTTON2': 'MOUSE5',
 'SNAPSHOT': 'PRINTSCREEN',
 'NEXT': 'PAGEDOWN',
 'PRIOR': 'PAGEUP'}
labelsByFuncName = {'CmdCloseActiveWindow': '/Carbon/UI/Commands/CmdCloseActiveWindow',
 'CmdCloseAllWindows': '/Carbon/UI/Commands/CmdCloseAllWindows',
 'CmdLogOff': 'UI/Commands/CmdLogOff',
 'CmdMinimizeActiveWindow': '/Carbon/UI/Commands/CmdMinimizeActiveWindow',
 'CmdToggleMinimizeMaximizeAllWindows': '/Carbon/UI/Commands/CmdMinimizeAllWindows',
 'CmdToggleCollapseAllWindows': '/Carbon/UI/Commands/ToggleCollapseAllWindows',
 'CmdQuitGame': 'UI/Commands/CmdQuitGame',
 'CmdResetMonitor': '/Carbon/UI/Commands/CmdResetMonitor',
 'CmdToggleAudio': '/Carbon/UI/Commands/CmdToggleAudio',
 'OnCtrlA': '/Carbon/UI/Commands/OnCtrlA',
 'OnCtrlC': '/Carbon/UI/Commands/OnCtrlC',
 'OnCtrlShiftTab': '/Carbon/UI/Commands/OnCtrlShiftTab',
 'OnCtrlTab': '/Carbon/UI/Commands/OnCtrlTab',
 'OnCtrlV': '/Carbon/UI/Commands/OnCtrlV',
 'OnCtrlX': '/Carbon/UI/Commands/OnCtrlX',
 'OnEsc': '/Carbon/UI/Commands/OnEsc',
 'OnReturn': '/Carbon/UI/Commands/OnReturn',
 'OnShiftTab': '/Carbon/UI/Commands/OnShiftTab',
 'OnTab': '/Carbon/UI/Commands/OnTab',
 'OpenMonitor': '/Carbon/UI/Commands/OpenMonitor',
 'PrintScreen': '/Carbon/UI/Commands/PrintScreen',
 'WinCmdToggleWindowed': '/Carbon/UI/Commands/WinCmdToggleWindowed',
 'CmdBack': '/Carbon/UI/Commands/Back',
 'CmdForward': '/Carbon/UI/Commands/Forward'}

def GetKeyName(key):
    import trinity
    newKey = trinity.app.GetKeyNameText(key)
    if not newKey:
        newKey = ', '.join([ each[3:] for each in VK_KEYS if getattr(uiconst, each) == key ])
        newKey = RENAMEMAP.get(newKey, newKey)
    return newKey


class CommandMapping:

    def __init__(self, callback, shortcut, category = None, isLocked = False, enabled = True, ignoreModifierKey = False, repeatable = False, hintPath = None):
        self.callback = callback
        self.name = self.callback.func_name
        self.SetShortcut(shortcut)
        self.category = category or 'general'
        self.isLocked = isLocked
        self.ignoreModifierKey = ignoreModifierKey
        self.repeatable = repeatable
        self.hint = hintPath

    def __repr__(self):
        return "<CommandMapping instance -  name='%s', shortcut='%s', callback=%s>" % (self.name, self.shortcut, self.callback)

    def GetShortcutAsString(self):
        if not self.shortcut:
            return ''
        retString = uicore.cmd.GetStringFromShortcutKeys(self.shortcut)
        return retString

    def GetDescription(self):
        if hasattr(self.callback, 'nameLabelPath'):
            return localization.GetByLabel(self.callback.nameLabelPath)
        if getattr(self.callback, 'nameString', None):
            return self.callback.nameString
        return uicore.cmd.FuncToDesc(self.name)

    def GetName(self):
        if getattr(self.callback, 'nameLabelPath', None):
            return localization.GetByLabel(self.callback.nameLabelPath)
        if getattr(self.callback, 'nameString', None):
            return self.callback.nameString

    def GetDetailedDescription(self):
        if hasattr(self.callback, 'detailedDescription'):
            return localization.GetByLabel(self.callback.detailedDescription)
        if getattr(self.callback, 'descriptionLabelPath', None):
            return localization.GetByLabel(self.callback.descriptionLabelPath)
        if getattr(self.callback, 'descriptionString', None):
            return self.callback.descriptionString
        if getattr(self.callback, 'descriptionFunc', None):
            return self.callback.descriptionFunc()

    def SetShortcut(self, shortcut):
        self.shortcut = self._ValidateShortcut(shortcut)

    def _ValidateShortcut(self, shortcut):
        if shortcut is None:
            return
        if type(shortcut) is int:
            shortcut = (shortcut,)
        return shortcut

    def GetAccelerator(self):
        if not self.shortcut:
            return None
        vkey = self.shortcut[-1]
        shortcutModKeys = self.shortcut[:-1]
        modKeys = []
        for modKey in uiconst.MODKEYS:
            modKeys.append(modKey in shortcutModKeys)

        return (tuple(modKeys), vkey)


class CommandMap:

    def __init__(self, defaultCmds = [], customCmds = {}):
        self.commandsByName = {}
        self.commandsByShortcut = {}
        self.accelerators = {}
        self.customCmds = customCmds
        for c in defaultCmds:
            self.AddCommand(c)

    def HasCommand(self, commandName):
        return commandName in self.commandsByName

    def AddCommand(self, command):
        for shortcut in self.customCmds.itervalues():
            if command.shortcut == shortcut:
                command.shortcut = None

        if command.name in self.customCmds:
            command.shortcut = self.customCmds[command.name]
            command.shortcut = self._ModernizeOldTypeShortcut(command.shortcut)
        if self.GetCommandByName(command.name) is None:
            self.commandsByName[command.name] = command
            if command.shortcut is not None:
                self.commandsByShortcut[command.shortcut] = command
        else:
            log.LogWarn('Trying to add the same command twice: %s' % command.name)

    def RemoveCommand(self, command):
        if command and self.GetCommandByName(command.name):
            del self.commandsByName[command.name]
            if command.shortcut is not None:
                del self.commandsByShortcut[command.shortcut]

    def RemapCommand(self, cmdname, newShortcut = None):
        if newShortcut:
            newShortcut = tuple(newShortcut)
        cmd = self.GetCommandByName(cmdname)
        self.UnloadAccelerator(cmd)
        oldShortcut = cmd.shortcut
        if oldShortcut and oldShortcut in self.commandsByShortcut:
            self.commandsByShortcut.pop(tuple(cmd.shortcut))
        self.customCmds[cmdname] = newShortcut
        if newShortcut:
            self.commandsByShortcut[newShortcut] = cmd
        settings.user.cmd.customCmds[cmdname] = newShortcut
        cmd.SetShortcut(newShortcut)
        self.LoadAccelerator(cmd)

    def _ModernizeOldTypeShortcut(self, shortcut):
        if not shortcut or len(shortcut) != 4:
            return shortcut
        for i in xrange(3):
            if shortcut[i] not in (0, 1):
                return shortcut

        newShortcut = []
        if shortcut[0]:
            newShortcut.append(uiconst.VK_CONTROL)
        if shortcut[1]:
            newShortcut.append(uiconst.VK_MENU)
        if shortcut[2]:
            newShortcut.append(uiconst.VK_SHIFT)
        try:
            vkKey = getattr(uiconst, 'VK_%s' % shortcut[-1].upper())
        except:
            return None

        newShortcut.append(vkKey)
        return tuple(newShortcut)

    def GetAllCommands(self):
        return self.commandsByName.values()

    def Reset(self):
        self.UnloadAccelerators()

    def GetAllUnmappedCommands(self):
        retCmds = []
        for c in self.commandsByName.values():
            if c.shortcut is None:
                retCmds.append(c)

        return retCmds

    def GetAllMappedCommands(self):
        retCmds = []
        for c in self.commandsByName.values():
            if c.shortcut is not None:
                retCmds.append(c)

        return retCmds

    def GetCommandByShortcut(self, shortcut):
        return self.commandsByShortcut.get(shortcut)

    def GetCommandByName(self, cmdname):
        return self.commandsByName.get(cmdname)

    def GetCommandCategoryNames(self):
        categories = []
        for c in self.GetAllCommands():
            if c.category not in categories:
                categories.append(c.category)

        return categories

    def UnloadAcceleratorsByCategory(self, category):
        for cmd in self.commandsByName.values():
            if cmd.category == category:
                self.UnloadAccelerator(cmd)

    def LoadAcceleratorsByCategory(self, category):
        for cmd in self.commandsByName.values():
            if cmd.category == category:
                self.LoadAccelerator(cmd)

    def LoadAccelerator(self, cmd):
        accelerator = cmd.GetAccelerator()
        if accelerator is None:
            return
        self.accelerators[accelerator] = cmd

    def UnloadAccelerator(self, cmd):
        accelerator = cmd.GetAccelerator()
        if accelerator is None or accelerator not in self.accelerators:
            return
        del self.accelerators[accelerator]

    def LoadAllAccelerators(self):
        for c in self.GetAllCommands():
            self.LoadAccelerator(c)

    def UnloadAllAccelerators(self):
        for c in self.commandsByName.values():
            self.UnloadAccelerator(c)


class CommandService(Service):
    __guid__ = 'svc.cmd'
    __update_on_reload__ = 1
    __startupdependencies__ = ['settings']
    __notifyevents__ = ['OnSessionChanged']

    def Run(self, memStream = None):
        super(CommandService, self).Run(memStream)
        self.labelsByFuncName = labelsByFuncName
        self.Reload()
        job_board_signals.on_job_board_feature_availability_changed.connect(self.OnJobBoardAvailabilityChanged)
        job_board_signals.on_missions_feature_availability_changed.connect(self.OnJobBoardAvailabilityChanged)

    def Reload(self, forceGenericOnly = False):
        self.settings.LoadSettings()
        if not settings.user.cmd.customCmds:
            settings.user.cmd.customCmds = {}
        self.defaultShortcutMapping = self.SetDefaultShortcutMappingCORE()
        self.defaultShortcutMapping.extend(self.SetDefaultShortcutMappingGAME())
        self.CheckDuplicateShortcuts()
        if hasattr(self, 'commandMap'):
            self.commandMap.UnloadAllAccelerators()
        self.commandMap = CommandMap(defaultCmds=self.defaultShortcutMapping, customCmds=settings.user.cmd.customCmds)
        if session.charid is not None and forceGenericOnly is False:
            self.commandMap.LoadAllAccelerators()
        else:
            self.commandMap.LoadAcceleratorsByCategory('general')

    def Stop(self, memStream):
        super(CommandService, self).Stop(memStream)

    @throttled(1.0)
    def OnJobBoardAvailabilityChanged(self, _oldValue, _newValue):
        self.Reload()

    def CheckDuplicateShortcuts(self):
        for cmd in self.defaultShortcutMapping:
            for cmdCheck in self.defaultShortcutMapping:
                if cmdCheck.shortcut:
                    sameName = cmdCheck.name == cmd.name
                    sameShortcut = cmdCheck.shortcut == cmd.shortcut
                    if sameShortcut and not sameName:
                        self.LogError('Same default shortcut used for multiple commands:', cmd)

    def OnSessionChanged(self, isRemote, sess, change):
        if 'userid' in change:
            self.Reload()
        if 'charid' in change:
            self.commandMap.LoadAllAccelerators()

    def SetDefaultShortcutMappingCORE(self):
        ret = []
        c = CommandMapping
        CTRL = uiconst.VK_CONTROL
        ALT = uiconst.VK_MENU
        SHIFT = uiconst.VK_SHIFT
        COMMAND = uiconst.VK_LWIN

        def k(win, mac):
            if sys.platform.startswith('darwin'):
                return mac
            return win

        m = [c(self.OnReturn, uiconst.VK_RETURN),
         c(self.OnCtrlA, (k(win=CTRL, mac=COMMAND), uiconst.VK_A)),
         c(self.OnCtrlC, (k(win=CTRL, mac=COMMAND), uiconst.VK_C)),
         c(self.OnCtrlX, (k(win=CTRL, mac=COMMAND), uiconst.VK_X)),
         c(self.OnCtrlV, (k(win=CTRL, mac=COMMAND), uiconst.VK_V)),
         c(self.OnEsc, uiconst.VK_ESCAPE),
         c(self.OnCtrlShiftTab, (CTRL, SHIFT, uiconst.VK_TAB)),
         c(self.OnCtrlTab, (CTRL, uiconst.VK_TAB)),
         c(self.OnTab, uiconst.VK_TAB),
         c(self.OnShiftTab, (SHIFT, uiconst.VK_TAB))]
        for cm in m:
            cm.category = 'general'
            cm.isLocked = True
            ret.append(cm)

        m = [c(self.CmdQuitGame, (ALT, SHIFT, uiconst.VK_Q)),
         c(self.CmdLogOff, None),
         c(self.CmdToggleAudio, (CTRL,
          ALT,
          SHIFT,
          uiconst.VK_F12)),
         c(self.WinCmdToggleWindowed, (ALT, uiconst.VK_RETURN)),
         c(self.CmdResetMonitor, (CTRL, ALT, uiconst.VK_RETURN)),
         c(self.OpenMonitor, (CTRL,
          ALT,
          SHIFT,
          uiconst.VK_M)),
         c(self.CmdBack, uiconst.VK_XBUTTON1),
         c(self.CmdForward, uiconst.VK_XBUTTON2)]
        if sys.platform.startswith('darwin'):
            m.append(c(self.PrintScreen, (CTRL, uiconst.VK_P)))
        else:
            m.append(c(self.PrintScreen, uiconst.VK_SNAPSHOT))
        for cm in m:
            cm.category = 'general'
            ret.append(cm)

        m = [c(self.CmdCloseAllWindows, (CTRL, ALT, uiconst.VK_W)),
         c(self.CmdToggleMinimizeMaximizeAllWindows, None),
         c(self.CmdMinimizeActiveWindow, None),
         c(self.CmdCloseActiveWindow, (CTRL, uiconst.VK_W)),
         c(self.CmdToggleCollapseAllWindows, None)]
        for cm in m:
            cm.category = 'window'
            ret.append(cm)

        return ret

    def SetDefaultShortcutMappingGAME(self):
        return []

    def EditCmd(self, cmdname, context = None):
        if self.IsLocked(cmdname):
            uicore.Message('ShortcutLocked')
            return
        command = self.commandMap.GetCommandByName(cmdname)
        self.MapCmd(cmdname, context)

    def MapCmd(self, *args, **kwds):
        pass

    def CheckKeyDown(self, edit, vkey, flag):
        if vkey == uiconst.VK_RETURN:
            return
        edit.SetValue(self.GetKeyNameFromVK(vkey))

    def MapCmdErrorCheck(self, retval):
        return ''

    def ClearMappedCmd(self, cmdname, showMsg = 1):
        if self.IsLocked(cmdname):
            if showMsg:
                uicore.Message('ShortcutLocked')
            return
        self.commandMap.RemapCommand(cmdname, None)
        sm.ScatterEvent('OnMapShortcut', cmdname, None, None, None, None)

    def RestoreDefaults(self):
        settings.user.cmd.customCmds = {}
        self.Reload()
        sm.ScatterEvent('OnRestoreDefaultShortcuts')

    def IsLocked(self, cmdname):
        command = self.commandMap.GetCommandByName(cmdname)
        if command and command.isLocked:
            return True
        else:
            return False

    def IsTaken(self, cmdname):
        return self.GetFuncByShortcut(cmdname) is None

    def MapKeys(self, VK):
        if VK in NUMPAD_KEYS:
            num = NUMPAD_KEYS.index(VK)
            VK = getattr(uiconst, 'VK_%s' % num)
        return VK

    def GetCommandCategoryNames(self):
        return self.commandMap.GetCommandCategoryNames()

    def GetKeyNameFromVK(self, VK):
        VK = self.MapKeys(VK)
        return ', '.join([ each[3:] for each in VK_KEYS if getattr(uiconst, each) == VK ])

    def GetVKFromChar(self, char):
        return [ each for each in VK_KEYS if unichr(getattr(uiconst, each)) == char ]

    def GetFuncByShortcut(self, shortcut):
        command = self.commandMap.GetCommandByShortcut(shortcut)
        if command:
            return command.name
        else:
            return None

    def GetShortcutByFuncName(self, funcname, format = False):
        command = self.commandMap.GetCommandByName(funcname)
        if command:
            if format:
                return command.GetShortcutAsString()
            else:
                return command.shortcut
        else:
            return None

    def GetShortcutStringByFuncName(self, funcname):
        command = self.commandMap.GetCommandByName(funcname)
        if command:
            return command.GetShortcutAsString()
        else:
            return ''

    def GetShortcutByString(self, stringfunc):
        command = self.commandMap.GetCommandByName(stringfunc)
        if command and command.shortcut:
            return command.GetShortcutAsString()
        else:
            return None

    def UnpackFuncName(self, funcname):
        nameSpace, className, funcname = funcname.split('.')
        return funcname

    def FuncToDesc(self, funcname):
        if funcname in self.labelsByFuncName:
            return localization.GetByLabel(self.labelsByFuncName[funcname])
        try:
            myCmd = self.commandMap.GetCommandByName(funcname)
            if myCmd and myCmd.callback and getattr(myCmd.callback, 'nameLabelPath', None):
                return localization.GetByLabel(myCmd.callback.nameLabelPath)
        except StandardError:
            pass

        return funcname

    def GetFuncName(self, cmdname):
        cmdname = cmdname.lower().strip()
        for letter in ('_', ' '):
            while cmdname.find(letter * 2) >= 0:
                cmdname = cmdname.replace(letter * 2, letter)

            _cmdname = cmdname.split(letter)
            cmdname = ''
            for part in _cmdname:
                cmdname += '%s%s' % (part[0].upper(), part[1:])

        return cmdname

    def GetActiveCmds(self):
        return self.commandMap.GetAllMappedCommands()

    def GetUnmappedCmds(self):
        return self.commandMap.GetAllUnmappedCommands()

    def GetCustomCmd(self, cmdname):
        return self.customCmds.get(cmdname, None)

    def Execute(self, cmdname, cmdNameExact = False):
        if not cmdNameExact:
            cmdname = cmdname.lower()
            if cmdname[0] == '/':
                cmdname = cmdname[1:]
            funcName = self.GetFuncName(cmdname)
        else:
            funcName = cmdname
        print 'execute', funcName
        func = getattr(self, funcName, None)
        if func is not None:
            try:
                apply(func)
                return '%s executed' % cmdname
            except:
                pass

    def CheckCtrlUp(self, wnd, msgID, ckey):
        chooseWndMenu = getattr(self, 'chooseWndMenu', None)
        if chooseWndMenu and not chooseWndMenu.destroyed and chooseWndMenu.state != uiconst.UI_HIDDEN:
            chooseWndMenu.ChooseHilited()
        self.chooseWndMenu = None
        return 1

    def _AppQuitGame(self):
        bluepy.Terminate(0, 'User requesting close')

    def CmdQuitGame(self):
        if uicore.Message('AskQuitGame', {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
            self.settings.SaveSettings()
            self._AppQuitGame()

    def CmdLogOff(self):
        if uicore.Message('AskLogoffGame', {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
            appUtils.Reboot('Generic Logoff')

    def CmdToggleAudio(self):
        settings.public.audio.Set('audioEnabled', not settings.public.audio.Get('audioEnabled', 1))
        if settings.public.audio.audioEnabled:
            uicore.audioHandler.Activate()
        else:
            uicore.audioHandler.Deactivate()
        return True

    def WinCmdToggleWindowed(self):
        uicore.device.ToggleWindowed()
        return True

    def CmdCloseAllWindows(self):
        for wnd in uicore.registry.GetWindows()[:]:
            if not uicore.registry.IsWindow(wnd):
                continue
            if wnd.IsKillable():
                if hasattr(wnd, 'CloseByUser'):
                    wnd.CloseByUser()
                else:
                    try:
                        wnd.Close()
                    except:
                        log.LogException()

            elif not wnd.InStack():
                wnd.Minimize()

        return True

    def CmdMinimizeAllWindows(self):
        wnds = uicore.registry.GetValidWindows()
        for wnd in wnds:
            if wnd.InStack() or wnd.align == uiconst.TOALL:
                continue
            uthread.new(wnd.Minimize)

        return True

    def CmdMaximizeAllWindows(self):
        for wnd in uicore.registry.GetWindows():
            if wnd.InStack():
                continue
            uthread.new(wnd.Maximize)

    def CmdToggleMinimizeMaximizeAllWindows(self):
        wnds = uicore.registry.GetValidWindows()
        if False in [ w.IsMinimized() for w in wnds ]:
            self.CmdMinimizeAllWindows()
        else:
            self.CmdMaximizeAllWindows()

    def CmdMinimizeActiveWindow(self):
        activeWnd = uicore.registry.GetActiveStackOrWindow()
        if activeWnd:
            if activeWnd.align == uiconst.TOALL or not hasattr(activeWnd, 'Minimize'):
                return
            activeWnd.Minimize()
            return True

    def CmdToggleCollapseAllWindows(self):
        uicore.registry.ToggleCollapseAllWindows()

    def CmdCloseActiveWindow(self):
        activeWnd = uicore.registry.GetActive()
        if not isinstance(activeWnd, Window):
            return
        if activeWnd and getattr(activeWnd, 'canCloseActiveWnd', 1):
            if hasattr(activeWnd, 'CloseByUser'):
                activeWnd.CloseByUser()
                return True
            if hasattr(activeWnd, 'Close'):
                activeWnd.Close()
                return True

    def CmdResetMonitor(self):
        uicore.device.ResetMonitor()
        return True

    def OnUp(self):
        fa = uicore.registry.GetFocus() or uicore.registry.GetActive()
        if fa and hasattr(fa, 'OnUp'):
            uthread.pool('commandSvc::OnKey OnUp', fa.OnUp)

    def OnDown(self):
        fa = uicore.registry.GetFocus() or uicore.registry.GetActive()
        if fa and hasattr(fa, 'OnDown'):
            uthread.pool('commandSvc::OnKey OnDown', fa.OnDown)

    def OnLeft(self):
        fa = uicore.registry.GetFocus() or uicore.registry.GetActive()
        if fa and hasattr(fa, 'OnLeft'):
            uthread.pool('commandSvc::OnKey OnLeft', fa.OnLeft)

    def OnRight(self):
        fa = uicore.registry.GetFocus() or uicore.registry.GetActive()
        if fa and hasattr(fa, 'OnRight'):
            uthread.pool('commandSvc::OnKey OnRight', fa.OnRight)

    def OnHome(self):
        fa = uicore.registry.GetFocus() or uicore.registry.GetActive()
        if fa and hasattr(fa, 'OnHome'):
            uthread.pool('commandSvc::OnKey OnHome', fa.OnHome)

    def OnEnd(self):
        fa = uicore.registry.GetFocus() or uicore.registry.GetActive()
        if fa and hasattr(fa, 'OnEnd'):
            uthread.pool('commandSvc::OnKey OnEnd', fa.OnEnd)

    def OnShiftTab(self):
        self.OnTab()

    def OnTab(self):
        oldfoc = uicore.registry.GetFocus()
        if oldfoc is None or oldfoc == uicore.desktop:
            uicore.registry.ToggleCollapseAllWindows()
        else:
            uicore.registry.FindFocus([1, -1][uicore.uilib.Key(uiconst.VK_SHIFT)])

    def CmdBack(self):
        activeWnd = uicore.registry.GetActive()
        focus = uicore.registry.GetFocus()
        if activeWnd and isinstance(activeWnd, Window) and hasattr(activeWnd, 'OnBack'):
            activeWnd.OnBack()
        elif focus:
            while focus.parent:
                if hasattr(focus, 'OnBack'):
                    focus.OnBack()
                focus = focus.parent

    def CmdForward(self):
        activeWnd = uicore.registry.GetActive()
        focus = uicore.registry.GetFocus()
        if activeWnd and isinstance(activeWnd, Window) and hasattr(activeWnd, 'OnForward'):
            activeWnd.OnForward()
        elif focus and hasattr(focus, 'OnForward'):
            focus.OnForward()

    def OnReturn(self):
        uicore.registry.Confirm()

    def OnCtrlA(self):
        focus = uicore.registry.GetFocus()
        if focus and hasattr(focus, 'SelectAll'):
            focus.SelectAll()
            return True
        active = uicore.registry.GetActive()
        if active and hasattr(active, 'SelectAll'):
            active.SelectAll()
            return True

    def OnCtrlC(self):
        focus = uicore.registry.GetFocus()
        if getattr(focus, 'Copy', None):
            return focus.Copy()

    def OnCtrlX(self):
        focus = uicore.registry.GetFocus()
        if getattr(focus, 'Cut', None):
            return focus.Cut()

    def OnCtrlV(self):
        text = GetClipboardData()
        if not text:
            return False
        focus = uicore.registry.GetFocus()
        if focus and hasattr(focus, 'Paste'):
            focus.Paste(text)
            return True

    def OnCtrlTab(self):
        w = self.GetWndMenu()
        if w:
            w.Next()
            return True

    def OnCtrlShiftTab(self):
        w = self.GetWndMenu()
        if w:
            w.Prev()
            return True

    def GetWndMenu(self):
        pass

    def _CheckWndMenu(self, *args):
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        if not ctrl:
            self.wmTimer = None
        chooseWndMenu = getattr(self, 'chooseWndMenu', None)
        if chooseWndMenu and not chooseWndMenu.destroyed and chooseWndMenu.state != uiconst.UI_HIDDEN:
            chooseWndMenu.ChooseHilited()
        self.chooseWndMenu = None

    def OnEsc(self, stopLoading = True):
        if CloseContextMenus():
            return 1
        modalResult = uicore.registry.GetModalResult(uiconst.ID_CANCEL, 'btn_cancel')
        if modalResult is not None:
            uicore.registry.GetModalWindow().SetModalResult(modalResult)
            return True
        if stopLoading and uicore.layer.loading.state == uiconst.UI_NORMAL:
            uthread.new(sm.GetService('loading').HideAllLoad)
            return True
        sys = uicore.layer.systemmenu
        if sys:
            if sys.isopen:
                uthread.new(sys.CloseMenu)
            else:
                uthread.new(sys.OpenView)
            return True

    OnEsc_Core = OnEsc

    def _BuildScreenshotName(self, fileName = None):
        year, month, weekday, day, hour, minute, second, msec = blue.os.GetTimeParts(blue.os.GetWallclockTime())
        date = '%d.%.2d.%.2d.%.2d.%.2d.%.2d' % (year,
         month,
         day,
         hour,
         minute,
         second)
        return u'{fileName}{separation}{date}.{extension}'.format(fileName=fileName or '', separation='_' if fileName else '', date=date, extension='png')

    def _GetDefaultScreenshotsDirectory(self):
        return u'{documentsPath}/{applicationName}/capture/Screenshots'.format(documentsPath=blue.sysinfo.GetUserDocumentsDirectory(), applicationName=boot.appname)

    def PrintScreen(self, directory = None, fileName = None):
        path = u'{directory}/{fileName}'.format(directory=directory or self._GetDefaultScreenshotsDirectory(), fileName=self._BuildScreenshotName(fileName))
        rt = trinity.device.GetRenderContext().GetDefaultBackBuffer()
        if not rt.isReadable:
            readable = trinity.Tr2RenderTarget(rt.width, rt.height, 1, rt.format)
            rt.Resolve(readable)
            bmp = trinity.Tr2HostBitmap(readable)
        else:
            bmp = trinity.Tr2HostBitmap(rt)
        if bmp.format == trinity.PIXEL_FORMAT.B8G8R8A8_UNORM:
            bmp.ChangeFormat(trinity.PIXEL_FORMAT.B8G8R8X8_UNORM)
        bmp.Save(path)
        return True

    def OpenMonitor(self, *args):
        EngineToolsLauncher.Open()

    def GetStringFromShortcutKeys(self, shortcut):
        retString = ''
        for key in shortcut:
            if key:
                newKey = GetKeyName(key)
                retString += '%s-' % newKey

        retString = retString[:-1]
        retString = localization.uiutil.PrepareLocalizationSafeString(retString, messageID='commandShortcut')
        try:
            retString.decode('cp1252')
        except UnicodeDecodeError:
            retString = '???'

        return retString
