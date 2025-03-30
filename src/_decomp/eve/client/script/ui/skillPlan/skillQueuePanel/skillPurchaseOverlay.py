#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillQueuePanel\skillPurchaseOverlay.py
import carbonui.control.button
import characterskills.client
import localization
import signals
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control import buttons, eveLabel, primaryButton
from eve.client.script.ui.shared.neocom import skillConst

def show_skill_purchase_overlay(parent, type_id, position):
    controller = SkillPurchaseOverlayController(type_id, position)
    overlay = SkillPurchaseOverlay(parent=parent, idx=0, controller=controller, opacity=0.0, padding=-20)
    animations.FadeIn(overlay, duration=0.3, curveType=uiconst.ANIM_OVERSHOT)
    return controller


class SkillPurchaseOverlayController(object):

    def __init__(self, type_id, position):
        self.type_id = type_id
        self._is_closed = False
        self._position = position
        self.on_closed = signals.Signal(signalName='on_closed')
        self._register_event_handlers()

    @property
    def are_requirements_trained(self):
        return len(self._get_untrained_required_skills()) == 0

    @property
    def is_available_for_purchase(self):
        return characterskills.client.is_available_for_purchase(self.type_id)

    @property
    def price(self):
        if not self.is_available_for_purchase:
            return None
        return characterskills.client.get_direct_purchase_price(self.type_id)

    def buy_skill(self):
        if self._is_closed:
            return
        try:
            sm.GetService('skills').PurchaseSkills([self.type_id], confirm=False)
        finally:
            self.close()

    def buy_and_train_skill(self):
        if self._is_closed:
            return
        try:
            sm.GetService('skills').PurchaseSkills([self.type_id], confirm=False)
            sm.GetService('skillqueue').AddSkillToQueue(self.type_id, 1, position=self._position)
        finally:
            self.close()

    def close(self):
        if self._is_closed:
            return
        self._is_closed = True
        self._unregister_event_handlers()
        self.on_closed()

    def view_market_details(self):
        try:
            sm.GetService('marketutils').ShowMarketDetails(self.type_id, None)
        finally:
            self.close()

    def OnSkillQueueChanged(self):
        self.close()

    def _get_untrained_required_skills(self):
        return sm.GetService('skills').GetSkillsMissingToUseItemRecursive(self.type_id)

    def _register_event_handlers(self):
        sm.RegisterForNotifyEvent(self, 'OnSkillQueueChanged')

    def _unregister_event_handlers(self):
        sm.UnregisterForNotifyEvent(self, 'OnSkillQueueChanged')


class SkillPurchaseOverlay(Container):
    default_align = uiconst.TOALL
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(SkillPurchaseOverlay, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self._layout()
        self.controller.on_closed.connect(self.close_animated)

    def close_animated(self):
        animations.FadeOut(self, duration=0.3, callback=self.Close)

    def _layout(self):
        Sprite(bgParent=self, texturePath='res:/UI/Texture/classes/Monetization/vignette.png', opacity=0.9)
        content_cont = ContainerAutoSize(parent=self, align=uiconst.CENTER, width=340)
        self._add_message(content_cont)
        self._add_buttons(content_cont)

    def _add_message(self, parent):
        if self.controller.is_available_for_purchase:
            text = localization.GetByLabel('UI/SkillQueue/ConfirmSkillPurchase', skill=self.controller.type_id, price=self.controller.price)
        else:
            text = localization.GetByLabel('UI/SkillQueue/ErrorSkillIsRare', skill=self.controller.type_id)
        eveLabel.EveLabelMedium(parent=parent, align=uiconst.TOTOP, text=text)

    def _add_buttons(self, parent):
        button_cont = FlowContainer(parent=parent, align=uiconst.TOTOP, top=16, centerContent=True, contentSpacing=(4, 4), height=36)
        self._add_cancel_button(button_cont)
        if self.controller.is_available_for_purchase:
            self._add_confirm_button(button_cont)
        else:
            self._add_market_details_button(button_cont)

    def _add_cancel_button(self, parent):
        carbonui.control.button.Button(parent=parent, align=uiconst.NOALIGN, label=localization.GetByLabel('UI/Common/Cancel'), func=self.controller.close, args=(), fixedheight=32, fixedwidth=120)

    def _add_confirm_button(self, parent):
        if self.controller.are_requirements_trained:
            func = self.controller.buy_and_train_skill
            label = localization.GetByLabel('UI/Skills/BuyAndTrain')
        else:
            func = self.controller.buy_skill
            label = localization.GetByLabel('UI/Skills/BuySkill')
        primaryButton.PrimaryButton(parent=parent, align=uiconst.NOALIGN, label=label, func=func, args=(), color=skillConst.COLOR_SKILL_1, fixedheight=32, fixedwidth=120)

    def _add_market_details_button(self, parent):
        carbonui.control.button.Button(parent=parent, align=uiconst.NOALIGN, label=localization.GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), func=self.controller.view_market_details, args=(), fixedheight=32, fixedwidth=120)
