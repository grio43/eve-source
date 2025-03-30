#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\rollingCounter.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel

class RollingCounter(Container):
    default_width = 13
    default_height = 30
    default_callback = None
    default_speed = 0.5
    default_text = ''
    default_color = (1, 1, 1, 1)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.callback = attributes.get('callback', self.default_callback)
        self.speed = attributes.get('speed', self.default_speed)
        text = attributes.get('text', self.default_text)
        self.rollInColor = attributes.get('color', self.default_color)
        self.rollOutColor = self.rollInColor
        self.scrollOut = Transform(parent=self, align=uiconst.TOPLEFT, height=self.height)
        self.scrollOutText = eveLabel.EveCaptionLarge(text=text, parent=self.scrollOut, align=uiconst.TOLEFT, color=(1, 1, 1, 1))
        self.scrollIn = Transform(parent=self, align=uiconst.TOPLEFT, height=self.height)
        self.scrollInText = eveLabel.EveCaptionLarge(text='', parent=self.scrollIn, align=uiconst.TOLEFT, color=(1, 1, 1, 1))
        self.scrolling = False

    def RollIn(self, newText, newColor = None):
        if self.scrolling:
            return False
        self.scrollInText.text = newText
        if newColor is not None:
            self.rollInColor = newColor
            self.scrollInText.color = newColor
        self._RollIn()
        return True

    def _RollIn(self):
        if self.scrolling:
            return
        self.scrolling = True
        self.scrollIn.top = 0
        self.scrollIn.scale = (1.0, 0.0)
        s = 0.2
        uicore.animations.MorphScalar(self.scrollOut, 'top', 0, self.height - 2, self.speed, curveType=uiconst.ANIM_SMOOTH)
        uicore.animations.MorphVector2(self.scrollOut, 'scale', (1, 1), (1, 0), self.speed, curveType=uiconst.ANIM_SMOOTH)
        shadowColor = (self.rollOutColor[0] * s,
         self.rollOutColor[1] * s,
         self.rollOutColor[2] * s,
         0)
        uicore.animations.SpColorMorphTo(self.scrollOutText, self.scrollOutText.GetRGBA(), shadowColor, self.speed * 0.9, 1, uiconst.ANIM_SMOOTH)
        uicore.animations.MorphVector2(self.scrollIn, 'scale', (1, 0), (1, 1), self.speed, curveType=uiconst.ANIM_SMOOTH, callback=self.OnRolledIn)
        shadowColor = (self.rollInColor[0] * s,
         self.rollInColor[1] * s,
         self.rollInColor[2] * s,
         0)
        uicore.animations.SpColorMorphTo(self.scrollInText, shadowColor, self.rollInColor, self.speed * 0.9, 1, uiconst.ANIM_SMOOTH)

    def OnRolledIn(self):
        self.scrolling = False
        scrolledIn = self.scrollIn
        self.scrollIn = self.scrollOut
        self.scrollOut = scrolledIn
        scrolledInText = self.scrollInText
        self.scrollInText = self.scrollOutText
        self.scrollOutText = scrolledInText
        if self.callback is not None:
            self.callback(self)
