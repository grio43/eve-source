#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanEditor\skillPlanEditorOverview.py
import evetypes
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.commonutils import StripTags
from carbonui import Density, uiconst
from carbonui.button import styling
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from characterdata import careerpath
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.skillPlan import skillPlanUISignals
from eve.client.script.ui.skillPlan.controls.milestoneIndicatorHeader import LoadMilestonesTooltipPanel
from eve.client.script.ui.skillPlan.milestone.skillPlanProgressIndicatorEditable import SkillPlanProgressIndicatorEditable
from localization import GetByLabel, GetByMessageID
from saveSkillPlanButton import SkillPlanEditorSaveButton
from skills.skillplan import skillPlanConst
from skills.skillplan.skillPlanConst import MAX_LEN_NAME, MAX_LEN_DESC
from skills.skillplan.skillPlanService import GetSkillPlanSvc

class SkillPlanEditorOverview(Container):

    def ApplyAttributes(self, attributes):
        super(SkillPlanEditorOverview, self).ApplyAttributes(attributes)
        self.skillPlan = None
        skillPlanUISignals.on_skill_requirements_changed.connect(self.OnSkillRequirementsChanged)
        skillPlanUISignals.on_milestone_added.connect(self.UpdateMilestoneCountLabel)
        skillPlanUISignals.on_milestone_removed.connect(self.UpdateMilestoneCountLabel)
        skillPlanUISignals.on_contents_list_started_reconstructing.connect(self.OnContentsListStartedReconstructing)
        skillPlanUISignals.on_contents_list_finished_reconstructing.connect(self.OnContentsListFinishedReconstructing)
        self.ConstructMilestoneEditor()
        self.detailsCont = ScrollContainer(parent=self, name='detailsCont')
        self._ConstructDetailsCont()
        self.buttonsCont = Container(parent=self, name='buttonsCont', align=uiconst.TOBOTTOM, height=styling.get_height(Density.NORMAL), padTop=10, idx=0)
        self._ConstructButtonsCont()
        self.UpdateSaveButtonState()

    def UpdateMilestoneCountLabel(self, *args):
        self.milestoneCountLabel.text = '%s/%s' % (len(self.skillPlan.GetMilestones()), skillPlanConst.MAX_NUM_MILESTONES)

    def _ConstructDetailsCont(self):
        EveLabelLarge(parent=self.detailsCont, align=uiconst.TOTOP, text=GetByLabel('UI/Common/Name'), padTop=12)
        self.nameEdit = SingleLineEditText(parent=self.detailsCont, align=uiconst.TOTOP, hintText=GetByLabel('UI/SkillPlan/EnterPlanName'), maxLength=MAX_LEN_NAME, showLetterCounter=True)
        self.nameEdit.OnChange = self.OnNameEditChanged
        EveLabelLarge(parent=self.detailsCont, align=uiconst.TOTOP, text=GetByLabel('UI/Common/Description'), padTop=12)
        self.descriptionEdit = EditPlainText(parent=self.detailsCont, align=uiconst.TOTOP, height=120, padTop=2, hintText=GetByLabel('UI/SkillPlan/EnterPlanDescription'), maxLength=MAX_LEN_DESC, allowFormatChanges=False)
        self.categoryCombo = Combo(name='categoryCombo', parent=self.detailsCont, align=uiconst.TOTOP, label=GetByLabel('UI/Common/Category'), padTop=32, options=self._GetCategoryComboOptions())

    def _GetCategoryComboOptions(self):
        options = [(GetByLabel('UI/Generic/None'), 0)]
        options += [ (GetByMessageID(c.nameID), cID) for cID, c in careerpath.get_career_paths().iteritems() ]
        return options

    def _ConstructButtonsCont(self):
        clearButtonParent = self.buttonsCont
        clearButtonParent = Container(parent=self.buttonsCont, align=uiconst.TOLEFT_PROP, width=0.5)
        self.clearButton = Button(name='clearButton', parent=clearButtonParent, align=uiconst.TOTOP, label=GetByLabel('UI/Inventory/Clear'), func=self.OnClearButton)
        saveButtonParent = self.buttonsCont
        saveButtonParent = Container(parent=self.buttonsCont, align=uiconst.TOALL, padLeft=4)
        self.saveButton = SkillPlanEditorSaveButton(name='saveButton', parent=saveButtonParent, align=uiconst.TOTOP, label=GetByLabel('UI/Common/Buttons/Save'), func=self.OnSaveButton)

    def OnSkillRequirementsChanged(self, skillPlanID):
        self.UpdateSaveButtonState()

    def OnNameEditChanged(self, _):
        self.UpdateSaveButtonState()

    def ConstructMilestoneEditor(self):
        topCont = Container(name='topCont', parent=self, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, height=20, padBottom=-6)
        topCont.LoadTooltipPanel = LoadMilestonesTooltipPanel
        EveLabelLarge(parent=topCont, name='skillPlanOverviewLabel', align=uiconst.TOPLEFT, text=GetByLabel('UI/SkillPlan/Milestones'))
        self.milestoneCountLabel = EveLabelLarge(parent=topCont, name='milestoneCountLabel', align=uiconst.TOPRIGHT)
        self.milestoneEditor = SkillPlanProgressIndicatorEditable(parent=self, align=uiconst.TOTOP_PROP, height=0.4)
        self.milestoneEditor.onMilestoneDataDroppedSignal.connect(self.OnMilestoneDataDropped)

    def OnMilestoneDataDropped(self, typeID, level, milestoneID = None):
        oldMilestone = milestoneID and self.skillPlan.GetMilestone(milestoneID)
        if oldMilestone:
            oldMilestoneTypeID = oldMilestone.GetTypeID()
            msgArgs = {'milestoneNameOld': evetypes.GetName(oldMilestoneTypeID),
             'milestoneNameNew': evetypes.GetName(typeID)}
            if eve.Message('ReplaceMilestoneWithNewMilestone', msgArgs, uiconst.YESNO) == uiconst.ID_YES:
                self.skillPlan.RemoveMilestone(milestoneID)
            else:
                return
        PlaySound(uiconst.SOUND_ADD_OR_USE)
        if level is None:
            self.skillPlan.AddTypeIDMilestone(typeID)
        else:
            self.skillPlan.AddSkillRequirementMilestone(typeID, level)

    def SetSkillPlan(self, skillPlan):
        self.skillPlan = skillPlan
        self.nameEdit.SetValue(self.skillPlan.GetName(), 0)
        self.descriptionEdit.SetText(self.skillPlan.GetDescription())
        if self.skillPlan.HasEditableCategoryID():
            self.categoryCombo.Show()
            self.categoryCombo.SetValue(self.skillPlan.GetCategoryID())
        else:
            self.categoryCombo.Hide()
        uthread2.StartTasklet(self.milestoneEditor.SetSkillPlan, self.skillPlan)
        self.UpdateSaveButtonState()
        self.UpdateMilestoneCountLabel()

    def OnClearButton(self, *args):
        if self.skillPlan:
            self.skillPlan.ClearSkillRequirements()
            self.skillPlan.ClearMilestones()
            self.nameEdit.Clear()
            self.categoryCombo.SetValue(0)
            self.descriptionEdit.Clear()
            skillPlanUISignals.on_skill_plan_cleared(self.skillPlan.GetID())

    def OnSaveButton(self, *args):
        self.skillPlan.AdjustMilestonesToAddAndDeletedIDs()
        self.SetNameAndDescriptionInPlan()
        if self.skillPlan.HasEditableCategoryID():
            self.skillPlan.SetCategoryID(self.categoryCombo.GetValue())
        GetSkillPlanSvc().Save(self.skillPlan)

    def SetNameAndDescriptionInPlan(self):
        if self.skillPlan:
            self.skillPlan.SetName(self.nameEdit.GetValue())
            desc = self.descriptionEdit.GetValue()
            desc = StripTags(desc, stripOnly=['font'])
            self.skillPlan.SetDescription(desc)

    def UpdateSaveButtonState(self):
        self.saveButton.UpdateState(self.skillPlan, self.nameEdit.GetValue(False))

    def OnContentsListStartedReconstructing(self):
        self.clearButton.Disable()
        self.saveButton.Disable()

    def OnContentsListFinishedReconstructing(self):
        self.clearButton.Enable()
        self.UpdateSaveButtonState()
