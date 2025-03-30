#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\moonmining\progressBar.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from carbonui.uicore import uicore
MINBAR_WIDTH = 0.008

class ProgressBar(Container):
    default_name = 'progressBar'
    default_align = uiconst.TOTOP
    default_height = 60

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        barHeight = attributes.barHeight
        color = attributes.color or (1, 1, 1, 1)
        text = attributes.text
        percentage = attributes.percentage
        self.leftLabel = EveLabelSmall(parent=self, text=text, align=uiconst.TOTOP)
        self.rightLabel = EveLabelSmall(parent=self, text='', align=uiconst.TOPRIGHT)
        self.barCont = Container(name='barCont', parent=self, align=uiconst.TOTOP, height=barHeight, padLeft=6, padRight=6)
        self.innerBarCont = Container(name='innerBarCont', parent=self.barCont, align=uiconst.TOALL)
        Frame(parent=self.innerBarCont, color=(0.5, 0.5, 0.5, 0.25))
        propWidth = max(MINBAR_WIDTH, percentage)
        self.propCont = Container(name='propCont', parent=self.innerBarCont, align=uiconst.TOLEFT_PROP, width=propWidth, padding=1)
        self.fillCont = Container(name='fillCont', parent=self.propCont, align=uiconst.TOALL, clipChildren=True)
        self.fill = Fill(parent=self.fillCont)
        self.marker = Sprite(parent=self.propCont, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/classes/Moonmining/inProgressMarker2.png', pos=(-4, 0, 9, 9), idx=0)
        self.endMarker = Sprite(parent=self.barCont, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/classes/Moonmining/scheduleMarker.png', pos=(-8, 0, 17, 9), idx=0)
        self.centerMarker = Sprite(parent=self.barCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/Moonmining/scheduleMarker.png', pos=(0, 0, 17, 9), idx=0)
        self.centerMarker.display = False
        self.flashSprite = Sprite(parent=self.fillCont, align=uiconst.TOALL, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', color=color, opacity=0.2, tileX=True)
        padTop = barHeight - 30 + 3
        dottedLine = Sprite(parent=self.innerBarCont, texturePath='res:/UI/Texture/classes/Moonmining/dottedLine.png', align=uiconst.TOALL, padTop=padTop, pos=(0, 0, 0, 0), state=uiconst.UI_DISABLED, tileX=True, tileY=True, opacity=0.25)
        self.ColorElement(color)

    def ColorElement(self, color):
        c = Color(*color)
        brightness = c.GetBrightness()
        fillColor = c.SetBrightness(max(brightness - 0.2, 0)).GetRGBA()
        fillColor = fillColor[:3] + (0.5,)
        self.fill.SetRGBA(*fillColor)

    def ChangeCenterMarkerDisplay(self, doDisplay):
        self.centerMarker.display = doDisplay
        self.endMarker.display = not doDisplay
        self.marker.display = not doDisplay

    def ChangeAnimationState(self, turnOnArrows, turnOnBlinking = True):
        if turnOnArrows:
            if not uicore.animations.IsAnimating(self.flashSprite, 'left'):
                self.flashSprite.display = True
                uicore.animations.MorphScalar(self.flashSprite, 'left', -120, 0, duration=4.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        else:
            self.flashSprite.StopAnimations()
            self.flashSprite.display = False
        if turnOnBlinking:
            if not uicore.animations.IsAnimating(self.fill, 'opacity'):
                uicore.animations.MorphScalar(self.fill, 'opacity', 0.5, 1.0, duration=1.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        else:
            self.fill.StopAnimations()
            self.fill.opacity = 0.5

    def UpdateProgress(self, percentage):
        self.propCont.width = max(MINBAR_WIDTH, percentage)
