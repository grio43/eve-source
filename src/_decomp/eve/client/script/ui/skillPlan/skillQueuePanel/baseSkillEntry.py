#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillQueuePanel\baseSkillEntry.py
import dogma.data as dogma_data
import localization
from carbonui import uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.common.lib import appConst
from localization.formatters.timeIntervalFormatters import FormatTimeIntervalShortWritten
BLUE_COLOR = (0.0, 0.52, 0.67, 1.0)
LIGHTBLUE_COLOR = (0.6, 0.8, 0.87, 1.0)
WHITE_COLOR = (1.0, 1.0, 1.0, 0.5)

class BaseSkillEntry(SE_BaseClassCore):
    __guid__ = 'listentry.BaseSkillEntry'
    __nonpersistvars__ = ['selection', 'id']
    lasttime = None
    lastprogress = None
    lastrate = None
    timer = None
    totalpoints = None
    hilitePartiallyTrained = None
    blueColor = BLUE_COLOR
    lightBlueColor = LIGHTBLUE_COLOR
    whiteColor = WHITE_COLOR
    skillPointsText = ''
    rank = 0.0
    default_highlightClass = ListEntryUnderlay

    def _OnClose(self, *args, **kw):
        super(BaseSkillEntry, self)._OnClose(*args, **kw)
        self.timer = None

    def ApplyAttributes(self, attributes):
        super(BaseSkillEntry, self).ApplyAttributes(attributes)
        self.inTrainingHilite = None
        self.timeLeftContainer = ContainerAutoSize(name='TimeLeftCont', parent=self, align=uiconst.TORIGHT, padding=(4, 0, 20, 0))
        self.textCont = Container(name='textCont', parent=self, align=uiconst.TOALL, padLeft=77, clipChildren=1)
        self.nameLevelLabel = None
        self.CheckConstructNameLevelLabel()
        self.timeLeftText = None
        self.endOfTraining = None
        self.skillBarInitialized = False
        self.skill_service = sm.GetService('skills')

    def CheckConstructNameLevelLabel(self):
        if not self.nameLevelLabel:
            cont = ContainerAutoSize(parent=self.textCont, align=uiconst.TOLEFT)
            self.nameLevelLabel = EveLabelLarge(name='nameLevelLabel', text='', parent=cont, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT)

    def CheckConstructInTrainingHiglight(self):
        if not self.inTrainingHilite:
            self.inTrainingHilite = Fill(parent=self, name='inTrainingHilite', padTop=1, padBottom=1, color=self.blueColor, opacity=0.15, state=uiconst.UI_HIDDEN)

    def Load(self, node):
        self.sr.node = node
        self.sr.node.meetRequirements = False
        self.lasttime = None
        self.lastsecs = None
        self.lastpoints = None
        self.timer = None
        self.endOfTraining = None
        data = node
        self.rec = data.skill
        trainedSkillLevel = data.skill.trainedSkillLevel or 0
        trainedSkillPoints = data.skill.trainedSkillPoints or 0
        if not self.skillBarInitialized:
            self.skillBarInitialized = True
            SkillBar(parent=self, align=uiconst.CENTERLEFT, left=2, state=uiconst.UI_DISABLED, skillID=self.rec.typeID, overrideLevel=node.trainToLevel, requiredLevel=node.trainToLevel)
            if trainedSkillLevel < 5:
                duration = long(self.skill_service.GetRawTrainingTimeForSkillLevel(self.rec.typeID, trainedSkillLevel + 1))
                self.timeLeftText = EveLabelLarge(parent=self.timeLeftContainer, align=uiconst.CENTERRIGHT, text=self._GetTimeLeftText(duration))
        self.skillPointsText = ''
        self.rank = 0.0
        if data.trained:
            self.rank = int(data.skill.skillRank + 0.4)
            spHi = sm.GetService('skills').SkillpointsNextLevel(data.skill.typeID) or 0.0
            if trainedSkillLevel >= 5:
                self.skillPointsText = localization.GetByLabel('UI/SkillQueue/Skills/SkillPointsValue', skillPoints=int(trainedSkillPoints))
            else:
                self.skillPointsText = localization.GetByLabel('UI/SkillQueue/Skills/SkillPointsAndNextLevelValues', skillPoints=int(trainedSkillPoints), skillPointsToNextLevel=int(spHi + 0.5))
                self.sr.node.meetRequirements = True
            self.hint = None
        else:
            self.sr.node.meetRequirements = sm.GetService('skills').IsSkillRequirementMet(data.invtype)
            if self.sr.node.meetRequirements:
                tappend = localization.GetByLabel('UI/SkillQueue/Skills/SkillRequirementsMet')
            else:
                tappend = localization.GetByLabel('UI/SkillQueue/Skills/SkillRequirementsNotMet')
            self.skillPointsText = tappend
            self.hint = tappend
            for each in dogma_data.get_type_attributes(data.invtype):
                if each.attributeID == const.attributeSkillTimeConstant:
                    self.rank = int(each.value)

        if data.Get('inTraining', 0):
            self.CheckConstructInTrainingHiglight()
            self.inTrainingHilite.state = uiconst.UI_DISABLED
        elif self.inTrainingHilite:
            self.inTrainingHilite.Hide()
        if data.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()

    def _GetTimeLeftText(self, duration):
        if duration > appConst.DAY:
            showTo = 'hour'
        elif duration > appConst.HOUR:
            showTo = 'minute'
        else:
            showTo = 'second'
        return FormatTimeIntervalShortWritten(duration, showFrom='day', showTo=showTo)

    def OnSkillpointChange(self, skillPoints = None):
        if self.destroyed:
            return
        skill = self.rec
        self.CheckConstructNameLevelLabel()
        self.nameLevelLabel.text = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndRankValue', skill=skill.typeID, rank=int(skill.skillRank + 0.4))

    def OnMouseEnter(self, *args):
        if hasattr(self, 'rec') and not sm.GetService('skills').HasSkill(self.rec.typeID):
            return
        super(BaseSkillEntry, self).OnMouseEnter(*args)

    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(self.rec.typeID, None)

    def SetTimeLeft(self, timeLeft):
        if not self.destroyed and self.timeLeftText:
            if timeLeft is None:
                timeLeftText = ''
            elif timeLeft <= 0:
                timeLeftText = localization.GetByLabel('UI/SkillQueue/Skills/CompletionImminent')
            else:
                timeLeftText = self._GetTimeLeftText(long(timeLeft))
            self.timeLeftText.text = timeLeftText
