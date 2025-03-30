#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\actions.py
import carbonui.const as uiconst
from carbonui.window.widget import WidgetWindow
from carbonui.primitives.container import Container
from eve.common.lib import appConst as const

class ActionPanel(WidgetWindow):
    __guid__ = 'form.ActionPanel'
    default_width = 360
    default_height = 160

    def ApplyAttributes(self, attributes):
        super(ActionPanel, self).ApplyAttributes(attributes)
        showActions = attributes.get('showActions', True)
        self.panelname = attributes.panelName
        self.lastActionSerial = None
        self.sr.actions = None
        self.sr.actionsTimer = None
        self.scope = uiconst.SCOPE_INFLIGHT
        if self.panelname:
            self.SetCaption(self.panelname)
        self.MakeUnKillable()
        main = self.sr.main
        main.clipChildren = True
        if showActions:
            self.sr.actions = Container(name='actions', align=uiconst.TOBOTTOM, parent=self.sr.main, height=32)
        self.PostStartup()
        self.UpdateAll()

    def _OnClose(self, *args):
        self.sr.actionsTimer = None
        self.Closing()

    def PostStartup(self):
        pass

    def Closing(self):
        pass

    def GetActions(self):
        return []

    def UpdateAll(self):
        if self.sr.main.state != uiconst.UI_PICKCHILDREN:
            self.sr.actionsTimer = None
            return
