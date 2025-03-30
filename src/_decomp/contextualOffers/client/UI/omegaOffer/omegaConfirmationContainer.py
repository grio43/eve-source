#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\client\UI\omegaOffer\omegaConfirmationContainer.py
from carbonui import uiconst, fontconst
from contextualOffers.client.UI.offerContentContainer import OfferContentContainer
from eve.client.script.ui.control.eveLabel import Label
from newFeatures.newFeatureNotifyButton import NewFeatureButton
from clonegrade.const import COLOR_OMEGA_GOLD

class OmegaConfirmationContainer(OfferContentContainer):
    default_name = 'omegaConfirmationContainer'
    default_background_hue = (0, 0, 0, 0.15)

    def ApplyAttributes(self, attributes):
        OfferContentContainer.ApplyAttributes(self, attributes)
        self.ConstructText()
        self.ConstructButtons()

    def ConstructText(self):
        text_color = COLOR_OMEGA_GOLD
        self.fanfareTitle = Label(name='fanfareHeader', parent=self, fontsize=88, bold=True, align=uiconst.TOPLEFT, left=50, top=110 - (100 * fontconst.fontSizeFactor - 100), color=text_color, idx=0)
        self.fanfareDescription = Label(name='fanfareDescription', parent=self, fontsize=60, bold=True, align=uiconst.TOPLEFT, left=50, top=190 + (50 * fontconst.fontSizeFactor - 50), color=text_color, idx=0)

    def ConstructButtons(self):
        self.doneButton = NewFeatureButton(name='doneButton', parent=self, align=uiconst.BOTTOMRIGHT, stretchTexturePath='res:/UI/Texture/Shared/BracketBorderWindow/button180.png', hiliteTexturePath='res:/UI/Texture/Shared/BracketBorderWindow/button180.png', height=31, width=112, fontSize=16, buttonColor=(0.8, 0.8, 0.8, 1), top=30, left=30, idx=0, onClick=self.OnButtonClick)

    def SetTitleText(self, title):
        self.fanfareTitle.SetText(title)

    def SetDescriptionText(self, description):
        self.fanfareDescription.SetText(description)

    def SetButtonText(self, buttonText):
        self.doneButton.SetText(buttonText)
