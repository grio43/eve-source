#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\tooltip\skillBtns.py
import eveformat
import eveicon
import uthread2
from carbonui.primitives.container import Container
from eve.client.script.ui.eveThemeColor import THEME_FOCUSDARK
from localization import GetByLabel
import inventorycommon.const as invConst
from carbonui import ButtonVariant, Density, uiconst, TextColor, AxisAlignment, TextBody, TextDetail
from carbonui.button.group import ButtonSizeMode, ButtonGroup
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.shared.neocom import skillConst
from eve.client.script.ui.shared.tooltip.itemObject import ItemObject
from eve.client.script.ui.skilltrading.applySkillPointsWindow import ApplySkillPointsWindow
from skills.skillplan.skillPlanTemplate import TypeRequirementSkillPlanTemplate, RequirementListSkillPlanTemplate
from skills.skillplan.skillPlanConst import MAX_PERSONAL_PLANS
from skills.skillplan.skillPlanService import GetSkillPlanSvc
from eve.client.script.ui.skillPlan import skillPlanUtil
from eve.client.script.ui.skillPlan.skillPlanConst import BUTTON_GROUP_ID_SKILL_PLANS, BUTTON_GROUP_ID_TOP_LEVEL, PANEL_SKILL_PLANS, PANEL_PERSONAL

