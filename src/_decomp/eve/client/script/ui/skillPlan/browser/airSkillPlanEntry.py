#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\airSkillPlanEntry.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.skillPlan.browser.skillPlanEntry import SkillPlanEntry
from eveui import Sprite

class AirSkillPlanEntry(SkillPlanEntry):

    def ConstructTextCont(self):
        textCont = Container(parent=self.mainCont, align=uiconst.TOTOP, height=33)
        Sprite(parent=textCont, align=uiconst.TOPLEFT, pos=(0, 0, 62, 25), texturePath='res:/UI/Texture/Classes/SkillPlan/airLogo.png')
