#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\qa\skin_trading.py
import eveicon
from carbonui import uiconst
from carbonui.control.forms import formComponent
from carbonui.control.forms.form import Form, FormActionSubmit, FormActionCancel
from carbonui.control.forms.formWindow import FormWindow
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from cosmetics.client.shipSkinTradingSvc import get_ship_skin_trading_svc

def expire_listing(card, listing_id):
    dialogue = QAExpireSkinListingDialogue(card=card, listing_id=listing_id)
    dialogue.ShowModal()


class QAExpireSkinListingDialogue(FormWindow):
    default_windowID = 'QAExpireSkinListingDialogue'

    def ApplyAttributes(self, attributes):
        super(FormWindow, self).ApplyAttributes(attributes)
        self.window_name = 'Expire SKIN Listing'
        self._listing_id = attributes.listing_id
        self._card = attributes.card
        components = [formComponent.Integer(name='Minutes before expiry', label='Minutes before expiry', value=1, min_value=1)]
        self.form = Form(name=self.window_name, icon=eveicon.load, components=components, actions=[FormActionSubmit(label='OK', func=self.on_form_submit), FormActionCancel()])
        self.SetCaption(self.form.name)
        if self.form.icon:
            self.icon = self.form.icon
        self.formCont = ContainerAutoSize(name='formCont', parent=self.content, align=uiconst.TOTOP, callback=self.OnFormContHeightChanged)
        self.ConstructLayout()
        self.ConnectSignals()

    def on_form_submit(self, form):
        minutes_to_expiry = form.get_component('Minutes before expiry').get_value()
        get_ship_skin_trading_svc().admin_expire_listing(self._listing_id, minutes_to_expiry)
        self._card.update_time_remaining_container()
