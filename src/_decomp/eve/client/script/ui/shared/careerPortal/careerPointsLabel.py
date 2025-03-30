#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\careerPointsLabel.py
import uthread2
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from careergoals.client.signal import on_goal_progress_changed
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eveui import Sprite
GLYPH_ICON_SIZE = 16

class CareerPointsLabel(ContainerAutoSize):
    default_name = 'CareerPointsLabel'
    default_height = GLYPH_ICON_SIZE
    default_align = uiconst.CENTER

    def __init__(self, careerNode, *args, **kwargs):
        super(CareerPointsLabel, self).__init__(*args, **kwargs)
        self._careerNodeObject = None
        self.currentProgress = None
        self.pointsLabel = None
        self.ConstructLayout()
        if careerNode:
            self.careerNodeObject = careerNode
        on_goal_progress_changed.connect(self.OnGoalProgressChanged)

    def Close(self):
        on_goal_progress_changed.disconnect(self.OnGoalProgressChanged)
        super(CareerPointsLabel, self).Close()

    @property
    def careerNodeObject(self):
        return self._careerNodeObject

    @careerNodeObject.setter
    def careerNodeObject(self, newNodeObject):
        self._careerNodeObject = newNodeObject
        if not newNodeObject.goal:
            return
        self.currentProgress = newNodeObject.goal.progress
        self.pointsLabel.text = self.careerNodeObject.GetCareerPathPointsText()

    def ConstructLayout(self):
        self.pointsIcon = Sprite(name='icon', parent=self, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/classes/careerPortal/career_point_icon.png', width=GLYPH_ICON_SIZE)
        self.ConstructPointsLabel()

    def ConstructPointsLabel(self, text = ''):
        if self.pointsLabel:
            self.pointsLabel.Close()
        self.pointsLabel = EveLabelMedium(name='label', parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, left=4, text=text, color=eveColor.WHITE)
        self.pointsLabel.text = text

    def OnGoalProgressChanged(self, goalID, value):
        if not value or not self.careerNodeObject or self.careerNodeObject.goal.goal_id != goalID:
            return
        uthread2.StartTasklet(self.AnimateProgressDifference, value - self.currentProgress)
        self.currentProgress = value

    def AnimateProgressDifference(self, difference):
        animations.FadeOut(self, duration=0.4)
        uthread2.Sleep(0.5)
        self.pointsLabel.text = '+%s' % difference
        self.pointsLabel.SetTextColor(eveColor.LEAFY_GREEN)
        self.pointsIcon.color = eveColor.LEAFY_GREEN
        animations.FadeIn(self, duration=0.4)
        animations.MoveInFromBottom(self, amount=10, callback=lambda : uthread2.StartTasklet(self.MoveBack))

    def MoveBack(self):
        uthread2.Sleep(1.0)
        animations.MoveOutBottom(self, amount=10)
        animations.FadeOut(self, duration=0.4)
        uthread2.Sleep(0.5)
        self.Reset()
        animations.FadeIn(self, duration=0.4)
        animations.MorphScalar(self, 'top', startVal=-10, endVal=4, duration=0.4)

    def Reset(self):
        self.pointsLabel.text = self.careerNodeObject.GetCareerPathPointsText()
        self._UpdatePointsColor()

    def _UpdatePointsColor(self):
        progress, target = self.careerNodeObject.GetCareerPathProgress()
        self.pointsLabel.SetTextColor(eveColor.LEAFY_GREEN if progress >= target else EveLabelMedium.default_color)
        self.pointsIcon.color = eveColor.LEAFY_GREEN if progress >= target else eveColor.WHITE
