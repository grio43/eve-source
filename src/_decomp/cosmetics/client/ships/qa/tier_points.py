#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\qa\tier_points.py
import eveicon
from carbonui import uiconst
from carbonui.control.forms import formComponent
from carbonui.control.forms.form import Form, FormActionSubmit, FormActionCancel
from carbonui.control.forms.formWindow import FormWindow
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from cosmetics.client.ships.skins.live_data import current_skin_design

class QATierPointsDialogue(FormWindow):
    default_windowID = 'QATierPointsDialogue'

    def ApplyAttributes(self, attributes):
        super(FormWindow, self).ApplyAttributes(attributes)
        self.window_name = 'Set QA Tier Points'
        components = [formComponent.Integer(name='QA Tier Points', label='QA Tier Points', value=current_skin_design.get().qa_tier_points)]
        self.form = Form(name=self.window_name, icon=eveicon.load, components=components, actions=[FormActionSubmit(label='Save', func=self.on_form_submit), FormActionCancel()])
        self.SetCaption(self.form.name)
        if self.form.icon:
            self.icon = self.form.icon
        self.formCont = ContainerAutoSize(name='formCont', parent=self.content, align=uiconst.TOTOP, callback=self.OnFormContHeightChanged)
        self.ConstructLayout()
        self.ConnectSignals()

    def on_form_submit(self, form):
        current_skin_design.get().set_qa_tier_points(form.get_component('QA Tier Points').get_value())


def set_current_design_qa_tier_points():
    dialogue = QATierPointsDialogue()
    dialogue.ShowModal()
