#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_console.py
import sys
from math import sqrt
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from traceback import format_exception
import blue
import evetypes
import stdlogutils
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveEdit
from carbonui.button.group import ButtonGroup
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.divider import Divider
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from carbonui.control.window import Window
from eve.devtools.script import slashError
SERVICENAME = 'console'

class ConsoleService(Service):
    __exportedcalls__ = {'ConstructLayout': []}
    __notifyevents__ = ['ProcessRestartUI']
    __dependencies__ = []
    __guid__ = 'svc.console'
    __servicename__ = SERVICENAME
    __displayname__ = SERVICENAME
    __slashhook__ = True

    def __init__(self):
        Service.__init__(self)
        self.consolecontents = ''
        self.outputcontents_default = self.outputcontents = "Use the variable 'MyResult' to display results here."

    def GetMenu(self, *args):
        return [['Python Console', self.ConstructLayout]]

    def Run(self, memStream = None):
        self.wnd = None

    def Stop(self, memStream = None):
        self.CleanUp()
        Service.Stop(self)

    def CleanUp(self):
        if self.wnd and not self.wnd.destroyed:
            self.Hide()

    def cmd_reportdesync(self, p):
        try:
            threshold, = p.Parse('f')
        except:
            threshold = 0.0

        serverTimestamp = 0
        bp = sm.GetService('michelle').GetBallpark()
        tries = 0
        while bp.currentTime != serverTimestamp and tries < 10:
            ret, serverTimestamp = sm.RemoteSvc('slash').SlashCmd('/reportdesync')
            if bp.currentTime < serverTimestamp:
                blue.pyos.synchro.SleepSim((serverTimestamp - bp.currentTime) * 1000)
            tries += 1

        txt = ''
        mismatchedBallsCount = 0
        for ballID, pos in ret.iteritems():
            if ballID in bp.balls:
                b = bp.balls[ballID]
                serverVec = ret[ballID]
                clientPos = (b.x, b.y, b.z)
                clientVel = (b.vx, b.vy, b.vz)
                diff = (clientPos[0] - serverVec[0], clientPos[1] - serverVec[1], clientPos[2] - serverVec[2])
                delta = sqrt(diff[0] ** 2 + diff[1] ** 2 + diff[2] ** 2)
                if delta > threshold:
                    diffVel = (clientVel[0] - serverVec[3], clientVel[1] - serverVec[4], clientVel[2] - serverVec[5])
                    deltaVel = sqrt(diffVel[0] * diffVel[0] + diffVel[1] * diffVel[1] + diffVel[2] * diffVel[2])
                    spdClient = sqrt(clientVel[0] * clientVel[0] + clientVel[1] * clientVel[1] + clientVel[2] * clientVel[2])
                    spdServer = sqrt(serverVec[3] * serverVec[3] + serverVec[4] * serverVec[4] + serverVec[5] * serverVec[5])
                    if hasattr(b, 'typeID') and b.typeID is not None:
                        typeName = evetypes.GetName(b.typeID)
                    else:
                        try:
                            typeName = evetypes.GetName(bp.slimItems[ballID].typeID)
                        except KeyError:
                            continue

                    dynamicThreshold = max(spdClient, spdServer) * (abs(serverTimestamp - bp.currentTime) + 1)
                    if delta > dynamicThreshold:
                        mismatchText = '<color=0xffff8080>LOCATION MISMATCH</color>:'
                    else:
                        mismatchText = 'Location Mismatch:'
                    if delta > 1:
                        deltaStr = '%.1f' % delta
                    else:
                        deltaStr = '%.2g' % delta
                    txt += '<b>%s (%s)</b> %s <b>%s m</b> ' % (ballID,
                     mismatchText,
                     typeName,
                     deltaStr)
                    txt += 'Client Speed: %.2f m/s - Server Speed: %.2f m/s - Delta Velocity: <b>%.2f m/s</b><br><br>' % (spdClient, spdServer, deltaVel)
                    mismatchedBallsCount += 1

        txt1 = "<font size='18'>Desync Report</font><br>"
        txt1 += 'This report shows object in the local ballpark that are more than %f m from the server position.<br><br>' % threshold
        if serverTimestamp != bp.currentTime:
            txt1 += '<color=0xfff0d410>Warning:</color> Mismatching client and server timestamps! The report is likely to include false positive results.<br>'
        if mismatchedBallsCount == 0:
            txt1 += '<color=0xff3ECD18><b>No objects with a position mismatch were detected!</b></color><br>'
        elif mismatchedBallsCount == 1:
            txt1 += '<color=0xffff8080><b>1 object with a position mismatch was detected!</b></color><br>'
        else:
            txt1 += '<color=0xffff8080><b>%s objects with a position mismatch were detected!</b></color><br>' % mismatchedBallsCount
        txt1 += '%s<br>Server timestamp: %s<br>Local timestamp: %s<br>' % (FmtDate(blue.os.GetSimTime()), serverTimestamp, bp.currentTime)
        txt1 += 'Location: %s - Char: %s - Ship: %s<br><br>' % (eve.session.locationid, eve.session.charid, eve.session.shipid)
        txt = txt1 + txt
        eve.Message('CustomInfo', {'info': txt}, modal=0)

    def cmd_execfile(self, p):
        if not (eve.session and eve.session.role & ROLE_PROGRAMMER):
            raise slashError.Error('You are not authorized to use this command.')
        filename, = p.Parse('s')
        execfile(filename, globals())
        return 'Ok'

    def DoExecute(self, *args):
        if not eve.session.role & ROLE_PROGRAMMER:
            return
        crud = self.input.GetAllText()
        returnDict = {}
        result2 = ''
        try:
            if crud:
                code = compile(crud, '<console>', 'exec')
                eval(code, globals(), returnDict)
        except:
            exc, e, tb = sys.exc_info()
            result2 = (''.join(format_exception(exc, e, tb)) + '\n').replace('\n', '<br>')
            exc = e = tb = None
            raise
        finally:
            if self.wnd and not self.wnd.destroyed:
                self.output.SetValue(result2 + str(returnDict.get('MyResult', '')))

    def DoClear(self, *args):
        self.input.SetValue('')
        self.output.SetValue(self.outputcontents_default)

    def DoCopy(self, *args):
        self.input.CopyAll()

    def DoPaste(self, *args):
        text = blue.clipboard.GetClipboardString()
        for chunk in stdlogutils.wrap_line(text, maxlines=-1, maxlen=1500, pfx=''):
            self.input.Paste(chunk)

    def ConstructLayout(self):
        self.wnd = wnd = Window.GetIfOpen(windowID=SERVICENAME)
        if wnd:
            self.wnd.Maximize()
            return
        self.Layout()

    def LayoutOld(self):
        self.wnd = wnd = Window.Open(windowID=SERVICENAME)
        wnd._OnClose = self.Hide
        wnd.SetCaption('Console')
        wnd.SetMinSize([352, 200])
        wnd.OnUIRefresh = lambda *args: None
        main = Container(name='con', parent=wnd.GetChild('main'), pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.output_container = Container(name='output', parent=main, align=uiconst.TOBOTTOM)
        self.output_container.height = max(32, settings.user.ui.Get('consoleoutputheight', 48))
        c = Container(name='control', parent=main, align=uiconst.TOBOTTOM, height=24)
        i = Container(name='input', parent=main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        divider = Divider(name='divider', align=uiconst.TOBOTTOM, idx=1, height=const.defaultPadding, parent=c, state=uiconst.UI_NORMAL)
        divider.Startup(self.output_container, 'height', 'y', 32, 128)
        self.input = EditPlainText(setvalue=self.consolecontents, parent=i)
        self.input.autoScrollToBottom = 1
        buttons = [['Copy All',
          self.DoCopy,
          None,
          81],
         ['Paste',
          self.DoPaste,
          None,
          81],
         ['Clear',
          self.DoClear,
          None,
          81],
         ['<color=0xff40ff40>Execute',
          self.DoExecute,
          None,
          81]]
        controls = ButtonGroup(btns=buttons, align=uiconst.TOBOTTOM, padding=(0, 8, 0, 8))
        controls.width = 64 * len(buttons)
        controls.height = 16
        c.children.append(controls)

        def checker(cb):
            checked = cb.GetValue()
            settings.user.ui.Set('consolestealth', checked)
            if checked:
                wnd.sr.stealth.hint = 'Stealth: ON<br>Console exceptions are not logged.<br>Click to disable stealth.'
            else:
                wnd.sr.stealth.hint = 'Stealth: OFF<br>Console exceptions are logged.<br>Click to enable stealth.'
            cb.state = uiconst.UI_HIDDEN
            cb.state = uiconst.UI_NORMAL

        wnd.sr.stealth = Checkbox(text='Stealth', parent=c, settingsKey='consolestealth', checked=settings.user.ui.Get('consolestealth', 0), callback=checker, align=uiconst.TOBOTTOM, padding=(0, 8, 0, 8))
        checker(wnd.sr.stealth)
        self.output = eveEdit.Edit(setvalue=self.outputcontents_default, parent=self.output_container, readonly=1, padding=(0, 8, 0, 8))
        self.output.autoScrollToBottom = 1
        uicore.registry.SetFocus(self.input)

    def Layout(self):
        self.wnd = wnd = Window.Open(windowID=SERVICENAME)
        wnd._OnClose = self.Hide
        wnd.SetCaption('Console')
        wnd.OnUIRefresh = lambda *args: None
        main = Container(name='con', parent=wnd.GetChild('main'))
        self.output_container = Container(name='output', parent=main, align=uiconst.TOBOTTOM)
        self.output_container.height = max(32, settings.user.ui.Get('consoleoutputheight', 48))
        self.control_container = ContainerAutoSize(name='control', parent=main, align=uiconst.TOBOTTOM, height=40, callback=self.ApplyWindowMinSize, only_use_callback_when_size_changes=True)
        input_container = Container(name='input', parent=main, align=uiconst.TOALL)
        self.input = EditPlainText(setvalue=self.consolecontents, parent=input_container)
        self.input.autoScrollToBottom = 1
        self.checkbox_container = ContainerAutoSize(parent=self.control_container, align=uiconst.TOLEFT)
        self.stealth = Checkbox(text='Stealth', parent=self.checkbox_container, settingsKey='consolestealth', checked=settings.user.ui.Get('consolestealth', 0), callback=self.OnStealthChecked, align=uiconst.CENTERLEFT, padRight=8)
        self.ConstructButtonGroup()
        self.output = eveEdit.Edit(setvalue=self.outputcontents_default, parent=self.output_container, readonly=1)
        self.output.autoScrollToBottom = 1
        uicore.registry.SetFocus(self.input)

    def ConstructButtonGroup(self):
        self.control_buttons = ButtonGroup(parent=self.control_container, align=uiconst.TOLEFT)
        self.control_buttons.AddButton('Copy All', self.DoCopy)
        self.control_buttons.AddButton('Paste', self.DoPaste)
        self.control_buttons.AddButton('Clear', self.DoClear)
        self.control_buttons.AddButton('<color=0xff40ff40>Execute', self.DoExecute)

    def ApplyWindowMinSize(self):
        width, height = self.wnd.GetWindowSizeForContentSize(height=self.control_container.height, width=self.control_container.width)
        self.wnd.SetMinSize([width, 224])

    def OnStealthChecked(self, cb):
        checked = cb.GetValue()
        settings.user.ui.Set('consolestealth', checked)
        if checked:
            self.stealth.hint = 'Stealth: ON<br>Console exceptions are not logged.<br>Click to disable stealth.'
        else:
            self.stealth.hint = 'Stealth: OFF<br>Console exceptions are logged.<br>Click to enable stealth.'
        cb.state = uiconst.UI_HIDDEN
        cb.state = uiconst.UI_NORMAL

    def Hide(self, *args):
        if self.wnd:
            settings.user.ui.Set('consoleoutputheight', self.output_container.height)
            self.consolecontents = self.input.GetValue()
            self.outputcontents = self.output.GetValue()
            self.wnd.Close()
        self.wnd = None

    def ProcessRestartUI(self):
        if self.wnd:
            self.Hide()
            self.ConstructLayout()
