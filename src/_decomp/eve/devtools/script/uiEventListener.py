#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiEventListener.py
import blue
import uthread
import trinity
import utillib
from carbonui import uiconst
from carbonui.control import scrollentries
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import GetWindowAbove
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup
from eve.devtools.script.uiEventListenerConsts import wmConst

class UIEventListener(Window):
    __guid__ = 'form.UIEventListener'
    default_windowID = 'UIEventListener'
    default_width = 450
    default_height = 300
    default_minSize = (default_width, default_height)
    default_caption = 'UI Event Listener'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.tabs = TabGroup(parent=self.content)
        self.windowsEventPanel = WindowsEventPanel(parent=self.content)
        self.uiEventPanel = UIEventPanel(parent=self.content)
        self.uiGlobalEventPanel = UIGlobalEventPanel(parent=self.content)
        self.shortcutPanel = UIShortcutPanel(parent=self.content)
        self.helpPanel = HelpPanel(parent=self.content)
        self.tabs.AddTab(label='Windows events', panel=self.windowsEventPanel)
        self.tabs.AddTab(label='UI events', panel=self.uiEventPanel)
        self.tabs.AddTab(label='UI global events', panel=self.uiGlobalEventPanel)
        self.tabs.AddTab(label='Shortcuts', panel=self.shortcutPanel)
        self.tabs.AddTab(label='Help', panel=self.helpPanel)


class BaseEventPanel(Container):
    __guid__ = 'uiEventListener.BaseEventPanel'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.events = []
        self.settingsName = 'BaseEventPanel.ignoreEvents'
        settings.user.ui.Set(self.settingsName, self.default_ignoreEvents)
        self.ignoreEvents = settings.user.ui.Get(self.settingsName, self.default_ignoreEvents)
        self.updatePending = False
        self.showMax = 100
        self.scrollUpdateRequested = False
        self.isPaused = False
        self.rightCont = Container(name='rightCont', parent=self, align=uiconst.TORIGHT, width=150, padding=3)
        eveLabel.Label(parent=self.rightCont, align=uiconst.TOTOP, text='<color=red>IGNORE LIST</color>')
        eveLabel.Label(parent=self.rightCont, align=uiconst.TOBOTTOM, text='Right-click logged entries to add that event type to ignore')
        self.ignoreScroll = eveScroll.Scroll(parent=self.rightCont, align=uiconst.TOALL)
        self._UpdateIgnoreScroll()
        btns = (('Clear', self.ResetEventData, ()), ('<color=green>Pause logging</color>', self.PauseResumeLogging, ()))
        btnGroup = ButtonGroup(parent=self, btns=btns)
        self.pauseResumeBtn = btnGroup.buttons[1]
        self.scroll = eveScroll.Scroll(parent=self, align=uiconst.TOALL, padding=3)
        uthread.new(self._UpdateScrollThread)

    def OnTabSelect(self):
        self.UpdateScroll()

    def ResetEventData(self):
        self.events = []
        self.scroll.Clear()

    def PauseResumeLogging(self):
        self.isPaused = not self.isPaused
        if self.isPaused:
            label = '<color=yellow>Resume logging</color>'
        else:
            label = '<color=green>Pause logging</color>'
        self.pauseResumeBtn.SetLabel(label)

    def AddEvent(self, **kw):
        time = self._GetTimestampText()
        event = utillib.KeyVal(**kw)
        if event.id not in self.ignoreEvents:
            self.events.insert(0, (time, event))
            self.UpdateScroll()

    def UpdateScroll(self):
        if not self.display:
            return
        self.scrollUpdateRequested = True

    def _UpdateScrollThread(self):
        updateDelay = 200
        while not self.destroyed:
            if self.scrollUpdateRequested:
                self._UpdateScroll()
                self.scrollUpdateRequested = False
                blue.synchro.SleepWallclock(updateDelay)
            else:
                blue.synchro.Yield()

    def _UpdateScroll(self):
        if self.isPaused:
            return
        wndAbove = GetWindowAbove(uicore.uilib.mouseOver)
        if isinstance(wndAbove, UIEventListener) and uicore.uilib.rightbtn:
            return
        scrolllist = []
        lastTime = None
        for time, event in self.events[:self.showMax]:
            if lastTime == time:
                time = ''
            else:
                lastTime = time
            label = time + '<t>' + self.GetScrollLabel(event)
            scrolllist.append(scrollentries.ScrollEntryNode(decoClass=scrollentries.SE_GenericCore, label=label, fontsize=14, event=event, OnGetMenu=self.GetScrollEntryMenu))

        self.scroll.Load(contentList=scrolllist, headers=self.SCROLL_HEADERS, ignoreSort=True)

    def GetScrollEntryMenu(self, entry):
        return (('Add to ignore', self.AddEventToIgnore, (entry,)),)

    def _UpdateIgnoreScroll(self):
        scrolllist = []
        for id, name in self.ignoreEvents.iteritems():
            scrolllist.append(scrollentries.ScrollEntryNode(decoClass=scrollentries.SE_GenericCore, label=name, id=id, fontsize=14, OnMouseDown=self.RemoveEventFromIgnore))

        self.ignoreScroll.Load(contentList=scrolllist)

    def AddEventToIgnore(self, entry):
        event = entry.sr.node.event
        self.ignoreEvents[event.id] = event.name
        settings.user.ui.Set(self.settingsName, self.ignoreEvents)
        self._UpdateIgnoreScroll()

    def RemoveEventFromIgnore(self, entry):
        node = entry.sr.node
        if node.id in self.ignoreEvents:
            self.ignoreEvents.pop(node.id)
            settings.user.ui.Set(self.settingsName, self.ignoreEvents)
        self._UpdateIgnoreScroll()

    def _GetTimestampText(self):
        year, month, weekday, day, hour, minute, second, msec = blue.os.GetTimeParts(blue.os.GetWallclockTime())
        return '%02i:%02i:%02i.%03i' % (hour,
         minute,
         second,
         msec)


