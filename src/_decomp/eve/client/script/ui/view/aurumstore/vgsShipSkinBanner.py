#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\vgsShipSkinBanner.py
import logging
from carbonui import Align, fontconst, uiconst
from carbonui.control.carousel import Carousel
from carbonui.loggers.buttonLogger import log_button_clicked
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.cosmetics.ship.shipSKINRWindow import ShipSKINRWindow
from eve.client.script.ui.shared.skins.uiutil import OPEN_SKINR_BUTTON_NES_BANNER_ANALYTIC_ID
from eve.client.script.ui.view.aurumstore import vgsUiConst
from eve.client.script.ui.view.aurumstore.vgsOffer import Ribbon
from localization import GetByLabel
CAROUSEL_TEXTURES = ['res:/UI/Texture/Vgs/SKINR/carousel/Astero.png',
 'res:/UI/Texture/Vgs/SKINR/carousel/Barghest.png',
 'res:/UI/Texture/Vgs/SKINR/carousel/Gila.png',
 'res:/UI/Texture/Vgs/SKINR/carousel/Ishtar.png',
 'res:/UI/Texture/Vgs/SKINR/carousel/Kiki.png',
 'res:/UI/Texture/Vgs/SKINR/carousel/Mackinaw.png',
 'res:/UI/Texture/Vgs/SKINR/carousel/Redeemer.png',
 'res:/UI/Texture/Vgs/SKINR/carousel/Vargur.png']
TEXT_AREA_HEIGHT = 48
logger = logging.getLogger(__name__)

class ShipSkinBanner(Container):
    default_width = vgsUiConst.CONTENT_PADDING + vgsUiConst.OFFER_IMAGE_SIZE * 2
    default_height = vgsUiConst.OFFER_IMAGE_SIZE
    default_state = uiconst.UI_NORMAL

    def __init__(self, *args, **kwargs):
        self.analyticID = OPEN_SKINR_BUTTON_NES_BANNER_ANALYTIC_ID
        super(ShipSkinBanner, self).__init__(*args, **kwargs)
        self.construct_layout()

    def construct_layout(self):
        self.construct_description()
        self.construct_carousel()
        Ribbon(name='ribbon', parent=self, align=Align.TOPLEFT, text=GetByLabel('UI/VirtualGoodsStore/SKINR/Ribbon'), texture_path='res:/UI/Texture/Vgs/SKINR/ribbon.png', padding=(-10, -10, 0, 0))
        self.transform = Transform(name='transform', parent=self, align=Align.TOALL, scalingCenter=(0.5, 0.5), bgColor=(0.0, 1.0, 0.0, 0.5))
        Sprite(name='background', parent=self.transform, align=Align.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Vgs/SKINR/background.png')

    def construct_description(self):
        self.description_container = Container(name='description_container', parent=self, align=Align.TOBOTTOM_NOPUSH, height=TEXT_AREA_HEIGHT, state=uiconst.UI_DISABLED, bgColor=vgsUiConst.OFFER_TEXT_BOX_COLOR)
        Label(name='description_label', parent=self.description_container, align=Align.TOTOP, text=GetByLabel('UI/VirtualGoodsStore/SKINR/Description'), fontsize=vgsUiConst.VGS_FONTSIZE_OFFER, padding=(vgsUiConst.OFFER_INFO_PADDING,
         2,
         vgsUiConst.OFFER_INFO_PADDING,
         -2), fontStyle=fontconst.STYLE_HEADER, uppercase=True, lineSpacing=-0.15, color=eveColor.WHITE)

    def construct_carousel(self):
        carousel = ShipSkinCarousel(name='carousel', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0,
         0,
         self.default_width,
         self.default_height))

    def OnMouseEnter(self, *args):
        animations.Tr2DScaleTo(self.transform, startScale=self.transform.scale, endScale=(1.02, 1.02), duration=0.2)

    def OnMouseExit(self, *args):
        animations.Tr2DScaleTo(self.transform, self.transform.scale, endScale=(1.0, 1.0), duration=0.2)

    def OnClick(self, *args):
        logger.info('Emitting analyticID: %s', self.analyticID)
        log_button_clicked(self)
        sm.GetService('vgsService').ToggleStore()
        ShipSKINRWindow.open_on_paragon_hub()


class ShipSkinCarousel(Carousel):

    def __init__(self, *args, **kwargs):
        super(ShipSkinCarousel, self).__init__(*args, **kwargs)
        for texture_path in CAROUSEL_TEXTURES:
            Sprite(parent=self, align=uiconst.TOLEFT, texturePath=texture_path, pos=(0,
             0,
             self.width,
             self.height))

        self.InitializeButtons()
        self.buttonContainer.top = 48
        self.hide_control_buttons()
