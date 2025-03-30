#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\extras\tourneyMatchStatusUI.py
import carbonui.const as uiconst
import blue
import tournamentmanagement.const as tourneyConst
import uthread
import tournamentmanagement.tournamentTimerFormatter as tournamentTimerFormatter
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control import eveLabel

class TourneyMatchStatusUI(Window):
    __guid__ = 'form.TourneyMatchStatusUI'
    default_scope = uiconst.SCOPE_ALL

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption('Match Status')
        self.SetMinSize((100, 100))
        self.MakeUnResizeable()
        self.MakeUnKillable()
        self.matchState = 0
        self.matchStartTime = 0
        self.overtimeLevel = 0
        self.matchLength = 0
        self.overtimeLength = 0
        self.ConstructLayout()
        self.matchTimer = tournamentTimerFormatter.TournamentTimerFormatter()
        self.timerThread = uthread.new(self._UpdateTimer)

    def ConstructLayout(self):
        self.pointsContainer = Container(name='pointsContainer', align=uiconst.TOTOP, parent=self.sr.main, height=40)
        self.myScore = eveLabel.Label(name='myScore', text='000', padding=5, parent=self.pointsContainer, align=uiconst.TOLEFT, fontsize=30, width=55)
        self.scoreDivider = Fill(name='scoreDivider', padding=1, height=40, width=10, parent=self.pointsContainer, align=uiconst.CENTER)
        self.opponentScore = eveLabel.Label(name='opponentScore', text='000', padding=5, parent=self.pointsContainer, align=uiconst.TORIGHT, fontsize=30, width=55)
        self.clockLabel = eveLabel.Label(text='Waiting...', parent=self.sr.main, top=15, align=uiconst.CENTER, fontsize=40)

    def OnTournamentMatchStateChange(self, redPoints, bluePoints, myTeam, matchStatus):
        self.matchState = matchStatus['matchState']
        self.matchStartTime = matchStatus['matchStartTime']
        self.overtimeLevel = matchStatus['overtimeLevel']
        self.matchLength = matchStatus['matchLength']
        self.overtimeLength = matchStatus['overtimeLength']
        if self.matchState > tourneyConst.tournamentStateWarpin:
            if myTeam == 0:
                self.myScore.SetRGBA(1, 0, 0, 1)
                self.myScore.text = redPoints
                self.opponentScore.text = bluePoints
            elif myTeam == 1:
                self.myScore.SetRGBA(0, 0.75, 1, 1)
                self.myScore.text = bluePoints
                self.opponentScore.text = redPoints

    def _UpdateTimer(self):
        while not self.destroyed and self.matchState < tourneyConst.tournamentStateComplete:
            text, color = self.matchTimer.GetTimerTextAndColor(self.matchState, self.matchStartTime, self.overtimeLevel, self.matchLength, self.overtimeLength)
            self.clockLabel.text = text
            self.clockLabel.SetRGBA(*color)
            blue.synchro.SleepWallclock(200)

    def Close(self, *args, **kwargs):
        self.timerThread.kill()
        self.timerThread = None
        Window.Close(self, *args, **kwargs)
