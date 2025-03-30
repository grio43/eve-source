#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shortcuts.py
from collections import defaultdict
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.services.command import GetKeyName, CommandMap
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveLabelSmall
KEYS = 49
SHIFT_CTRL = 50
SHIFT_ALT = 51
CTRL_ALT = 52
SHIFT_CTRL_ALT = 53
CELL_SPACING = (5, 5)
SHIFT_COLOR = (0.8,
 0.1,
 0.1,
 0.75)
CTRL_COLOR = (0.1,
 0.8,
 0.1,
 0.75)
ALT_COLOR = (0.1,
 0.85,
 0.9,
 0.75)
OTHER_COLOR = (0.9,
 0.9,
 0.9,
 0.75)
contextIncarna = 2

class KeyboardWnd(Window):
    default_minSize = (1080, 440)
    default_height = 440
    default_width = 1080
    default_windowID = 'keyboardWnd'
    __notifyevents__ = ['OnMapShortcut', 'OnRestoreDefaultShortcuts']

    def DebugReload(self, *args):
        self.Close()
        KeyboardWnd.Open()

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.topParent = Container(name='topParent', parent=self.content, align=uiconst.TOTOP, height=40, clipChildren=False, padding=(0, 8, 0, 0))
        self.keyboard_container = Container(parent=self.content, align=uiconst.TOALL, clipChildren=True)
        Button(parent=self.topParent, label='Reload', align=uiconst.TOPRIGHT, func=self.DebugReload, idx=0)
        leftDot = 6
        leftText = leftDot + 12
        top = 40
        Dot(parent=self.topParent, align=uiconst.TOPRIGHT, color=SHIFT_COLOR, left=leftDot, top=top)
        EveLabelSmall(parent=self.topParent, align=uiconst.TOPRIGHT, text='Shift', left=leftText, top=top)
        Dot(parent=self.topParent, align=uiconst.TOPRIGHT, color=CTRL_COLOR, left=leftDot, top=top + 12)
        EveLabelSmall(parent=self.topParent, align=uiconst.TOPRIGHT, text='Ctrl', left=leftText, top=top + 12)
        Dot(parent=self.topParent, align=uiconst.TOPRIGHT, color=ALT_COLOR, left=leftDot, top=top + 24)
        EveLabelSmall(parent=self.topParent, align=uiconst.TOPRIGHT, text='Alt', left=leftText, top=top + 24)
        Dot(parent=self.topParent, align=uiconst.TOPRIGHT, color=OTHER_COLOR, left=leftDot, top=top + 36)
        EveLabelSmall(parent=self.topParent, align=uiconst.TOPRIGHT, text='Shift, Ctrl & Alt combos', left=leftText, top=top + 36)
        options = [('All', None),
         ('Only keys', KEYS),
         ('Shift', uiconst.VK_SHIFT),
         ('Ctrl', uiconst.VK_CONTROL),
         ('Alt', uiconst.VK_MENU),
         ('Shift+Ctrl', SHIFT_CTRL),
         ('Shift+Alt', SHIFT_ALT),
         ('Ctrl+Alt', CTRL_ALT),
         ('Shift+Ctrl+Alt', SHIFT_CTRL_ALT)]
        self.displayCombo = Combo(parent=self.topParent, options=options, name='displayCombo', label='Show what?', callback=self.OnComboDisplayChanged, left=10)
        options = [('Default Settings', 0), ('Your Settings', 1)]
        self.settingsCombo = Combo(parent=self.topParent, options=options, name='settingsCombo', label='Settings', callback=self.OnSettingComboChanged, left=200)
        self.keyDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYDOWN, self.OnGlobalKeyCallback)
        sm.RegisterNotify(self)
        self.RefreshKeyboard()

    def RefreshKeyboard(self):
        self.keyboard_container.Flush()
        self.keyToCont = defaultdict(list)
        self.BuildKeyBoard()
        self.MarkShortcutsByComboValue()

    def OnGlobalKeyCallback(self, wnd, eventID, (vkey, flag)):
        conts = self.keyToCont.get(vkey, None)
        if conts:
            for eachCont in conts:
                eachCont.BlinkBtn()

        return 1

    def OnComboDisplayChanged(self, *args):
        self.MarkShortcutsByComboValue()

    def MarkShortcutsByComboValue(self):
        value = self.displayCombo.GetValue()
        self.ClearAllDots()
        if value is None:
            self.MarkAllShortcuts()
        else:
            self._MarkKeyShortcuts()
            if value == KEYS:
                pass
            elif value == uiconst.VK_SHIFT:
                self._MarkShiftShortcuts()
            elif value == uiconst.VK_CONTROL:
                self._MarkCtrlShortcuts()
            elif value == uiconst.VK_MENU:
                self._MarkAltShortcuts()
            elif value == SHIFT_CTRL:
                self._MarkOtherShortcutsWithModKeys({uiconst.VK_SHIFT, uiconst.VK_CONTROL})
            elif value == SHIFT_ALT:
                self._MarkOtherShortcutsWithModKeys({uiconst.VK_SHIFT, uiconst.VK_MENU})
            elif value == CTRL_ALT:
                self._MarkOtherShortcutsWithModKeys({uiconst.VK_CONTROL, uiconst.VK_MENU})
            elif value == SHIFT_CTRL_ALT:
                self._MarkOtherShortcutsWithModKeys({uiconst.VK_SHIFT, uiconst.VK_CONTROL, uiconst.VK_MENU})

    def OnSettingComboChanged(self, *args):
        self.RefreshKeyboard()

    def BuildKeyBoard(self):
        rowCont = LayoutGrid(parent=self.keyboard_container, columns=1, cellSpacing=(0, 5), top=4, left=10)
        fRow = LayoutGrid(parent=rowCont, columns=16, cellSpacing=CELL_SPACING)
        self.AddBtnsToRow(fRow, F_ROW)
        space = LayoutGrid(parent=rowCont, columns=1, padTop=BTN_SIZE)
        row1 = LayoutGrid(parent=rowCont, columns=16, cellSpacing=CELL_SPACING)
        self.AddBtnsToRow(row1, ROW_1)
        row2 = LayoutGrid(parent=rowCont, columns=16, cellSpacing=CELL_SPACING)
        self.AddBtnsToRow(row2, ROW_2)
        row3 = LayoutGrid(parent=rowCont, columns=16, cellSpacing=CELL_SPACING)
        self.AddBtnsToRow(row3, ROW_3)
        row4 = LayoutGrid(parent=rowCont, columns=16, cellSpacing=CELL_SPACING)
        self.AddBtnsToRow(row4, ROW_4)
        row5 = LayoutGrid(parent=rowCont, columns=16, cellSpacing=CELL_SPACING)
        self.AddBtnsToRow(row5, ROW_5)
        self.BuildRightGrids()

    def BuildRightGrids(self):
        rightGrid1 = LayoutGrid(parent=self.keyboard_container, columns=3, cellSpacing=CELL_SPACING, left=700, top=4)
        self.AddBtnsToRow(rightGrid1, RIGHT_BTNS)
        numpadGrid = LayoutGrid(parent=self.keyboard_container, columns=4, cellSpacing=CELL_SPACING, left=860, top=96)
        self.AddBtnsToRow(numpadGrid, NUMPAD)

    def AddBtnsToRow(self, row, btns):
        for x, size in btns:
            w, h = size
            c = KeyboardKeys(parent=row, align=uiconst.CENTERLEFT, pos=(0,
             0,
             w,
             h))
            if x:
                self.keyToCont[x].append(c)
                keyName = GetKeyName(x)
                keyName = keyName.lower() if len(keyName) == 1 else keyName
                c.SetText(keyName)
                Frame(parent=c, opacity=0.8)

    def FindKeysAndContForCmd(self, cmd):
        if cmd.shortcut is None:
            return (None, None, None)
        vkey = cmd.shortcut[-1]
        shortcutModKeys = cmd.shortcut[:-1]
        conts = self.keyToCont.get(vkey, None)
        return (vkey, shortcutModKeys, conts)

    def MarkAllShortcuts(self):
        self._MarkKeyShortcuts()
        self._MarkShiftShortcuts()
        self._MarkCtrlShortcuts()
        self._MarkAltShortcuts()
        self._MarkOtherShortcuts()

    def _MarkKeyShortcuts(self):
        for cmd in self.GetAllCommands():
            vkey, shortcutModKeys, conts = self.FindKeysAndContForCmd(cmd)
            if vkey is None or conts is None or shortcutModKeys:
                continue
            for x in conts:
                x.SetAsShortcut(cmd)

    def _MarkShiftShortcuts(self):
        for cmd in self.GetAllCommands():
            vkey, shortcutModKeys, conts = self.FindKeysAndContForCmd(cmd)
            if vkey is None or conts is None:
                continue
            if shortcutModKeys == (uiconst.VK_SHIFT,):
                for x in conts:
                    x.ShowShiftDot(cmd)

    def _MarkCtrlShortcuts(self):
        for cmd in self.GetAllCommands():
            vkey, shortcutModKeys, conts = self.FindKeysAndContForCmd(cmd)
            if vkey is None or conts is None:
                continue
            if shortcutModKeys == (uiconst.VK_CONTROL,):
                for x in conts:
                    x.ShowCtrlDot(cmd)

    def _MarkAltShortcuts(self):
        for cmd in self.GetAllCommands():
            vkey, shortcutModKeys, conts = self.FindKeysAndContForCmd(cmd)
            if vkey is None or conts is None:
                continue
            if shortcutModKeys == (uiconst.VK_MENU,):
                for x in conts:
                    x.ShowAltDot(cmd)

    def _MarkOtherShortcuts(self):
        for cmd in self.GetAllCommands():
            vkey, shortcutModKeys, conts = self.FindKeysAndContForCmd(cmd)
            if vkey is None or conts is None or not shortcutModKeys:
                continue
            if len(shortcutModKeys) > 1:
                for x in conts:
                    x.ShowOtherDot(cmd)

    def GetAllCommands(self):
        useDefault = self.settingsCombo.GetValue() == 0
        if useDefault:
            cmdSvc = sm.GetService('cmd')
            mapping = cmdSvc.SetDefaultShortcutMappingCORE()
            mapping.extend(cmdSvc.SetDefaultShortcutMappingGAME())
            mappingFis = [ x for x in mapping if cmdSvc.GetCategoryContext(x.category) != (contextIncarna,) ]
            cmdMap = CommandMap(defaultCmds=mappingFis)
            return cmdMap.GetAllCommands()
        else:
            return uicore.cmd.commandMap.GetAllCommands()

    def _MarkOtherShortcutsWithModKeys(self, modkeys):
        for cmd in self.GetAllCommands():
            vkey, shortcutModKeys, conts = self.FindKeysAndContForCmd(cmd)
            if vkey is None or conts is None or not shortcutModKeys:
                continue
            if set(shortcutModKeys) == modkeys:
                for x in conts:
                    x.ShowOtherDot(cmd)

    def Close(self, *args, **kwargs):
        try:
            uicore.event.UnregisterForTriuiEvents(self.keyDownCookie)
        except StandardError:
            import log
            log.LogTraceback('error when unregistering cookie')

        Window.Close(self, *args, **kwargs)

    def ClearAllDots(self):
        for conts in self.keyToCont.itervalues():
            for c in conts:
                c.ClearAllDots()

    def OnMapShortcut(self, *args):
        self.RefreshKeyboard()

    def OnRestoreDefaultShortcuts(self, *args):
        self.RefreshKeyboard()


