#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\stepHeader.py
import math
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveHeaderLarge, EveCaptionLarge
from eveui import Sprite

class StepHeader(ContainerAutoSize):
    default_name = 'StepHeader'
    default_alignMode = uiconst.TOLEFT
    default_height = 20
    default_title = ''
    default_subtitle = ''

    def ApplyAttributes(self, attributes):
        super(StepHeader, self).ApplyAttributes(attributes)
        Sprite(name='leftGradient', parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/headerGradientStrip.png', pos=(0, 0, 224, 16), opacity=0.5)
        self.caption = EveCaptionLarge(parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, padding=(30, 0, 30, 0), text=attributes.title, opacity=1.0)
        Sprite(name='leftGradient', parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, rotation=math.pi, texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/headerGradientStrip.png', pos=(0, 0, 224, 16), opacity=0.5)
        self.description = EveHeaderLarge(parent=self, align=uiconst.CENTERTOP, top=40, width=350, text='<center>' + attributes.subtitle)
