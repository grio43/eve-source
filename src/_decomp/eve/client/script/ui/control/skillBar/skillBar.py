#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\skillBar\skillBar.py
import carbonui.const as uiconst
import characterskills
from carbonui.primitives.container import Container
from eve.client.script.ui.control.skillBar.controller import CreateSkillBarController
from eve.client.script.ui.control.skillBar.skillLevel import BOX_SIZE
from skillLevel import SkillLevel

class SkillBar(Container):
    default_height = SkillLevel.default_height
    default_width = 5 * SkillLevel.default_width
    default_state = uiconst.UI_NORMAL
    default_name = 'SkillBar'
    isDragObject = True

    def ApplyAttributes(self, attributes):
        super(SkillBar, self).ApplyAttributes(attributes)
        if 'controller' in attributes:
            self.skill = attributes.get('controller')
        else:
            skillID = attributes.get('skillID', None)
            requiredLevel = attributes.get('requiredLevel', None)
            overrideLevel = attributes.get('overrideLevel', None)
            self._ConstructController(skillID, requiredLevel, overrideLevel)
        self.levelClass = attributes.get('levelClass', SkillLevel)
        self.boxSize = attributes.get('boxSize', BOX_SIZE)
        self.showEmpty = attributes.get('showEmpty', False)
        self.levels = []
        self.Layout()

    def _ConstructController(self, skillID, requiredLevel = None, overrideLevel = None):
        self.skill = CreateSkillBarController(skillID, requiredLevel=requiredLevel, overrideLevel=overrideLevel)

    def Layout(self):
        self.Flush()
        self.levels = []
        for x in range(characterskills.MAX_SKILL_LEVEL):
            level = self.levelClass(name='SkillLevel%d' % (x + 1), parent=self, align=uiconst.TOLEFT, controller=self.skill, level=x + 1, boxSize=self.boxSize, showEmpty=self.showEmpty)
            self.levels.append(level)

    def SetSkillID(self, skillID):
        self._ConstructController(skillID=skillID)
        self.Layout()

    def SetRequiredLevel(self, level):
        self.skill.requiredLevel = level

    def GetMenu(self):
        return self.skill.GetMenu()

    def GetDragData(self):
        return self.skill.GetDragData()

    def Update(self):
        self.skill.onUpdate()

    def Refresh(self):
        for level in self.levels:
            level.Refresh()
