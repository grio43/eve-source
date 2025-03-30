#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\browser\careerPathToggleButtonGroup.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.util.color import Color
from characterdata import careerpath
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.control.toggleButtonGroupButton import BaseToggleButtonGroupButton, ToggleButtonGroupButton
from eve.client.script.ui.shared.careerPortal import careerConst
from eve.client.script.ui.skillPlan.skillPlanInfoIcon import SkillPlanInfoIcon
from eveui import Sprite
from localization import GetByMessageID
LINE_OPACITY = 0.6
LINE_OPACITY_SELECTED = 1.0
LINE_LEFT = 80
LINE_LEFT_SELECTED = 92

def GetButtonName(careerPathID):
    return 'CareerPathButton_%s' % careerpath.get_career_path_internal_name(careerPathID)


class SimpleCareerPathToggleButtonGroupButton(ToggleButtonGroupButton):

    def ApplyAttributes(self, attributes):
        super(SimpleCareerPathToggleButtonGroupButton, self).ApplyAttributes(attributes)
        self.careerPathID = attributes.btnID
        self.name = GetButtonName(self.careerPathID)


class CareerPathToggleButtonGroupButton(BaseToggleButtonGroupButton):

    def ApplyAttributes(self, attributes):
        super(CareerPathToggleButtonGroupButton, self).ApplyAttributes(attributes)
        careerPathHint = attributes.careerPathHint
        self.careerPathID = attributes.btnID
        careerPath = careerpath.get_career_path(self.careerPathID)
        careerName = GetByMessageID(careerPath.nameID)
        self.name = GetButtonName(self.careerPathID)
        iconCont = Container(parent=self, align=uiconst.CENTERTOP, pos=(0, 0, 270, 290))
        self.icon = Sprite(parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 80, 80), texturePath=careerConst.ICON_BY_CAREER_ID[self.careerPathID], opacity=1.0)
        Sprite(name='fixedBG', parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 182, 162), texturePath='res:/UI/Texture/classes/skillPlan/careerPathButtons/fixedBG.png', opacity=1.0)
        self.glowBG = Sprite(name='glowBG', parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 270, 290), texturePath='res:/UI/Texture/classes/skillPlan/careerPathButtons/glowBG.png', color=eveColor.WHITE, opacity=0.2)
        self.hexagonBG = Sprite(name='hexagonBG', parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 140, 162), texturePath='res:/UI/Texture/classes/skillPlan/careerPathButtons/hexagonBG.png', color=eveColor.WHITE, opacity=0.1)
        self.selectedFrame = Sprite(name='selectedFrame', parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 246, 279), texturePath='res:/UI/Texture/classes/skillPlan/careerPathButtons/selectionHighlight.png', color=eveColor.SMOKE_BLUE, opacity=0.0)
        self.leftLine = Fill(parent=iconCont, align=uiconst.CENTER, opacity=LINE_OPACITY, pos=(-LINE_LEFT,
         0,
         2,
         45))
        self.rightLine = Fill(parent=iconCont, align=uiconst.CENTER, opacity=LINE_OPACITY, pos=(LINE_LEFT,
         0,
         2,
         45))
        titleCont = ContainerAutoSize(parent=self, name='titleCont', align=uiconst.CENTERBOTTOM, height=30, left=8)
        titleLabelCont = ContainerAutoSize(parent=titleCont, name='titleLabelCont', align=uiconst.TOLEFT, height=30)
        EveCaptionLarge(parent=titleLabelCont, name='titleLabel', align=uiconst.CENTER, state=uiconst.UI_DISABLED, text=careerName)
        showInfoCont = ContainerAutoSize(parent=titleCont, name='showInfoCont', align=uiconst.TOLEFT, height=30, padLeft=10, padTop=1)
        SkillPlanInfoIcon(parent=showInfoCont, name='showInfo', align=uiconst.CENTER, hint=careerPathHint)

    def SetSelected(self, animate = True):
        super(CareerPathToggleButtonGroupButton, self).SetSelected(animate)
        duration = 0.15
        if animate:
            animations.FadeTo(self.selectedFrame, self.selectedFrame.opacity, 0.2, duration=duration)
            animations.FadeTo(self.glowBG, self.glowBG.opacity, 0.8, duration=duration)
            animations.FadeTo(self.hexagonBG, self.hexagonBG.opacity, 1.0, duration=duration)
            animations.SpColorMorphTo(self.icon, self.icon.GetRGBA(), Color.BLACK, duration=duration)
            animations.MorphScalar(self.leftLine, 'left', self.leftLine.left, -LINE_LEFT_SELECTED, duration=duration)
            animations.MorphScalar(self.rightLine, 'left', self.rightLine.left, LINE_LEFT_SELECTED, duration=duration)
            animations.FadeTo(self.leftLine, self.leftLine.opacity, LINE_OPACITY_SELECTED, duration=duration)
            animations.FadeTo(self.rightLine, self.rightLine.opacity, LINE_OPACITY_SELECTED, duration=duration)
        else:
            self.selectedFrame.opacity = 0.2
            self.glowBG.opacity = 0.8
            self.hexagonBG.opacity = 1.0
            self.icon.SetRGBA(*Color.BLACK)
            self.leftLine.left = -LINE_LEFT_SELECTED
            self.rightLine.left = LINE_LEFT_SELECTED
            self.leftLine.opacity = LINE_OPACITY_SELECTED
            self.rightLine.opacity = LINE_OPACITY_SELECTED

    def SetDeselected(self, animate = True):
        super(CareerPathToggleButtonGroupButton, self).SetDeselected(animate)
        duration = 0.15
        if animate:
            animations.FadeTo(self.selectedFrame, self.selectedFrame.opacity, 0.0, duration=duration)
            animations.FadeTo(self.glowBG, self.glowBG.opacity, 0.2, duration=duration)
            animations.FadeTo(self.hexagonBG, self.hexagonBG.opacity, 0.1, duration=duration)
            animations.SpColorMorphTo(self.icon, self.icon.GetRGBA(), eveColor.WHITE, duration=duration)
            animations.MorphScalar(self.leftLine, 'left', self.leftLine.left, -LINE_LEFT, duration=duration)
            animations.MorphScalar(self.rightLine, 'left', self.rightLine.left, LINE_LEFT, duration=duration)
            animations.FadeTo(self.leftLine, self.leftLine.opacity, LINE_OPACITY, duration=duration)
            animations.FadeTo(self.rightLine, self.rightLine.opacity, LINE_OPACITY, duration=duration)
        else:
            self.selectedFrame.opacity = 0.0
            self.glowBG.opacity = 0.2
            self.hexagonBG.opacity = 0.1
            self.icon.SetRGBA(*eveColor.WHITE)
            self.leftLine.left = -LINE_LEFT
            self.rightLine.left = LINE_LEFT
            self.leftLine.opacity = LINE_OPACITY
            self.rightLine.opacity = LINE_OPACITY

    def OnMouseEnter(self, *args):
        if self.isDisabled or self.IsSelected():
            return
        PlaySound('skills_planner_path_hover_play')
        animations.FadeTo(self.hexagonBG, self.hexagonBG.opacity, 0.5, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        if self.isDisabled or self.IsSelected():
            return
        animations.FadeTo(self.hexagonBG, self.hexagonBG.opacity, 0.1, duration=uiconst.TIME_EXIT)
