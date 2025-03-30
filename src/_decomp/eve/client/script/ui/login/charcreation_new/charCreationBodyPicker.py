#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\charCreationBodyPicker.py
import carbonui.const as uiconst
import localization
from carbon.common.script.util import timerstuff
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.login.charcreation_new.hexes import CCHexButtonHead, CCHexButtonBody
from eve.client.script.ui.login.charcreation_new.charCreation import GHOST_TEXTURE_PATH
from eve.client.script.ui.login.charcreation_new.sceneManager import GetCharacterCreationSceneManager

class CCHeadBodyPicker(Container):
    __guid__ = 'uicls.CCHeadBodyPicker'
    default_name = 'CCHeadBodyPicker'
    default_opacity = 0
    default_width = 130
    default_height = 130

    def ApplyAttributes(self, attributes):
        super(CCHeadBodyPicker, self).ApplyAttributes(attributes)
        self.headCallback = attributes.headCallback
        self.bodyCallback = attributes.bodyCallback
        self.ConstructLayout()
        self.updateTimer = timerstuff.AutoTimer(33, self.UpdatePosition)
        animations.FadeIn(self, duration=0.25)

    def ConstructLayout(self, *args):
        self.headHex = CCHexButtonHead(name='headHex', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, 0, 64, 64), pickRadius=21, info=None, id=0, hexName=localization.GetByLabel('UI/CharacterCreation/ZoomIn'), func=self.HeadClicked, iconNum=0, showIcon=False)
        self.headSolid = self.headHex.selection
        self.headSolid.SetState(uiconst.UI_DISABLED)
        self.headFrame = self.headHex.frame
        self.bodyHex = CCHexButtonBody(name='bodyHex', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, 16, 128, 128), pickRadius=42, info=None, id=0, hexName=localization.GetByLabel('UI/CharacterCreation/ZoomOut'), func=self.BodyClicked, iconNum=0, showIcon=False)
        self.bodySolid = self.bodyHex.selection
        self.bodySolid.SetState(uiconst.UI_DISABLED)
        self.bodyFrame = self.bodyHex.frame
        sprite = Sprite(name='ghostSprite', parent=self, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, pos=(0, 7, 128, 128), idx=0, texturePath=GHOST_TEXTURE_PATH)
        sprite.SetRect(0, 0, 0, 0)

    def UpdatePosition(self, *args):
        if self.destroyed:
            return
        camera = GetCharacterCreationSceneManager().camera
        if camera is not None:
            portion = camera.GetPortionFromDistance()
            self.headSolid.SetOpacity(max(0.2, 1.0 - portion))
            self.bodySolid.SetOpacity(max(0.2, portion))
            for hex in (self.headHex, self.bodyHex):
                if hex.selection.opacity >= 0.5 and len(self.children) and hex == self.children[-1]:
                    toSwap = self.children[-2]
                    self.children.remove(toSwap)
                    self.children.append(toSwap)
                    break

    def MouseOverPart(self, frameName, *args):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_over_play'))
        frame = self.get(frameName, None)
        if frame:
            frame.state = uiconst.UI_DISABLED

    def MouseExitPart(self, frameName, *args):
        frame = self.get(frameName, None)
        if frame:
            frame.state = uiconst.UI_HIDDEN

    def HeadClicked(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_down_play'))
        self.headFrame.state = uiconst.UI_HIDDEN
        self.bodyFrame.state = uiconst.UI_HIDDEN
        if self.headCallback:
            self.headCallback()

    def BodyClicked(self, *args):
        sm.StartService('audio').SendUIEvent(unicode('ui_icc_button_mouse_down_play'))
        self.headFrame.state = uiconst.UI_HIDDEN
        self.bodyFrame.state = uiconst.UI_HIDDEN
        if self.bodyCallback:
            self.bodyCallback()
