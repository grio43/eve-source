#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterskills\client\UI\missingSkillbooksWnd.py
import eveicon
import evetypes
import characterskills.common
from carbonui import uiconst, PickState, Axis, ButtonVariant, TextColor
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.window.resizer import Orientation
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.skillPlan import skillPlanUtil
from eve.client.script.ui.skillPlan.skillPlanConst import BUTTON_GROUP_ID_TOP_LEVEL, BUTTON_GROUP_ID_SKILL_PLANS, PANEL_SKILL_PLANS, PANEL_PERSONAL
from localization import GetByLabel
from skills.skillplan.skillPlanConst import MAX_PERSONAL_PLANS
from skills.skillplan.skillPlanService import GetSkillPlanSvc
MAIN_CONT_PADDING = 16
CONTENTS_CONT_PADDING = 12
WINDOW_WIDTH_DOUBLE = 360
WINDOW_WIDTH_SINGLE = 360
SKILL_LIST_MAX_HEIGHT = 100
CONTENT_SIZE_PROP_DOUBLE = 0.48
CONTENT_SIZE_PROP_SINGLE = 1.0
BUTTON_HEIGHT = 40
BUTTON_MIN_WIDTH = 130

class MissingSkillbooksWnd(Window):
    default_width = WINDOW_WIDTH_DOUBLE
    default_height = 300
    default_windowID = 'missingSkillbooksWnd'
    default_useDefaultPos = True
    default_captionLabelPath = 'UI/SkillPlan/MissingSkillbooksWindow/ConfirmPurchaseTitle'
    default_iconNum = 'res:/UI/Texture/WindowIcons/skills.png'

    def ApplyAttributes(self, attributes):
        super(MissingSkillbooksWnd, self).ApplyAttributes(attributes)
        self.MakeUnResizeable()
        self.context = attributes.context
        self.CreateBaseLayout()
        self.CreateAvailableForPurchaseLayout()
        self.CreateUnavailableForPurchaseLayout()
        self.CreateBottomButtonsLayout()
        self.UpdateLayout()
        self.UpdateHeight()

    def CreateBaseLayout(self):
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self.sr.main, align=uiconst.TOTOP)
        self.contentsCont = ContainerAutoSize(name='contentsCont', parent=self.mainCont, align=uiconst.TOTOP, padTop=CONTENTS_CONT_PADDING)
        self.availableForPurchaseCont = ContainerAutoSize(name='availableForPurchaseCont', parent=self.contentsCont, align=uiconst.TOTOP, height=CONTENT_SIZE_PROP_DOUBLE)
        self.bottomCont = ContainerAutoSize(name='bottomCont', parent=self.mainCont, align=uiconst.TOTOP, padTop=CONTENTS_CONT_PADDING)
        self.CreateSeparator()
        self.unavailableForPurchaseCont = ContainerAutoSize(name='unavailableForPurchaseCont', parent=self.contentsCont, align=uiconst.TOTOP, height=CONTENT_SIZE_PROP_DOUBLE)

    def CreateAvailableForPurchaseLayout(self):
        self.availableListScrollCont = None
        self.CreatePurchaseSectionTitle(self.availableForPurchaseCont, GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/AvailableForRemoteInjection'), on_click=lambda : self.ToggleSection(self.availableListScrollCont))
        self.availableListScrollCont = ScrollContainer(parent=self.availableForPurchaseCont, name='listScrollCont', align=uiconst.TOTOP, height=SKILL_LIST_MAX_HEIGHT)
        if len(self.context.available_for_purchase) > 0:
            skillNames = [ '- %s\n' % evetypes.GetName(type_id) for type_id in self.context.available_for_purchase ]
        else:
            skillNames = ''
        EveLabelMedium(parent=self.availableListScrollCont, name='skillListLabel', align=uiconst.TOTOP, text=skillNames)
        cost = sum(map(characterskills.common.get_direct_purchase_price, self.context.available_for_purchase))
        EveLabelMedium(parent=self.availableForPurchaseCont, name='priceLabel', align=uiconst.TOTOP, text=GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/PriceLabel', cost=cost), padTop=2)
        self.availableButtonGroup = ButtonGroup(parent=self.availableForPurchaseCont, align=uiconst.TOTOP, padTop=4, button_size_mode=ButtonSizeMode.STRETCH, orientation=Axis.VERTICAL)
        self.buyAndInjectButton = Button(parent=self.availableButtonGroup, name='buyAndInjectButton', label=GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/BuyAndInjectButton'), hint=GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/BuyAndInjectTooltip'), align=uiconst.TOTOP, func=self._OnBuyAndInjectButton)
        self.availableCheckMarketButton = Button(parent=self.availableButtonGroup, name='availableCheckMarketButton', label=GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/CheckMarketButton'), hint=GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/CheckMarketTooltip'), align=uiconst.TOTOP, func=self._OnAvailableCheckMarketButton, texturePath=eveicon.market_details, variant=ButtonVariant.GHOST)
        self.availableCreateSkillPlanButton = Button(parent=self.availableButtonGroup, name='createSkillPlanBtn', label=GetByLabel('Tooltips/SkillPlanner/SkillPlanButtonTooltip'), align=uiconst.TORIGHT, func=self._OnCreateSkillPlanButton, texturePath=eveicon.skill_plan, variant=ButtonVariant.GHOST)
        self.availableCreateSkillPlanButton.GetHint = self._GetSkillPlanButtonHint

    def CreateUnavailableForPurchaseLayout(self):
        self.unavailableListScrollCont = None
        self.CreatePurchaseSectionTitle(self.unavailableForPurchaseCont, GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/UnavailableForRemoteInjection'), eveColor.HOT_RED, on_click=lambda : self.ToggleSection(self.unavailableListScrollCont))
        self.unavailableListScrollCont = ScrollContainer(parent=self.unavailableForPurchaseCont, name='listScrollCont', align=uiconst.TOTOP, height=SKILL_LIST_MAX_HEIGHT)
        if len(self.context.unavailable_for_purchase) > 0:
            skillNames = [ '- %s\n' % evetypes.GetName(type_id) for type_id in self.context.unavailable_for_purchase ]
        else:
            skillNames = ''
        EveLabelMedium(parent=self.unavailableListScrollCont, name='skillListLabel', align=uiconst.TOTOP, text=skillNames)
        self.unavailableButtonGroup = ButtonGroup(parent=self.unavailableForPurchaseCont, align=uiconst.TOTOP, padTop=2, button_size_mode=ButtonSizeMode.STRETCH, orientation=Axis.VERTICAL)
        self.unavailableCheckMarketButton = Button(parent=self.unavailableButtonGroup, name='unavailableCheckMarketButton', label=GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/CheckMarketButton'), hint=GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/CheckMarketTooltip'), align=uiconst.TOTOP, func=self._OnUnavailableCheckMarketButton, texturePath=eveicon.market_details)
        self.unavailableCreateSkillPlanButton = Button(parent=self.unavailableButtonGroup, name='createSkillPlanBtn', label=GetByLabel('Tooltips/SkillPlanner/SkillPlanButtonTooltip'), align=uiconst.TORIGHT, func=self._OnCreateSkillPlanButton, texturePath=eveicon.skill_plan, variant=ButtonVariant.GHOST)
        self.unavailableCreateSkillPlanButton.GetHint = self._GetSkillPlanButtonHint

    def CreateBottomButtonsLayout(self):
        self.sharedButtonCont = ButtonGroup(name='sharedButtonCont', parent=self.bottomCont, align=uiconst.TOBOTTOM, height=BUTTON_HEIGHT, button_size_mode=ButtonSizeMode.STRETCH, orientation=Axis.VERTICAL)
        self.sharedCheckMarketButton = Button(parent=self.sharedButtonCont, name='sharedCheckMarketButton', label=GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/CheckMarketButton'), hint=GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/CheckMarketTooltip'), align=uiconst.TOBOTTOM, func=self._OnSharedCheckMarketButton, texturePath=eveicon.market_details)
        self.createSkillPlanButton = Button(parent=self.sharedButtonCont, name='createSkillPlanBtn', label=GetByLabel('Tooltips/SkillPlanner/SkillPlanButtonTooltip'), align=uiconst.TORIGHT, func=self._OnCreateSkillPlanButton, texturePath=eveicon.skill_plan, variant=ButtonVariant.GHOST)
        self.createSkillPlanButton.GetHint = self._GetSkillPlanButtonHint

    def CreateSeparator(self):
        self.separatorLine = Line(parent=self.contentsCont, align=uiconst.TOTOP, color=eveColor.ICE_WHITE, weight=1, opacity=0.5, padTop=10, padBottom=10)

    def CreatePurchaseSectionTitle(self, parentContainer, titleLabel, titleColor = None, on_click = None):
        return SkillListHeadingContainer(parent=parentContainer, name='mainTitleCont', align=uiconst.TOTOP, height=22, padBottom=4, titleLabel=titleLabel, titleColor=titleColor, on_click=on_click)

    def ToggleSection(self, section):
        section.display = not section.display
        self.UpdateHeight()

    def UpdateHeight(self):
        height = 0
        contentHeight = 0
        if self.availableForPurchaseCont.display:
            self.availableButtonGroup.FlagForceUpdateAlignment()
            self.availableButtonGroup._AssureAlignmentUpdated()
            self.availableForPurchaseCont.SetSizeAutomatically()
            contentHeight += self.availableForPurchaseCont.height
        if self.unavailableForPurchaseCont.display:
            if not self.availableForPurchaseCont.display:
                self.unavailableButtonGroup.FlagForceUpdateAlignment()
                self.unavailableButtonGroup._AssureAlignmentUpdated()
            self.unavailableForPurchaseCont.SetSizeAutomatically()
            contentHeight += self.unavailableForPurchaseCont.height
        if self.availableForPurchaseCont.display and self.unavailableForPurchaseCont.display:
            self.sharedButtonCont.FlagForceUpdateAlignment()
            self.sharedButtonCont._AssureAlignmentUpdated()
        if self.separatorLine.display:
            contentHeight += 15
        height += contentHeight + CONTENTS_CONT_PADDING
        self.bottomCont.SetSizeAutomatically()
        height += self.bottomCont.height + CONTENTS_CONT_PADDING
        _, height = self.GetWindowSizeForContentSize(height=height)
        self.height = height

    def UpdateLayout(self):
        availableForPurchase = len(self.context.available_for_purchase) > 0
        unavailableForPurchase = len(self.context.unavailable_for_purchase) > 0
        self._ResizeWindow(availableForPurchase, unavailableForPurchase)
        self._UpdateButtonsAndContentDisplay(availableForPurchase, unavailableForPurchase)

    def _ShouldShowSkillPlanButton(self):
        return self.context.skill_plan_template is not None

    def _CanCreatePlan(self):
        numPlans = len(GetSkillPlanSvc().GetAllPersonal())
        return numPlans < MAX_PERSONAL_PLANS

    def _GetSkillPlanButtonHint(self):
        hint = GetByLabel('Tooltips/SkillPlanner/SkillPlanButtonTooltip')
        numPlans = len(GetSkillPlanSvc().GetAllPersonal())
        if self._CanCreatePlan():
            return hint
        else:
            return u'{}\n\n<color={}>{}</color>'.format(hint, TextColor.WARNING, GetByLabel('UI/SkillPlan/MaximumSkillPlanReached', numPlans=numPlans))

    def _UpdateButtonsAndContentDisplay(self, availableForPurchase, unavailableForPurchase):
        self.availableForPurchaseCont.display = availableForPurchase
        self.unavailableForPurchaseCont.display = unavailableForPurchase
        self.sharedButtonCont.display = availableForPurchase and unavailableForPurchase
        self.separatorLine.display = availableForPurchase and unavailableForPurchase
        self.availableCheckMarketButton.display = not self.sharedButtonCont.display
        self.unavailableCheckMarketButton.display = not self.sharedButtonCont.display
        self.availableCreateSkillPlanButton.display = not self.sharedButtonCont.display
        self.unavailableCreateSkillPlanButton.display = not self.sharedButtonCont.display
        self.createSkillPlanButton.display = self._ShouldShowSkillPlanButton()
        self.availableCreateSkillPlanButton.display = self._ShouldShowSkillPlanButton()
        self.unavailableCreateSkillPlanButton.display = self._ShouldShowSkillPlanButton()

    def _ResizeWindow(self, availableForPurchase, unavailableForPurchase):
        if availableForPurchase and unavailableForPurchase:
            self.width = WINDOW_WIDTH_DOUBLE
            self.availableForPurchaseCont.width = CONTENT_SIZE_PROP_DOUBLE
            self.unavailableForPurchaseCont.width = CONTENT_SIZE_PROP_DOUBLE
        else:
            self.width = WINDOW_WIDTH_SINGLE
            self.availableForPurchaseCont.width = CONTENT_SIZE_PROP_SINGLE
            self.unavailableForPurchaseCont.width = CONTENT_SIZE_PROP_SINGLE

    def _OnCancelButton(self, *args):
        self.SetModalResult(uiconst.ID_CLOSE)
        self.CloseByUser()

    def _OnBuyAndInjectButton(self, *args):
        success = self._BuyMissingSkills()
        if success and len(self.context.unavailable_for_purchase) == 0:
            self.SetModalResult(uiconst.ID_YES)
            self.Close()
        else:
            self.UpdateLayout()
            self.UpdateHeight()

    def _OnSharedCheckMarketButton(self, *args):
        self.context.multibuy_all_skills()
        self.SetModalResult(uiconst.ID_CLOSE)
        self.Close()

    def _OnAvailableCheckMarketButton(self, *args):
        self.context.multibuy_available_skills()
        self.SetModalResult(uiconst.ID_CLOSE)
        self.Close()

    def _OnUnavailableCheckMarketButton(self, *args):
        self.context.multibuy_unavailable_skills()
        self.SetModalResult(uiconst.ID_CLOSE)
        self.Close()

    def _BuyMissingSkills(self):
        return self.context.purchase_available_skills()

    def _OnCreateSkillPlanButton(self, *args):
        template = self.context.skill_plan_template
        if not self._CanCreatePlan():
            skillPlanUtil.SetPersistedPanelID(BUTTON_GROUP_ID_TOP_LEVEL, PANEL_SKILL_PLANS)
            skillPlanUtil.SetPersistedPanelID(BUTTON_GROUP_ID_SKILL_PLANS, PANEL_PERSONAL)
            template = None
        sm.GetService('cmd').OpenSkillsWindow(forceClose=True, skillPlanTemplate=template)
        self.SetModalResult(uiconst.ID_CLOSE)
        self.CloseByUser()


