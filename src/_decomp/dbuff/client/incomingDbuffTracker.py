#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dbuff\client\incomingDbuffTracker.py
import signals

class IncomingDbuffTracker(object):
    __notifyevents__ = ['OnSessionChanged']
    incomingDbuffs = {}
    signalOnDbuffStateUpdate = None

    def __init__(self):
        sm.RegisterNotify(self)
        self.signalOnDbuffStateUpdate = signals.Signal(signalName='signalOnDbuffStateUpdate')
        self._ResetState()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'shipid' in change or 'locationid' in change or 'structureid' in change:
            self._ResetState()

    def OnDbuffUpdated(self, shipID, dbuffState):
        if shipID != session.shipid:
            return
        if dbuffState:
            self._SetIncomingBuffs({dbuffCollectionID:(value, expiryTime) for dbuffCollectionID, (value, expiryTime) in dbuffState})
        else:
            self._ResetState()

    def _ResetState(self):
        self._SetIncomingBuffs({})

    def _SetIncomingBuffs(self, state):
        self.incomingDbuffs = state
        self.signalOnDbuffStateUpdate()
