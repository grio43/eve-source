#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\debugwindow.py
from npcs.divisions import get_division_name
from carbonui.control.combo import Combo
import uthread2
from carbonui.button.group import ButtonGroup
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.shared.userentry import AgentEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
import eve.common.lib.appConst as appConst
import carbonui.const as uiconst
import blue

class CareerAgentDebugWnd(Window):
    default_caption = 'Career Agents Debug'
    default_width = 350
    default_height = 350
    default_minSize = (340, 220)
    default_windowID = 'careerAgentDebugWnd'

    def ApplyAttributes(self, attributes):
        super(CareerAgentDebugWnd, self).ApplyAttributes(attributes)
        btnGroup = ButtonGroup(parent=self.content, align=uiconst.TOBOTTOM)
        self.AddCombo()
        self.agentScroll = Scroll(parent=self.content, padBottom=20)
        btnGroup.AddButton(label='Open All Agents in view', func=self.OpenAll)
        btnGroup.AddButton(label='Close All Agent wnds', func=self.CloseAllAgentWnds)
        self.LoadAgents()

    def AddCombo(self):
        options = []
        for careerID in appConst.agentDivisionsCareer:
            options.append((get_division_name(careerID), careerID))

        options.sort(key=lambda x: x[0])
        factionOptions = []
        for factionID in appConst.factionsEmpires:
            factionOptions.append((cfg.eveowners.Get(factionID).name, factionID))

        factionOptions.sort(key=lambda x: x[0])
        options.extend(factionOptions)
        options.insert(0, ('All', None))
        comboPrefsKey = ('char', 'ui', 'careerAgentDebugFilter')
        self.filterCombo = Combo(parent=self.content, align=uiconst.TOTOP, options=options, padBottom=20, callback=self.OnComboChanged, prefskey=comboPrefsKey, select=settings.char.ui.Get(comboPrefsKey[2], None), maxVisibleEntries=10)

    def LoadAgents(self):
        allCareerAgents = self.GetAllCareerAgents()
        toPrime = set()
        for agent in allCareerAgents:
            toPrime.add(agent.agentID)

        cfg.eveowners.Prime(toPrime)
        filterValue = self.filterCombo.GetValue()
        scrollList = []
        for agent in allCareerAgents:
            if filterValue and filterValue not in (agent.divisionID, agent.factionID):
                continue
            agentName = cfg.eveowners.Get(agent.agentID).name
            entry = GetFromClass(AgentEntry, {'charID': agent.agentID})
            scrollList.append((agentName, entry))

        scrollList = SortListOfTuples(scrollList)
        self.agentScroll.LoadContent(contentList=scrollList)

    def GetAllCareerAgents(self):
        allCareerAgents = sm.GetService('agents').GetAgentsByType(appConst.agentTypeCareerAgent)
        return allCareerAgents

    def OpenAll(self, *args):
        uthread2.StartTasklet(self._OpenAll_thread)

    def _OpenAll_thread(self):
        allCareerAgents = self.GetAllCareerAgents()
        for node in self.agentScroll.GetNodes():
            sm.GetService('agents').OpenDialogueWindow(node.charID)
            blue.pyos.BeNice()

    def CloseAllAgentWnds(self, *args):
        agentSvc = sm.GetService('agents')
        for agentID in agentSvc.agentDialogWindows.keys():
            window = agentSvc.agentDialogWindows.pop(agentID, None)
            if window or not window.destroyed:
                window.Close()

    def OnComboChanged(self, *args):
        self.filterCombo.UpdateSettings()
        self.LoadAgents()