class WindowsEventPanel(BaseEventPanel):
    __guid__ = 'uiEventListener.WindowsEventPanel'
    SCROLL_HEADERS = ['time',
     'msgID',
     'wParam',
     'lParam',
     'details']
    default_ignoreEvents = {wmConst.WM_MOUSEMOVE: 'WM_MOUSEMOVE',
     wmConst.WM_NCHITTEST: 'WM_NCHITTEST',
     wmConst.WM_GETDLGCODE: 'WM_GETDLGCODE'}

    def ApplyAttributes(self, attributes):
        BaseEventPanel.ApplyAttributes(self, attributes)
        self.leftCont = Container(name='leftCont', parent=self, align=uiconst.TOLEFT, width=100)
        self._otherWindowProc = trinity.mainWindow.onWindowsMessage
        self._otherFilter = trinity.app.GetWindowsMessageFilter()
        trinity.mainWindow.onWindowsMessage = self.OnAppEvent
        trinity.app.SetWindowsMessageFilter(False, self._otherFilter[1])

    def OnAppEvent(self, msgID, wParam, lParam):
        if self._otherWindowProc:
            ret = self._otherWindowProc(msgID, wParam, lParam)
        else:
            ret = (0, False)
        msgName = wmConst().GetMSGName(msgID)
        self.AddEvent(id=msgID, name=msgName, wParam=wParam, lParam=lParam)
        return ret

    def _OnClose(self):
        trinity.mainWindow.onWindowsMessage = self._otherWindowProc
        trinity.app.SetWindowsMessageFilter(*self._otherFilter)

    def GetScrollLabel(self, event):
        if event.name is None:
            event.name = '<color=red>%s</color>' % hex(event.id).upper()
        details = self.GetDetails(event.id, event.wParam, event.lParam)
        label = '%s<t>%s<t>%s<t>%s' % (event.name,
         hex(event.wParam).upper(),
         hex(event.lParam).upper(),
         details)
        return label

    def GetDetails(self, msgID, wParam, lParam):
        if msgID in (wmConst.WM_KEYDOWN,
         wmConst.WM_KEYUP,
         wmConst.WM_SYSKEYDOWN,
         wmConst.WM_SYSKEYUP):
            vk = uicore.cmd.GetKeyNameFromVK(wParam)
            if msgID == wmConst.WM_KEYDOWN:
                repeatCount = lParam & 65535
                if repeatCount > 1:
                    vk += ', repeatCount=%s' % repeatCount
            return vk
        if msgID == wmConst.WM_CHAR:
            return unichr(wParam)
        if msgID in (wmConst.WM_XBUTTONDOWN, wmConst.WM_XBUTTONUP):
            if wParam & 65536:
                return 'XBUTTON1'
            else:
                return 'XBUTTON2'
        return '-'


