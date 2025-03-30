#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\enlistmentFlow\insurgencySideSelector.py
from carbonui.uianimations import animations
from carbonui.primitives.transform import Transform
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentConst import BANNER_TEXTURE_BY_SIDE, ICON_TEXTURE_BY_SIDE, LABEL_PATH_BY_SIDE
from carbonui import const as uiconst, TextCustom
from localization import GetByLabel
from carbonui.util.color import Color
IDLE_BRIGHTNESS = 0.5

class InsurgencySideSelector(Container):
    default_align = uiconst.TOPLEFT
    default_width = 166
    default_height = 346
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(InsurgencySideSelector, self).ApplyAttributes(attributes)
        self.enlistmentController = attributes.enlistmentController
        self.insurgencySideID = attributes.insurgencySideID
        bgTexturePath = BANNER_TEXTURE_BY_SIDE.get(self.insurgencySideID, '')
        iconTexturePath = ICON_TEXTURE_BY_SIDE.get(self.insurgencySideID, '')
        labelPath = LABEL_PATH_BY_SIDE.get(self.insurgencySideID, '')
        contentCont = Container(parent=self)
        self.scalingCont = Transform(parent=self, align=uiconst.CENTERTOP, pos=(0, 0, 166, 346), scalingCenter=(0.5, 0.5))
        icon = Sprite(name='icon', parent=self.scalingCont, pos=(0, 40, 120, 120), align=uiconst.CENTERTOP, texturePath=iconTexturePath, state=uiconst.UI_DISABLED)
        self.bgSprite = Sprite(name='bannerBg', parent=self.scalingCont, pos=(0, 0, 166, 346), align=uiconst.CENTERTOP, texturePath=bgTexturePath, state=uiconst.UI_DISABLED, color=Color(eveColor.WHITE).SetBrightness(IDLE_BRIGHTNESS).GetRGBA())
        self.insurgencySideLabel = TextCustom(name='insurgencySideLabel', parent=contentCont, align=uiconst.CENTERTOP, text=GetByLabel(labelPath), fontsize=18, top=icon.top + icon.height + 16)

    def OnMouseEnter(self, *args):
        if self.enlistmentController.isMovingCircle:
            return
        animations.MorphVector2(self.scalingCont, 'scale', self.scalingCont.scale, endVal=(1.1, 1.1), duration=0.2)
        self.enlistmentController.on_insurgency_side_mouse_enter(self.insurgencySideID)
        self.bgSprite.SetRGBA(*eveColor.WHITE)

    def OnMouseExit(self, *args):
        animations.MorphVector2(self.scalingCont, 'scale', self.scalingCont.scale, endVal=(1.0, 1.0), duration=0.2)
        self.enlistmentController.on_insurgency_side_mouse_exit(self.insurgencySideID)
        self.bgSprite.SetRGBA(*Color(eveColor.WHITE).SetBrightness(IDLE_BRIGHTNESS).GetRGBA())

    def OnClick(self, *args):
        self.enlistmentController.SelectInsurgencySide(self.insurgencySideID)
        self.enlistmentController.on_empire_pirates_clicked()
