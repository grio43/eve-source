#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\agents\missionDetailsWindow.py
import uthread
from carbonui import const as uiconst
from eve.client.script.ui.control.eveEdit import Edit
from carbonui.control.window import Window
from eve.client.script.ui.station.agents import agentDialogueUtil
from eve.common.lib import appConst
import blue
CLOSE_ACTIONIDS = (appConst.agentMissionReset,
 appConst.agentMissionDeclined,
 appConst.agentMissionCompleted,
 appConst.agentMissionQuit,
 appConst.agentMissionFailed,
 appConst.agentMissionOffered,
 appConst.agentMissionOfferRemoved)

class MissionDetailsWindow(Window):
    __notifyevents__ = ['OnSessionChanged', 'OnAgentMissionChange']
    default_windowID = 'MissionDetails'
    default_minSize = (420, 400)
    default_caption = ''
    default_width = 600
    default_height = 800

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.agentID = None
        self.sr.browser = Edit(parent=self.sr.main, padding=appConst.defaultPadding, readonly=1)
        self.sr.browser.AllowResizeUpdates(0)
        self.sr.browser.sr.window = self

    def ReconstructLayout(self, agentID, charID = None, contentID = None, maximize = True):
        self.agentID = agentID
        missionInfo = sm.GetService('agents').GetMissionInfo(agentID, charID, contentID)
        if not missionInfo:
            return self.Close()
        if self.state != uiconst.UI_NORMAL and maximize:
            self.Maximize()
        if self.state in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN):
            html = agentDialogueUtil.GetMissionDetailsWindowHTML(missionInfo, agentID)
            blue.pyos.synchro.Yield()
            self.sr.browser.LoadHTML(html)

    def OnEndScale_(self, *args):
        uthread.new(self.Reload)

    def Reload(self, *args):
        if self.destroyed:
            return
        uthread.new(self.sr.browser.LoadHTML, None, scrollTo=self.sr.browser.GetScrollProportion())

    def OnSessionChanged(self, isRemote, sess, change):
        if 'stationid' in change:
            self.ReconstructLayout(self.agentID, maximize=False)

    def OnAgentMissionChange(self, actionID, agentID):
        if agentID != self.agentID or self.destroyed:
            return
        if actionID in CLOSE_ACTIONIDS:
            self.Close()
        else:
            self.ReconstructLayout(agentID)