BTN_SIZE = 40
NORMAL_BTN = (BTN_SIZE, BTN_SIZE)
F_GAP = (0.6 * BTN_SIZE, BTN_SIZE)
F_ROW = [(uiconst.VK_ESCAPE, NORMAL_BTN),
 (None, F_GAP),
 (uiconst.VK_F1, NORMAL_BTN),
 (uiconst.VK_F2, NORMAL_BTN),
 (uiconst.VK_F3, NORMAL_BTN),
 (uiconst.VK_F4, NORMAL_BTN),
 (None, F_GAP),
 (uiconst.VK_F5, NORMAL_BTN),
 (uiconst.VK_F6, NORMAL_BTN),
 (uiconst.VK_F7, NORMAL_BTN),
 (uiconst.VK_F8, NORMAL_BTN),
 (None, F_GAP),
 (uiconst.VK_F9, NORMAL_BTN),
 (uiconst.VK_F10, NORMAL_BTN),
 (uiconst.VK_F11, NORMAL_BTN),
 (uiconst.VK_F12, NORMAL_BTN)]
ROW_1 = [(uiconst.VK_OEM_3, NORMAL_BTN),
 (uiconst.VK_1, NORMAL_BTN),
 (uiconst.VK_2, NORMAL_BTN),
 (uiconst.VK_3, NORMAL_BTN),
 (uiconst.VK_4, NORMAL_BTN),
 (uiconst.VK_5, NORMAL_BTN),
 (uiconst.VK_6, NORMAL_BTN),
 (uiconst.VK_7, NORMAL_BTN),
 (uiconst.VK_8, NORMAL_BTN),
 (uiconst.VK_9, NORMAL_BTN),
 (uiconst.VK_0, NORMAL_BTN),
 (uiconst.VK_OEM_MINUS, NORMAL_BTN),
 (uiconst.VK_OEM_PLUS, NORMAL_BTN),
 (uiconst.VK_BACK, (2 * BTN_SIZE, BTN_SIZE))]
