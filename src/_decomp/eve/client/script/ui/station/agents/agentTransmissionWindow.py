#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\agents\agentTransmissionWindow.py
import blue
import uthread
from carbon.common.script.util.commonutils import StripTags
from carbonui import const as uiconst
from eve.client.script.ui.control.eveEdit import Edit
from carbonui.control.window import Window
from eve.client.script.ui.station.agents import agentDialogueUtil
from eve.common.lib import appConst
from localization import GetByLabel

class AgentTransmissionWindow(Window):
    __notifyevents__ = []
    default_minSize = (512, 512)
    default_fixedWidth = 512
    default_windowID = 'AgentTransmissionWindow'

    def ApplyAttributes(self, attributes):
        super(AgentTransmissionWindow, self).ApplyAttributes(attributes)
        agentID = attributes.agentID
        message = attributes.message
        self.loadupdates = 0
        self.statustext = ''
        self.views = []
        self.activeView = 0
        self.SetCaption('')
        self.sr.browser = Edit(parent=self.sr.main, padding=appConst.defaultPadding, readonly=1)
        self.sr.browser.AllowResizeUpdates(0)
        self.sr.browser.sr.window = self
        self.LoadWnd(agentID, message)

    def LoadWnd(self, agentID, message):
        self.agentID = agentID
        self.UpdateCaption()
        html = self.GetHTML(message)
        uthread.new(self.LoadHTML, html)

    def UpdateCaption(self):
        agentInfo = sm.GetService('agents').GetAgentByID(self.agentID)
        agentNameAndLevel = agentDialogueUtil.GetAgentNameAndLevel(self.agentID, agentInfo.level)
        caption = StripTags(GetByLabel('UI/Agents/Dialogue/AgentConversationWith', agentNameAndLevel=agentNameAndLevel), stripOnly=['localized'])
        self.SetCaption(caption)

    def GetHTML(self, message):
        agentService = sm.GetService('agents')
        agentInfo = agentService.GetAgentByID(self.agentID)
        agentSays = agentService.ProcessMessage(message, self.agentID)
        agentLocationWrap = agentService.GetAgentMoniker(self.agentID).GetAgentLocationWrap()
        html = '\n            <html>\n                <body background-color=#00000000 link=#FFA800>\n                    <br>\n                    %(agentHeader)s\n                    <br>\n                    <table width=465>\n                        <tr>\n                            <td width=40 valign=top>\n                                <img style:vertical-align:bottom src="icon:ui_9_64_2" size="32">\n                            </td>\n                            <td>\n                                <font size=12>%(agentSays)s</font>\n                            </td>\n                        </tr>\n                    </table>\n                </body>\n            </html>\n        ' % {'agentHeader': agentDialogueUtil.GetAgentLocationHeader(agentInfo, agentLocationWrap, 0),
         'agentSays': agentSays}
        return html

    def LoadHTML(self, html, hideBackground = 0, newThread = 1):
        self.sr.browser.sr.hideBackground = hideBackground
        self.sr.browser.LoadHTML(html, newThread=newThread)

    def LoadPage(self, html, popup):
        if self.state != uiconst.UI_NORMAL and popup:
            self.Maximize()
        if self.state in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN):
            blue.pyos.synchro.Yield()
            self.sr.browser.LoadHTML(html)

    def OnEndScale_(self, *args):
        self.reloadedScaleSize = (self.width, self.height)
        uthread.new(self.Reload, 0)

    def Reload(self, forced = 1, *args):
        if not self or self.destroyed:
            return
        url = self.sr.browser.sr.currentURL
        if url and forced:
            uthread.new(self.GoTo, url, self.sr.browser.sr.currentData, scrollTo=self.sr.browser.GetScrollProportion())
        else:
            uthread.new(self.sr.browser.LoadHTML, None, scrollTo=self.sr.browser.GetScrollProportion())
