#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\forms\formCollapsibleSection.py
import carbonui
import eveicon
from carbonui import Align, Density, ButtonVariant, uiconst, TextColor
from carbonui.control.button import Button
from carbonui.control.forms import formFields
from carbonui.control.forms.formsUtil import FormatAsIncompleteInput
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uiconst import PickState
from eve.client.script.ui import eveColor
from localization import GetByLabel
from signals import Signal

class FormSectionState:
    UNTOUCHED = 1
    ACTIVE = 2
    INCOMPLETE = 3
    COMPLETE = 4


class HeaderContainer(Container):
    default_height = 24
    default_pickState = PickState.ON

    def ApplyAttributes(self, attributes):
        super(HeaderContainer, self).ApplyAttributes(attributes)
        section_num = attributes.section_num
        self.form = attributes.form
        self.on_click = Signal('on_click')
        num_cont = Container(name='numCont', parent=self, align=Align.TOLEFT, width=self.height)
        self.circleSprite = Sprite(bgParent=num_cont, texturePath='res:/UI/Texture/Classes/PieCircle/circle32.png', opacity=0.6)
        self.number_text = carbonui.TextDetail(parent=num_cont, align=Align.CENTER, text=str(section_num), color=eveColor.BLACK, shadowOffset=(0, 0), bold=True)
        self.iconCont = Container(parent=self, align=uiconst.TOLEFT, bgTexturePath='res:/UI/Texture/Classes/PieCircle/circle32.png', bgColor=list(eveColor.SMOKE_BLUE[:3]) + [0.2], width=self.height, display=False, padLeft=8)
        self.icon = Sprite(name='icon', parent=self.iconCont, align=uiconst.CENTER, pickState=PickState.OFF, color=TextColor.SECONDARY, pos=(0, 0, 16, 16))
        right_cont = ContainerAutoSize(parent=self, align=Align.TORIGHT)
        self.continue_btn = Button(name='ContinueBtn', parent=right_cont, align=Align.CENTERRIGHT, density=Density.COMPACT, variant=ButtonVariant.GHOST, label=GetByLabel('UI/Common/Expand'), func=self.OnClick, display=False)
        self.state_icon = Sprite(name='stateIcon', parent=right_cont, align=Align.CENTERRIGHT, pos=(0, 0, 16, 16), texturePath=eveicon.checkmark, color=eveColor.SUCCESS_GREEN, display=False)
        self.header = carbonui.TextDetail(parent=Container(parent=self, padLeft=8), align=Align.CENTERLEFT, autoFadeSides=True)

    def OnClick(self, *args):
        self.on_click()

    def SetSectionState(self, state, is_expanded):
        self.state_icon.display = state == FormSectionState.COMPLETE
        if state in (FormSectionState.INCOMPLETE, FormSectionState.UNTOUCHED) and not is_expanded:
            self.continue_btn.state = uiconst.UI_NORMAL
        else:
            self.continue_btn.state = uiconst.UI_HIDDEN
        self.header.SetRGBA(*self._GetTextColor(state))
        self.circleSprite.rgb = self._GetCircleBGColor(state)[:3]
        self.number_text.SetRGBA(*self._GetNumberTextColor(state))
        self.number_text.bold = state != FormSectionState.COMPLETE

    def _GetNumberTextColor(self, state):
        if state == FormSectionState.COMPLETE:
            return eveColor.SUCCESS_GREEN
        else:
            return eveColor.BLACK

    def _GetTextColor(self, state):
        if state == FormSectionState.COMPLETE:
            return TextColor.DISABLED
        elif state == FormSectionState.ACTIVE:
            return TextColor.HIGHLIGHT
        else:
            return TextColor.NORMAL

    def _GetCircleBGColor(self, state):
        if state == FormSectionState.COMPLETE:
            color = list(eveColor.COPPER_OXIDE_GREEN[:3]) + [0.2]
        elif state == FormSectionState.INCOMPLETE:
            color = eveColor.WARNING_ORANGE
        elif state == FormSectionState.UNTOUCHED:
            color = eveColor.GUNMETAL_GREY
        else:
            color = eveColor.WHITE
        return color

    def SetHeaderText(self, text):
        self.header.text = text

    def SetIcon(self, icon = None):
        if icon:
            self.icon.texturePath = icon
            self.iconCont.display = True
        else:
            self.iconCont.display = False


class FormCollapsibleSection(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(FormCollapsibleSection, self).ApplyAttributes(attributes)
        section_num = attributes.section_num
        self.form = attributes.form
        self._section_state = attributes.section_state or FormSectionState.UNTOUCHED
        self.on_expanded = Signal('on_expaned')
        self.ConstructLayout(section_num)
        self._SetSectionState(self._section_state)
        self.form.on_submit_failed.connect(self.OnSubmitFailed)

    def OnSubmitFailed(self, form):
        if self.form.is_valid():
            self._SetSectionState(FormSectionState.COMPLETE)
        else:
            self._SetSectionState(FormSectionState.INCOMPLETE)

    def ConstructLayout(self, section_num):
        if section_num > 1:
            Line(parent=self, align=Align.TOTOP, opacity=0.2, padding=(0, 16, 0, 16))
        self.header_cont = HeaderContainer(name='headerCont', align=Align.TOTOP, parent=self, section_num=section_num, form=self.form, pickState=PickState.ON)
        self.header_cont.on_click.connect(self.OnHeaderContClicked)
        self.fields_cont = ContainerAutoSize(name='fieldsCont', parent=self, align=Align.TOTOP, padTop=8, padBottom=-16, display=self._section_state == FormSectionState.ACTIVE)
        self.ConstructFields()

    def ConstructFields(self):
        formFields.ConstructFields(parent=self.fields_cont, form=self.form)

    def _SetSectionState(self, state):
        self._section_state = state
        self.header_cont.SetSectionState(state, self.fields_cont.display)
        self.UpdateHeaderText()
        self.header_cont.SetIcon(self._GetHeaderIcon())

    def UpdateHeaderText(self):
        self.header_cont.SetHeaderText(self._GetHeaderText())

    def _GetHeaderText(self):
        text = self.form.get_label()
        if self._section_state == FormSectionState.INCOMPLETE:
            text = FormatAsIncompleteInput(text)
        return text

    def _GetHeaderIcon(self):
        return None

    def OnHeaderContClicked(self):
        if not self.fields_cont.display:
            self.ExpandFields()

    def ExpandFields(self):
        self.fields_cont.display = True
        self._SetSectionState(FormSectionState.ACTIVE)
        self.on_expanded(self)

    def CollapseFields(self):
        self.fields_cont.display = False
        if self._section_state == FormSectionState.UNTOUCHED:
            return
        if self.form.is_valid():
            self._SetSectionState(FormSectionState.COMPLETE)
        else:
            self._SetSectionState(FormSectionState.INCOMPLETE)
