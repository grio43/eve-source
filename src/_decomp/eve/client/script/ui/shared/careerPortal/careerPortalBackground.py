#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\careerPortalBackground.py
import math
import carbonui.const as uiconst
import trinity
import uthread2
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.careerPortal import careerConst, cpSignals
HOVER_TRANSITION_DURATION = 0.3
DEFAULT_BACKGROUND = 'res:/UI/Texture/classes/careerPortal/backgrounds/hangar_background_bright.png'

class CareerPortalBackground(Container):
    default_clipChildren = True
    default_align = uiconst.CENTER
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(CareerPortalBackground, self).ApplyAttributes(attributes)
        self.PrepareUI()
        self._ConnectSignals()

    def Close(self):
        self._DisconnectSignals()
        super(CareerPortalBackground, self).Close()

    def _ConnectSignals(self):
        careerConst.SELECTED_CAREER_PATH_SETTING.on_change.connect(self.SwitchToCareerBackground)
        careerConst.CAREER_WINDOW_STATE_SETTING.on_change.connect(self.OnCareerWindowStateChanged)
        cpSignals.on_career_node_hover_on.connect(self.OnCareerNodeHoverOn)
        cpSignals.on_career_node_hover_off.connect(self.OnCareerNodeHoverOff)

    def _DisconnectSignals(self):
        careerConst.SELECTED_CAREER_PATH_SETTING.on_change.disconnect(self.SwitchToCareerBackground)
        careerConst.CAREER_WINDOW_STATE_SETTING.on_change.disconnect(self.OnCareerWindowStateChanged)
        cpSignals.on_career_node_hover_on.disconnect(self.OnCareerNodeHoverOn)
        cpSignals.on_career_node_hover_off.disconnect(self.OnCareerNodeHoverOff)

    def PrepareUI(self):
        Fill(bgParent=self, name='blackFill', color=eveColor.BLACK, opacity=0.95)
        self.airLogo = Sprite(parent=self, name='airLogo', align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/careerPortal/backgrounds/air_logo.png', width=153, height=20, top=32, left=32, color=eveColor.AIR_TURQUOISE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.4)
        self.circleBg = Sprite(parent=self, name='circleBg', align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/careerPortal/backgrounds/bg_detail.png')
        self.bgHighlights = BackgroundHighlights(parent=self, name='bgDetail', align=uiconst.CENTER)
        self.largeDottedLine = Sprite(parent=self, name='largeDottedLine', align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/careerPortal/backgrounds/bg_dottedLine.png', textureSecondaryPath='res:/UI/Texture/classes/careerPortal/backgrounds/bg_lineMask.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        self.smallDottedLine = Sprite(parent=self, name='smallDottedLine', align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/careerPortal/backgrounds/bg_dottedLine.png', textureSecondaryPath='res:/UI/Texture/classes/careerPortal/backgrounds/bg_lineMask.png', spriteEffect=trinity.TR2_SFX_MODULATE, opacity=0.5)
        self.backgroundSprite = Sprite(parent=self, name='backgroundSprite', align=uiconst.CENTER, opacity=0.4, texturePath=DEFAULT_BACKGROUND)
        self._StartRotation()
        self._RevealCareerBackground(careerConst.SELECTED_CAREER_PATH_SETTING.get())

    def SetSize(self, width, height):
        self.UpdateSize(width, height)

    def UpdateSize(self, width, height):
        self.circleBg.SetSize(width, width)
        self.bgHighlights.SetSize(width, width)
        self.largeDottedLine.SetSize(width, width)
        smallDottedLineWidth = width / 1.6
        self.smallDottedLine.SetSize(smallDottedLineWidth, smallDottedLineWidth)
        self.smallDottedLine.scaleSecondary = (0.7, 0.7)
        bgWidth = height * 1.7778
        self.backgroundSprite.SetSize(bgWidth, height)

    def OnCareerWindowStateChanged(self, state):
        width = self.parent.displayWidth
        height = self.parent.displayHeight
        self.UpdateSize(width, height)
        self.bgHighlights.StopAllHighlights()

    def SwitchToCareerBackground(self, careerID):
        animations.FadeOut(self.backgroundSprite, duration=0.4, callback=lambda : self._RevealCareerBackground(careerID))

    def _RevealCareerBackground(self, careerID):
        texturePath = careerConst.BG_IMAGE_BY_CAREER_ID.get(careerID, DEFAULT_BACKGROUND)
        self.backgroundSprite.texturePath = texturePath
        animations.FadeIn(self.backgroundSprite, endVal=0.4, duration=0.75)

    def OnCareerNodeHoverOn(self, careerPathID):
        self.bgHighlights.HighlightDetailForCareer(careerPathID)

    def OnCareerNodeHoverOff(self, careerPathID):
        self.bgHighlights.StopHighlightForCareer(careerPathID)

    def _StartRotation(self):
        animations.Tr2DRotateTo(self.largeDottedLine, startAngle=self.largeDottedLine.rotation, endAngle=-2 * math.pi, duration=460.0, loops=-1, curveType=uiconst.ANIM_LINEAR)
        animations.Tr2DRotateTo(self.smallDottedLine, startAngle=self.smallDottedLine.rotation, endAngle=2 * math.pi, duration=460.0, loops=-1, curveType=uiconst.ANIM_LINEAR)


class BackgroundHighlights(Container):

    def ApplyAttributes(self, attributes):
        super(BackgroundHighlights, self).ApplyAttributes(attributes)
        self.bgSpriteByCareerID = {}
        for careerPath, texturePath in careerConst.BG_DETAIL_BY_CAREER_ID.iteritems():
            self.bgSpriteByCareerID[careerPath] = self._ConstructSprite(texturePath)

    def _ConstructSprite(self, texturePath):
        return Sprite(parent=self, align=uiconst.TOALL, texturePath=texturePath, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)

    def HighlightDetailForCareer(self, careerPathID):
        detailSprite = self.bgSpriteByCareerID.get(careerPathID, None)
        if not detailSprite:
            return
        animations.FadeIn(detailSprite, endVal=2.0, duration=HOVER_TRANSITION_DURATION)
        animations.MorphScalar(detailSprite, 'glowBrightness', startVal=0, endVal=0.45, duration=HOVER_TRANSITION_DURATION)

    def StopHighlightForCareer(self, careerPathID):
        detailSprite = self.bgSpriteByCareerID.get(careerPathID, None)
        if not detailSprite:
            return
        self._StopHighlight(detailSprite)

    @staticmethod
    def _StopHighlight(detailSprite):
        animations.FadeTo(detailSprite, startVal=detailSprite.opacity, endVal=1.0, duration=HOVER_TRANSITION_DURATION)
        animations.MorphScalar(detailSprite, 'glowBrightness', startVal=detailSprite.glowBrightness, endVal=0, duration=HOVER_TRANSITION_DURATION)

    def StopAllHighlights(self):
        for detailSprite in self.bgSpriteByCareerID.values():
            self._StopHighlight(detailSprite)
