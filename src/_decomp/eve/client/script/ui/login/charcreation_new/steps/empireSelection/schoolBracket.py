#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelection\schoolBracket.py
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.loggers.buttonLogger import log_button_clicked
from carbonui.primitives.bracket import Bracket
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from eve.client.script.ui.login.charcreation_new import soundConst
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionConst import ICONS_BY_SCHOOLID
from eve.client.script.ui.login.charcreation_new.charCreationSignals import onEmpireFactionSelected, onEmpireSchoolSelected, onEmpireSchoolButtonClicked
from eveui import Sprite
OPACITY_SELECTED = 1.0
OPACITY_IDLE = 0.5
OPACITY_HOVER = 1.0

class SchoolMarker(Container):
    default_bgTexturePath = 'res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/bracketBackground.png'
    default_width = 129
    default_height = 139
    default_state = uiconst.UI_DISABLED
    default_opacity = 0.0
    default_pickingMaskTexturePath = 'res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/bracketPickingMask.png'
    default_analyticID = ''

    def ApplyAttributes(self, attributes):
        super(SchoolMarker, self).ApplyAttributes(attributes)
        self.schoolID = attributes.schoolID
        self.analyticID = attributes.get('analyticID', self.default_analyticID)
        onEmpireSchoolSelected.connect(self.OnSchoolSelected)
        self.isSelected = False
        self.icon = Sprite(name='icon', parent=self, align=uiconst.CENTERTOP, pos=(0, 28, 64, 64), texturePath=ICONS_BY_SCHOOLID[self.schoolID], opacity=OPACITY_IDLE)
        self.selectedSprite = Sprite(name='selectedSprite', parent=self, align=uiconst.CENTERTOP, pos=(0, 10, 134, 159), texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/bracketSelected.png', opacity=0.0)
        self.hoverglow = Sprite(name='hoverGlow', parent=self, align=uiconst.CENTERTOP, pos=(0, -10, 144, 132), texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/bracketHoverglow.png', opacity=0.0)

    def FadeOut(self, *args):
        self.Disable()
        animations.FadeOut(self)

    def FadeIn(self, *args):
        self.Enable()
        animations.FadeIn(self)

    def SetSelected(self):
        animations.FadeIn(self.selectedSprite, OPACITY_SELECTED, duration=0.15)
        animations.FadeIn(self.icon, OPACITY_SELECTED, duration=0.15)
        self.isSelected = True
        PlaySound(soundConst.MAP_ICON_CLICK)

    def SetDeselected(self):
        animations.FadeOut(self.selectedSprite, duration=0.15)
        animations.FadeIn(self.icon, OPACITY_IDLE, duration=0.15)
        self.isSelected = False

    def OnSchoolSelected(self, schoolID):
        if schoolID == self.schoolID:
            self.SetSelected()
        else:
            self.SetDeselected()

    def OnMouseEnter(self, *args):
        animations.FadeIn(self.hoverglow, 0.1, duration=0.4)
        if not self.isSelected:
            PlaySound(soundConst.MAP_ICON_HOVER)
            animations.FadeIn(self.icon, OPACITY_HOVER, duration=0.2)
            animations.FadeIn(self.selectedSprite, 0.25, duration=0.2)

    def OnMouseExit(self, *args):
        animations.FadeIn(self.hoverglow, 0.0, duration=0.4)
        if not self.isSelected:
            animations.FadeIn(self.icon, OPACITY_IDLE, duration=0.2)
            animations.FadeIn(self.selectedSprite, 0.0, duration=0.2)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_SETSELECTED)
        onEmpireSchoolButtonClicked(self.schoolID)
        log_button_clicked(self)


class SchoolBracket(Bracket):
    default_width = 129
    default_height = 302
    default_state = uiconst.UI_PICKCHILDREN
    default_integerCoordinates = False

    def ApplyAttributes(self, attributes):
        super(SchoolBracket, self).ApplyAttributes(attributes)
        self.scene = attributes.scene
        self.system = attributes.system
        self.factionID = attributes.factionID
        self.schoolID = attributes.schoolID
        self.trackTransform = trinity.EveTransform()
        self.trackTransform.translation = self.system.position
        self.scene.objects.append(self.trackTransform)
        onEmpireFactionSelected.connect(self.OnEmpireFactionSelected)
        self.marker = SchoolMarker(parent=self, align=uiconst.CENTERTOP, schoolID=self.schoolID, analyticID='SchoolMarker_schoolID_%s' % self.schoolID)

    def OnEmpireFactionSelected(self, factionID):
        if factionID == self.factionID:
            self.marker.FadeIn()
        else:
            self.marker.FadeOut()

    def GetPosition(self):
        return self.trackTransform.translation
