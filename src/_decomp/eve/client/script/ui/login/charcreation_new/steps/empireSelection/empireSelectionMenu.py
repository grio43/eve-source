#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelection\empireSelectionMenu.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.uianimations import animations
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionButton import EmpireSelectionButton
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionConst import EMPIRE_FACTIONIDS, MINIMIZE_ANIMATION_DURATION
from eve.client.script.ui.login.charcreation_new.charCreationSignals import onEmpireFactionSelected
from eveui import Sprite

class EmpireSelectionMenu(Container):
    default_height = 208

    def ApplyAttributes(self, attributes):
        super(EmpireSelectionMenu, self).ApplyAttributes(attributes)
        onEmpireFactionSelected.connect(self.OnEmpireSelectionButton)
        self.buttons = []
        self.isLarge = True
        self.ConstructButtons()
        self.ConstructionSelectionNotch()
        self.bgCont = Container(name='bgCont', parent=self)
        self.ConstructBackground()

    def ConstructButtons(self):
        for i, factionID in enumerate(EMPIRE_FACTIONIDS):
            analyticID = 'empireSelectionButton_faction_%s' % factionID
            button = EmpireSelectionButton(parent=self, align=uiconst.TOPLEFT_PROP, pos=(i / 3.0,
             0,
             0.25,
             0.99), maxWidth=self.height, factionID=factionID, analyticID=analyticID)
            self.buttons.append(button)

    def OnEmpireSelectionButton(self, factionID):
        x = EMPIRE_FACTIONIDS.index(factionID)
        animations.MorphScalar(self.selectionNotch, 'left', self.selectionNotch.left, x / 3.0, duration=MINIMIZE_ANIMATION_DURATION)
        if self.isLarge:
            for button in self.buttons:
                button.ReduceSize()

            self.isLarge = False

    def ConstructionSelectionNotch(self):
        self.selectionNotch = Container(name='selectionNotch', parent=self, align=uiconst.TOPLEFT_PROP, pos=(0.5, 0.0, 0.25, 0.99), maxWidth=self.height)
        Sprite(name='selectionNotch', parent=self.selectionNotch, align=uiconst.CENTERTOP, top=2, height=4, pos=(0, 2, 50, 4), texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/selectionNotch.png')
        Sprite(name='selectionNotch', parent=self.selectionNotch, align=uiconst.CENTERBOTTOM, pos=(0, 2, 50, 4), texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/selectionNotch.png', rotation=math.pi)

    def ConstructBackground(self):
        Sprite(name='topLine', parent=self.bgCont, align=uiconst.TOTOP, height=2, texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/selectionGradientLine.png')
        Sprite(name='bottomLine', parent=self.bgCont, align=uiconst.TOBOTTOM, height=2, texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/selectionGradientLine.png')
        GradientSprite(name='bgGradient', bgParent=self.bgCont, rgbData=((0, (0.0, 0.0, 0.0)),), alphaData=((0.0, 0.0),
         (0.25, 0.6),
         (0.75, 0.6),
         (1.0, 0.0)))