class SkillListHeadingContainer(Container):

    def ApplyAttributes(self, attributes):
        self.default_state = uiconst.UI_NORMAL
        self.default_pickState = PickState.ON
        super(SkillListHeadingContainer, self).ApplyAttributes(attributes)
        self.titleLabel = attributes.get('titleLabel', '')
        self.titleColor = attributes.get('titleColor', None)
        self.on_click = attributes.get('on_click', None)
        self.background_color = (0.2, 0.2, 0.2, 0.2)
        self.ConstructLayout()

    def ConstructLayout(self):
        spriteCont = ContainerAutoSize(parent=self, name='iconCont', align=uiconst.TOLEFT, padRight=10)
        Sprite(parent=spriteCont, name='skillbookIcon', align=uiconst.CENTER, texturePath=eveicon.skill_book, height=16, width=16, left=4)
        titleCont = ContainerAutoSize(parent=self, name='labelCont', align=uiconst.TOLEFT, padRight=2)
        title = EveLabelLarge(parent=titleCont, name='titleLabel', align=uiconst.CENTERLEFT, text=self.titleLabel, maxWidth=250)
        if self.titleColor is not None:
            title.SetDefaultColor(self.titleColor)
        InfoIcon(parent=ContainerAutoSize(parent=self, name='showInfoCont', align=uiconst.TOLEFT, height=16), name='showInfo', align=uiconst.CENTER, hint=GetByLabel('UI/SkillPlan/MissingSkillbooksWindow/RemoteInjectionTooltip'))

    def OnMouseEnter(self, *args):
        self.background_color = (0.2, 0.2, 0.2, 0.8)

    def OnMouseExit(self, *args):
        self.background_color = (0.2, 0.2, 0.2, 0.5)

    def OnClick(self, *args):
        if self.on_click:
            self.on_click()
