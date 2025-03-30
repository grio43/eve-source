#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\skillHistoryPanel.py
import characterskills as charskills
import evetypes
from carbon.common.script.util.format import FmtDate
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.lib import appConst
from localization import GetByLabel
from localization.formatters.numericFormatters import FormatNumeric
from utillib import KeyVal
import blue
ACTIONS = {appConst.skillEventClonePenalty: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillClonePenalty'),
 appConst.skillEventTrainingStarted: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingStarted'),
 appConst.skillEventTrainingComplete: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingComplete'),
 appConst.skillEventTrainingCancelled: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingCanceled'),
 appConst.skillEventGMGive: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/GMGiveSkill'),
 appConst.skillEventQueueTrainingCompleted: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingComplete'),
 appConst.skillEventFreeSkillPointsUsed: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillPointsApplied'),
 appConst.skillEventSkillExtracted: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillLevelExtracted'),
 appConst.skillEventGift: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillGift')}
ENTRYHEIGHT = 40

class SkillHistoryPanel(Container):
    default_name = 'SkillHistoryPanel'
    __notifyevents__ = ['OnHighlightSkillHistorySkills']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))
        self.scroll.sr.id = 'charsheet_skillhistory'

    def LoadPanel(self):
        scrolllist = self.GetHistoryScrollList()
        self.scroll.Load(contentList=scrolllist, headers=[GetByLabel('UI/Common/Date'),
         GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Skill'),
         GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Action'),
         GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Level')], noContentHint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/NoRecordsFound'), reversesort=True)

    def GetHistoryScrollList(self):

        def GetPts(lvl):
            return charskills.GetSPForLevelRaw(stc, lvl)

        rs = sm.GetService('skills').GetSkillHistory()
        scrolllist = []
        for r in rs:
            skill = sm.GetService('skills').GetSkill(r.skillTypeID)
            if skill:
                stc = skill.skillRank
                levels = [0,
                 GetPts(1),
                 GetPts(2),
                 GetPts(3),
                 GetPts(4),
                 GetPts(5)]
                level = 5
                for i in range(len(levels)):
                    if levels[i] > r.absolutePoints:
                        level = i - 1
                        break

                data = KeyVal()
                data.label = FmtDate(r.logDate, 'ls') + '<t>'
                data.label += evetypes.GetName(r.skillTypeID) + '<t>'
                data.label += ACTIONS.get(r.eventTypeID, GetByLabel('UI/Generic/Unknown')) + '<t>'
                data.label += FormatNumeric(level)
                data.Set('sort_%s' % GetByLabel('UI/Common/Date'), r.logDate)
                data.id = r.skillTypeID
                data.level = level
                data.GetMenu = self.GetEntryMenu
                data.MenuFunction = self.GetEntryMenu
                data.OnDblClick = (self.OnEntryDblClick, data)
                addItem = GetFromClass(Generic, data=data)
                scrolllist.append(addItem)

        return scrolllist

    def GetEntryMenu(self, entry, *args):
        return [(GetByLabel('UI/Common/ShowInfo'), self.ShowInfo, (entry.sr.node.id, 1))]

    def ShowInfo(self, *args):
        skillID = args[0]
        sm.GetService('info').ShowInfo(skillID, None)

    def OnEntryDblClick(self, otherSelf, nodeData):
        skillTypeID = getattr(nodeData, 'id', None)
        if skillTypeID is not None:
            self.ShowInfo(skillTypeID)

    def OnHighlightSkillHistorySkills(self, skillTypeIds):
        self.DeselectAllNodes()
        blue.pyos.synchro.SleepWallclock(500)
        skillTypeIds = skillTypeIds[:]
        for node in self.scroll.GetNodes():
            recordKey = (node.id, node.level)
            if recordKey in skillTypeIds:
                self.scroll._SelectNode(node)
                skillTypeIds.remove(recordKey)

    def DeselectAllNodes(self):
        for node in self.scroll.GetNodes():
            self.scroll._DeselectNode(node)