class SkillActionContainer(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    isDragObject = False

    def ApplyAttributes(self, attributes):
        super(SkillActionContainer, self).ApplyAttributes(attributes)
        self.required_skills = attributes.get('requiredSkills', None)
        self._missing_skills = attributes.get('missingSkills', None)
        self.type_id = attributes.get('typeID', None)
        self.item = attributes.get('item', None)
        self.on_click = attributes.get('on_click', None)
        self.skill_plan_name = attributes.get('skillPlanName', None)
        skillSvc = sm.GetService('skills')
        itemObject = ItemObject(itemTypeID=self.type_id, item=self.item)
        if not self.required_skills:
            self.required_skills = skillSvc.GetSkillsMissingToUseItemRecursiveList(self.type_id)
        if not self._missing_skills:
            if self.type_id or self.item:
                self._missing_skills = skillSvc.GetMissingSkillBooksFromList(self.required_skills)
            else:
                self._missing_skills = []
        is_rare_skill = False
        has_rare_req = False
        if len(self._missing_skills) and self.type_id:
            is_rare_skill = itemObject.IsRareSkill()
            has_rare_req = itemObject.IsMissingRarePrereqs()
        all_expanded_skill_requirements = self.GetSkillsMissingToUseItemExpandedList(skillSvc, self.required_skills)
        expanded_skill_requirements = [ x for x in all_expanded_skill_requirements if x[0] not in self._missing_skills ]
        required_skill_points = self.GetRequiredSkillPoints(all_expanded_skill_requirements)
        skill_point_container = Container(parent=self, align=uiconst.TOTOP, height=32, padBottom=8)
        ApplySkillPointsButton(parent=skill_point_container, align=uiconst.TORIGHT, padLeft=8, on_click=self.on_click, variant=ButtonVariant.GHOST, skillTypeIDsAndLevels=expanded_skill_requirements, offer_injection=len(self._missing_skills) == 0)
        skill_point_label_container = Container(parent=skill_point_container, align=uiconst.TOALL, bgColor=THEME_FOCUSDARK.rgb + (0.1,))
        sp_value_cont = ContainerAutoSize(parent=skill_point_label_container, align=uiconst.TORIGHT)
        sp_value = TextDetail(parent=sp_value_cont, align=uiconst.CENTERRIGHT, text=eveformat.number(required_skill_points), padRight=12)
        sp_label_cont = Container(parent=skill_point_label_container, align=uiconst.TOALL, clipChildren=True)
        sp_label = TextDetail(parent=sp_label_cont, align=uiconst.CENTERLEFT, padLeft=8, text=GetByLabel('UI/Skills/SkillPointsRequired'), color=TextColor.SECONDARY, autoFadeSides=16)
        btn_group = ButtonGroup(parent=self, align=uiconst.TOTOP, density=Density.NORMAL, button_alignment=AxisAlignment.END, button_size_mode=ButtonSizeMode.DYNAMIC_STRETCH, ignore_overflow=True)
        if self.type_id:
            skill_plan_template = TypeRequirementSkillPlanTemplate(self.type_id)
        else:
            skill_plan_template = RequirementListSkillPlanTemplate(self.required_skills, self.skill_plan_name)
        if len(self._missing_skills) > 0:
            BuyAndTrainButton(parent=btn_group, on_click=self.on_click, requiredSkills=all_expanded_skill_requirements, missingSkills=self._missing_skills, variant=ButtonVariant.NORMAL, isRarePreReqs=has_rare_req, isRareSkill=is_rare_skill, skillPlanTemplate=skill_plan_template)
        else:
            AddToQueueButton(parent=btn_group, on_click=self.on_click, requiredSkills=expanded_skill_requirements, variant=ButtonVariant.NORMAL)
        CreateSkillPlanButton(parent=btn_group, on_click=self.on_click, skillPlanTemplate=skill_plan_template, variant=ButtonVariant.GHOST)

    def GetRequiredSkillPoints(self, skill_ids_and_levels):
        svc = sm.GetService('skills')
        return sum(svc.GetSkillPointsRequiredForSkills(skill_ids_and_levels).itervalues())

    def GetSkillsMissingToUseItemExpandedList(self, skillSvc, requiredSkills):
        ret = []
        for skillTypeID, level in requiredSkills:
            trainedLevel = skillSvc.GetMyLevel(skillTypeID)
            if trainedLevel is None:
                trainedLevel = 0
            for i in range(level + 1):
                if i <= 0:
                    continue
                if i <= trainedLevel:
                    continue
                ret.append((skillTypeID, i))

        return ret


class _SkillActionButton(Button):

    def ApplyAttributes(self, attributes):
        self._isFinished = False
        super(_SkillActionButton, self).ApplyAttributes(attributes)
        self.UpdateState()
        self.func = self.ClickFunc
        self.on_click = attributes.get('on_click', None)

    def ClickFunc(self, *args):
        if self.on_click:
            self.on_click()

    def UpdateState(self):
        self.UpdateLabel()
        self.UpdateIcon()

    def UpdateLabel(self):
        self.label = self._GetText()

    def UpdateIcon(self):
        self.texturePath = self._GetIcon()

    def _GetIcon(self):
        return None

    def _GetText(self):
        return None


class AddToQueueButton(_SkillActionButton):

    def ApplyAttributes(self, attributes):
        self.requiredSkills = attributes.requiredSkills
        queueSvc = sm.GetService('skillqueue')
        allSkillsInQueue = True
        for skillID, level in self.requiredSkills:
            if not queueSvc.IsSkillInQueue(skillID):
                allSkillsInQueue = False
                break
            if queueSvc.FindHighestLevelInQueue(skillID) < level:
                allSkillsInQueue = False
                break

        attributes.enabled = not allSkillsInQueue
        super(AddToQueueButton, self).ApplyAttributes(attributes)
        self._isFinished = allSkillsInQueue
        self.UpdateLabel()

    def ClickFunc(self, *args):
        super(AddToQueueButton, self).ClickFunc(*args)
        self.Disable()
        try:
            sm.GetService('skillqueue').AddSkillsToQueue(self.requiredSkills, ignoreAlreadyPresent=True)
            sm.GetService('skillqueue').CommitTransaction(activate=True)
            self._isFinished = True
        except Exception:
            self.Enable()

        self.UpdateState()

    def _GetText(self):
        return GetByLabel('UI/Skills/TrainSkills')

    def GetHint(self):
        if self._isFinished:
            return GetByLabel('Tooltips/SkillPlanner/AddAllSkillsToQueueButtonFinished')
        return GetByLabel('Tooltips/SkillPlanner/AddAllSkillsToQueueButton')


class ApplySkillPointsButton(_SkillActionButton):

    def ApplyAttributes(self, attributes):
        self._offer_injection = attributes.offer_injection
        super(ApplySkillPointsButton, self).ApplyAttributes(attributes)
        self.skillTypeIDsAndLevels = attributes.skillTypeIDsAndLevels

    def ClickFunc(self, *args):
        super(ApplySkillPointsButton, self).ClickFunc(*args)
        if sm.GetService('skills').GetFreeSkillPoints():
            wnd = ApplySkillPointsWindow.GetIfOpen()
            if wnd:
                wnd.CloseByUser()
                uthread2.sleep(0.05)
            ApplySkillPointsWindow.Open(skillTypeIDsAndLevels=self.skillTypeIDsAndLevels)
        elif sm.GetService('cloneGradeSvc').IsOmega():
            sm.GetService('marketutils').ShowMarketDetails(invConst.typeSkillInjector, None)
        else:
            sm.GetService('vgsService').OpenStore(typeIds=[invConst.typeAlphaTrainingInjector])

    def UpdateState(self):
        if sm.GetService('skills').GetFreeSkillPoints():
            self.hint = GetByLabel('UI/SkillQueue/ApplySkillPoints')
            self.texturePath = eveicon.add
            self.enabled = self._offer_injection
        elif sm.GetService('cloneGradeSvc').IsOmega():
            self.hint = GetByLabel('UI/Market/MarketQuote/BuyType', typeID=invConst.typeSkillInjector)
            self.texturePath = 'res:/UI/Texture/classes/skilltrading/marketSkillinjector.png'
            self.enabled = True
        else:
            self.hint = GetByLabel('UI/Market/MarketQuote/BuyType', typeID=invConst.typeAlphaTrainingInjector)
            self.texturePath = 'res:/UI/Texture/classes/skilltrading/alphaSkillInjector.png'
            self.enabled = True


class CreateSkillPlanButton(_SkillActionButton):

    def ApplyAttributes(self, attributes):
        super(CreateSkillPlanButton, self).ApplyAttributes(attributes)
        self.skillPlanTemplate = attributes.skillPlanTemplate

    def ClickFunc(self, *args):
        super(CreateSkillPlanButton, self).ClickFunc(*args)
        template = self.skillPlanTemplate
        if not self._CanCreatePlan():
            skillPlanUtil.SetPersistedPanelID(BUTTON_GROUP_ID_TOP_LEVEL, PANEL_SKILL_PLANS)
            skillPlanUtil.SetPersistedPanelID(BUTTON_GROUP_ID_SKILL_PLANS, PANEL_PERSONAL)
            template = None
        sm.GetService('cmd').OpenSkillsWindow(forceClose=True, skillPlanTemplate=template)

    def _GetIcon(self):
        return eveicon.skill_plan

    def GetHint(self):
        hint = GetByLabel('Tooltips/SkillPlanner/SkillPlanButtonTooltip')
        numPlans = len(GetSkillPlanSvc().GetAllPersonal())
        if self._CanCreatePlan():
            return hint
        else:
            return u'{}\n\n<color={}>{}</color>'.format(hint, TextColor.WARNING, GetByLabel('UI/SkillPlan/MaximumSkillPlanReached', numPlans=numPlans))

    def _CanCreatePlan(self):
        numPlans = len(GetSkillPlanSvc().GetAllPersonal())
        return numPlans < MAX_PERSONAL_PLANS


class BuyAndTrainButton(_SkillActionButton):
    default_name = 'BuyAndTrainButton'

    def ApplyAttributes(self, attributes):
        super(BuyAndTrainButton, self).ApplyAttributes(attributes)
        self.requiredSkills = attributes.requiredSkills
        self.missingSkills = attributes.missingSkills
        self.isRarePreReqs = attributes.get('isRarePreReqs', False)
        self.isRareSkill = attributes.get('isRareSkill', False)
        self.skillPlanTemplate = attributes.get('skillPlanTemplate', None)
        self._isFinished = False
        self.skillSvc = sm.GetService('skills')
        self.func = self.ClickFunc
        self.UpdateState()

    def IsActive(self):
        if self._isFinished:
            return False
        if self.isRarePreReqs:
            return False
        if len(self.missingSkills) == 0:
            return False
        return True

    def ClickFunc(self, *args):
        super(BuyAndTrainButton, self).ClickFunc(*args)
        self.Disable()
        try:
            if self.missingSkills:
                skills_purchased = self.skillSvc.PurchaseSkills(self.missingSkills, skillPlanTemplate=self.skillPlanTemplate)
                if skills_purchased:
                    self.skillSvc.WaitUntilSkillsAreAvailable(skills_purchased)
                    if len(skills_purchased) == len(self.missingSkills):
                        self.missingSkills = []
                    else:
                        self.missingSkills = [ typeID for typeID in self.missingSkills if typeID not in skills_purchased ]
                else:
                    self.Enable()
                    self.UpdateState()
                    return
            self._isFinished = not bool(self.missingSkills)
            if not self._isFinished:
                self.Enable()
                skillsToQueue = [ (typeID, level) for typeID, level in self.requiredSkills if typeID not in self.missingSkills ]
            else:
                skillsToQueue = self.requiredSkills
            sm.GetService('skillqueue').AddSkillsToQueue(skillsToQueue, ignoreAlreadyPresent=True)
            sm.GetService('skillqueue').CommitTransaction(activate=True)
        except Exception:
            self.Enable()
            raise

        self.UpdateState()

    def UpdateState(self):
        self.UpdateLabel()

    def UpdateLabel(self):
        self.label = self.GetText()

    def GetColor(self):
        if self.isRarePreReqs:
            return (1.0, 1.0, 1.0, 0.5)
        return skillConst.COLOR_SKILL_2

    def GetText(self):
        if self._isFinished:
            pass
        return GetByLabel('UI/Skills/BuyAndTrain')

    def UpdateIsEnabledByState(self):
        if self._isFinished or self.isRarePreReqs:
            self.Disable()
        else:
            self.Enable()

    def GetHint(self):
        if self.isRareSkill:
            if self.isRarePreReqs:
                return GetByLabel('UI/Skills/ErrorRareSkillAndRequirements')
            else:
                return GetByLabel('UI/Skills/ErrorRareSkill')
        if self.isRarePreReqs:
            return GetByLabel('UI/Skills/ErrorRareRequirements')
