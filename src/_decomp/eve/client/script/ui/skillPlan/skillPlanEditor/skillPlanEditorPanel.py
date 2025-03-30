#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanEditor\skillPlanEditorPanel.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from eve.client.script.ui.skillPlan import skillPlanUISignals
from eve.client.script.ui.skillPlan.skillPlanEditor.skillPlanEditorContents import SkillPlanEditorContents
from eve.client.script.ui.skillPlan.skillPlanEditor.skillPlanEditorOverview import SkillPlanEditorOverview
from eve.client.script.ui.skillPlan.skillPlanEditor.skillPlanSkillsCatalogue import SkillPlanEditorSkillsCataloguePanel
from skills.skillplan.skillPlanDiff import IsEditedPlanDifferentFromOriginal

class SkillPlanEditorPanel(Container):

    def ApplyAttributes(self, attributes):
        super(SkillPlanEditorPanel, self).ApplyAttributes(attributes)
        skillPlan = attributes.skillPlan
        rightCont = Container(name='rightCont', parent=self, align=uiconst.TORIGHT_PROP, width=0.5)
        leftCont = Container(name='mainCont', parent=self, align=uiconst.TOALL, padRight=32)
        self.ConstructSkillCatalogue(leftCont, skillPlan)
        self.skillPlanOverview = SkillPlanEditorOverview(parent=rightCont, align=uiconst.TORIGHT_PROP, width=0.5, maxWidth=350, padding=(32, 50, 0, 0))
        self.skillPlanContents = SkillPlanEditorContents(parent=rightCont, padTop=44)
        self.SetSkillPlan(skillPlan)

    def ConstructSkillCatalogue(self, leftCont, skillPlan):
        backButtonCont = Container(parent=leftCont, align=uiconst.TOTOP, height=44)
        self.backButton = Button(parent=backButtonCont, name='backButton', align=uiconst.TOPLEFT, iconSize=20, texturePath='res:/UI/Texture/classes/SkillPlan/buttonIcons/backIcon.png', func=self.OnBack)
        self.skillCatalogue = SkillPlanEditorSkillsCataloguePanel(name='skillsCatalogue', parent=leftCont, skillPlan=skillPlan)
        self.skillCatalogue.ConstructLayout()

    def SetSkillPlan(self, skillPlan):
        self.skillPlanContents.SetSkillPlan(skillPlan)
        self.skillCatalogue.SetSkillPlan(skillPlan)
        self.skillPlanOverview.SetSkillPlan(skillPlan)

    def OnBack(self, *args):
        if not self.ShouldContinueAfterAskingAboutLeavingEditor():
            return
        skillPlanUISignals.on_close_new_button()

    def ShouldContinueAfterAskingAboutLeavingEditor(self):
        skillPlan = self.skillPlanOverview.skillPlan
        if skillPlan:
            self.skillPlanOverview.SetNameAndDescriptionInPlan()
            if IsEditedPlanDifferentFromOriginal(skillPlan):
                if eve.Message('AskCloseSkillPlanEditor', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return False
        return True
