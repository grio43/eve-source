#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\contents\skillPlanTitle.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.control.glowSprite import GlowSprite

class SkillPlanTitle(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(SkillPlanTitle, self).ApplyAttributes(attributes)
        spriteCont = Container(parent=self, name='spriteCont', align=uiconst.TORIGHT, width=16)
        self.showInfo = GlowSprite(parent=spriteCont, name='showInfo', align=uiconst.BOTTOMLEFT, height=16, width=16, texturePath='res:/ui/Texture/Icons/show_info20.png', hint=attributes.get('infoHint', ''))
        EveCaptionLarge(parent=self, name='skillPlanTitle', align=uiconst.TORIGHT, text=attributes.get('title', ''), padRight=2)
