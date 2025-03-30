#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracketsAndTargets\skyhookBracket.py
import blue
import localization
from eve.client.script.spacecomponents.activatecontroller import ActivateCounterController
from eve.client.script.ui.inflight.bracketsAndTargets.inSpaceBracket import InSpaceBracket
from eve.client.script.ui.control.countdownTimer import CountdownTimer, TIMER_RUNNING_OUT_NO_ANIMATION
from eve.client.script.ui.control.damageRing import DamageRing
import orbitalSkyhook.const as reinforceConst

class SkyhookBracket(InSpaceBracket):

    def ApplyAttributes(self, attributes):
        InSpaceBracket.ApplyAttributes(self, attributes)
        self.damage = DamageRing(name='DamageRing', parent=self)
        self.skyhookTimer = CountdownTimer(name='StructureCounter', parent=self, countsDown=True, timerFunc=blue.os.GetWallclockTime, timerRunningOutAnimation=TIMER_RUNNING_OUT_NO_ANIMATION)
        self.skyhookTimer.Hide()

    def Startup(self, slimItem, ball = None, transform = None):
        InSpaceBracket.Startup(self, slimItem, ball=ball, transform=transform)
        self.Update()

    def Showing(self):
        return self.sr.selection is not None and self.sr.selection.display

    def Select(self, status):
        if bool(status) != self.Showing():
            InSpaceBracket.Select(self, status)
            self.Update()

    def OnSlimItemChange(self, oldSlim, newSlim):
        self.slimItem = newSlim
        self.Update()

    def Update(self):
        self.SetSubLabelCallback(self.UpdateLabel)
        self.UpdateTimer()

    def UpdateLabel(self):
        if not self.slimItem.skyhook_state or not self.IsVisible():
            return
        labelList = []
        if self.slimItem.component_activate:
            isActive, activeTimestamp = self.slimItem.component_activate
            if not isActive:
                if activeTimestamp:
                    remaining = max(activeTimestamp - blue.os.GetWallclockTime(), 0L)
                else:
                    remaining = 0
                text = '%s: %s' % (localization.GetByLabel('UI/Structures/States/Onlining'), localization.formatters.FormatTimeIntervalShortWritten(remaining, showFrom='day', showTo='second'))
                labelList.append(text)
        if self.slimItem.skyhook_timer:
            start, end, paused = self.slimItem.skyhook_timer
            remaining = max(end - (paused or blue.os.GetWallclockTime()), 0L)
            stateLabel = u'{state}: {time} {paused}'.format(state=self.GetStateLabel(), time=localization.formatters.FormatTimeIntervalShortWritten(remaining, showFrom='day', showTo='second'), paused=localization.GetByLabel('UI/Structures/States/Paused') if paused else '')
        else:
            stateLabel = self.GetStateLabel()
        labelList.append(stateLabel)
        label = '<br>'.join(labelList)
        return label

    def GetStateLabel(self):
        label = ''
        if self.slimItem.skyhook_repairing is not None:
            label = localization.GetByLabel('UI/Structures/States/Repairing')
        elif self.slimItem.skyhook_state:
            label = localization.GetByLabel(reinforceConst.STATE_LABELS[self.slimItem.skyhook_state])
        return label

    def UpdateTimer(self):
        if self.destroyed:
            return None
        visible = self.IsVisible()
        start, end, paused = self.slimItem.skyhook_timer or (0, 0, None)
        validTime = start and end and bool(int(end - start))
        if validTime:
            self.skyhookTimer.SetExpiryTime(end, end - start, paused)
        if self.slimItem.skyhook_state:
            self.skyhookTimer.SetTimerColor(reinforceConst.STATE_COLOR.get(self.slimItem.skyhook_state, (1, 1, 1, 1)))
        if validTime and (self.IsSelectedOrHilted() or self.slimItem.skyhook_damage) and visible:
            self.skyhookTimer.Show()
        else:
            self.skyhookTimer.Hide()
        if self.slimItem.skyhook_damage and visible:
            self.damage.Show()
            self.damage.SetDamage(self.slimItem.skyhook_damage)
        else:
            self.damage.Hide()
        self.ResizeActivationTimer()

    def ResizeActivationTimer(self):
        activationController = self.GetCounterControllerForClass(ActivateCounterController)
        if not activationController or not activationController.timer:
            return
        if self.skyhookTimer.display:
            activationController.timer.scale = (1.4, 1.4)
        else:
            activationController.timer.scale = (1.0, 1.0)

    def IsVisible(self):
        return sm.GetService('michelle').IsBallVisible(self.itemID)
