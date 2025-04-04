#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shipTree\shipTreeShipIcon.py
from carbon.client.script.environment.AudioUtil import PlaySound
import log
import carbonui.const as uiconst
import evetypes
import inventorycommon.typeHelpers
import shipTreeConst
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.const import ANIM_REPEAT, ANIM_WAVE
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.shared.shipTree import shipTreeUtil
from eve.client.script.ui.shared.shipTree.shipTreeConst import COLOR_BG, COLOR_HOVER_UNLOCKED, COLOR_HOVER_LOCKED, COLOR_HOVER_MASTERED
from eveservices.menu import GetMenuService
from utillib import KeyVal
import uthread2
OPACITY_LOCKED = 0.4
OPACITY_MASTERY_LOCKED = 0.2

class ShipTreeShipIcon(Container):
    default_name = 'ShipTreeShipIcon'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    isDragObject = True
    __notifyevents__ = 'OnShipTreeShipFocused'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.typeID = attributes.typeID
        self.factionID = attributes.factionID
        self.groupNode = attributes.groupNode
        self.expertSystemTypeIDs = attributes.expertSystemTypeIDs
        self.activeRelatedExpertSystem = attributes.get('activeRelatedExpertSystem', False)
        self.masteryLevel = None
        self.isMasteryIconBlinking = False
        self.bgFrame = Frame(bgParent=self, cornerSize=10, opacity=0.5, texturePath='res:/UI/Texture/Classes/ShipTree/groups/frameUnlocked.png')
        self.expertSystemBgBlinkFill = None
        self.bgBlinkFill = None
        self.bgThumpFill = None
        self.bgVignette = Sprite(name='bgFill', bgParent=self, texturePath='res:/UI/Texture/Classes/ShipTree/groups/bgFill.png')
        Sprite(name='bgVignette', bgParent=self, texturePath='res:/UI/Texture/Classes/ShipTree/groups/bgVignette.png', color=COLOR_BG)
        self.recentUnlockBG = None
        texturePath = shipTreeUtil.GetTagIconForType(self.typeID)
        if texturePath:
            self.techIcon = Sprite(name='techIcon', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=32, height=32, texturePath=texturePath, idx=0)
        else:
            self.techIcon = None
        self.iconTransform = Transform(parent=self, align=uiconst.TOALL, scalingCenter=(0.5, 0.5))
        try:
            texturePath = inventorycommon.typeHelpers.GetHoloIconPath(self.typeID)
        except AttributeError as e:
            texturePath = None
            log.LogException(e)

        self.iconSprite = Sprite(name='iconSprite', parent=self.iconTransform, align=uiconst.TOPLEFT_PROP, state=uiconst.UI_DISABLED, texturePath=texturePath, blendMode=trinity.TR2_SBM_ADD, ignoreColorBlindMode=True, pos=(0.5,
         0.08,
         self.width - 36,
         self.width - 36), idx=0)
        self.masteryIcon = Sprite(name='masterySprite', parent=self, align=uiconst.CENTERBOTTOM, state=uiconst.UI_DISABLED, pos=(0, -3, 45, 45), idx=0)
        if self.activeRelatedExpertSystem:
            self.expertSystemBgFrame = Frame(bgParent=self, cornerSize=10, opacity=1.0, texturePath='res:/UI/Texture/Classes/ExpertSystems/ExpertSystem_ShipTree_BG.png')
            self.expertSystemsAnimSprite = Sprite(bgParent=self, texturePath='res:/UI/Texture/Classes/ExpertSystems/ExpertSystem_ShipTree_BG_Overlay.png')
            uicore.animations.SpSwoopBlink(self.expertSystemsAnimSprite, duration=3, loops=uiconst.ANIM_REPEAT)
            self.masteryIcon.state = uiconst.UI_HIDDEN
            Sprite(parent=self, name='expertSystemIcon', texturePath='res:/UI/Texture/classes/ExpertSystems/logo_simple_20.png', width=20, height=20, align=uiconst.CENTERBOTTOM, top=10, state=uiconst.UI_DISABLED)
        elif self.expertSystemTypeIDs:
            self.masteryIcon.state = uiconst.UI_HIDDEN
            Sprite(parent=self, name='expertSystemIcon', texturePath='res:/UI/Texture/classes/ExpertSystems/logo_inactive_20.png', width=20, height=20, align=uiconst.CENTERBOTTOM, top=10, state=uiconst.UI_DISABLED)

    def UpdateState(self, animate = True):
        self.masteryLevel = sm.GetService('certificates').GetCurrCharMasteryLevel(self.typeID)
        duration = 0.6 if animate else 0.01
        if self.groupNode.IsLocked():
            self._UpdateStateLocked(duration)
        else:
            self._UpdateStateUnlocked(duration)
            if self.groupNode.IsRecentlyUnlocked():
                if not self.recentUnlockBG:
                    self.ConstructRecentUnlockBG()
                    i = self.parent.children.index(self)
                    uicore.animations.FadeTo(self.recentUnlockBG, 0.7, 0.0, duration=2.4, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE, timeOffset=i * 0.15)
                    sm.GetService('audio').SendUIEvent('isis_line_2filled')
            elif self.recentUnlockBG:
                uicore.animations.FadeOut(self.recentUnlockBG)
            if sm.GetService('shipTree').IsShipMasteryRecentlyIncreased(self.typeID):
                if not self.isMasteryIconBlinking:
                    uicore.animations.FadeTo(self.masteryIcon, OPACITY_MASTERY_LOCKED, 1.5, duration=2.4, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
                    if self.IsElite():
                        sm.GetService('audio').SendUIEvent('isis_masteryunlock_elite')
                    else:
                        sm.GetService('audio').SendUIEvent('isis_masteryunlock')
                self.isMasteryIconBlinking = True
            else:
                uicore.animations.FadeTo(self.masteryIcon, 1.0)
        texturePath = sm.GetService('certificates').GetMasteryIconForLevel(self.masteryLevel)
        self.masteryIcon.texturePath = texturePath

    def ConstructRecentUnlockBG(self):
        if not self.recentUnlockBG:
            if self.IsElite():
                color = COLOR_HOVER_MASTERED
            else:
                color = COLOR_HOVER_UNLOCKED
            self.recentUnlockBG = Sprite(name='recentUnlockBG', bgParent=self, texturePath='res:/UI/Texture/Classes/ShipTree/groups/bgVignette.png', color=color)

    def IsElite(self):
        return self.masteryLevel == 5

    def GetDragData(self):
        ret = KeyVal(__guid__='uicls.GenericDraggableForTypeID', typeID=self.typeID, label=evetypes.GetName(self.typeID))
        return (ret,)

    def _UpdateStateLocked(self, duration):
        self.bgVignette.SetRGBA(*shipTreeConst.COLOR_SHIPICON_LOCKED)
        for obj in (self.techIcon, self.iconSprite):
            if obj:
                uicore.animations.FadeTo(obj, obj.opacity, OPACITY_LOCKED, duration=duration)

        uicore.animations.FadeTo(self.masteryIcon, self.masteryIcon.opacity, OPACITY_MASTERY_LOCKED, duration=duration)
        uicore.animations.FadeTo(self.bgFrame, self.bgFrame.opacity, 0.25, duration=duration)
        self.iconSprite.SetRGBA(1.0, 1.0, 1.0, self.iconSprite.opacity)
        self.bgFrame.SetTexturePath('res:/UI/Texture/Classes/ShipTree/groups/frameLocked.png')

    def _UpdateStateUnlocked(self, duration):
        for obj in (self.techIcon, self.iconSprite):
            if obj:
                uicore.animations.FadeTo(obj, obj.opacity, 1.0, duration=duration)

        if not self.isMasteryIconBlinking:
            uicore.animations.FadeTo(self.masteryIcon, self.masteryIcon.opacity, 1.0, duration=duration)
        uicore.animations.FadeTo(self.bgFrame, self.bgFrame.opacity, 0.5, duration=duration)
        if self.IsElite():
            texturePath = 'res:/UI/Texture/Classes/ShipTree/groups/frameElite.png'
            c = shipTreeConst.COLOR_MASTERED
            self.bgVignette.SetRGBA(c[0], c[1], c[2], 0.15)
            self.iconSprite.SetRGBA(c[0], c[1], c[2], self.iconSprite.opacity)
        else:
            texturePath = 'res:/UI/Texture/Classes/ShipTree/groups/frameUnlocked.png'
            self.bgVignette.SetRGBA(*shipTreeConst.COLOR_SHIPICON_UNLOCKED)
            self.iconSprite.SetRGBA(1.0, 1.0, 1.0, self.iconSprite.opacity)
        self.bgFrame.SetTexturePath(texturePath)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if not self.groupNode.IsLocked():
            uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, 3.0, duration=3.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
            uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.05, 1.05), duration=0.3)
        else:
            uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, 1.0, duration=0.3)
            uicore.animations.FadeTo(self.masteryIcon, self.masteryIcon.opacity, 1.0, duration=0.3)
        sm.GetService('shipTreeUI').ShowInfoBubble(self, factionID=self.factionID, typeID=self.typeID, expertSystems=self.expertSystemTypeIDs)
        sm.GetService('audio').SendUIEventByTypeID(self.typeID)
        self.ConstructBgBlinkFill()
        uicore.animations.FadeTo(self.bgBlinkFill, self.bgBlinkFill.opacity, 0.5, duration=0.3)

    def OnMouseExit(self, *args):
        opacity = OPACITY_LOCKED if self.groupNode.IsLocked() else 1.0
        uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, opacity, duration=0.3)
        opacity = OPACITY_MASTERY_LOCKED if self.groupNode.IsLocked() else 1.0
        uicore.animations.FadeTo(self.masteryIcon, self.masteryIcon.opacity, opacity, duration=0.3)
        if self.bgBlinkFill:
            uicore.animations.FadeOut(self.bgBlinkFill, duration=0.3)
        uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.0, 1.0), duration=0.3)
        sm.GetService('audio').SendUIEvent('ui_shipsound_stop')

    def Close(self):
        Container.Close(self)
        sm.GetService('shipTreeUI').CloseInfoBubble()
        sm.GetService('audio').SendUIEvent('ui_shipsound_stop')

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        sm.GetService('info').ShowInfo(self.typeID)

    def OnShipTreeShipFocused(self, typeID):
        if typeID == self.typeID:
            self.Blink()
        elif self.bgBlinkFill:
            uicore.animations.FadeOut(self.bgBlinkFill)

    def Blink(self):
        self.ConstructBgBlinkFill()
        uicore.animations.FadeTo(self.bgBlinkFill, 0.0, 1.0, loops=ANIM_REPEAT, duration=1.2, curveType=ANIM_WAVE)

    def Thump(self, duration = 0.3, delay = 0):
        if not self.bgThumpFill:
            self.bgThumpFill = Sprite(name='bgFillBlink', bgParent=self, texturePath='res:/UI/Texture/Classes/ShipTree/groups/bgWhite.png')
        self.bgThumpFill.SetRGBA(1, 1, 1, 0)
        uicore.animations.FadeTo(self.bgThumpFill, 0.0, 3, duration=duration, curveType=ANIM_WAVE, timeOffset=delay)
        uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, 3, duration=duration, curveType=uiconst.ANIM_WAVE, timeOffset=delay)
        uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.15, 1.15), duration=duration, curveType=uiconst.ANIM_WAVE, timeOffset=delay)
        uthread2.start_tasklet(self._DelayedThumpSound, delay=delay)

    def _DelayedThumpSound(self, delay):
        uthread2.sleep(delay)
        PlaySound('ship_goals_reveal_ship_play')

    def StartExpertSystemBlink(self):
        self.ConstructExpertSystemBgBlinkFill()
        uicore.animations.FadeTo(self.expertSystemBgBlinkFill, 0.0, 1.0, loops=ANIM_REPEAT, duration=1.2, curveType=ANIM_WAVE)

    def StopExpertSystemBlink(self):
        self.ConstructExpertSystemBgBlinkFill()
        uicore.animations.FadeOut(self.expertSystemBgBlinkFill, duration=1.2)

    def ConstructExpertSystemBgBlinkFill(self):
        if not self.expertSystemBgBlinkFill:
            self.expertSystemBgBlinkFill = Sprite(name='bgFillBlink', bgParent=self, texturePath='res:/UI/Texture/Classes/ShipTree/groups/bgVignette.png', color=Color.GREEN, opacity=0.0)

    def ConstructBgBlinkFill(self):
        if not self.bgBlinkFill:
            self.bgBlinkFill = Sprite(name='bgFillBlink', bgParent=self, texturePath='res:/UI/Texture/Classes/ShipTree/groups/bgVignette.png')
        if self.groupNode.IsLocked():
            self.bgBlinkFill.SetRGBA(*COLOR_HOVER_LOCKED)
        elif self.IsElite():
            self.bgBlinkFill.SetRGBA(*COLOR_HOVER_MASTERED)
        else:
            self.bgBlinkFill.SetRGBA(*COLOR_HOVER_UNLOCKED)
