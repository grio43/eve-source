#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charSelection\characterSlots.py
import math
import blue
import carbonui.const as uiconst
import carbonui.fontconst
import eve.client.script.ui.login.charSelection.characterSelectionColors as csColors
import eve.client.script.ui.login.charSelection.characterSelectionUtils as csUtil
import evetypes
import inventorycommon.typeHelpers
import localization
import log
import trinity
import uthread
from caching.memoize import Memoize
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util import timerstuff
from carbon.common.script.util.format import IntToRoman
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.control.eveIcon import CorpIcon
from eve.client.script.ui.login.charSelection.characterSelectionUtils import SetColor, MakeTransparent, SetEffectOpacity, SetSaturation
from eve.client.script.ui.shared.neocom.corporation.war.atWarTooltip import LoadAtWarTooltipPanel
from eve.client.script.ui.shared.radialMenu.radialMenu import ThreePartContainer
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem
from eve.common.script.sys.idCheckers import IsVoidSpaceSystem
from eve.common.script.util import eveFormat
from security.client.fonticons import get_font_icon_text
SHIP_BOUNDING_BOXES = {}

class SmallSlot(Container):
    __notifyevents__ = ['OnExternalDragInitiated', 'OnExternalDragEnded', 'OnTokensRedeemed']
    default_align = uiconst.TOLEFT
    default_width = 200
    default_state = uiconst.UI_NORMAL
    maxImageSize = 256
    paddingName = 20
    outerFrameWidth = 2
    innerFrameWidth = 1
    distanceFromOuterToInnerFrame_side = 4
    distanceFromOuterToInnerFrame_bottom = 4
    distanceFromInnerFrameToContent_sides = 6
    distanceFromInnerFrameToContent_bottom = 6
    isEmptySlot = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.callback = attributes.get('callback', None)
        self.doubleClickCallback = attributes.get('doubleClickCallback', None)
        self.slotIdx = attributes.get('slotIdx')
        self.charID = None
        self.mouseOverState = False
        self.enteringGameWithSlot = False
        innerslotPadding = self.outerFrameWidth + self.distanceFromOuterToInnerFrame_side
        self.innerSlotCont = Container(parent=self, name='innerSlotCont', padding=innerslotPadding)
        self.slotBackground = Fill(bgParent=self.innerSlotCont, color=csColors.SLOT_BACKGROUND, padding=0)
        frameCornerSize = 2 + self.innerFrameWidth
        glowFrameTexturePath = 'res:/UI/Texture/classes/CharacterSelection/glowDotFrame.png'
        self.normalGlowFrame = Frame(parent=self.innerSlotCont, name='glowFrame', color=csColors.FRAME_GLOW_ACTIVE, frameConst=(glowFrameTexturePath,
         5,
         -2,
         0), padding=0)
        self.normalFrame = Frame(parent=self.innerSlotCont, name='normalFrame', padding=0, color=csColors.INNER_FRAME_INACTIVE, frameConst=('ui_1_16_161',
         frameCornerSize,
         -2,
         0))
        self.drawLineLeft = ThreePartContainer(parent=self.innerSlotCont, name='endDots', align=uiconst.TOLEFT_NOPUSH, state=uiconst.UI_DISABLED, pos=(0, 0, 2, 0), idx=0, leftTexturePath='res:/UI/Texture/classes/CharacterSelection/topDot.png', rightTexturePath='res:/UI/Texture/classes/CharacterSelection/bottomDots.png', sideSize=20, color=csColors.FRAME_GLOW_ACTIVE, orientation='vertical')
        self.drawLineLeft.opacity = 0
        self.drawLineRight = ThreePartContainer(parent=self.innerSlotCont, name='endDots', align=uiconst.TORIGHT_NOPUSH, state=uiconst.UI_DISABLED, pos=(0, 0, 2, 0), idx=0, leftTexturePath='res:/UI/Texture/classes/CharacterSelection/topDot.png', rightTexturePath='res:/UI/Texture/classes/CharacterSelection/bottomDots.png', sideSize=20, color=csColors.FRAME_GLOW_ACTIVE, orientation='vertical')
        self.drawLineRight.opacity = 0
        offSetBottom = self.outerFrameWidth + self.distanceFromOuterToInnerFrame_bottom
        texturePath = 'res:/UI/Texture/classes/CharacterSelection/selectFrame.png'
        self.selectionFrameGlow = Frame(parent=self.innerSlotCont, name='selectionFrame', color=csColors.FRAME_GLOW_ACTIVE, frameConst=(texturePath,
         22,
         0,
         0), padding=(-innerslotPadding,
         -innerslotPadding,
         -innerslotPadding,
         -offSetBottom))
        self.selectionFrameGlow.opacity = 0
        frameCornerSize = 2 + self.outerFrameWidth
        self.selectionFrame = Frame(parent=self.innerSlotCont, name='selectionFrame', color=csColors.OUTER_FRAME, frameConst=('ui_1_16_161',
         frameCornerSize,
         -2,
         0), padding=(-innerslotPadding,
         -innerslotPadding,
         -innerslotPadding,
         -offSetBottom))
        self.selectionFrame.opacity = 0
        infoContPadding = self.distanceFromInnerFrameToContent_sides + self.innerFrameWidth
        self.infoCont = ContainerAutoSize(parent=self.innerSlotCont, name='infoCont', padding=infoContPadding, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.nameCont = Container(parent=self, name='nameCont', align=uiconst.TOTOP, height=28, padLeft=0, padRight=0, idx=0)
        inactivePadding = (innerslotPadding,
         0,
         innerslotPadding,
         4)
        self.nameSelectionFillActive = Fill(bgParent=self.nameCont, padding=(0, 0, 0, 4), color=csColors.NAME_CONT_FILL_ACTIVE)
        self.nameSelectionFillInactive = Fill(bgParent=self.nameCont, padding=inactivePadding, color=csColors.NAME_CONT_FILL_INACTIVE)
        self.nameSelectionFillRedeemMode = Fill(bgParent=self.nameCont, padding=inactivePadding, color=csColors.NAME_CONT_FILL_ACTIVE)
        self.innerNameCont = Container(parent=self.nameCont, padRight=innerslotPadding, clipChildren=True)
        self.characterNameLabel = eveLabel.EveLabelLargeBold(parent=self.innerNameCont, name='characterNameLabel', align=uiconst.CENTERLEFT, text='', padLeft=8 + innerslotPadding, top=-2)
        self.characterNameLabel.letterspace = 1
        self.characterNameLabel.SetTextColor(csColors.NAME_LABEL_ACTIVE)
        extraPadding = self.GetExtraWidth()
        self.portraitCont = Container(parent=self.infoCont, name='portraitCont', align=uiconst.TOTOP, height=self.width - extraPadding, clipChildren=True)
        self.portraitInnerCont = Container(parent=self.portraitCont, name='portraitInnerCont', align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=True, state=uiconst.UI_PICKCHILDREN)
        self.portraitSprite = Sprite(parent=self.portraitInnerCont, name='portraitSprite', align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/CharacterSelection/silhuette.png', pos=(0, 0, 0, 0), state=uiconst.UI_PICKCHILDREN, color=(0.5, 0.5, 0.5, 1.0), saturation=csColors.PORTRAIT_INACTIVE_SATURATION, spriteEffect=trinity.TR2_SFX_SOFTLIGHT)
        self.portraitGrid = Sprite(parent=self.portraitInnerCont, texturePath='res:/UI/Texture/classes/CharacterSelection/Grid_ships_plus2.png', align=uiconst.TOALL, pos=(0, 0, 0, 0), color=csColors.GRID_ACTIVE, state=uiconst.UI_DISABLED, tileX=True, tileY=True)
        offset = self.distanceFromInnerFrameToContent_bottom + self.innerFrameWidth
        self.shipAndLocationCont = CharacterDetailsLocation(parent=self.innerSlotCont, padding=(infoContPadding,
         infoContPadding,
         infoContPadding,
         offset), callback=self.OnClick, isEmptySlot=self.isEmptySlot, clipChildren=True)
        self.skillQueueCont = SkillQueueCont(parent=self.infoCont, padTop=self.distanceFromInnerFrameToContent_sides)
        self.AddCharacterDetailsLines()
        sm.RegisterNotify(self)

    def AddCharacterDetailsLines(self):
        self.skillContainer = CharacterDetailsLine(parent=self.infoCont, iconPath='res:/UI/Texture/classes/CharacterSelection/skills.png', text='')
        self.walletContainer = CharacterDetailsLine(parent=self.infoCont, iconPath='res:/UI/Texture/classes/CharacterSelection/isk.png', text='')
        self.mailContainer = CharacterDetailsLine(parent=self.infoCont, iconPath='res:/UI/Texture/classes/CharacterSelection/mail.png', text='', addLine=False)

    def SetMouseExitState(self, animate = False):
        if self.enteringGameWithSlot:
            return
        self.mouseOverState = False
        self.SetDisabled(animate=animate)

    def SetMouseOverState(self, animate = False):
        self.mouseOverState = True
        self.SetEnabled(animate=animate)
        SetColor(self.selectionFrame, csColors.OUTER_FRAME, animate=animate)
        SetColor(self.selectionFrameGlow, csColors.FRAME_GLOW_ACTIVE, animate=animate)
        SetColor(self.normalGlowFrame, csColors.FRAME_GLOW_ACTIVE, animate=animate)
        SetColor(self.normalFrame, csColors.INNER_FRAME_ACTIVE, animate=animate)

    def SetEnabled(self, redeemMode = False, animate = False):
        if redeemMode:
            MakeTransparent(self.nameSelectionFillActive, animate=animate)
            SetColor(self.nameSelectionFillRedeemMode, csColors.NAME_CONT_FILL_ACTIVE, animate=animate)
        else:
            SetColor(self.nameSelectionFillActive, csColors.NAME_CONT_FILL_ACTIVE, animate=animate)
            MakeTransparent(self.nameSelectionFillRedeemMode, animate=animate)
        MakeTransparent(self.nameSelectionFillInactive, animate=animate)
        self.shipAndLocationCont.SetSelected(animate=animate)
        self.SetInfoLineActiveState(isActive=True, animate=animate)
        self.shipAndLocationCont.SetActiveState(isActive=True, animate=animate)
        if not csUtil.IsMonochromeStyleEnabled():
            SetColor(self.portraitSprite, (1, 1, 1, 1), animate=animate)
            SetEffectOpacity(self.portraitSprite, newOpacity=0, animate=animate)
            SetSaturation(self.portraitSprite, newSaturation=1.0, animate=animate)
        self.skillQueueCont.SetSelected(animate=animate)

    def SetDisabled(self, animate = False):
        SetColor(self.normalFrame, csColors.INNER_FRAME_INACTIVE, animate=animate)
        SetColor(self.normalGlowFrame, csColors.FRAME_GLOW_INACTIVE, animate=animate)
        MakeTransparent(self.selectionFrame, animate=animate)
        MakeTransparent(self.selectionFrameGlow, animate=animate)
        MakeTransparent(self.nameSelectionFillActive, animate=animate)
        MakeTransparent(self.nameSelectionFillRedeemMode, animate=animate)
        SetColor(self.nameSelectionFillInactive, csColors.NAME_CONT_FILL_INACTIVE, animate=animate)
        self.shipAndLocationCont.SetDeselected(animate=animate)
        self.SetInfoLineActiveState(isActive=False, animate=animate)
        self.shipAndLocationCont.SetActiveState(isActive=False, animate=animate)
        SetColor(self.portraitSprite, csColors.PORTRAIT_INACTIVE, animate=animate)
        SetEffectOpacity(self.portraitSprite, newOpacity=csColors.PORTRAIT_INACTIVE_EFFECT_OPACITY, animate=animate)
        SetSaturation(self.portraitSprite, newSaturation=csColors.PORTRAIT_INACTIVE_SATURATION, animate=animate)
        self.skillQueueCont.SetDeselected(animate=animate)

    def SetInfoLineActiveState(self, isActive = True, animate = False):
        for eachCont in (self.skillContainer, self.walletContainer, self.mailContainer):
            eachCont.SetActiveState(isActive=isActive, animate=animate)

    def GetShipAndLocationContHeight(self):
        return self.shipAndLocationCont.GetHeight()

    def SetShipContHeight(self, height):
        self.shipAndLocationCont.SetShipContHeight(height)

    def OnClick(self, *_):
        if self.callback:
            self.callback(self)

    def OnDblClick(self, *_):
        if self.doubleClickCallback:
            self.doubleClickCallback(self)

    @classmethod
    def GetExtraWidth(cls):
        outerFrameToInnerFrame = cls.outerFrameWidth + cls.distanceFromOuterToInnerFrame_side
        innerFrameToConent = cls.innerFrameWidth + cls.distanceFromInnerFrameToContent_sides
        totalPadding = outerFrameToInnerFrame + innerFrameToConent
        return 2 * totalPadding

    def GetSlotHeight(self, shipVisible = True):
        w, infoContHeight = self.infoCont.GetAbsoluteSize()
        shipContHeight = self.shipAndLocationCont.GetHeight(shipVisible=shipVisible)
        nameContHeight = self.nameCont.height
        innerContPadding = self.innerSlotCont.padTop + self.innerSlotCont.padBottom
        infoContPadding = self.infoCont.padTop + self.infoCont.padBottom
        shipContPadding = self.shipAndLocationCont.padBottom
        totalPadding = innerContPadding + infoContPadding + shipContPadding
        contentHeight = infoContHeight + shipContHeight + nameContHeight + totalPadding
        return contentHeight

    def ExpandSlot(self, animate = True):
        if animate:
            uicore.animations.MorphScalar(self, 'opacity', startVal=self.opacity, endVal=1.0, duration=csUtil.COLLAPSE_TIME)
        else:
            self.opacity = 1.0
        self.shipAndLocationCont.ExpandShipSection(animate=animate)

    def SetActiveInRedeeemMode(self):
        pass

    def CollapseSlot(self, animate = True):
        self.shipAndLocationCont.CollapseShipSection(animate=animate)

    def OnIconMouseEnter(self, icon, buttonIconOnMouseEnter):
        preparingForDelete = self.characterDetails and bool(self.characterDetails.GetDeletePrepareTime())
        if not preparingForDelete:
            self.SetMouseOverState(animate=False)
        buttonIconOnMouseEnter()

    def OnExternalDragInitiated(self, dragSource, dragData):
        self.SetActiveInRedeeemMode()

    def OnExternalDragEnded(self, *args):
        if uicore.uilib.mouseOver == self or uicore.uilib.mouseOver.IsUnder(self):
            self.SetMouseOverState(animate=True)
        else:
            self.SetMouseExitState(animate=True)

    def OnTokensRedeemed(self, charID, stationID, tokensRedeemed, numItemsCreated):
        if charID != self.charID:
            return
        uicore.animations.BlinkOut(self, startVal=1.0, endVal=0.5, duration=0.3, loops=1, curveType=uiconst.ANIM_BOUNCE)

    def AnimateSlotIn(self, animationOffset = 0.0, soundFunction = None, charContHeight = 100):
        self.enteringGameWithSlot = False
        minBlinkValue = 0.2
        blinkDuration = 0.1
        lineAnimationOffset = animationOffset
        lineAnimationDuration = 0.4
        lineFadeOutOffset = lineAnimationOffset + lineAnimationDuration
        lineFadeOutDuration = 0.2
        uicore.animations.MorphScalar(self.drawLineLeft, 'padTop', startVal=(charContHeight - 30) / 2.0, endVal=0.0, duration=lineAnimationDuration, timeOffset=lineAnimationOffset)
        uicore.animations.MorphScalar(self.drawLineLeft, 'padBottom', startVal=(charContHeight - 30) / 2.0, endVal=0.0, duration=lineAnimationDuration, timeOffset=lineAnimationOffset)
        uicore.animations.MorphScalar(self.drawLineLeft, 'opacity', startVal=0.8, endVal=0, duration=lineFadeOutDuration, timeOffset=lineFadeOutOffset)
        uicore.animations.MorphScalar(self.drawLineRight, 'padTop', startVal=(charContHeight - 30) / 2.0, endVal=0.0, duration=lineAnimationDuration, timeOffset=lineAnimationOffset)
        uicore.animations.MorphScalar(self.drawLineRight, 'padBottom', startVal=(charContHeight - 30) / 2.0, endVal=0.0, duration=lineAnimationDuration, timeOffset=lineAnimationOffset)
        uicore.animations.MorphScalar(self.drawLineRight, 'opacity', startVal=0.8, endVal=0, duration=lineFadeOutDuration, timeOffset=lineFadeOutOffset)
        normalFrameFadeOffset = lineFadeOutDuration + lineFadeOutOffset - 0.2
        normalFrameFadeDuration = 0.4
        uthread.new(soundFunction, event='character_selection_animobject', sleepTime=normalFrameFadeOffset)
        uicore.animations.MorphScalar(self.normalFrame, 'opacity', startVal=0, endVal=csColors.INNER_FRAME_INACTIVE[3], duration=normalFrameFadeDuration, timeOffset=normalFrameFadeOffset)
        nameContDuration = 0.2
        uicore.animations.MorphScalar(self.nameCont, 'opacity', startVal=0.0, endVal=1.0, duration=nameContDuration, timeOffset=normalFrameFadeOffset)
        uicore.animations.BlinkIn(self.nameSelectionFillActive, startVal=0.0, endVal=1.0, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, callback=None, sleep=False, timeOffset=normalFrameFadeOffset)
        portraitOffset = normalFrameFadeOffset + normalFrameFadeDuration - 0.2
        portraitDuration = 0.2
        uicore.animations.MorphScalar(self.portraitInnerCont, 'padTop', startVal=self.portraitCont.height / 2.0, endVal=0, duration=portraitDuration, timeOffset=portraitOffset)
        uicore.animations.MorphScalar(self.portraitInnerCont, 'padBottom', startVal=self.portraitCont.height / 2.0, endVal=0, duration=portraitDuration, timeOffset=portraitOffset)
        uicore.animations.BlinkIn(self.portraitInnerCont, startVal=1.0, endVal=minBlinkValue, duration=blinkDuration, curveType=uiconst.ANIM_BOUNCE, timeOffset=portraitOffset + portraitDuration)
        uicore.animations.SpColorMorphTo(self.slotBackground, startColor=(0, 0, 0, 0), endColor=csColors.SLOT_BACKGROUND, duration=1.0, timeOffset=portraitOffset)
        skillQueueOffset = portraitOffset + portraitDuration
        skillQueueDuration = 0.1
        uicore.animations.MorphScalar(self.skillQueueCont, 'opacity', startVal=0.0, endVal=1.0, duration=skillQueueDuration, timeOffset=skillQueueOffset)
        uthread.new(soundFunction, event='character_selection_animobject', sleepTime=skillQueueOffset)
        contOffset = skillQueueOffset + skillQueueDuration
        contDuration = 0.03
        for contIdx, eachCont in enumerate([self.skillContainer, self.walletContainer, self.mailContainer]):
            contOffset += contIdx * contDuration
            uicore.animations.BlinkIn(eachCont.icon, startVal=csColors.LINES_ICON_INACTIVE[3], endVal=minBlinkValue, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=contOffset)
            uicore.animations.BlinkIn(eachCont.textLabel, startVal=1.0, endVal=minBlinkValue, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=contOffset)
            uicore.animations.MorphScalar(eachCont, 'opacity', startVal=0.0, endVal=1.0, duration=contDuration, loops=2, timeOffset=contOffset)
            bigTextLabel = getattr(eachCont, 'bigTextLabel', None)
            if bigTextLabel:
                uicore.animations.BlinkIn(bigTextLabel, startVal=1.0, endVal=minBlinkValue, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=contOffset)

        shipLocationOffset = contOffset + contDuration
        shipLocationBlinkOffset = shipLocationOffset + 0.05
        shipLocationDuration = 0.2
        uicore.animations.MorphScalar(self.shipAndLocationCont, 'opacity', startVal=0.0, endVal=1.0, duration=shipLocationDuration, loops=1, timeOffset=shipLocationBlinkOffset)
        uicore.animations.BlinkIn(self.shipAndLocationCont.locationCont, startVal=1.0, endVal=minBlinkValue, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=shipLocationBlinkOffset)
        uicore.animations.BlinkIn(self.shipAndLocationCont.shipParentCont, startVal=1.0, endVal=minBlinkValue, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=shipLocationOffset)

    def AnimateSlotOut(self, animationOffset = 0.0, soundFunction = None, charContHeight = 100):
        minBlinkValue = 0.2
        blinkDuration = 0.1
        uthread.new(soundFunction, event='character_selection_animobject', sleepTime=animationOffset)
        shipLocationOffset = animationOffset
        shipLocationBlinkOffset = shipLocationOffset + 0.05
        shipLocationDuration = 0.2
        uicore.animations.MorphScalar(self.shipAndLocationCont, 'opacity', startVal=1.0, endVal=0.0, duration=shipLocationDuration, loops=1, timeOffset=shipLocationBlinkOffset)
        uicore.animations.BlinkOut(self.shipAndLocationCont.locationCont, startVal=1.0, endVal=minBlinkValue, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=shipLocationBlinkOffset)
        uicore.animations.BlinkOut(self.shipAndLocationCont.shipParentCont, startVal=1.0, endVal=minBlinkValue, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=shipLocationOffset)
        contOffset = shipLocationOffset + shipLocationDuration
        contDuration = 0.03
        for contIdx, eachCont in enumerate([self.mailContainer, self.walletContainer, self.skillContainer]):
            contOffset += contIdx * contDuration
            uicore.animations.BlinkOut(eachCont.icon, startVal=eachCont.icon.opacity, endVal=minBlinkValue, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=contOffset)
            uicore.animations.BlinkOut(eachCont.textLabel, startVal=eachCont.icon.opacity, endVal=minBlinkValue, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=contOffset)
            uicore.animations.MorphScalar(eachCont, 'opacity', startVal=1.0, endVal=0.0, duration=contDuration, loops=2, timeOffset=contOffset)
            bigTextLabel = getattr(eachCont, 'bigTextLabel', None)
            if bigTextLabel:
                uicore.animations.BlinkOut(bigTextLabel, startVal=1.0, endVal=minBlinkValue, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=contOffset)

        skillQueueOffset = contOffset + contDuration
        skillQueueDuration = 0.1
        uicore.animations.MorphScalar(self.skillQueueCont, 'opacity', startVal=1.0, endVal=0.0, duration=skillQueueDuration, timeOffset=skillQueueOffset)
        uthread.new(soundFunction, event='character_selection_animobject', sleepTime=skillQueueOffset)
        portraitOffset = skillQueueOffset + skillQueueDuration
        portraitDuration = 0.2
        uicore.animations.MorphScalar(self.portraitInnerCont, 'padTop', startVal=0, endVal=self.portraitCont.height / 2.0, duration=portraitDuration, timeOffset=portraitOffset)
        uicore.animations.MorphScalar(self.portraitInnerCont, 'padBottom', startVal=0, endVal=self.portraitCont.height / 2.0, duration=portraitDuration, timeOffset=portraitOffset)
        uicore.animations.BlinkOut(self.portraitInnerCont, startVal=1.0, endVal=minBlinkValue, duration=blinkDuration, curveType=uiconst.ANIM_BOUNCE, timeOffset=portraitOffset + portraitDuration)
        uicore.animations.SpColorMorphTo(self.slotBackground, startColor=csColors.SLOT_BACKGROUND, endColor=(0, 0, 0, 0), duration=0.5, timeOffset=portraitOffset)
        normalFrameFadeOffset = portraitOffset + portraitDuration
        normalFrameFadeDuration = 0.4
        uicore.animations.MorphScalar(self.normalFrame, 'opacity', startVal=csColors.INNER_FRAME_INACTIVE[3], endVal=0, duration=normalFrameFadeDuration, timeOffset=normalFrameFadeOffset)
        nameContDuration = 0.2
        uicore.animations.MorphScalar(self.nameCont, 'opacity', startVal=1.0, endVal=0.0, duration=nameContDuration, timeOffset=normalFrameFadeOffset)
        uicore.animations.BlinkOut(self.nameSelectionFillActive, startVal=0.0, endVal=1.0, duration=blinkDuration, loops=2, curveType=uiconst.ANIM_BOUNCE, callback=None, sleep=False, timeOffset=normalFrameFadeOffset)
        lineAnimationOffset = normalFrameFadeOffset + nameContDuration
        lineAnimationDuration = 0.4
        lineFadeOutOffset = lineAnimationOffset + lineAnimationDuration
        lineFadeOutDuration = 0.2
        uicore.animations.MorphScalar(self.drawLineLeft, 'padTop', startVal=0, endVal=(charContHeight - 30) / 2.0, duration=lineAnimationDuration, timeOffset=lineAnimationOffset)
        uicore.animations.MorphScalar(self.drawLineLeft, 'padBottom', startVal=0, endVal=(charContHeight - 30) / 2.0, duration=lineAnimationDuration, timeOffset=lineAnimationOffset)
        uicore.animations.MorphScalar(self.drawLineLeft, 'opacity', startVal=0.8, endVal=0.0, duration=lineFadeOutDuration, timeOffset=lineFadeOutOffset)
        uicore.animations.MorphScalar(self.drawLineRight, 'padTop', startVal=0, endVal=(charContHeight - 30) / 2.0, duration=lineAnimationDuration, timeOffset=lineAnimationOffset)
        uicore.animations.MorphScalar(self.drawLineRight, 'padBottom', startVal=0, endVal=(charContHeight - 30) / 2.0, duration=lineAnimationDuration, timeOffset=lineAnimationOffset)
        uicore.animations.MorphScalar(self.drawLineRight, 'opacity', startVal=0.8, endVal=0, duration=lineFadeOutDuration, timeOffset=lineFadeOutOffset, curveType=uiconst.ANIM_BOUNCE)

    def PlaySelectedAnimation(self):
        self.enteringGameWithSlot = True
        uicore.animations.BlinkIn(self.selectionFrame, startVal=csColors.OUTER_FRAME[3], endVal=0.0, duration=0.1, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=0.2)
        uicore.animations.BlinkIn(self.nameSelectionFillActive, startVal=csColors.NAME_CONT_FILL_ACTIVE[3], endVal=0.0, duration=0.1, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=0.2)
        uicore.animations.BlinkIn(self.shipAndLocationCont.locationBg, startVal=csColors.LOCATION_FILL_ACTIVE[3], endVal=0.0, duration=0.1, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=0.2)
        uicore.animations.BlinkIn(self.skillQueueCont.fill, startVal=csColors.SKILLQUEUE_FILL_ACTIVE[3], endVal=0.0, duration=0.1, loops=2, curveType=uiconst.ANIM_BOUNCE, timeOffset=0.2)
        sm.GetService('audio').SendUIEvent('character_select_character')


class SmallCharacterSlot(SmallSlot):
    default_name = 'smallCharacterSlot'
    __notifyevents__ = ['OnExternalDragInitiated', 'OnExternalDragEnded', 'OnTokensRedeemed']

    def ApplyAttributes(self, attributes):
        SmallSlot.ApplyAttributes(self, attributes)
        self.slotLoaded = False
        self.characterDetails = None
        self.deleteCallback = attributes.get('deleteCallback', None)
        self.undoDeleteCallback = attributes.get('undoDeleteCallback', None)
        self.terminateCallback = attributes.get('terminateCallback', None)
        self.corpCont = Container(parent=self.portraitInnerCont, name='corpLabel', align=uiconst.BOTTOMLEFT, pos=(0, 0, 48, 48), idx=0)
        self.allianceLogo = Sprite(parent=self.portraitInnerCont, name='allianceLogo', align=uiconst.BOTTOMRIGHT, state=uiconst.UI_NORMAL, pos=(0, 0, 48, 48), idx=0, spriteEffect=trinity.TR2_SFX_SOFTLIGHT)
        self.allianceLogo.OnClick = self.OnClick
        atWarLeft = self.corpCont.left + self.corpCont.width
        atWarTop = self.corpCont.top + self.corpCont.height - 20
        self.atWarSprite = Sprite(parent=self.portraitInnerCont, name='characterIsAtWar', align=uiconst.BOTTOMLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/war/atWar_24.png', pos=(atWarLeft,
         atWarTop,
         20,
         20), spriteEffect=trinity.TR2_SFX_SOFTLIGHT, idx=0)
        self.atWarSprite.SetRGBA(1.0, 0.0, 0.0, 1.0)
        self.deleteCont = ContainerAutoSize(parent=self.nameCont, name='deleteCont', align=uiconst.TORIGHT, alignMode=uiconst.TORIGHT, pos=(12, -2, 32, 16), state=uiconst.UI_PICKCHILDREN, idx=0)
        self.deleteCont.display = False
        self.deleteButton1 = DeleteButton(parent=self.deleteCont, name='deleteButton', texturePath='res:/UI/Texture/Icons/Plus_Small.png', state=uiconst.UI_NORMAL, color=(1.0, 0.0, 0.0, 1.0), callback=self.DeleteButton1Clicked, hint=localization.GetByLabel('UI/CharacterSelection/CompleteTermination'), rotation=math.pi / 4.0, onMouseEnterCallback=self.OnMouseEnter, onMouseExitCallback=self.OnMouseExit)
        iconOnMouseEnter = self.deleteButton1.OnMouseEnter
        self.deleteButton1.OnMouseEnter = (self.OnIconMouseEnter, self.deleteButton1, iconOnMouseEnter)
        self.deleteButton2 = DeleteButton(parent=self.deleteCont, name='cancelDeteleButton', texturePath='res:/UI/Texture/Icons/Plus_Small.png', state=uiconst.UI_NORMAL, callback=self.DeleteButton2Clicked, color=(1.0, 1.0, 1.0, 1.0), hint=localization.GetByLabel('UI/CharacterSelection/RemoveFromBiomass'))
        iconOnMouseEnter = self.deleteButton2.OnMouseEnter
        self.deleteButton2.OnMouseEnter = (self.OnIconMouseEnter, self.deleteButton2, iconOnMouseEnter)
        self.timeCont = Container(parent=self.deleteCont, name='timeCont', align=uiconst.TORIGHT, width=20)
        self.timeLabel = eveLabel.EveLabelLargeBold(parent=self.timeCont, name='textLabel', align=uiconst.CENTERLEFT, text='00:00:00', state=uiconst.UI_DISABLED)
        self.timeCont.width = self.timeLabel.textwidth + 6
        sm.RegisterNotify(self)

    def LoadSlot(self, charID, characterDetails):
        self.charID = charID
        self.characterDetails = characterDetails
        sm.GetService('photo').GetPortrait(charID, 512, self.portraitSprite)
        self.portraitGrid.display = False
        self.characterNameLabel.text = cfg.eveowners.Get(charID).name
        corpID, allianceID = characterDetails.GetCorporationInfo()
        self.corpCont.Flush()
        self.corpLogo = eveIcon.GetLogoIcon(itemID=corpID, parent=self.corpCont, align=uiconst.TOPLEFT, name='corpLogo', state=uiconst.UI_NORMAL, size=48, ignoreSize=True, dontUseThread=True)
        self.corpLogo.OnClick = self.OnClick
        self.corpLogo.OnMouseEnter = lambda *args: PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if isinstance(self.corpLogo, CorpIcon):
            for eachLogo in self.corpLogo.children:
                eachLogo.originalColor = eachLogo.GetRGBA()
                if eachLogo.spriteEffect == trinity.TR2_SFX_MASK:
                    newColor = self.FindPlayerCorpLogoColor(eachLogo)
                    SetColor(eachLogo, newColor, animate=False)
                else:
                    eachLogo.spriteEffect = trinity.TR2_SFX_SOFTLIGHT
                    SetColor(eachLogo, csColors.PORTRAIT_INACTIVE, animate=False)
                    SetEffectOpacity(eachLogo, csColors.PORTRAIT_INACTIVE_EFFECT_OPACITY, animate=False)
                    SetSaturation(eachLogo, 0.0, animate=False)

        else:
            self.corpLogo.spriteEffect = trinity.TR2_SFX_SOFTLIGHT
            SetColor(self.corpLogo, csColors.PORTRAIT_INACTIVE, animate=False)
            SetEffectOpacity(self.corpLogo, csColors.PORTRAIT_INACTIVE_EFFECT_OPACITY, animate=False)
            SetSaturation(self.corpLogo, 0.0, animate=False)
        self.corpLogo.hint = cfg.eveowners.Get(corpID).name
        if csUtil.IsMonochromeStyleEnabled():
            if isinstance(self.corpLogo, CorpIcon):
                for eachLogo in self.corpLogo.children:
                    csUtil.SetMonochromeStyle(eachLogo, True)

            else:
                csUtil.SetMonochromeStyle(self.corpLogo, True)
        self.allianceLogo.SetTexturePath('')
        if allianceID is not None:
            uthread.new(self.LoadAllianceLogo, self.allianceLogo, allianceID)
        self.shipAndLocationCont.LoadInfo(characterDetails)
        newlyFinishedSkills = characterDetails.GetFinishedSkills()
        if newlyFinishedSkills:
            skillText = localization.GetByLabel('UI/CharacterSelection/NumSkillsCompleted', skillCount=newlyFinishedSkills)
        else:
            sp = characterDetails.GetSkillInfo() or 0
            skillText = localization.formatters.FormatNumeric(sp, useGrouping=True)
        self.skillContainer.SetTextAndEnableContainer(skillText)
        balance = characterDetails.GetWalletBalance()
        balance = eveFormat.FmtISK(balance, showFractionsAlways=0)
        walletChange = characterDetails.GetWalletChanged()
        if walletChange > 0:
            iconPath2 = 'res:/UI/Texture/classes/CharacterSelection/up.png'
        elif walletChange < 0:
            iconPath2 = 'res:/UI/Texture/classes/CharacterSelection/down.png'
        else:
            iconPath2 = None
        self.walletContainer.SetTextAndEnableContainer(balance)
        if walletChange:
            value = eveFormat.FmtISK(walletChange, showFractionsAlways=bool(abs(walletChange) < 1))
            prefix = '<color=#FFFF1919>' if walletChange < 0 else '<color=#FF19FF19>+'
            walletHint = '%s<br>%s%s</color>' % (localization.GetByLabel('UI/Neocom/Blink/ISKBalanceChanged'), prefix, value)
        else:
            walletHint = ''
        self.walletContainer.SetSecondIcon(iconPath2, walletHint)
        unreadMails = characterDetails.GetUnreaddMailCount()
        if unreadMails:
            unreadMailsText = localization.GetByLabel('UI/CharacterSelection/NumUnreadMails', mailCount=unreadMails)
        else:
            unreadMailsText = localization.GetByLabel('UI/CharacterSelection/NoUnreadMails')
        self.mailContainer.SetTextAndEnableContainer(unreadMailsText)
        characterIsAtWar = characterDetails.IsCharacterAtWar()
        self.atWarSprite.display = characterIsAtWar
        self.atWarSprite.LoadTooltipPanel = lambda tooltipPanel, *args: self.LoadAtWarTooltipPanel(tooltipPanel, characterDetails)
        trainingInfo = characterDetails.GetSkillInTrainingInfo()
        currentSkill = trainingInfo.get('currentSkill', None)
        if currentSkill is not None:
            level = trainingInfo.get('level', 1)
            romanNumber = IntToRoman(min(5, int(level)))
            startTime = trainingInfo.get('trainingStartTime')
            finishTime = trainingInfo.get('trainingEndTime')
            now = blue.os.GetWallclockTime()
            timeLeft = max(0, finishTime - now)
            fromSP = trainingInfo.get('fromSP')
            finishSP = trainingInfo.get('finishSP')
            trainedSP = trainingInfo.get('trainedSP')
            currentTimeProgress = min(1.0, float(now - startTime) / (finishTime - startTime))
            currentTrained = currentTimeProgress * (finishSP - fromSP) + (trainedSP - fromSP)
            progress = currentTrained / finishSP
            progress = min([progress, 1.0])
            progress = max([progress, 0.0])
            skillText = localization.GetByLabel('UI/CharacterSelection/SkillAndLevel', skill=currentSkill, levelInRoman=romanNumber)
            timeText = localization.formatters.FormatTimeIntervalShortWritten(long(timeLeft), showFrom='day', showTo='minute')
            queueEndTime = trainingInfo.get('queueEndTime', 0)
            if queueEndTime != finishTime:
                queueTimeLeft = max(0, queueEndTime - now)
                queueTimeText = localization.formatters.FormatTimeIntervalShortWritten(long(queueTimeLeft), showFrom='day', showTo='minute')
                timeText = '%s +' % timeText
                hint = '%s<br>%s' % (localization.GetByLabel('UI/SkillQueue/TrainingQueue'), queueTimeText)
            else:
                hint = ''
            self.skillQueueCont.SetProgress(progress=progress)
            self.skillQueueCont.SetText(skillText, timeText, hint)
        self.skillQueueCont.SetSkillQueueActivityState(bool(currentSkill))
        self.SetDeleteUI(animate=False)
        self.slotLoaded = True

    def CountDown_thread(self):
        deletePrepareTime = self.characterDetails.GetDeletePrepareTime()
        if deletePrepareTime is None:
            self.countDownThread = None
            self.deleteButton1.display = False
            return
        now = blue.os.GetWallclockTime()
        timeLeft = deletePrepareTime - now
        timeLeftText = localization.formatters.FormatTimeIntervalShort(long(max(0, timeLeft)), showFrom='hour', showTo='second')
        self.timeLabel.text = timeLeftText
        if timeLeft < 0:
            self.countDownThread = None
            self.deleteButton1.display = True
            self.deleteButton1.ExpandButton()
            uicore.animations.BlinkOut(self.timeLabel, startVal=1.0, endVal=0.0, duration=0.3, loops=3, curveType=uiconst.ANIM_WAVE)

    def LoadAllianceLogo(self, logo, allianceID):
        sm.GetService('photo').GetAllianceLogo(allianceID, 64, logo, orderIfMissing=True)
        logo.hint = cfg.eveowners.Get(allianceID).ownerName
        logo.OnMouseEnter = lambda *args: PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def SetMouseExitState(self, animate = False):
        if self.enteringGameWithSlot or not self.slotLoaded:
            return
        preparingForDelete = self.characterDetails and bool(self.characterDetails.GetDeletePrepareTime())
        if not preparingForDelete:
            self.deleteCont.display = False
        SmallSlot.SetMouseExitState(self, animate=animate)
        self.SetIconsColorInactive(animate=animate)
        self.AdjustNameLabel()

    def SetMouseOverState(self, animate = False):
        if not self.slotLoaded:
            return
        SmallSlot.SetMouseOverState(self, animate=animate)
        if not csUtil.IsMonochromeStyleEnabled():
            self.SetIconsColorActive(animate=animate)
        self.deleteCont.display = True
        self.AdjustNameLabel()

    def AdjustNameLabel(self):
        if self.characterNameLabel.textwidth > self.width - 100:
            slotWidth, h = self.innerNameCont.GetAbsoluteSize()
            fadeEnd = slotWidth - 20 - self.characterNameLabel.left
            self.characterNameLabel.SetRightAlphaFade(fadeEnd, maxFadeWidth=20)

    def SetDisabled(self, animate = False):
        SmallSlot.SetDisabled(self, animate)
        if self.characterDetails.IsPreparingForDeletion():
            SetColor(self.portraitSprite, csColors.BIOMASS_PORTRAIT, animate=animate)
            SetEffectOpacity(self.portraitSprite, newOpacity=csColors.PORTRAIT_INACTIVE_EFFECT_OPACITY, animate=animate)
            SetSaturation(self.portraitSprite, newSaturation=csColors.PORTRAIT_INACTIVE_SATURATION, animate=animate)
        self.shipAndLocationCont.SetDeselected(animate=animate)

    def SetIconsColorActive(self, animate = False):
        SetEffectOpacity(self.allianceLogo, 0, animate=animate)
        SetSaturation(self.allianceLogo, 1.0, animate=animate)
        if isinstance(self.corpLogo, CorpIcon):
            self.SetPlayerCorpLogoColor(self.corpLogo, isActive=True, animate=animate)
        else:
            SetEffectOpacity(self.corpLogo, 0, animate=animate)
        SetColor(self.atWarSprite, csColors.AT_WAR_ACTIVE, animate=animate)

    def SetIconsColorInactive(self, animate = False):
        SetEffectOpacity(self.allianceLogo, csColors.PORTRAIT_INACTIVE_EFFECT_OPACITY, animate=animate)
        SetSaturation(self.allianceLogo, 0.0, animate=animate)
        if isinstance(self.corpLogo, CorpIcon):
            self.SetPlayerCorpLogoColor(self.corpLogo, isActive=False, animate=animate)
        else:
            SetEffectOpacity(self.corpLogo, csColors.PORTRAIT_INACTIVE_EFFECT_OPACITY, animate=animate)
        SetColor(self.atWarSprite, csColors.AT_WAR_INACTIVE, animate=animate)

    def SetPlayerCorpLogoColor(self, logo, isActive = True, animate = False):
        for layerNum, eachSprite in enumerate(logo.children):
            if eachSprite.spriteEffect == trinity.TR2_SFX_MASK:
                if isActive:
                    newColor = eachSprite.originalColor
                else:
                    newColor = self.FindPlayerCorpLogoColor(eachSprite)
            else:
                if isActive:
                    effectOpacity = 1.0
                    saturation = 1.0
                    newColor = eachSprite.originalColor
                    spriteEffect = trinity.TR2_SFX_COPY
                else:
                    effectOpacity = csColors.PORTRAIT_INACTIVE_EFFECT_OPACITY
                    saturation = 0.0
                    newColor = csColors.PORTRAIT_INACTIVE
                    spriteEffect = trinity.TR2_SFX_SOFTLIGHT
                SetEffectOpacity(eachSprite, effectOpacity, animate=animate)
                SetSaturation(eachSprite, saturation, animate=animate)
                eachSprite.spriteEffect = spriteEffect
            SetColor(eachSprite, newColor, animate=animate)

    def FindPlayerCorpLogoColor(self, sprite):
        currentColor = sprite.originalColor
        currentColor = [ min(1.0, value) for value in currentColor ]
        newColor = Color(*currentColor).SetSaturation(0.05).SetAlpha(0.9).GetRGBA()
        return newColor

    def OnDropData(self, dragSource, dragData):
        if self.characterDetails.IsPreparingForDeletion():
            return
        tokens = [ {'tokenID': eachData['item'].tokenID,
         'massTokenID': eachData['item'].massTokenID,
         'typeID': eachData['item'].typeID} for eachData in dragData ]
        useHomeStation = True
        if self.characterDetails and self.characterDetails.GetCurrentStation():
            useHomeStation = False
        if useHomeStation:
            message = localization.GetByLabel('UI/Redeem/ConfirmRedeemToHomeStation', charID=self.characterDetails.charID)
            ret = uicore.Message('AskAreYouSure', {'cons': message}, uiconst.YESNO)
            if ret != uiconst.ID_YES:
                return
        redeemInfo = sm.GetService('redeem').ClaimRedeemTokens(tokens, self.charID, useHomeStation=useHomeStation)
        if redeemInfo and redeemInfo['isk_balance'] is not None:
            balanceText = eveFormat.FmtISK(redeemInfo['isk_balance'], showFractionsAlways=0)
            self.walletContainer.SetTextAndEnableContainer(balanceText)

    def SetActiveInRedeeemMode(self):
        SmallSlot.SetActiveInRedeeemMode(self)
        if self.characterDetails and not self.characterDetails.IsPreparingForDeletion():
            self.SetEnabled(redeemMode=True)
        else:
            self.SetDisabled()

    def RefreshCharacterDetails(self, characterDetails):
        self.characterDetails = characterDetails

    def SetDeleteUI(self, animate = True):
        deletePrepareTime = self.characterDetails.GetDeletePrepareTime()
        if deletePrepareTime:
            self.SetMouseExitState()
            self.deleteCont.display = True
            self.timeCont.display = True
            self.deleteButton2.hint = localization.GetByLabel('UI/CharacterSelection/RemoveFromBiomass')
            now = blue.os.GetWallclockTime()
            timeLeft = deletePrepareTime - now
            timeLeftText = localization.formatters.FormatTimeIntervalShort(long(max(0, timeLeft)), showFrom='hour', showTo='second')
            self.timeLabel.text = timeLeftText
            self.portraitSprite.saturation = csColors.PORTRAIT_INACTIVE_SATURATION
            self.portraitSprite.effectOpacity = csColors.PORTRAIT_INACTIVE_EFFECT_OPACITY
            if animate:
                uicore.animations.MorphScalar(self.deleteButton2.iconCont, 'rotation', startVal=self.deleteButton2.iconCont.rotation, endVal=0, duration=2.0)
                uicore.animations.SpColorMorphTo(self.deleteButton2.icon, self.deleteButton2.icon.GetRGB(), csColors.BIOMASS_RED, csUtil.COLLAPSE_TIME)
                uicore.animations.SpColorMorphTo(self.portraitSprite, self.portraitSprite.GetRGB(), csColors.BIOMASS_PORTRAIT, csUtil.COLLAPSE_TIME)
            else:
                self.deleteButton2.iconCont.rotation = 0
                self.deleteButton2.icon.SetRGBA(*csColors.BIOMASS_RED)
                self.portraitSprite.SetRGBA(*csColors.BIOMASS_PORTRAIT)
            if timeLeft < 0:
                self.deleteButton1.ExpandButton(animate=animate)
                if animate:
                    uicore.animations.SpColorMorphTo(self.deleteButton2.icon, self.deleteButton2.icon.GetRGB(), csColors.BIOMASS_RED, csUtil.COLLAPSE_TIME)
                else:
                    self.deleteButton2.icon.SetRGBA(*csColors.BIOMASS_RED)
            else:
                self.deleteButton1.CollapseButton(animate=animate)
                self.countDownThread = timerstuff.AutoTimer(1000, self.CountDown_thread)
        else:
            self.timeCont.display = False
            self.deleteButton1.CollapseButton(animate=animate)
            self.deleteButton2.hint = localization.GetByLabel('UI/CharacterSelection/Terminate')
            iconRotation = -math.pi / 4.0
            if animate:
                uicore.animations.SpColorMorphTo(self.deleteButton2.icon, self.deleteButton2.icon.GetRGB(), csColors.BIOMASS_WHITE, csUtil.COLLAPSE_TIME)
                uicore.animations.MorphScalar(self.deleteButton2.iconCont, 'rotation', startVal=self.deleteButton1.iconCont.rotation, endVal=iconRotation, duration=2.0)
                self.SetMouseExitState()
            else:
                self.deleteButton2.iconCont.rotation = iconRotation
                self.deleteButton2.icon.SetRGBA(*csColors.BIOMASS_WHITE)
        self.AdjustNameLabel()

    def DeleteButton2Clicked(self):
        deletePrepTime = self.characterDetails.GetDeletePrepareTime()
        if self.deleteCallback and deletePrepTime is None:
            self.deleteCallback(self.charID)
            return
        if deletePrepTime and self.undoDeleteCallback:
            self.undoDeleteCallback(self.charID)

    def DeleteButton1Clicked(self):
        if self.terminateCallback:
            self.terminateCallback(self.charID)

    def LoadAtWarTooltipPanel(self, tooltipPanel, characterDetails, *args):
        wars = characterDetails.GetCharacterWars()
        corpID, allianceID = characterDetails.GetCorporationInfo()
        ownerID = allianceID or corpID
        LoadAtWarTooltipPanel(tooltipPanel, ownerID, wars)


class SmallEmptySlot(SmallSlot):
    default_name = 'smallCharacterSlot'
    isEmptySlot = True
    isDropLocation = False

    def InCohort(self):
        return False

    def ApplyAttributes(self, attributes):
        SmallSlot.ApplyAttributes(self, attributes)
        self.nameSelectionFillActive.opacity = 0
        self.ownSlot = attributes.get('ownSlot', True)
        if self.ownSlot:
            text = localization.GetByLabel('UI/CharacterSelection/AddCharacter')
            texturePath = 'res:/UI/Texture/classes/CharacterSelection/plus2.png'
        else:
            text = localization.GetByLabel('UI/CharacterSelection/AddSlot')
            texturePath = 'res:/UI/Texture/classes/CharacterSelection/padlock.png'
        self.characterNameLabel.text = text
        self.characterNameLabel.SetAlign(uiconst.CENTER)
        self.characterNameLabel.left = -12
        self.plus = Sprite(parent=self.portraitInnerCont, align=uiconst.CENTER, texturePath=texturePath, idx=0, width=64, height=64, state=uiconst.UI_DISABLED, color=csColors.PLUS_INACTIVE)
        self.walletContainer.SetBigText(text)
        self.shipAndLocationCont.SetDisabled()
        self.skillQueueCont.SetSkillqueueForEmpty()
        self.SetMouseExitState()

    def SetMouseExitState(self, animate = False):
        SmallSlot.SetMouseExitState(self, animate=animate)
        SetColor(self.plus, csColors.PLUS_INACTIVE, animate=animate)

    def SetMouseOverState(self, animate = False):
        SmallSlot.SetMouseOverState(self, animate=animate)
        SetColor(self.plus, csColors.PLUS_ACTIVE, animate=animate)


class SkillQueueCont(Container):
    default_align = uiconst.TOTOP
    default_height = 30
    default_padBottom = 8
    default_clipChildren = True
    paddingTimeText = 8
    paddingSkillText = 8

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.glowFrame, self.normalFrame, self.fill = csUtil.AddFrameWithFillAndGlow(parent=self, fillColor=csColors.SKILLQUEUE_BACKGROUND_INACTIVE)
        self.isActive = True
        textCont = Container(name='textCont', parent=self)
        self.timeText = eveLabel.EveLabelMedium(parent=ContainerAutoSize(parent=textCont, align=uiconst.TORIGHT), name='textLabel', align=uiconst.CENTERRIGHT, text='', left=self.paddingTimeText, state=uiconst.UI_NORMAL)
        self.skillText = eveLabel.EveLabelMedium(parent=Container(parent=textCont, padRight=5), name='textLabel', align=uiconst.CENTERLEFT, text='', left=self.paddingSkillText, autoFadeSides=15)
        self.skillFill = Fill(parent=self, align=uiconst.TOLEFT_PROP, width=0.0, color=csColors.SKILLQUEUE_FILL_ACTIVE)
        self.skillEdge = Fill(parent=self, align=uiconst.TOLEFT, width=1, color=csColors.SKILLQUEUE_BRIGHT_EDGE)

    def SetText(self, skillText, timeText, hint):
        self.skillText.SetText('<b>%s</b>' % skillText)
        self.timeText.SetText(timeText)
        self.timeText.hint = hint
        width, h = self.GetAbsoluteSize()
        availableWidth = width - self.timeText.textwidth - self.paddingSkillText - self.paddingTimeText
        if self.skillText.textwidth > availableWidth:
            fadeEnd = availableWidth - 10
            self.skillText.SetRightAlphaFade(fadeEnd, maxFadeWidth=10)

    def SetSkillQueueActivityState(self, isActive = True):
        self.isActive = isActive
        if isActive:
            self.skillText.display = True
            self.timeText.display = True
            self.skillText.SetRGBA(*csColors.SKILLQUEUE_TEXT_TRAINING_INACTIVE)
            self.timeText.SetRGBA(*csColors.SKILLQUEUE_TEXT2_TRAINING_INACTIVE)
            self.fill.SetRGBA(*csColors.SKILLQUEUE_BACKGROUND_ACTIVE)
            self.normalFrame.SetRGBA(*csColors.SKILLQUEUE_FRAME_TRAINING_ACTIVE)
            self.skillFill.display = True
            self.skillEdge.display = True
        else:
            self.skillText.SetText(localization.GetByLabel('UI/CharacterSelection/NoSkillTraining'))
            self.skillText.SetRGBA(*csColors.SKILLQUEUE_TEXT_NOT_TRAINING_INACTIVE)
            self.timeText.SetRGBA(*csColors.SKILLQUEUE_TEXT_NOT_TRAINING_INACTIVE)
            self.timeText.display = False
            self.fill.SetRGBA(*csColors.SKILLQUEUE_BACKGROUND_INACTIVE)
            self.normalFrame.SetRGBA(*csColors.SKILLQUEUE_FRAME_NOT_TRAINING_ACTIVE)
            self.skillFill.display = False
            self.skillEdge.display = False

    def SetSkillqueueForEmpty(self):
        self.fill.SetRGBA(*csColors.SKILLQUEUE_FILL_INACTIVE)
        self.skillFill.display = False
        self.skillEdge.display = False
        self.normalFrame.SetRGBA(*csColors.SKILLQUEUE_FRAME_NOT_TRAINING_INACTIVE)

    def SetProgress(self, progress = 0.0):
        self.skillFill.width = progress

    def SetSelected(self, animate = False):
        SetColor(self.glowFrame, csColors.FRAME_GLOW_ACTIVE, animate=animate)
        SetColor(self.fill, csColors.SKILLQUEUE_BACKGROUND_ACTIVE, animate=animate)
        if self.isActive:
            SetColor(self.normalFrame, csColors.SKILLQUEUE_FRAME_TRAINING_ACTIVE, animate=animate)
            SetColor(self.skillFill, csColors.SKILLQUEUE_FILL_ACTIVE, animate=animate)
            SetColor(self.skillText, csColors.SKILLQUEUE_TEXT_TRAINING_ACTIVE, animate=animate)
            SetColor(self.timeText, csColors.SKILLQUEUE_TEXT2_TRAINING_ACTIVE, animate=animate)
        else:
            SetColor(self.normalFrame, csColors.SKILLQUEUE_FRAME_NOT_TRAINING_ACTIVE, animate=animate)
            SetColor(self.skillText, csColors.SKILLQUEUE_TEXT_NOT_TRAINING_ACTIVE, animate=animate)
            SetColor(self.timeText, csColors.SKILLQUEUE_TEXT_NOT_TRAINING_ACTIVE, animate=animate)

    def SetDeselected(self, animate = False):
        SetColor(self.glowFrame, csColors.FRAME_GLOW_INACTIVE, animate=animate)
        SetColor(self.fill, csColors.SKILLQUEUE_BACKGROUND_INACTIVE, animate=animate)
        if self.isActive:
            SetColor(self.normalFrame, csColors.SKILLQUEUE_FRAME_TRAINING_INACTIVE, animate=animate)
            SetColor(self.skillFill, csColors.SKILLQUEUE_FILL_INACTIVE, animate=animate)
            SetColor(self.skillText, csColors.SKILLQUEUE_TEXT_TRAINING_INACTIVE, animate=animate)
            SetColor(self.timeText, csColors.SKILLQUEUE_TEXT2_TRAINING_INACTIVE, animate=animate)
        else:
            SetColor(self.normalFrame, csColors.SKILLQUEUE_FRAME_NOT_TRAINING_INACTIVE, animate=animate)
            SetColor(self.skillText, csColors.SKILLQUEUE_TEXT_NOT_TRAINING_INACTIVE, animate=animate)
            SetColor(self.timeText, csColors.SKILLQUEUE_TEXT_NOT_TRAINING_INACTIVE, animate=animate)


class CharacterDetailsLocation(Container):
    default_align = uiconst.TOBOTTOM
    default_alignMode = uiconst.TOTOP
    paddingShipAlignmentTop = 20
    paddingShipAlignmentBottom = 40
    locationContHeight = 60
    minShipSize = 40
    topOffset = (paddingShipAlignmentTop - paddingShipAlignmentBottom) / 2

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.glowFrame, self.normalFrame, fill = csUtil.AddFrameWithFillAndGlow(parent=self, showFill=False, frameColor=csColors.LOCATION_FRAME_INACTIVE)
        self.characterDetails = None
        self.fullHeight = self.height
        self.isEmptySlot = attributes.get('isEmptySlot', False)
        self.callback = attributes.get('callback')
        self.locationCont = Container(parent=self, name='locationCont', height=self.locationContHeight, align=uiconst.TOBOTTOM)
        self.shipParentCont = Container(parent=self, name='shipParentCont', align=uiconst.TOALL, clipChildren=True)
        self.shipNameLabel = eveLabel.EveLabelSmall(parent=self.shipParentCont, name='shipText', align=uiconst.CENTERBOTTOM, top=4)
        self.shipCont = Container(parent=self.shipParentCont, name='shipCont', align=uiconst.TOALL, clipChildren=True)
        self.locationBg = Fill(bgParent=self.locationCont, color=csColors.LOCATION_FILL_ACTIVE)
        self.shipbg = Fill(bgParent=self.shipParentCont, color=(0, 0, 0, 0.7))
        self.vignette = Sprite(parent=self.shipCont, texturePath='res:/UI/Texture/classes/CharacterSelection/vignette.png', align=uiconst.TOALL, pos=(0,
         self.topOffset,
         0,
         0), padding=10, color=csColors.VIGNETTE_INACTIVE, state=uiconst.UI_DISABLED)
        self.shipGrid = Sprite(parent=self.shipCont, texturePath='res:/UI/Texture/classes/CharacterSelection/bigGrid.png', align=uiconst.CENTER, pos=(0,
         self.topOffset,
         256,
         256), color=csColors.GRID_ACTIVE, state=uiconst.UI_DISABLED)
        self.shipScaleXCont = ShipScale(parent=self.shipCont, name='shipScaleXCont', align=uiconst.CENTER, top=self.topOffset)
        self.shipScaleYCont = ShipScale(parent=self.shipCont, name='shipScaleYCont', align=uiconst.CENTER, isVertical=True, top=self.topOffset)
        self.shipScaleXCont.display = False
        self.shipScaleYCont.display = False
        self.shipIconCont = Container(parent=self.shipCont, name='shipIconCont', align=uiconst.CENTER, idx=0, top=self.topOffset)
        self.shipIcon = Sprite(parent=self.shipIconCont, name='shipIcon', align=uiconst.CENTER, pos=(0, 0, 128, 128), state=uiconst.UI_DISABLED, blendMode=trinity.TR2_SBM_ADD, spriteEffect=trinity.TR2_SFX_SOFTLIGHT, color=csColors.SHIP_ICON_ACTIVE)
        locationText = attributes.get('locationText', '')
        extraText = attributes.get('extraText', '')
        self.locationTextCont = Container(parent=self.locationCont, name='locationTextCont', align=uiconst.TOALL)
        self.textLabel = eveLabel.EveLabelLargeBold(parent=self.locationTextCont, name='textLabel', align=uiconst.CENTER, state=uiconst.UI_NORMAL, text=locationText, top=-10)
        self.textLabel.OnClick = self.OnClick
        self.extraTextLabel = eveLabel.EveLabelMedium(parent=self.locationTextCont, name='textLabel', align=uiconst.CENTER, text=extraText, top=10)

    def OnClick(self, *args):
        if self.callback:
            self.callback()

    def LoadInfo(self, characterDetails):
        self.characterDetails = characterDetails
        self.SetLocationText()
        currentShipTypeID = characterDetails.GetCurrentShip()
        texturePath = None
        try:
            graphicID = evetypes.GetGraphicID(currentShipTypeID)
            if graphicID is not None:
                texturePath = inventorycommon.typeHelpers.GetHoloIconPath(currentShipTypeID)
        except AttributeError as e:
            log.LogException(e)

        self.shipIcon.SetTexturePath(texturePath)
        self.shipNameLabel.text = evetypes.GetName(currentShipTypeID)
        shipBoundingBox = SHIP_BOUNDING_BOXES.get(currentShipTypeID, None)
        if shipBoundingBox is None:
            shipBoundingBox = GetShipBoundingBox(texturePath)
        if shipBoundingBox:
            SHIP_BOUNDING_BOXES[currentShipTypeID] = shipBoundingBox
            shipWidth = shipBoundingBox['maxX'] - shipBoundingBox['minX']
            shipHeight = shipBoundingBox['maxY'] - shipBoundingBox['minY']
        else:
            shipWidth = 128
            shipHeight = 128
        self.shipIconCont.width = shipWidth
        self.shipIconCont.height = shipHeight
        if texturePath:
            self.shipScaleXCont.display = True
            self.shipScaleYCont.display = True
            self.shipScaleXCont.width = shipWidth
            self.shipScaleYCont.height = shipHeight
            self.shipScaleXCont.top = int(shipHeight / 2.0) + 10 + self.topOffset
            self.shipScaleYCont.left = -int(shipWidth / 2.0) - 15

    def SetLocationText(self, fontColor = (1.0, 1.0, 1.0, 1.0), secColorAlpha = 1.0):
        if not self.characterDetails:
            return
        stationID = self.characterDetails.GetCurrentStation()
        locationID, securityStatus = self.characterDetails.GetCurrentLocationInfo()
        securityText, secColor = eveFormat.FmtSystemSecStatus(securityStatus, 1)
        if csUtil.IsMonochromeStyleEnabled():
            secColor = Color.GRAY5
        secColor = int(Color.RGBtoHex(secColor[0], secColor[1], secColor[2], secColorAlpha), 16)
        normalTextColor = int(Color.RGBtoHex(*fontColor), 16)
        fontPath = None
        if locationID is None:
            locationText = ''
        elif IsAbyssalSpaceSystem(locationID):
            locationText = sm.GetService('abyss').get_mangled_system_name(locationID, self.characterDetails.charID)
            locationText = '<color=%s>%s' % (normalTextColor, locationText)
            fontPath = carbonui.fontconst.TRIGLAVIAN
        elif IsVoidSpaceSystem(locationID):
            locationText = localization.GetByLabel('UI/Common/Unknown')
        else:
            locationText = cfg.evelocations.Get(locationID).name
            securityModifierText = self._GetSecurityModifierText(locationID)
            locationText = '<color=%s>%s</color>%s <color=%s>%s' % (secColor,
             securityText,
             securityModifierText,
             normalTextColor,
             locationText)
        if stationID:
            stationInfo = self.characterDetails.GetCurrentStationAndStationLocation()
            stationName = stationInfo.get('stationName', '')
            orbitName = stationInfo.get('shortOrbitName', '')
            if orbitName:
                extraText = '>>> [%s] %s &lt;&lt;&lt;' % (orbitName, stationName)
            else:
                extraText = '>>> %s &lt;&lt;&lt;' % (stationName,)
        else:
            extraText = localization.GetByLabel('UI/CharacterSelection/NotDocked')
        self.textLabel.fontPath = fontPath
        self.textLabel.SetText(locationText)
        slotWidth, h = self.GetAbsoluteSize()
        self.extraTextLabel.SetText(extraText)
        self.extraTextLabel.SetRGBA(*fontColor)
        if self.extraTextLabel.textwidth > slotWidth:
            self.extraTextLabel.SetAlign(uiconst.CENTERLEFT)
            self.extraTextLabel.left = 4
            fadeEnd = slotWidth - 10
            self.extraTextLabel.SetRightAlphaFade(fadeEnd, maxFadeWidth=20)
        else:
            self.extraTextLabel.left = 0
            self.extraTextLabel.SetAlign(uiconst.CENTER)
            self.extraTextLabel.SetRightAlphaFade(0, maxFadeWidth=0)

    @Memoize(1)
    def _GetSecurityModifierText(self, locationID):
        mapSvc = sm.RemoteSvc('map')
        modifiedSecuritySystems = mapSvc.GetSecurityModifiedSystems()
        indexedSystems = modifiedSecuritySystems.Index('solarSystemID')
        if locationID in indexedSystems:
            system = indexedSystems[locationID]
            return get_font_icon_text(system.security, system.modifiedSecurity)
        return ''

    def GetHeight(self, shipVisible = True):
        if not shipVisible:
            return self.locationContHeight + max(self.shipNameLabel.textheight + 2 * self.shipNameLabel.top, 20)
        padding = self.paddingShipAlignmentTop + self.paddingShipAlignmentBottom
        return max(self.shipIconCont.height, self.minShipSize) + self.locationCont.height + padding

    def SetShipContHeight(self, height):
        self.height = height
        self.fullHeight = height

    def SetDisabled(self):
        self.vignette.padLeft = -30
        self.vignette.padRight = -30
        self.vignette.padTop = -30
        self.vignette.padBottom = -30
        self.normalFrame.SetRGBA(*csColors.LOCATION_FRAME_INACTIVE)
        self.locationBg.SetRGBA(*csColors.LOCATION_FILL_INACTIVE)
        self.vignette.SetRGBA(*csColors.VIGNETTE_DISABLED)

    def SetActiveState(self, isActive = True, animate = False):
        if isActive:
            uthread.new(self.SetLocationText, fontColor=csColors.LOCATION_TEXT_ACTIVE)
            SetColor(self.glowFrame, csColors.FRAME_GLOW_ACTIVE, animate=animate)
        else:
            uthread.new(self.SetLocationText, fontColor=csColors.LOCATION_TEXT_INACTIVE, secColorAlpha=0.6)
            SetColor(self.glowFrame, csColors.FRAME_GLOW_INACTIVE, animate=animate)

    def SetSelected(self, animate = False):
        SetColor(self.shipGrid, csColors.GRID_ACTIVE, animate=animate)
        SetColor(self.shipIcon, csColors.SHIP_ICON_ACTIVE, animate=animate)
        SetColor(self.normalFrame, csColors.LOCATION_FRAME_ACTIVE, animate=animate)
        SetColor(self.locationBg, csColors.LOCATION_FILL_ACTIVE, animate=animate)
        SetColor(self.shipNameLabel, csColors.SHIP_NAME_ACTIVE, animate=animate)
        self.SetActiveVignetteColor(animate=animate)

    def SetDeselected(self, animate = False):
        SetColor(self.shipGrid, csColors.GRID_INACTIVE, animate=animate)
        SetColor(self.shipIcon, csColors.SHIP_ICON_INACTIVE, animate=animate)
        SetColor(self.normalFrame, csColors.LOCATION_FRAME_INACTIVE, animate=animate)
        SetColor(self.locationBg, csColors.LOCATION_FILL_INACTIVE, animate=animate)
        SetColor(self.shipNameLabel, csColors.SHIP_NAME_INACTIVE, animate=animate)
        self.SetInactiveVignetteColor(animate=animate)

    def SetActiveVignetteColor(self, animate = False):
        if self.isEmptySlot:
            SetColor(self.vignette, csColors.VIGNETTE_DISABLED, animate=animate)
        else:
            SetColor(self.vignette, csColors.VIGNETTE_ACTIVE, animate=animate)

    def SetInactiveVignetteColor(self, animate = False):
        if self.isEmptySlot:
            SetColor(self.vignette, csColors.VIGNETTE_DISABLED, animate=animate)
        else:
            SetColor(self.vignette, csColors.VIGNETTE_INACTIVE, animate=animate)

    def CollapseShipSection(self, animate = True):
        newHeight = self.locationContHeight + max(self.shipNameLabel.textheight + 2 * self.shipNameLabel.top, 20)
        if animate:
            uicore.animations.MorphScalar(self.shipCont, 'opacity', startVal=self.shipCont.opacity, endVal=0, duration=0.2)
            uicore.animations.MorphScalar(self, 'height', startVal=self.height, endVal=newHeight, duration=csUtil.COLLAPSE_TIME)
        else:
            uicore.animations.StopAnimation(self.shipCont, 'opacity')
            self.shipCont.opacity = 0
            uicore.animations.StopAnimation(self, 'height')
            self.height = newHeight

    def ExpandShipSection(self, animate = True):
        if animate:
            uicore.animations.MorphScalar(self.shipCont, 'opacity', startVal=self.shipCont.opacity, endVal=1.0, duration=0.6)
            uicore.animations.MorphScalar(self, 'height', startVal=self.height, endVal=self.fullHeight, duration=csUtil.COLLAPSE_TIME)
        else:
            uicore.animations.StopAnimation(self.shipCont, 'opacity')
            self.shipCont.opacity = 1.0
            uicore.animations.StopAnimation(self, 'height')
            self.height = self.fullHeight

    def Close(self):
        self._GetSecurityModifierText.clear_memoized()
        super(CharacterDetailsLocation, self).Close()


class CharacterDetailsLine(Container):
    default_height = 20
    default_align = uiconst.TOTOP
    paddingText = 6
    paddingIcon = 4

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        iconPath = attributes.iconPath
        self.addLine = attributes.get('addLine', True)
        self.icon = Sprite(parent=self, name='icon', align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, texturePath=iconPath, pos=(self.paddingIcon,
         0,
         24,
         24), spriteEffect=trinity.TR2_SFX_SOFTLIGHT, color=csColors.LINES_ICON_INACTIVE)
        iconPath2 = attributes.iconPath2
        left = self.icon.left + self.icon.width + 2
        self.icon2 = Sprite(parent=self, name='icon2', align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, texturePath=iconPath2, pos=(left,
         0,
         24,
         24), spriteEffect=trinity.TR2_SFX_SOFTLIGHT, color=csColors.LINES_ICON_INACTIVE)
        self.icon.display = False
        self.icon2.display = False
        text = attributes.get('text', '')
        self.textLabel = eveLabel.EveLabelMedium(parent=self, name='textLabel', align=uiconst.CENTERRIGHT, text=text, left=self.paddingText)
        if self.addLine:
            self.AddLine()
        self.height = max(self.height, self.textLabel.textheight + 4)
        if text:
            self.SetTextAndEnableContainer(text)

    def SetTextAndEnableContainer(self, text):
        self.textLabel.SetText(text)
        self.EnableContainer()

    def EnableContainer(self):
        self.icon.display = True
        self.icon2.display = True

    def SetSecondIcon(self, texturePath, hint = ''):
        self.icon2.SetTexturePath(texturePath)
        self.icon2.display = True
        self.icon2.state = uiconst.UI_NORMAL if texturePath else uiconst.UI_DISABLED
        self.icon2.hint = hint

    def SetActiveState(self, isActive = True, animate = False):
        if isActive:
            SetColor(self.textLabel, csColors.LINES_TEXT_ACTIVE, animate=animate)
            SetColor(self.icon, csColors.LINES_ICON_ACTIVE, animate=animate)
            SetColor(self.icon2, csColors.LINES_ICON_ACTIVE, animate=animate)
            if self.addLine:
                self.endDots.opacity = csColors.FRAME_GLOW_ACTIVE[3]
                SetColor(self.bottomLine, csColors.LINES_ACTIVE, animate=animate)
        else:
            SetColor(self.textLabel, csColors.LINES_TEXT_INACTIVE, animate=animate)
            SetColor(self.icon, csColors.LINES_ICON_INACTIVE, animate=animate)
            SetColor(self.icon2, csColors.LINES_ICON_INACTIVE, animate=animate)
            if self.addLine:
                self.endDots.opacity = csColors.FRAME_GLOW_INACTIVE[3]
                SetColor(self.bottomLine, csColors.LINES_INACTIVE, animate=animate)

    def SetBigText(self, text):
        bigTextLabel = getattr(self, 'bigTextLabel', None)
        if bigTextLabel is None or bigTextLabel.destroyed:
            self.bigTextLabel = eveLabel.CaptionLabel(parent=self, name='bigTextLabel', align=uiconst.CENTER, text='', fontsize=14, uppercase=False, letterspace=0, bold=False)
            self.bigTextLabel.SetTextColor(csColors.ADDCHARACTER_TEXT_ACTIVE)
        self.bigTextLabel.SetText(text)

    def AddLine(self):
        padBottom = 0
        weight = 1
        self.bottomLine = Line(parent=self, align=uiconst.TOBOTTOM, weight=weight, color=csColors.LINES_ACTIVE, padBottom=padBottom)
        self.endDots = ThreePartContainer(parent=self, name='endDots', align=uiconst.TOBOTTOM_NOPUSH, state=uiconst.UI_DISABLED, pos=(0,
         0,
         0,
         weight), idx=0, leftTexturePath='res:/UI/Texture/classes/CharacterSelection/glowLineEndLeft.png', rightTexturePath='res:/UI/Texture/classes/CharacterSelection/glowLineEndRight.png', sideSize=8, color=csColors.FRAME_GLOW_ACTIVE)


class DeleteButton(Container):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TORIGHT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.width = 14
        self.fullWidth = self.width
        texturePath = attributes.get('texturePath', None)
        self.callback = attributes.get('callback')
        color = attributes.get('color', (1, 0, 0, 1))
        rotation = attributes.get('rotation', 0)
        self.onMouseEnterCallback = attributes.get('onMouseEnterCallback')
        self.onMouseExitCallback = attributes.get('onMouseExitCallback')
        self.iconCont = Transform(parent=self, align=uiconst.CENTER, pos=(0, 0, 10, 10), state=uiconst.UI_DISABLED, rotation=rotation)
        self.icon = Sprite(parent=self.iconCont, texturePath=texturePath, align=uiconst.TOPLEFT, pos=(0, 0, 10, 10), state=uiconst.UI_DISABLED, color=color)

    def OnClick(self, *args):
        if self.callback:
            self.callback()
        self.icon.top = 0

    def OnMouseDown(self, *args):
        self.icon.top = 2

    def OnMouseUp(self, *args):
        self.icon.top = 0

    def OnMouseEnter(self, *args):
        self.icon.SetAlpha(1.5)

    def OnMouseExit(self, *args):
        self.icon.SetAlpha(1.0)

    def ExpandButton(self, animate = True):
        if animate:
            uicore.animations.MorphScalar(self, 'width', startVal=self.width, endVal=self.fullWidth, duration=csUtil.COLLAPSE_TIME)
        else:
            self.width = self.fullWidth

    def CollapseButton(self, animate = True):
        if animate:
            uicore.animations.MorphScalar(self, 'width', startVal=self.width, endVal=0, duration=csUtil.COLLAPSE_TIME)
        else:
            self.width = 0


class ShipScale(Container):
    default_state = uiconst.UI_DISABLED
    default_clipChildren = True
    default_length = 256
    default_weight = 5
    default_scaleWeight = 3

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        isVertical = attributes.get('isVertical', False)
        length = attributes.get('length', self.default_length)
        weight = attributes.get('weight', self.default_weight)
        self.scaleWeigth = attributes.get('scaleWeight', self.default_scaleWeight)
        scaleColor = attributes.get('scaleColor', csColors.GRID_SCALE)
        endColor = attributes.get('endColor', scaleColor)
        if isVertical:
            self.height = length
            self.width = weight
            texturePath = 'res:/UI/Texture/classes/CharacterSelection/scaleY.png'
            startScaleAlign = uiconst.TOBOTTOM_NOPUSH
            endScaleAlign = uiconst.TOTOP_NOPUSH
            spriteHeight = self.height
            spriteWidth = self.scaleWeigth
        else:
            self.height = weight
            self.width = length
            texturePath = 'res:/UI/Texture/classes/CharacterSelection/scaleX.png'
            startScaleAlign = uiconst.TOLEFT_NOPUSH
            endScaleAlign = uiconst.TORIGHT_NOPUSH
            spriteHeight = self.scaleWeigth
            spriteWidth = self.width
        Line(parent=self, align=startScaleAlign, color=endColor)
        Line(parent=self, align=endScaleAlign, color=endColor)
        self.scaleSprite = Sprite(parent=self, texturePath=texturePath, align=uiconst.CENTER, pos=(0,
         0,
         spriteWidth,
         spriteHeight), color=scaleColor, state=uiconst.UI_DISABLED)


def GetShipBoundingBox(texturePath, ignoredColors = None):
    if texturePath is None:
        return
    if ignoredColors is None:
        ignoredColors = [(0, 0, 0, 1)]
    image = blue.resMan.GetResource(texturePath, 'raw')
    blue.resMan.Wait()
    maxX = None
    minX = None
    maxY = None
    minY = None
    if not image.height:
        return
    for x in xrange(image.width):
        for y in xrange(image.height):
            color = image.GetPixelColor(x, y)
            if color in ignoredColors:
                continue
            if minX is None:
                minX = x
            if maxX is None or maxX < x:
                maxX = x
            if minY is None or minY > y:
                minY = y
            if maxY is None or maxY < y:
                maxY = y

    return {'maxX': maxX or image.width,
     'minX': minX or 0,
     'maxY': maxY or image.height,
     'minY': minY or 0}
