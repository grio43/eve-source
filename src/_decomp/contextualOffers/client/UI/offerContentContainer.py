#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\client\UI\offerContentContainer.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame

class OfferContentContainer(Container):
    default_background_hue = (0, 0, 0, 0)
    default_background_image = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onButtonClick = attributes.onButtonClick
        self.backgroundHue = attributes.get('backgroundHue', self.default_background_hue)
        self.backgroundImage = attributes.get('backgroundImage', self.default_background_image)
        self.backgroundHueFrame = Frame(parent=self, align=uiconst.CENTERTOP, width=self.width, height=self.height, cornerSize=12, texturePath='res:/UI/Texture/Shared/BracketBorderWindow/mask_Window770.png', color=self.backgroundHue)

    def OnButtonClick(self):
        self.onButtonClick()
