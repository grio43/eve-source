#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\skillBar\skillLevel.py
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
import clonegrade
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1
import uthread
BOX_SIZE = 10
BOX_SIZE_SMALL = 4
COLOR_NOT_REQUIRED = (0, 0, 0, 0.9)
COLOR_UNTRAINED = (1.0, 1.0, 1.0, 0.3)
COLOR_TRAINED = (0.8, 0.8, 0.8, 1.0)
COLOR_TRAINED_OMEGA = Color(*clonegrade.COLOR_OMEGA_ORANGE).SetAlpha(0.8).GetRGBA()
COLOR_REQUIRES_OMEGA = Color(*clonegrade.COLOR_OMEGA_ORANGE).SetAlpha(0.6).GetRGBA()
COLOR_QUEUED = COLOR_SKILL_1

class SkillLevel(Container):
    default_width = 12
    default_height = 12
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(SkillLevel, self).ApplyAttributes(attributes)
        self.skill = attributes.get('controller')
        self.level = attributes.get('level')
        self.boxSize = attributes.get('boxSize', BOX_SIZE)
        self.showEmpty = attributes.get('showEmpty', False)
        self.Layout()
        self.skill.onUpdate.connect(self.Refresh)

    def Refresh(self):
        self.Flush()
        self.Layout()

    def Layout(self):
        import expertSystems.client
        if self.skill.requiredLevel and not self.isRequired:
            if self.showEmpty:
                self.AddBox((0, 0, 0, 0.9))
            return
        if self.skill.IsLevelTrainedByExpertSystem(self.level) and expertSystems.is_expert_systems_enabled():
            Container(parent=self, name='expertSystemUnderline', align=uiconst.TOBOTTOM_NOPUSH, bgColor=expertSystems.Color.base, height=2, top=-2, padding=(1, 0, 1, 0))
        if self.isTraining:
            self.AddInTraining(COLOR_TRAINED)
        elif self.isTrained:
            if self.isOmega and self.isRestricted:
                self.AddBox(COLOR_TRAINED_OMEGA)
            else:
                self.AddBox(COLOR_TRAINED)
        elif self.isTrainable:
            if self.isQueued:
                self.AddBox(COLOR_QUEUED)
            else:
                self.AddBox(COLOR_UNTRAINED)
            if self.isPartiallyTrained:
                self.AddPartiallyTrained(COLOR_TRAINED)
        elif self.isOmega and self.isRestricted:
            self.AddBoxSmall(COLOR_REQUIRES_OMEGA)
        else:
            self.AddBoxSmall(COLOR_UNTRAINED)

    def AddInTraining(self, color):
        box = self.AddBox(color)

        def thread():
            while not box.destroyed:
                animations.SpColorMorphTo(box, startColor=COLOR_QUEUED, endColor=color, duration=0.4, timeOffset=0.5, sleep=True)
                animations.SpColorMorphTo(box, startColor=color, endColor=COLOR_QUEUED, duration=0.8, timeOffset=0.2, sleep=True)

        uthread.new(thread)

    def AddBox(self, color):
        return Fill(parent=self, align=uiconst.CENTER, pos=(0,
         0,
         self.boxSize,
         self.boxSize), color=color)

    def AddBoxSmall(self, color):
        Fill(parent=self, align=uiconst.CENTER, pos=(0,
         0,
         BOX_SIZE_SMALL,
         BOX_SIZE_SMALL), color=color, idx=0)

    def AddOmegaLocked(self):
        Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/SkillBar/OmegaLocked.png', color=COLOR_TRAINED_OMEGA, pos=(0, 0, 12, 12))

    def AddPartiallyTrained(self, color):
        Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/SkillBar/PartiallyTrained.png', color=color, pos=(0,
         0,
         self.boxSize + 2,
         self.boxSize + 2), idx=0)

    @property
    def isTrained(self):
        return self.level <= self.skill.level

    @property
    def isTrainable(self):
        return self.skill.IsLevelTrainable(self.level)

    @property
    def isQueued(self):
        return self.skill.IsLevelQueued(self.level)

    @property
    def isTraining(self):
        return self.skill.IsLevelTraining(self.level)

    @property
    def isPartiallyTrained(self):
        return self.level == self.skill.level + 1 and self.skill.isPartiallyTrained

    @property
    def isRequired(self):
        if self.skill.requiredLevel is None:
            return False
        return self.level <= self.skill.requiredLevel

    @property
    def isRestricted(self):
        return self.skill.isRestricted

    @property
    def isOmega(self):
        return self.skill.restrictedLevel < self.level
