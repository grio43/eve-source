#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\crimewatch.py
from __future__ import absolute_import
from .base import Event
import crimewatch.const as cwConst

class NpcCombatStateChanged(Event):
    atom_id = 59
    __notifyevents__ = ['OnNpcTimerUpdate']

    def OnNpcTimerUpdate(self, state, expiry_time):
        self.invoke(state=state)


class NpcCombatStarted(Event):
    atom_id = 60
    __notifyevents__ = ['OnNpcTimerUpdate']

    def OnNpcTimerUpdate(self, state, expiry_time):
        if state == cwConst.npcTimerStateActive:
            self.invoke()


class NpcCombatEnded(Event):
    atom_id = 61
    __notifyevents__ = ['OnNpcTimerUpdate']

    def OnNpcTimerUpdate(self, state, expiry_time):
        if state == cwConst.npcTimerStateTimer:
            self.invoke()