class UIEventPanel(BaseEventPanel):
    __guid__ = 'uiEventListener.UIEventPanel'
    SCROLL_HEADERS = ['time',
     'eventID',
     'object name',
     'object id',
     'class',
     'args',
     'param']
    default_ignoreEvents = {uiconst.UI_MOUSEENTER: 'OnMouseEnter',
     uiconst.UI_MOUSEEXIT: 'OnMouseExit',
     uiconst.UI_MOUSEHOVER: 'OnMouseHover',
     uiconst.UI_MOUSEMOVE: 'OnMouseMove'}

    def ApplyAttributes(self, attributes):
        BaseEventPanel.ApplyAttributes(self, attributes)
        self.realEventHandler = uicore.uilib._TryExecuteHandler
        uicore.uilib._TryExecuteHandler = self._TryExecuteHandler

    def _TryExecuteHandler(self, eventID, obj, eventArgs = None, param = None):
        handlerObj = self.realEventHandler(eventID, obj, eventArgs, param)
        if handlerObj:
            name = uicore.uilib.EVENTMAP[eventID]
            self.AddEvent(id=eventID, name=name, obj=obj, eventArgs=eventArgs, param=param)

    def _OnClose(self):
        uicore.uilib._TryExecuteHandler = self.realEventHandler

    def GetScrollLabel(self, event):
        return '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (event.name,
         event.obj.name,
         hex(id(event.obj)).upper(),
         getattr(event.obj, '__guid__', event.obj.__class__.__name__),
         event.eventArgs,
         event.param)


class UIGlobalEventPanel(BaseEventPanel):
    __guid__ = 'uiEventListener.UIGlobalEventPanel'
    SCROLL_HEADERS = ['time',
     'eventID',
     'called function',
     'winParams',
     'args',
     'kw']
    default_ignoreEvents = {}

    def ApplyAttributes(self, attributes):
        BaseEventPanel.ApplyAttributes(self, attributes)
        self.realEventHandler = uicore.uilib.CheckCallbacks
        uicore.uilib.CheckCallbacks = self.CheckCallbacks

    def CheckCallbacks(self, obj, msgID, param):
        callbackDict = uicore.uilib._triuiRegsByMsgID.get(msgID, {})
        for cookie, (wr, args, kw) in callbackDict.items():
            func = wr()
            name = uicore.uilib.EVENTMAP.get(msgID, '<color=red>%s</color>' % msgID)
            self.AddEvent(id=msgID, name=name, func=func, winParams=param, args=args, kw=kw)

        self.realEventHandler(obj, msgID, param)

    def _OnClose(self):
        uicore.uilib.CheckCallbacks = self.realEventHandler

    def GetScrollLabel(self, event):
        func = event.func
        if func:
            class_name = getattr(func.im_class, '__guid__', func.im_class.__name__)
            func = '%s.%s' % (class_name, func.im_func.func_name)
        return '%s<t>%s<t>%s<t>%s<t>%s' % (event.name,
         func,
         event.winParams,
         event.args,
         event.kw)


class UIShortcutPanel(BaseEventPanel):
    __guid__ = 'uiEventListener.UIShortcutPanel'
    SCROLL_HEADERS = ['time', 'name']
    default_ignoreEvents = {}
    __notifyevents__ = ('OnCommandExecuted',)

    def ApplyAttributes(self, attributes):
        BaseEventPanel.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)

    def OnCommandExecuted(self, name):
        self.AddEvent(id=name, name=name)

    def GetScrollLabel(self, event):
        return event.name


class HelpPanel(Container):
    __guid__ = 'uiEventListener.HelpPanel'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        text = '\n<b>Windows events:</b> These are raw operating system events that are cought by trinity and forwarded to uicore.uilib (uilib.py) where they are processed and used to execute UI events, UI global events and shortcuts.\n\n<b>UI events:</b> UI events coming from uilib are handled by bound methods, defined in UI classes. To catch one of those events, simply define the appropriately named method within your class (OnClick for example). The meaning of the arguments passed on to the event handlers differ between events.    \n\n<b>UI global events:</b> In some cases it can be useful to listen to global events. For example, a container might be interested to know when the mouse is clicked, regardless of what is being clicked. This can be achieved by registering an event listener through uicore.uilib.RegisterForTriuiEvents\n\n<b>Shortcuts:</b> Shortcut key commands are handled in uicore.cmd (command.py and game specific file such as evecommands.py). \n'
        eveLabel.Label(parent=self, align=uiconst.TOALL, text=text, padding=10, fontsize=13)
