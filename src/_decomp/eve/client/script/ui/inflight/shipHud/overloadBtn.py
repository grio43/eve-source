#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\overloadBtn.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore

class OverloadBtn(Container):
    default_height = 20
    default_width = 20
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_pickRadius = 8
    iconTexturePath = 'res:/UI/Texture/classes/ShipUI/overloadBtn%sOff.png'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        fitKey = attributes.fitKey
        self.active = False
        self.powerEffectID = attributes.powerEffectID
        self.activationID = attributes.activationID
        self.orgPos = self.top
        Sprite(name='icon', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), state=uiconst.UI_DISABLED, texturePath=self.iconTexturePath % fitKey)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        if settings.user.ui.Get('lockOverload', 0):
            existingModal = uicore.registry.GetModalWindow()
            if existingModal and existingModal.msgKey == 'LockedOverloadState':
                return
            eve.Message('error')
            eve.Message('LockedOverloadState')
            return
        if self.active:
            eve.Message('click')
            sm.GetService('godma').StopOverloadRack(self.activationID)
        else:
            eve.Message('click')
            sm.GetService('godma').OverloadRack(self.activationID)

    def OnMouseDown(self, *args):
        self.top = self.orgPos + 1

    def OnMouseUp(self, *args):
        self.top = self.orgPos

    def OnMouseExit(self, *args):
        self.top = self.orgPos

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