ROW_2 = [(uiconst.VK_TAB, (1.6 * BTN_SIZE, BTN_SIZE)),
 (uiconst.VK_Q, NORMAL_BTN),
 (uiconst.VK_W, NORMAL_BTN),
 (uiconst.VK_E, NORMAL_BTN),
 (uiconst.VK_R, NORMAL_BTN),
 (uiconst.VK_T, NORMAL_BTN),
 (uiconst.VK_Y, NORMAL_BTN),
 (uiconst.VK_U, NORMAL_BTN),
 (uiconst.VK_I, NORMAL_BTN),
 (uiconst.VK_O, NORMAL_BTN),
 (uiconst.VK_P, NORMAL_BTN),
 (uiconst.VK_OEM_4, NORMAL_BTN),
 (uiconst.VK_OEM_6, NORMAL_BTN),
 (uiconst.VK_OEM_5, (1.4 * BTN_SIZE, BTN_SIZE))]
ROW_3 = [(uiconst.VK_CAPITAL, (1.9 * BTN_SIZE, BTN_SIZE)),
 (uiconst.VK_A, NORMAL_BTN),
 (uiconst.VK_S, NORMAL_BTN),
 (uiconst.VK_D, NORMAL_BTN),
 (uiconst.VK_F, NORMAL_BTN),
 (uiconst.VK_G, NORMAL_BTN),
 (uiconst.VK_H, NORMAL_BTN),
 (uiconst.VK_J, NORMAL_BTN),
 (uiconst.VK_K, NORMAL_BTN),
 (uiconst.VK_L, NORMAL_BTN),
 (uiconst.VK_OEM_1, NORMAL_BTN),
 (uiconst.VK_OEM_7, NORMAL_BTN),
 (uiconst.VK_RETURN, (2.2 * BTN_SIZE, BTN_SIZE))]
