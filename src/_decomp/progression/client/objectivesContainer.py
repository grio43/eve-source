#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\objectivesContainer.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uiconst import SOUND_ENTRY_HOVER
from progression.client.const import BACKGROUND_COLOR_GRAY, COLOR_INFO_FOREGROUND
from progression.client.objectiveEntry import ObjectiveEntry

class ObjectivesContainer(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(ObjectivesContainer, self).ApplyAttributes(attributes)
        self.progressionSvc = attributes.progressionSvc
        progressionHistory = self.progressionSvc.GetProgressionHistory()
        self.progressionHistoryLength = len(progressionHistory) - 1
        self.timerWidgets = []
        self.entry = None
        self.navContainer = ContainerAutoSize(name='NavContainer', parent=self, align=uiconst.TOTOP, height=24, state=uiconst.UI_NORMAL)
        self.progressCont = ContainerAutoSize(name='progressCont', parent=self.navContainer, align=uiconst.TOLEFT, height=24, state=uiconst.UI_NORMAL)
        self.circleProgressCont = ContainerAutoSize(name='circleProgressCont', parent=self.navContainer, align=uiconst.TOLEFT, height=24)
        allButLatestObjectives = progressionHistory[:-1]
        for objective in allButLatestObjectives:
            self.ConstructProgressSection(animate=False, hint=objective.title)

        self.ConstructCurrentBubble(self.ConstructEntry)

    def ConstructEntry(self):
        self.ConstructProgressArrow()
        self.entryContainer = ContainerAutoSize(parent=self, align=uiconst.TOTOP)
        self.entry = ObjectiveEntry(parent=self.entryContainer, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)

    def ConstructProgressSection(self, animate = False, hint = None):
        NavigationBubble(name='NavCircleTooltipContainer', parent=self.progressCont, align=uiconst.TOLEFT, width=12, height=12, hint=hint, state=uiconst.UI_NORMAL)
        if animate:
            navConnectionCont = Container(name='NavConnectionContainer', parent=self.progressCont, align=uiconst.TOLEFT, width=0, height=2)
            animations.MorphScalar(navConnectionCont, 'width', startVal=0, endVal=12, duration=0.2, curveType=uiconst.ANIM_LINEAR)
        else:
            navConnectionCont = Container(name='NavConnectionContainer', parent=self.progressCont, align=uiconst.TOLEFT, width=12, height=2)
        Sprite(name='NavConnection', parent=navConnectionCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=12, height=2, texturePath='res:/UI/Texture/Classes/DungeonMessaging/NavConnection.png', color=COLOR_INFO_FOREGROUND)

    def ConstructCurrentBubble(self, callback = None):
        progressionHistory = self.progressionSvc.GetProgressionHistory()
        latestObjective = progressionHistory[-1]
        if latestObjective.tasks:
            cls = NavigationCurrentBubble
        else:
            cls = NavigationBubble
            if not self.entry:
                self.ConstructEntry()
        self.currentNavigationBubble = cls(name='NavigationCurrentBubble', parent=self.circleProgressCont, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, width=12, height=12, padLeft=-3, padRight=3, callback=callback, hint=latestObjective.title, scalingCenter=(0.5, 0.5))

    def ConstructProgressArrow(self):
        paddingOffset = self.progressionHistoryLength * 24
        if self.IsFinalObjective():
            paddingOffset -= 2
        self.arrowCont = Container(parent=self, align=uiconst.TOTOP, height=6, padLeft=paddingOffset)
        Sprite(name='ProgressArrow', parent=self.arrowCont, state=uiconst.UI_DISABLED, width=12, height=6, texturePath='res:/UI/Texture/Classes/DungeonMessaging/TitleBoxArrow.png', color=BACKGROUND_COLOR_GRAY)

    def UpdateWidgetObjective(self):
        if self.entry:
            self.entry.ConstructTitle()
            self.entry.UpdateWidgets()

    def UpdateEntryRoomJoined(self):
        if self.entry:
            self.entry.UpdateWidgetsOnRoomJoined()

    def IsFinalObjective(self):
        progressionHistory = self.progressionSvc.GetProgressionHistory()
        if not progressionHistory:
            return False
        latestObjective = progressionHistory[-1]
        return not latestObjective.tasks

    def CompleteObjective(self, lastTaskCompleted):
        self.AdvanceProgressArrow()
        progressionHistory = self.progressionSvc.GetProgressionHistory()
        previousObjective = progressionHistory[-2]
        self.ConstructProgressSection(animate=True, hint=previousObjective.title)
        self.entry.CompleteObjective(lastTaskCompleted)
        if self.IsFinalObjective():
            self.currentNavigationBubble.Close()
            self.ConstructCurrentBubble()
        else:
            latestObjective = progressionHistory[-1]
            self.currentNavigationBubble.hint = latestObjective.title

    def AdvanceProgressArrow(self):
        if self.IsFinalObjective():
            arrowPad = 22
        else:
            arrowPad = 24
        animations.MorphScalar(self.arrowCont, 'padLeft', self.arrowCont.padLeft, self.arrowCont.padLeft + arrowPad, 0.2, curveType=uiconst.ANIM_LINEAR)


class NavigationCurrentBubble(Transform):

    def ApplyAttributes(self, attributes):
        super(NavigationCurrentBubble, self).ApplyAttributes(attributes)
        callback = attributes.callback
        self.icon = Sprite(name='NavInProgressCircle', parent=self, state=uiconst.UI_DISABLED, width=24, height=24, texturePath='res:/UI/Texture/Classes/DungeonMessaging/NavActive2x.png')
        PlaySound('messaging_system_dot_play')
        animations.MorphVector2(self, 'scale', startVal=self.scale, endVal=(0.5, 0.5), duration=0.6, callback=callback, curveType=uiconst.ANIM_BOUNCE)

    def OnMouseEnter(self, *args):
        PlaySound(SOUND_ENTRY_HOVER)
        self.icon.opacity = 0.7

    def OnMouseExit(self, *args):
        self.icon.opacity = 1.0


class NavigationBubble(Container):

    def ApplyAttributes(self, attributes):
        super(NavigationBubble, self).ApplyAttributes(attributes)
        progressTransform = Transform(name='NavCircleContainer', parent=self, align=uiconst.TOLEFT, width=12, height=12, scalingCenter=(0.5, 0.5))
        self.icon = Sprite(name='NavDonebubble', parent=progressTransform, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=12, height=12, texturePath='res:/UI/Texture/Classes/DungeonMessaging/NavDone.png', color=COLOR_INFO_FOREGROUND)

    def OnMouseEnter(self, *args):
        PlaySound(SOUND_ENTRY_HOVER)
        self.icon.opacity = 0.7

    def OnMouseExit(self, *args):
        self.icon.opacity = 1.0
