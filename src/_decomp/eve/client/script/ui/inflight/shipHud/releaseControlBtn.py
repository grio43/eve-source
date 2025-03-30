#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\releaseControlBtn.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from localization import GetByLabel
import math
from carbonui.uicore import uicore
from structures.types import IsFlexStructure
MOUSE_OFF_OPACITY = 0.5
MOUSE_ON_OPACITY = 1.0
COLOR_TAKE_CONTROL = (172 / 255.0,
 84 / 255.0,
 40 / 255.0,
 1.0)

class ReleaseControlBtn(Container):
    default_name = 'ReleaseControlBtn'
    default_width = 104
    default_height = 44
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.func = attributes.func
        self.structureTypeID = attributes.structureTypeID
        if IsFlexStructure(self.structureTypeID):
            self.hintText = GetByLabel('UI/Inflight/HUDOptions/BoardPreviousShipFromFlex')
        else:
            self.hintText = GetByLabel('UI/Inflight/HUDOptions/ReleaseControl')
        self.pickParent = Container(name='speedCircularPickParent', parent=self, align=uiconst.CENTERBOTTOM, pos=(0, 0, 144, 144), pickRadius=72, state=uiconst.UI_NORMAL)
        self.pickParent.OnMouseMove = self.OnMoveInPickParent
        self.pickParent.OnMouseExit = self.OnMouseExit
        self.pickParent.OnMouseEnter = self.OnMouseEnter
        self.pickParent.OnClick = self.OnClick
        self.pickParent.GetTooltipPosition = self.GetPickParentTooltipPosition
        self.arrowSprite = Sprite(parent=self.pickParent, name='releaseArrow', pos=(0, 0, 104, 44), align=uiconst.CENTERBOTTOM, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/releaseArrow.png', opacity=MOUSE_OFF_OPACITY, color=COLOR_TAKE_CONTROL)
        Sprite(parent=self.pickParent, name='buttonBody', pos=(0, 0, 104, 44), align=uiconst.CENTERBOTTOM, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/buttonBody.png')

    def OnMouseEnter(self, *args):
        self.OnMoveInPickParent()

    def OnMoveInPickParent(self, *args):
        isInside = self.IsInside()
        if isInside:
            hint = self.hintText
            opacity = MOUSE_ON_OPACITY
        else:
            hint = ''
            opacity = MOUSE_OFF_OPACITY
        self.pickParent.hint = hint
        self.arrowSprite.opacity = opacity

    def GetPickParentTooltipPosition(self):
        if self.pickParent is None or self.pickParent.destroyed:
            return (uicore.uilib.x - 5,
             uicore.uilib.y - 5,
             10,
             10)
        retLeft, retTop, retWidth, retHeight = self.GetAbsolute()
        return (retLeft,
         retTop + 14,
         retWidth,
         retHeight)

    def IsInside(self):
        if uicore.uilib.GetMouseOver() != self.pickParent:
            return False
        l, t, w, h = self.pickParent.GetAbsolute()
        centerX = l + w / 2
        centerY = t + h / 2
        y = float(uicore.uilib.y - centerY)
        x = float(uicore.uilib.x - centerX)
        if x and y:
            angle = math.atan(x / y)
            deg = angle / math.pi * 180.0
            factor = (45.0 + deg) / 90.0
            if factor < 0.0 or factor > 1.0:
                return False
            return True
        return False

    def OnMouseExit(self, *args):
        self.arrowSprite.opacity = MOUSE_OFF_OPACITY
        self.hint = ''

    def OnClick(self, *args):
        if self.IsInside():
            self.func(self.structureTypeID)
