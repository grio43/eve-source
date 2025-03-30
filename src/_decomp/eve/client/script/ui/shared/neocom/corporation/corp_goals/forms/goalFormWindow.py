#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_goals\forms\goalFormWindow.py
import carbonui
import eveformat
from carbonui import Align, uiconst, TextColor, TextAlign
from carbonui.control.forms.formCollapsibleSection import FormCollapsibleSection, FormSectionState
from carbonui.control.forms.formWindow import FormWindow
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.window.header.small import SmallWindowHeader
from corporation.client.goals.featureFlag import are_corporation_goal_payments_enabled
from corporation.client.goals.goalConst import ContributionMethodTypes
from eveformat import currency
from localization import GetByLabel

class GoalFormWindow(FormWindow):
    default_minSize = (300, FormWindow.default_height)
    sections = []

    def ConstructFields(self):
        self.contribution_method_section = ContributionMethodFormCollapsibleSection(parent=self.formCont, align=Align.TOTOP, form=self.form.get_component('contribution_method_sub_form'), section_num=1, padTop=8, section_state=FormSectionState.ACTIVE)
        self.contribution_method_section.on_expanded.connect(self.OnSectionExpanded)
        self.description_section = DescriptionFormCollapsibleSection(parent=self.formCont, align=Align.TOTOP, form=self.form.get_component('description_sub_form'), section_num=2, section_state=FormSectionState.UNTOUCHED)
        self.description_section.on_expanded.connect(self.OnSectionExpanded)
        self.sections = [self.contribution_method_section, self.description_section]
        if are_corporation_goal_payments_enabled():
            self.payment_section = PaymentFormCollapsibleSection(parent=self.formCont, align=Align.TOTOP, form=self.form.get_component('payment_sub_form'), section_num=3, section_state=FormSectionState.UNTOUCHED, display=not self.selectedShipInsurance(self.contribution_method_section.form.contribution_method_component))
            self.payment_section.on_expanded.connect(self.OnSectionExpanded)
            self.contribution_method_section.form.contribution_method_component.on_value_set_by_user.connect(self.OnContributionMethodChanged)
            self.sections.append(self.payment_section)

    def ConstructLayout(self):
        self.ConstructFields()
        if are_corporation_goal_payments_enabled():
            self.ConstructSummarySection()
        self.ConstructButtons()

    def ConstructSummarySection(self):
        TotalCostSegment(parent=self.formCont, align=Align.TOTOP, form=self.form)

    def OnSectionExpanded(self, section):
        for s in self.sections:
            if s != section:
                s.CollapseFields()

    def selectedShipInsurance(self, component):
        return component.get_value() == ContributionMethodTypes.SHIP_INSURANCE

    def OnContributionMethodChanged(self, component):
        if self.selectedShipInsurance(component):
            self.payment_section.display = False
        elif self.payment_section.display is False:
            self.payment_section.display = True
        self.payment_section.reset_header_state()

    def Prepare_Header_(self):
        self._SetHeader(SmallWindowHeader())


class TotalCostSegment(ContainerAutoSize):
    default_padTop = 16
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(TotalCostSegment, self).ApplyAttributes(attributes)
        self.form = attributes.form
        Line(parent=self, align=Align.TOTOP, opacity=0.2)
        carbonui.TextBody(parent=self, align=Align.TOTOP, text=GetByLabel('UI/Corporations/Goals/TotalProjectCost'), color=TextColor.SECONDARY, textAlign=TextAlign.RIGHT, padTop=16)
        self.label = carbonui.TextHeader(parent=self, align=Align.TOTOP, textAlign=TextAlign.RIGHT)
        self.form.get_component('amount_paid_per_unit').on_value_set_by_user.connect(self.on_amount_change)
        self.form.get_component('desired_progress').on_value_set_by_user.connect(self.on_target_changed)
        self._calculate_and_update_amount()

    def _calculate_and_update_amount(self):
        self.label.text = currency.isk(self.get_isk_amount(), fraction=True)

    def get_isk_amount(self):
        amount_per_unit = self.form.get_component('amount_paid_per_unit').get_value()
        desired_progress = self.form.get_component('desired_progress').get_value() or 0
        isk_amount = amount_per_unit * desired_progress
        return isk_amount

    def on_amount_change(self, component):
        self._calculate_and_update_amount()

    def on_target_changed(self, component):
        self._calculate_and_update_amount()

    def GetHint(self):
        return currency.isk_readable(self.get_isk_amount())

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2


class ContributionMethodFormCollapsibleSection(FormCollapsibleSection):

    def _SetSectionState(self, state):
        super(ContributionMethodFormCollapsibleSection, self)._SetSectionState(state)

    def _GetHeaderIcon(self):
        if self._section_state == FormSectionState.COMPLETE:
            return self.form.get_contribution_method().icon
        else:
            return None

    def _GetHeaderText(self):
        if self._section_state == FormSectionState.COMPLETE:
            try:
                contribution_method = self.form.get_contribution_method(include_data=True)
                full_description = contribution_method.full_description
            except:
                contribution_method = self.form.get_contribution_method(include_data=False)
                full_description = contribution_method.full_description

            progress = self.form.get_component('desired_progress').get_value()
            return u'{} X {}'.format(eveformat.number(progress), full_description)
        else:
            self.header_cont.SetIcon(None)
            return super(ContributionMethodFormCollapsibleSection, self)._GetHeaderText()


class DescriptionFormCollapsibleSection(FormCollapsibleSection):

    def _GetHeaderText(self):
        if self._section_state == FormSectionState.COMPLETE:
            return self.form.get_component('name').get_value()
        else:
            return super(DescriptionFormCollapsibleSection, self)._GetHeaderText()


class PaymentFormCollapsibleSection(FormCollapsibleSection):

    def reset_header_state(self):
        self._SetSectionState(FormSectionState.UNTOUCHED)