ROW_4 = [(uiconst.VK_SHIFT, (2.5 * BTN_SIZE, BTN_SIZE)),
 (uiconst.VK_Z, NORMAL_BTN),
 (uiconst.VK_X, NORMAL_BTN),
 (uiconst.VK_C, NORMAL_BTN),
 (uiconst.VK_V, NORMAL_BTN),
 (uiconst.VK_B, NORMAL_BTN),
 (uiconst.VK_N, NORMAL_BTN),
 (uiconst.VK_M, NORMAL_BTN),
 (uiconst.VK_OEM_COMMA, NORMAL_BTN),
 (uiconst.VK_OEM_PERIOD, NORMAL_BTN),
 (uiconst.VK_OEM_2, NORMAL_BTN),
 (uiconst.VK_UP, NORMAL_BTN),
 (uiconst.VK_SHIFT, (1.6 * BTN_SIZE, BTN_SIZE))]
ROW_5 = [(uiconst.VK_CONTROL, (1.5 * BTN_SIZE, BTN_SIZE)),
 (uiconst.VK_LWIN, (1.4 * BTN_SIZE, BTN_SIZE)),
 (uiconst.VK_MENU, (1.4 * BTN_SIZE, BTN_SIZE)),
 (uiconst.VK_SPACE, (6 * BTN_SIZE, BTN_SIZE)),
 (uiconst.VK_MENU, (1.4 * BTN_SIZE, BTN_SIZE)),
 (uiconst.VK_LWIN, (1.4 * BTN_SIZE, BTN_SIZE)),
 (uiconst.VK_APPS, NORMAL_BTN),
 (uiconst.VK_CONTROL, (1.5 * BTN_SIZE, BTN_SIZE))]
shortcut = (44,)
shortcut = (145,)
shortcut = (19,)
RIGHT_BTNS = [(uiconst.VK_SNAPSHOT, NORMAL_BTN),
 (uiconst.VK_SCROLL, NORMAL_BTN),
 (uiconst.VK_PAUSE, NORMAL_BTN),
 (None, NORMAL_BTN),
 (None, NORMAL_BTN),
 (None, NORMAL_BTN),
 (uiconst.VK_INSERT, NORMAL_BTN),
 (uiconst.VK_HOME, NORMAL_BTN),
 (uiconst.VK_PRIOR, NORMAL_BTN),
 (uiconst.VK_DELETE, NORMAL_BTN),
 (uiconst.VK_END, NORMAL_BTN),
 (uiconst.VK_NEXT, NORMAL_BTN),
 (None, NORMAL_BTN),
 (None, NORMAL_BTN),
 (None, NORMAL_BTN),
 (None, NORMAL_BTN),
 (uiconst.VK_UP, NORMAL_BTN),
 (None, NORMAL_BTN),
 (uiconst.VK_LEFT, NORMAL_BTN),
 (uiconst.VK_DOWN, NORMAL_BTN),
 (uiconst.VK_RIGHT, NORMAL_BTN)]
