#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\logviewer.py
import os
import carbonui.const as uiconst
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER
from carbon.common.script.util.format import FmtDate
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.primitives.container import Container
from carbonui.button.group import ButtonGroup
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
import blue
from carbonui.uicore import uicore
LOGTYPE_MAPPING = {0: ('info', '0xffeeeeee'),
 1: ('notice', '0xff22dd22'),
 2: ('warning', '0xffcccc00'),
 3: ('error', '0xffcc0000')}
DEV_OPTIONS = (('Info', 0),
 ('Notice', 1),
 ('Warning', 2),
 ('Error', 3))
PLAYER_OPTIONS = (('Notice', 1), ('Warning', 2), ('Error', 3))

class LogViewer(Window):
    default_caption = 'Log Viewer'
    default_minSize = (400, 400)
    default_windowID = 'LogViewer'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        optionsContainer = Container(parent=self.sr.main, align=uiconst.TOTOP, height=18, padding=(6, 6, 4, 0))
        Label(parent=optionsContainer, text='<b>Threshold:</b>', align=uiconst.TOLEFT, padRight=4)
        if session.role & ROLEMASK_ELEVATEDPLAYER:
            options = DEV_OPTIONS
        else:
            options = PLAYER_OPTIONS
        for text, value in options:
            isChecked = blue.logInMemory.threshold == value
            RadioButton(parent=optionsContainer, text=text, groupname='threshold', align=uiconst.TOLEFT, width=100, checked=isChecked, callback=self.OnLogThresholdRadioButtons, retval=value, padLeft=4)

        ButtonGroup(parent=self.sr.main, line=False, btns=[['Copy',
          self.ExportLogInMemory,
          (),
          51], ['Attach',
          self.AttachToLogServer,
          (),
          51], ['Save',
          self.SaveLogsToFile,
          (),
          51]])
        self.scroll = Scroll(parent=self.sr.main, id='logviewerscroll', align=uiconst.TOALL, padding=4)
        self.logSaveHandle = None
        self.PopulateScroll()
        blue.pyos.SetLogEchoFunction(blue.logInMemory.threshold, self._log_echo)

    def Close(self, *args, **kwargs):
        blue.pyos.SetLogEchoFunction(0, None)
        self.logSaveHandle = None
        Window.Close(self, *args, **kwargs)

    def OnLogThresholdRadioButtons(self, button):
        threshold = button.data['value']
        blue.logInMemory.threshold = int(threshold)
        blue.pyos.SetLogEchoFunction(blue.logInMemory.threshold, self._log_echo)

    def GetNodesFromLogMessage(self, timestamp, facility, level, log_object, msg):
        s = LOGTYPE_MAPPING.get(level, ('Unknown', '0xffeeeeee'))
        lineno = 0
        nodes = []
        timestampAsString = FmtDate(timestamp, 'nl')
        for line in msg.split('\n'):
            label = '%s<t>%s<t>%s::%s<t><color=%s>%s</color><t>%s' % (str(timestamp + lineno)[-15:],
             timestampAsString,
             facility,
             log_object,
             s[1],
             s[0],
             line.replace('<', '&lt;'))
            nodes.append(ScrollEntryNode(decoClass=SE_GenericCore, label=label))
            lineno += 1

        if self.logSaveHandle:
            txt = '%s\t%s::%s\t%s\t%s\n' % (timestampAsString,
             facility,
             log_object,
             s[0],
             msg)
            self.logSaveHandle.Write(txt)
        return nodes

    def PopulateScroll(self):
        entries = blue.logInMemory.GetEntries()
        contentList = []
        for e in entries:
            facility, log_object, level, timestamp, msg = e
            nodes = self.GetNodesFromLogMessage(timestamp, facility, level, log_object, msg)
            contentList.extend(nodes)

        self.scroll.Load(contentList=contentList, headers=['#',
         'time',
         'channel',
         'type',
         'message'], fixedEntryHeight=18)

    def _log_echo(self, level, facility, log_object, msg):
        nodes = self.GetNodesFromLogMessage(blue.os.GetTime(), facility, level, log_object, msg)
        self.scroll.AddEntries(-1, nodes)

    def GetInMemoryLogs(self):
        txt = 'Time\tFacility\tType\tMessage\r\n'
        entries = blue.logInMemory.GetEntries()
        entries.reverse()
        for e in entries:
            s = LOGTYPE_MAPPING.get(e[2], ('Unknown', ''))
            for line in e[4].split('\n'):
                try:
                    txt += '%s\t%s::%s\t%s\t%s\r\n' % (FmtDate(e[3], 'nl'),
                     e[0],
                     e[1],
                     s[0],
                     line)
                except Exception:
                    txt += '***Error writing out logline***\r\n'

        return txt

    def ExportLogInMemory(self):
        blue.pyos.SetClipboardData(self.GetInMemoryLogs())
        uicore.Message('CustomInfo', {'info': 'Logs copied to clipboard.'})

    def AttachToLogServer(self):
        blue.AttachToLogServer()
        uicore.Message('CustomInfo', {'info': 'Done attaching to Log Server.'})

    def SaveLogsToFile(self):
        path = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'logs', 'evelogs.log')
        self.logSaveHandle = blue.ResFile()
        self.logSaveHandle.Create(path)
        entries = blue.logInMemory.GetEntries()
        for e in entries:
            facility, log_object, level, timestamp, msg = e
            s = LOGTYPE_MAPPING.get(level, ('Unknown', '0xffeeeeee'))
            timestampAsString = FmtDate(timestamp, 'nl')
            txt = '%s\t%s::%s\t%s\t%s\n' % (timestampAsString,
             facility,
             log_object,
             s[0],
             msg)
            self.logSaveHandle.Write(txt)

        uicore.Message('CustomInfo', {'info': 'Saving logs directly to file at %s' % path})
