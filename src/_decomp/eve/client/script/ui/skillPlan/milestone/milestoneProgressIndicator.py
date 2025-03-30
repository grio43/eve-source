#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\milestone\milestoneProgressIndicator.py
import blue
import milestoneTooltips
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.skillPlan import skillPlanUtil
from eve.client.script.ui.skillPlan.milestone.milestoneProgressGauge import MilestoneProgressGauge
from localization import GetByLabel
from signals import Signal
from skills.skillplan.milestone.const import MilestoneSubType
from skills.skillplan.milestone.milestonesUtil import GetMilestoneSubType
lineWidth = 4

class MilestoneProgressIndicator(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(MilestoneProgressIndicator, self).ApplyAttributes(attributes)
        self.milestone = attributes.milestone
        self.skillPlan = attributes.skillPlan
        self.isEditable = attributes.isEditable
        highlightNotInTraining = attributes.highlightNotInTraining
        self.on_data_dropped = Signal('on_data_dropped')
        self.checkmark = Sprite(parent=self, name='checkmark', align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/SkillPlan/lockButtonCheckmark.png', width=20, height=20, top=0)
        radius = self.height / 2
        self.progressGauge = MilestoneProgressGauge(parent=self, radius=radius, state=uiconst.UI_NORMAL, highlightNotInTraining=highlightNotInTraining, controller=self.milestone)
        self.progressGauge.ConstructTooltipPanel = self.ConstructTooltipPanel
        self.progressGauge.OnClick = self.OnClick
        self.progressGauge.GetMenu = self.GetMenu
        self.icon = GlowSprite(name='icon', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=skillPlanUtil.GetMilestoneTexturePath(self.milestone.GetTypeID()))
        self.UpdateProgress(animate=False)

    def OnClick(self, *args):
        typeID = self.milestone.GetTypeID()
        if typeID:
            sm.GetService('info').ShowInfo(typeID)

    def OnMouseEnter(self, *args):
        self.icon.OnMouseEnter()

    def OnMouseExit(self, *args):
        self.icon.OnMouseExit()

    def UpdateProgress(self, animate = True):
        self.progressGauge.UpdateProgress(animate)
        self.checkmark.display = self.milestone.IsCompleted()

    def SetRadius(self, radius):
        self.width = self.height = radius * 2
        self.progressGauge.SetRadius(radius)
        self.icon.width = self.icon.height = radius * 0.8
        self.checkmark.top = radius * 0.8

    def GetMenu(self):
        if self.milestone.GetID() is not None:
            menu = sm.GetService('menu').GetMenuFromItemIDTypeID(None, self.milestone.GetTypeID(), includeMarketDetails=True)
            if self.isEditable:
                menu.append(None)
                menu.append((GetByLabel('UI/SkillPlan/RemoveMilestone'), self.Remove))
            if session.role & ROLE_PROGRAMMER:
                menu.append(None)
                menu.append((u'GM: Copy Milestone ID', blue.pyos.SetClipboardData, (str(self.milestone.GetID()),)))
            return menu

    def Remove(self):
        if self.milestone.GetID() is not None:
            PlaySound('skills_planner_skill_remove_play')
            self.skillPlan.RemoveMilestone(self.milestone.GetID())

    def OnDropData(self, dragSource, dragData):
        if self.isEditable:
            self.on_data_dropped(dragSource, dragData, self.milestone.GetID())
            animations.FadeTo(self.progressGauge, self.progressGauge.opacity, 1.0, duration=uiconst.TIME_EXIT)

    def OnDragEnter(self, dragSource, dragData):
        if self.isEditable:
            animations.FadeTo(self.progressGauge, self.progressGauge.opacity, 0.5, duration=0.3)

    def OnDragExit(self, *args):
        if self.isEditable:
            animations.FadeTo(self.progressGauge, self.progressGauge.opacity, 1.0, duration=uiconst.TIME_EXIT)

    def _GetTooltipClass(self):
        typeID = self.milestone.GetTypeID()
        if GetMilestoneSubType(typeID) in (MilestoneSubType.SHIP_MILESTONE, MilestoneSubType.MODULE_MILESTONE, MilestoneSubType.OTHER_MILESTONE):
            return milestoneTooltips.TypeIDMilestoneInfoTooltip
        if GetMilestoneSubType(typeID) == MilestoneSubType.SKILL_MILESTONE:
            return milestoneTooltips.SkillMilestoneInfoTooltip

    def ConstructTooltipPanel(self):
        if self.milestone.GetTypeID() is None:
            return
        if uicore.IsDragging():
            return
        tooltipClass = self._GetTooltipClass()
        isShip = GetMilestoneSubType(self.milestone.GetTypeID()) == MilestoneSubType.SHIP_MILESTONE
        return tooltipClass(skillPlan=self.skillPlan, milestone=self.milestone, isEditable=self.isEditable, iconSize=128 if isShip else 64)