NUMPAD = [(uiconst.VK_NUMLOCK, NORMAL_BTN),
 (uiconst.VK_DIVIDE, NORMAL_BTN),
 (uiconst.VK_MULTIPLY, NORMAL_BTN),
 (uiconst.VK_SUBTRACT, NORMAL_BTN),
 (uiconst.VK_NUMPAD7, NORMAL_BTN),
 (uiconst.VK_NUMPAD8, NORMAL_BTN),
 (uiconst.VK_NUMPAD9, NORMAL_BTN),
 (uiconst.VK_ADD, NORMAL_BTN),
 (uiconst.VK_NUMPAD4, NORMAL_BTN),
 (uiconst.VK_NUMPAD5, NORMAL_BTN),
 (uiconst.VK_NUMPAD6, NORMAL_BTN),
 (None, NORMAL_BTN),
 (uiconst.VK_NUMPAD1, NORMAL_BTN),
 (uiconst.VK_NUMPAD2, NORMAL_BTN),
 (uiconst.VK_NUMPAD3, NORMAL_BTN),
 (uiconst.VK_RETURN, NORMAL_BTN),
 (uiconst.VK_NUMPAD0, NORMAL_BTN),
 (None, NORMAL_BTN),
 (uiconst.VK_DECIMAL, NORMAL_BTN)]

class KeyboardKeys(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.bgFill = Fill(bgParent=self, opacity=0.0)
        self.shiftDot = Dot(parent=self, align=uiconst.TOPLEFT, color=SHIFT_COLOR)
        self.shiftDot.display = False
        self.ctrlDot = Dot(parent=self, align=uiconst.TOPRIGHT, color=CTRL_COLOR)
        self.ctrlDot.display = False
        self.altDot = Dot(parent=self, align=uiconst.BOTTOMLEFT, color=ALT_COLOR)
        self.altDot.display = False
        self.otherDotCmds = set()
        self.otherDot = Dot(parent=self, align=uiconst.BOTTOMRIGHT, color=OTHER_COLOR)
        self.otherDot.display = False
        self.label = EveLabelSmall(parent=self, text='', align=uiconst.CENTER)

    def SetText(self, text):
        self.label.SetText(text)

    def SetAsShortcut(self, cmd):
        self.label.SetTextColor((1, 0, 0, 1))
        self.label.SetState(uiconst.UI_NORMAL)
        self.SetHintOnObject(self.label, cmd)

    def ClearAllDots(self):
        self.shiftDot.display = False
        self.ctrlDot.display = False
        self.altDot.display = False
        self.otherDot.display = False
        self.otherDotCmds.clear()

    def BlinkBtn(self):
        uicore.animations.FadeTo(self.bgFill, startVal=0.5, endVal=0.0, duration=0.25)

    def ShowShiftDot(self, cmd):
        self.shiftDot.display = True
        self.SetHintOnObject(self.shiftDot, cmd)

    def ShowCtrlDot(self, cmd):
        self.ctrlDot.display = True
        self.SetHintOnObject(self.ctrlDot, cmd)

    def ShowAltDot(self, cmd):
        self.altDot.display = True
        self.SetHintOnObject(self.altDot, cmd)

    def ShowOtherDot(self, cmd):
        self.otherDotCmds.add(cmd)
        self.otherDot.display = True
        hintLabels = []
        for eachCmd in self.otherDotCmds:
            hintLabels.append(self._GetHintForCmd(eachCmd))

        self.otherDot.hint = '<br><br>'.join(hintLabels)

    def SetHintOnObject(self, obj, cmd):
        obj.hint = self._GetHintForCmd(cmd)

    def _GetHintForCmd(self, cmd):
        description = cmd.GetDescription()
        shortcutString = cmd.GetShortcutAsString()
        return '%s<br><b>%s</b>' % (description, shortcutString)


class Dot(Container):
    default_height = 12
    default_width = 12
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        color = attributes.color or (1, 1, 1, 1)
        self.dot = Sprite(parent=self, align=uiconst.CENTER, pos=(0, 0, 8, 8), texturePath='res:/UI/Texture/Shared/smallDot.png', color=color, state=uiconst.UI_DISABLED)
