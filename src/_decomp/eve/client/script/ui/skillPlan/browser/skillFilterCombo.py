#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\skillFilterCombo.py
from carbonui.control.combo import Combo
from skills.skillConst import FILTER_SHOWALL, FILTER_TRAINABLENOW, FILTER_INJECTED, FILTER_HAVEPREREQUISITS
from localization import GetByLabel

class SkillFilterCombo(Combo):
    default_options = ((GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ShowAllSkills'), FILTER_SHOWALL),
     (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ShowOnlyCurrentSkills'), FILTER_INJECTED),
     (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ShowOnlyTrainableSkills'), FILTER_TRAINABLENOW),
     (GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ShowOnlyHavePrerequisits'), FILTER_HAVEPREREQUISITS))
    default_select = FILTER_SHOWALL

    def ApplyAttributes(self, attributes):
        super(SkillFilterCombo, self).ApplyAttributes(attributes)
