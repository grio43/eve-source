#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\selectedPlan\lockButton.py
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelSmall
OPACITY_IDLE = 0.6
OPACITY_HOVER = 0.9
LOCK_BUTTON_SIZE = 48

class SkillPlanLockButton(Container):
    default_width = LOCK_BUTTON_SIZE
    default_height = LOCK_BUTTON_SIZE
    default_state = uiconst.UI_NORMAL
    backgroundColorLocked = None
    backgroundColor = None
    frameColor = None
    frameColorLocked = None
    iconTexturePath = None
    iconSize = None

    def ApplyAttributes(self, attributes):
        super(SkillPlanLockButton, self).ApplyAttributes(attributes)
        self.callback = attributes.get('func', None)
        self.iconSprite = Sprite(parent=self, name='icon', align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.iconTexturePath, width=self.iconSize, height=self.iconSize)
        self.bgFill = Sprite(bgParent=self, name='bgFill', texturePath='res:/UI/Texture/classes/SkillPlan/lockButtonBG.png')
        self.bgFrame = Sprite(name='bgFrame', bgParent=self, texturePath='res:/UI/Texture/classes/SkillPlan/lockButtonFrame.png')
        self.checkmark = Sprite(parent=self, name='checkmark', align=uiconst.CENTERBOTTOM, texturePath='res:/UI/Texture/classes/SkillPlan/lockButtonCheckmark.png', width=20, height=20, top=-10)

    def OnClick(self, *args):
        if self.callback:
            self.callback()

    def Lock(self):
        self.bgFill.SetRGBA(*self.backgroundColorLocked)
        self.bgFrame.SetRGBA(*self.frameColorLocked)
        self.checkmark.Hide()

    def Unlock(self):
        self.bgFill.SetRGBA(*self.backgroundColor)
        self.bgFrame.SetRGBA(*self.frameColor)
        self.checkmark.Show()

    def OnMouseEnter(self, *args):
        super(SkillPlanLockButton, self).OnMouseEnter(*args)
        animations.FadeTo(self.bgFill, self.bgFill.opacity, OPACITY_HOVER, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        super(SkillPlanLockButton, self).OnMouseExit(*args)
        animations.FadeTo(self.bgFill, self.bgFill.opacity, OPACITY_IDLE, duration=uiconst.TIME_EXIT)


class OmegaLockButton(SkillPlanLockButton):
    frameColor = eveColor.WHITE
    frameColorLocked = eveColor.SAND_YELLOW
    backgroundColor = Color(*eveColor.BURNISHED_GOLD).SetOpacity(OPACITY_IDLE).GetRGBA()
    backgroundColorLocked = backgroundColor
    iconSize = 24
    iconTexturePath = 'res:/UI/Texture/classes/CloneGrade/Omega_24.png'


class MissingSkillsLockButton(SkillPlanLockButton):
    frameColor = eveColor.WHITE
    backgroundColor = Color(*eveColor.COPPER_OXIDE_GREEN).SetOpacity(OPACITY_IDLE).GetRGBA()
    frameColorLocked = eveColor.PRIMARY_BLUE
    backgroundColorLocked = Color(*eveColor.SMOKE_BLUE).SetOpacity(OPACITY_IDLE).GetRGBA()
    iconSize = 20
    iconTexturePath = 'res:/UI/Texture/Classes/SkillPlan/buttonIcons/skillIcon.png'

    def ApplyAttributes(self, attributes):
        super(MissingSkillsLockButton, self).ApplyAttributes(attributes)
        self.numMissingFrame = Container(name='numMissingFrame', parent=self, align=uiconst.BOTTOMRIGHT, pos=(0, 0, 20, 20))
        Sprite(bgParent=self.numMissingFrame, texturePath='res:/UI/Texture/Classes/SkillPlan/smallCircleSolid.png', color=eveColor.HOT_RED)
        self.numMissingLabel = EveLabelSmall(name='numMissingLabel', parent=self.numMissingFrame, align=uiconst.CENTER, color=TextColor.HIGHLIGHT)

    def Lock(self, numMissing):
        super(MissingSkillsLockButton, self).Lock()
        self.numMissingFrame.Show()
        self.numMissingLabel.SetText(str(numMissing))

    def Unlock(self):
        super(MissingSkillsLockButton, self).Unlock()
        self.numMissingFrame.Hide()
