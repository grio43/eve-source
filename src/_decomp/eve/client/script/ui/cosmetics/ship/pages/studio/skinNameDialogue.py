#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\skinNameDialogue.py
import eveicon
from carbonui import uiconst
from carbonui.control.forms import formComponent, formValidators
from carbonui.control.forms.form import Form, FormActionSubmit, FormActionCancel
from carbonui.control.forms.formWindow import FormWindow
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.common.ships.skins.static_data import skin_const
from localization import GetByLabel
from signals import Signal

class SkinNameDialogue(FormWindow):
    default_windowID = 'SkinNameDialogue'
    COMPONENT_NAME = 'name'
    COMPONENT_LINE = 'line'

    def ApplyAttributes(self, attributes):
        super(FormWindow, self).ApplyAttributes(attributes)
        self.window_name = attributes.window_name
        self.on_submit = Signal('on_submit')
        self.on_submit_failed = Signal('on_submit_failed')
        components = [formComponent.Text(name=self.COMPONENT_NAME, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SKINName'), value=current_skin_design.get().name, validators=[formValidators.Length(skin_const.name_min_length, skin_const.name_max_length), formValidators.IllegalCharacters()]), formComponent.Text(name=self.COMPONENT_LINE, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SKINLineNameOptional'), value=current_skin_design.get().line_name, validators=[formValidators.Length(skin_const.line_name_min_length, skin_const.line_name_max_length), formValidators.IllegalCharacters()])]
        self.form = Form(name=self.window_name, icon=eveicon.load, components=components, actions=[FormActionSubmit(label=self.get_action_button_name(), func=self.on_form_submit), FormActionCancel()])
        self.SetCaption(self.form.name)
        if self.form.icon:
            self.icon = self.form.icon
        self.formCont = ContainerAutoSize(name='formCont', parent=self.content, align=uiconst.TOTOP, callback=self.OnFormContHeightChanged)
        self.ConstructLayout()
        self.ConnectSignals()

    def get_action_button_name(self):
        return GetByLabel('UI/Common/Buttons/Save')

    def on_form_submit(self, form):
        current_skin_design.get().name = form.get_component(self.COMPONENT_NAME).get_value()
        current_skin_design.get().line_name = form.get_component(self.COMPONENT_LINE).get_value()
        current_skin_design.add_to_undo_history()

    def OnSubmitActionFailed(self, action):
        self.on_submit_failed(self.form.get_submit_failed_reasons_text())

    def OnSubmitActionExecuted(self, action):
        self.on_submit()
        self.SetModalResult(self.form.get_value())
        self.Close()


class RenameSkinDialogue(SkinNameDialogue):

    def get_action_button_name(self):
        return GetByLabel('UI/Common/Buttons/Apply')
