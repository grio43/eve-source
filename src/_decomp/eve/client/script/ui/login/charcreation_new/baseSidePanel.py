#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\baseSidePanel.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import GradientSprite
from eveui import Sprite

class BaseSidePanel(Container):
    default_mainContPadding = None

    def ApplyAttributes(self, attributes):
        super(BaseSidePanel, self).ApplyAttributes(attributes)
        self.mainCont = Container(name='mainCont', parent=self, padding=self.default_mainContPadding)
        bgCont = Container(name='bgCont', parent=self)
        GradientSprite(name='bgGradient', bgParent=bgCont, rgbData=((0, (0.0, 0.0, 0.0)),), alphaData=((0.0, 0.0),
         (0.25, 0.8),
         (0.75, 0.8),
         (1.0, 0.0)))
        Sprite(name='topLine', parent=bgCont, align=uiconst.TOTOP, height=2, texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/selectionGradientLine.png')
        Sprite(name='topNotch', parent=bgCont, align=uiconst.CENTERTOP, pos=(0, 2, 50, 4), texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/selectionNotch.png')
        Sprite(name='bottomLine', parent=bgCont, align=uiconst.TOBOTTOM, height=2, texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/selectionGradientLine.png')
        Sprite(name='bottomNotch', parent=bgCont, align=uiconst.CENTERBOTTOM, pos=(0, 2, 50, 4), texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/selectionNotch.png', rotation=math.pi)
