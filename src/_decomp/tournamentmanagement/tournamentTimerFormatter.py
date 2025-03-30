#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\tournamentmanagement\tournamentTimerFormatter.py
import blue
from tournamentmanagement import const as tourneyConst

class TournamentTimerFormatter(object):

    def __init__(self, defaultText = 'Waiting...'):
        self.defaultText = defaultText
        self.timerText = defaultText
        self.timerColor = (1, 1, 1, 1)

    def GetTimerTextAndColor(self, matchState, matchStartTime, overtimeLevel, matchLength, overtimeLength):
        if matchState >= tourneyConst.tournamentStateComplete:
            return (self.timerText, self.timerColor)
        if matchState < tourneyConst.tournamentStateCountdown:
            self.timerColor = (1, 1, 1, 1)
            return (self.defaultText, self.timerColor)
        if matchState in (tourneyConst.tournamentStateCountdown, tourneyConst.tournamentStateStarting):
            countdownTimeSec = blue.os.TimeDiffInMs(blue.os.GetWallclockTime(), matchStartTime) / 1000.0
            displayTimeSec = max(0, countdownTimeSec)
            self.timerColor = (1, 1, 0, 1)
            self.timerText = self.FormatTimerText(displayTimeSec)
            return (self.timerText, self.timerColor)
        elapsedTimeSec = blue.os.TimeDiffInMs(matchStartTime, blue.os.GetWallclockTime()) / 1000.0
        if overtimeLevel > 0:
            displayTimeSec = max(0, matchLength + overtimeLength - elapsedTimeSec)
            self.timerColor = (1, 0, 0, 1)
            overtimeText = ' TiDi:{:.0f}%'.format(tourneyConst.tournamentOtLevelToTidi[overtimeLevel] * 100.0)
            self.timerText = self.FormatTimerText(displayTimeSec) + overtimeText
        else:
            displayTimeSec = max(0, matchLength - elapsedTimeSec)
            self.timerColor = (1, 1, 1, 1)
            self.timerText = self.FormatTimerText(displayTimeSec)
        return (self.timerText, self.timerColor)

    def FormatTimerText(self, displayTimeSec):
        timeRemaining = int(displayTimeSec)
        return '{:d}:{:02d}'.format(timeRemaining / 60, timeRemaining % 60)
