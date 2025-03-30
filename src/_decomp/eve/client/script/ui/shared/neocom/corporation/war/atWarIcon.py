#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\atWarIcon.py
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.glowSprite import GlowSprite
import carbonui.const as uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.shared.info.infoConst import TAB_WARHISTORY
from eve.client.script.ui.shared.neocom.corporation.war.atWarTooltip import LoadAtWarTooltipPanelFindWars
from eve.common.lib import appConst
BG_ICON_OPACITY = 0.5

class AtWarCont(Container):
    default_name = 'atWarCont'
    default_width = 0
    iconSize = 36
    fullWidth = 50

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.bgIcon = self.atWarIcon = None
        for eachName, opacity in (('bgIcon', BG_ICON_OPACITY), ('atWarIcon', 1.0)):
            icon = GlowSprite(name='atWarIcon', parent=self, align=uiconst.CENTERLEFT, pos=(0,
             0,
             self.iconSize,
             self.iconSize), texturePath='res:/UI/Texture/classes/war/atWar_64.png', color=(0.6,
             0.145,
             0.12,
             opacity), colorType=uiconst.COLORTYPE_UIBASE)
            setattr(self, eachName, icon)

        self.bgIcon.state = uiconst.UI_DISABLED
        self.atWarIcon.LoadTooltipPanel = self.LoadTooltipPanel
        self.atWarIcon.OnClick = self.OnClickIcon
        self.atWarIcon.OnMouseEnter = self.OnGlowSpriteMouseEnter
        self.atWarIcon.OnMouseExit = self.OnGlowSpriteMouseExit
        self.atWarIcon.OnMouseDown = self.OnGlowSpriteMouseDown
        self.atWarIcon.OnMouseUp = self.OnGlowSpriteMouseUp

    def ShowIcon(self, animate = True):
        uicore.animations.StopAllAnimations(self)
        uicore.animations.StopAllAnimations(self.atWarIcon)
        if animate:
            uicore.animations.MorphScalar(self, 'width', 0, self.fullWidth, duration=0.5)
            uicore.animations.MorphScalar(self.atWarIcon, 'opacity', 0, 1.0, duration=0.25, timeOffset=0.25)
        else:
            self.width = self.fullWidth
            self.atWarIcon.opacity = 1.0

    def HideIcon(self, animate = True):
        uicore.animations.StopAllAnimations(self)
        uicore.animations.StopAllAnimations(self.atWarIcon)
        if animate:
            uicore.animations.MorphScalar(self, 'width', self.width, 0, duration=0.5)
            uicore.animations.MorphScalar(self.atWarIcon, 'opacity', self.atWarIcon.opacity, 0.0, duration=0.25)
        else:
            self.width = 0
            self.atWarIcon.opacity = 0.0

    def OnClickIcon(self, *args):
        typeID = appConst.typeAlliance if session.allianceid else appConst.typeCorporation
        itemID = session.allianceid or session.corpid
        sm.GetService('info').ShowInfo(typeID, itemID, selectTabType=TAB_WARHISTORY)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LoadAtWarTooltipPanelFindWars(tooltipPanel)

    def OnGlowSpriteMouseEnter(self, *args):
        GlowSprite.OnMouseEnter(self.atWarIcon, *args)
        uicore.animations.MorphScalar(self.bgIcon, 'opacity', self.bgIcon.opacity, 0.0, duration=uiconst.TIME_ENTRY)

    def OnGlowSpriteMouseExit(self, *args):
        GlowSprite.OnMouseExit(self.atWarIcon, *args)
        uicore.animations.MorphScalar(self.bgIcon, 'opacity', self.bgIcon.opacity, BG_ICON_OPACITY, duration=uiconst.TIME_EXIT)

    def OnGlowSpriteMouseDown(self, *args):
        GlowSprite.OnMouseDown(self.atWarIcon, *args)

    def OnGlowSpriteMouseUp(self, *args):
        GlowSprite.OnMouseUp(self.atWarIcon, *args)
