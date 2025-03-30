#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\airSkillPlanContainer.py
import math
import trinity
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay
from eve.client.script.ui.skillPlan.browser.airSkillPlanEntry import AirSkillPlanEntry
from eve.client.script.ui.skillPlan.controls.skillPlanLine import SkillPlanLine
from eveui import Sprite
from localization import GetByLabel
from skills.skillplan.skillPlanConst import PLAN_ID_AIR
from skills.skillplan.skillPlanService import GetSkillPlanSvc

class AirSkillPlanContainer(Container):

    def ApplyAttributes(self, attributes):
        super(AirSkillPlanContainer, self).ApplyAttributes(attributes)
        AirSkillPlanEntry(parent=self, align=uiconst.TOPLEFT_PROP, pos=(0.5, 0.5, 300, 130), skillPlan=GetSkillPlanSvc().Get(PLAN_ID_AIR))
        self.leftFrame = Sprite(name='leftFrame', parent=self, align=uiconst.CENTER, pos=(-310, 0, 186, 269), texturePath='res:/UI/Texture/Classes/SkillPlan/airBg.png', opacity=0.0)
        self.rightFrame = Sprite(name='rightFrame', parent=self, align=uiconst.CENTER, pos=(310, 0, 186, 269), texturePath='res:/UI/Texture/Classes/SkillPlan/airBg.png', rotation=math.pi, opacity=0.0)
        Sprite(name='arrow', parent=self, align=uiconst.TOPLEFT_PROP, pos=(0.5, 0.8, 16, 16), texturePath='res:/UI/Texture/Classes/SkillPlan/airArrow.png')
        BlurredSceneUnderlay(name='bgBlack', parent=self, align=uiconst.TOPLEFT_PROP, pos=(0.5, 0.82, 40, 40), textureSecondaryPath='res:/UI/Texture/Classes/SkillPlan/factionButtons/bgFill.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        lockCont = Container(parent=self, align=uiconst.CENTERBOTTOM, state=uiconst.UI_NORMAL, pos=(0, 0, 48, 48), hint=GetByLabel('UI/SkillPlan/CareerPathsLockedByAIR'))
        Sprite(name='arrowIcon', parent=lockCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/ess/mainBank/lock.png', pos=(0, 0, 33, 34))
        Sprite(name='bgStroke', bgParent=lockCont, texturePath='res:/UI/Texture/Classes/SkillPlan/factionButtons/bgStroke.png', opacity=0.1)
        BlurredSceneUnderlay(name='bgBlack', bgParent=lockCont, textureSecondaryPath='res:/UI/Texture/Classes/SkillPlan/factionButtons/bgFill.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        SkillPlanLine(parent=self, align=uiconst.TOBOTTOM, padding=(20, 0, 20, 24))
        SkillPlanLine(parent=self, align=uiconst.TOPLEFT_PROP, pos=(0.5, 1.0, 3, 0.32))
        timeOffset = 0.8
        duration = 0.4
        animations.FadeIn(self.leftFrame, 0.9, duration=duration, timeOffset=timeOffset, curveType=uiconst.ANIM_OVERSHOT4)
        animations.MorphScalar(self.leftFrame, 'left', self.leftFrame.left, -305, duration=duration, timeOffset=timeOffset)
        animations.FadeIn(self.rightFrame, 0.9, duration=duration, timeOffset=timeOffset, curveType=uiconst.ANIM_OVERSHOT4)
        animations.MorphScalar(self.rightFrame, 'left', self.rightFrame.left, 305, duration=duration, timeOffset=timeOffset)
