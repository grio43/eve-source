#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shipTree\skillLevelsCont.py
import carbonui.const as uiconst
import localization
from carbonui import TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
import clonegrade
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
BLUE_COLOR = (0.0, 0.52, 0.67, 1.0)
LIGHTBLUE_COLOR = (0.6, 0.8, 0.87, 1.0)
OMEGA_COLOR = Color(*clonegrade.COLOR_OMEGA_ORANGE).SetAlpha(0.8).GetRGBA()

class SkillLevelsCont(Container):
    default_align = uiconst.TORIGHT
    default_state = uiconst.UI_NORMAL
    default_width = 47
    default_height = 10
    default_frameColor = (1.0, 1.0, 1.0, 0.3)
    default_bgColor = (1.0, 1.0, 1.0, 0.0)
    default_barColor = (1.0, 1.0, 1.0, 0.5)

    def ApplyAttributes(self, attributes):
        import expertSystems.client
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.get('typeID', None)
        self.groupID = attributes.get('groupID', None)
        self.barColor = attributes.get('barColor', self.default_barColor)
        frameColor = attributes.get('frameColor', self.default_frameColor)
        bgColor = attributes.get('bgColor', self.default_bgColor)
        self.bgFrame = Frame(bgParent=self, color=frameColor)
        self.bgFill = Fill(bgParent=self, color=bgColor)
        self.cnts = []
        self.bars = []
        self.lines = []
        for i in xrange(5):
            padLeft = 2 if i == 0 else 1
            cnt = Container(parent=self, name='cnt_level%d' % i, align=uiconst.TOLEFT_PROP, width=0.2, padding=(padLeft,
             2,
             0,
             2))
            line = Fill(parent=cnt, name='level%d' % i, align=uiconst.TOBOTTOM_NOPUSH, color=expertSystems.Color.base, height=1)
            bar = Fill(parent=cnt, name='bar_level%d' % i, align=uiconst.TOALL, color=self.barColor)
            self.cnts.append(cnt)
            self.bars.append(bar)
            self.lines.append(line)

        self.Update()

    def Update(self):
        skill = self.GetSkill()
        self.SetLevel(skill)

    def SetBarPadding(self, padding):
        for i, bar in enumerate(self.cnts):
            if i == 0:
                bar.padLeft = padding + 1
            else:
                bar.padLeft = padding

    def GetSkill(self):
        return sm.GetService('skills').GetSkill(self.typeID)

    def GetMyLevel(self):
        return sm.GetService('skills').GetMyLevelIncludingLapsed(self.typeID)

    def SetLevel(self, skill):
        cloneGradeSvc = sm.GetService('cloneGradeSvc')
        skillQueue = sm.GetService('skillqueue').GetQueue()
        skillInTraining = sm.GetService('skillqueue').SkillInTraining()
        myLevel = self.GetMyLevel()
        level = myLevel if myLevel else 0
        effectiveLevel = skill.effectiveSkillLevel if skill else 0
        if skill and skill.trainedSkillPoints == 0:
            hint = localization.GetByLabel('UI/SkillQueue/Skills/SkillNotTrained')
        elif level == 5:
            hint = localization.GetByLabel('UI/SkillQueue/Skills/SkillAtMaximumLevel')
        else:
            hint = localization.GetByLabel('UI/SkillQueue/Skills/SkillAtLevel', skillLevel=level)
        inTraining = 0
        plannedInQueue = 0
        for trainingSkill in skillQueue:
            if trainingSkill.trainingTypeID == self.typeID:
                plannedInQueue = trainingSkill.trainingToLevel

        if skillInTraining and skillInTraining.typeID == self.typeID:
            inTraining = 1
        for i in xrange(5):
            fill = self.bars[i]
            line = self.lines[i]
            fill.SetRGBA(*self.barColor)
            if level > i:
                fill.display = True
                if not cloneGradeSvc.IsOmega() and cloneGradeSvc.IsSkillLevelRestricted(self.typeID, i + 1):
                    fill.SetRGBA(*OMEGA_COLOR)
            else:
                fill.display = False
            if effectiveLevel > i:
                line.display = True
            else:
                line.display = False
            if plannedInQueue and i >= level and i <= plannedInQueue - 1:
                hint = localization.GetByLabel('UI/SkillQueue/Skills/SkillTrainingToLevel', skillLevel=plannedInQueue)
                fill.SetRGBA(*BLUE_COLOR)
                fill.display = True
            if inTraining and i == level:
                fill.SetRGBA(*LIGHTBLUE_COLOR)
                sm.GetService('ui').BlinkSpriteA(fill, 1.0, time=1000.0, maxCount=0, passColor=0, minA=0.5)

        self.hint = hint
