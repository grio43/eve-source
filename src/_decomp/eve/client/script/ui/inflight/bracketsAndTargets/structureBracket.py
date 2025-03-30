#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracketsAndTargets\structureBracket.py
import blue
import structures
import localization
from eve.client.script.ui.inflight.bracketsAndTargets.inSpaceBracket import InSpaceBracket
from eve.client.script.ui.control.countdownTimer import CountdownTimer, TIMER_RUNNING_OUT_NO_ANIMATION
from eve.client.script.ui.control.damageRing import DamageRing

class StructureBracket(InSpaceBracket):

    def ApplyAttributes(self, attributes):
        InSpaceBracket.ApplyAttributes(self, attributes)
        self.damage = DamageRing(name='DamageRing', parent=self)
        self.timer = CountdownTimer(name='StructureCounter', parent=self, countsDown=True, timerFunc=blue.os.GetWallclockTime, timerRunningOutAnimation=TIMER_RUNNING_OUT_NO_ANIMATION)
        self.timer.Hide()

    def Startup(self, slimItem, ball = None, transform = None):
        InSpaceBracket.Startup(self, slimItem, ball=ball, transform=transform)
        self.Update()

    def Showing(self):
        return self.sr.selection is not None and self.sr.selection.display

    def Select(self, status):
        if bool(status) != self.Showing():
            InSpaceBracket.Select(self, status)
            self.Update()

    def GetDocked(self):
        if self.IsVisible():
            return self.slimItem.docked or 0

    def OnSlimItemChange(self, oldSlim, newSlim):
        self.slimItem = newSlim
        self.Update()

    def Update(self):
        self.SetSubLabelCallback(self.UpdateLabel)
        self.UpdateTimer()

    def UpdateLabel(self):
        if not self.slimItem.state or not self.IsVisible():
            return
        label = self.GetStateLabel()
        if self.slimItem.timer:
            start, end, paused = self.slimItem.timer
            remaining = max(end - (paused or blue.os.GetWallclockTime()), 0L)
            label = u'{state}: {time} {paused} {unanchoring}'.format(state=self.GetStateLabel(), time=localization.formatters.FormatTimeIntervalShortWritten(remaining, showFrom='day', showTo='second'), paused=localization.GetByLabel('UI/Structures/States/Paused') if paused else '', unanchoring=localization.GetByLabel('UI/Structures/States/Unanchoring') if self.slimItem.unanchoring else '')
        elif self.slimItem.unanchoring:
            label = u'{state}: {unanchoring}'.format(state=self.GetStateLabel(), unanchoring=localization.GetByLabel('UI/Structures/States/Unanchoring'))
        if self.slimItem.upkeepState == structures.UPKEEP_STATE_LOW_POWER:
            if self.slimItem.state not in structures.OFFLINE_STATES:
                label += ' %s' % localization.GetByLabel('UI/Structures/States/LowPower')
        elif self.slimItem.upkeepState == structures.UPKEEP_STATE_ABANDONED:
            label += ' %s' % localization.GetByLabel('UI/Structures/States/Abandoned')
        if 'deedState' in self.slimItem.__dict__ and not self.slimItem.deedState:
            label += ' %s' % localization.GetByLabel('UI/Structures/States/DeedAbsent')
        return label

    def GetStateLabel(self):
        label = ''
        if self.slimItem.state == structures.STATE_DEPLOY_VULNERABLE:
            label = localization.GetByLabel('UI/Structures/States/Deploying')
            if self.slimItem.deployTimes is not None:
                start, end = self.slimItem.deployTimes
                if start and end:
                    remaining = max(end - blue.os.GetWallclockTime(), 0L)
                    if remaining > 0:
                        label = localization.GetByLabel('UI/Structures/States/TimeUntilDeployed', time=localization.formatters.FormatTimeIntervalShortWritten(remaining, showFrom='day', showTo='second'))
            if self.slimItem.repairing is not None:
                label += ' - %s' % localization.GetByLabel('UI/Structures/States/Repairing')
        elif self.slimItem.repairing is not None:
            if self.slimItem.state == structures.STATE_ANCHOR_VULNERABLE:
                label = localization.GetByLabel('UI/Structures/States/AnchorPreparing')
            else:
                label = localization.GetByLabel('UI/Structures/States/Repairing')
        elif self.slimItem.state:
            label = localization.GetByLabel(structures.STATE_LABELS[self.slimItem.state])
        return label

    def UpdateTimer(self):
        if self.destroyed:
            return None
        visible = self.IsVisible()
        start, end, paused = self.slimItem.timer or (0, 0, None)
        validTime = start and end and bool(int(end - start))
        if validTime:
            self.timer.SetExpiryTime(end, end - start, paused)
        if self.slimItem.state:
            self.timer.SetTimerColor(structures.STATE_COLOR.get(self.slimItem.state, (1, 1, 1, 1)))
        if validTime and (self.IsSelectedOrHilted() or self.slimItem.damage) and visible:
            self.timer.Show()
        else:
            self.timer.Hide()
        if self.slimItem.damage and visible:
            self.damage.Show()
            self.damage.SetDamage(self.slimItem.damage)
        else:
            self.damage.Hide()

    def IsVisible(self):
        return sm.GetService('michelle').IsBallVisible(self.itemID)
