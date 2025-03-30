#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\incursions\taleSystemEffectCont.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.incursions.taleSystemEffect import TaleSystemEffect
from localization import GetByLabel
ICONSIZE = 22

class TaleSystemEffectCont(Container):
    default_name = 'TaleSystemEffectCont'
    default_height = ICONSIZE

    def ApplyAttributes(self, attributes):
        super(TaleSystemEffectCont, self).ApplyAttributes(attributes)
        effects = attributes.effects
        influence = attributes.influence
        for effectInfo in effects:
            effect = TaleSystemEffect(name=effectInfo['name'], align=uiconst.TOLEFT, parent=self, width=ICONSIZE, padRight=6, texturePath=effectInfo['texturePath'], hint=GetByLabel(effectInfo['hint']), isScalable=effectInfo['isScalable'])
            effect.SetInfluence(influence)
