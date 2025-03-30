#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\buffBarContainer.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.inflight.shipHud.buffButtons import BuffSlotParent
from eve.client.script.ui.inflight.shipHud.systemWideEffectsContainer import SystemWideEffectsContainer
from eve.common.script.mgt import buffBarConst
from eve.common.script.mgt.buffBarConst import ADD_GENERIC_BUFFBAR_BUTTON_SIGNAL, REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL
from eve.common.script.sys.eveCfg import IsControllingStructure
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import uthread2

class BuffBarContainer(ContainerAutoSize):
    __guid__ = 'uicls.BuffBarContainer'
    default_width = 500
    default_height = 5
    default_name = 'buffBarContainer'
    default_state = uiconst.UI_PICKCHILDREN
    uniqueUiName = pConst.UNIQUE_NAME_EFFECTS_BAR
    __notifyevents__ = ['OnEwarStartFromTactical',
     'OnEwarEndFromTactical',
     'OnAddFX',
     'OnRemoveFX',
     'OnRefreshBuffBar']

    def ApplyAttributes(self, attributes):
        setattr(self, pConst.ALLOWS_POINTER_CLIPPING, True)
        self.pending = False
        self.busyRefreshing = False
        super(BuffBarContainer, self).ApplyAttributes(attributes)
        self.genericBuffBarButtons = set()
        ADD_GENERIC_BUFFBAR_BUTTON_SIGNAL.connect(self.OnAddGenericBuffBarButton)
        REMOVE_GENERIC_BUFFBAR_BUTTON_SIGNAL.connect(self.OnRemoveGenericBuffBarButton)
        self.btnParByEffectType = {}
        self.CreateAllButtons()
        self.RefreshAllButtonDisplay(doAnimate=False)
        incomingDbuffTracker = sm.GetService('dbuffClient').incomingDbuffTracker
        incomingDbuffTracker.signalOnDbuffStateUpdate.connect(self.OnDbuffStateUpdate)
        incomingDotWeaponTracker = sm.GetService('dotWeaponSvc').incomingDotTracker
        incomingDotWeaponTracker.signalOnDotWeaponUpdate.connect(self.OnDotWeaponUpdate)
        sm.RegisterNotify(self)

    def Close(self):
        incomingDbuffTracker = sm.GetService('dbuffClient').incomingDbuffTracker
        incomingDbuffTracker.signalOnDbuffStateUpdate.disconnect(self.OnDbuffStateUpdate)
        incomingDotWeaponTracker = sm.GetService('dotWeaponSvc').incomingDotTracker
        incomingDotWeaponTracker.signalOnDotWeaponUpdate.disconnect(self.OnDotWeaponUpdate)
        sm.UnregisterNotify(self)
        super(BuffBarContainer, self).Close()

    def CreateAllButtons(self):
        self.Flush()
        self.systemEffectsCont = SystemWideEffectsContainer(parent=self, idx=0, align=uiconst.TOLEFT, height=40)
        for jammingType, graphicID in buffBarConst.BUFF_SLOT_ICONS.iteritems():
            self.btnParByEffectType[jammingType] = BuffSlotParent(name=jammingType, parent=self, effectType=jammingType, graphicID=graphicID)

    def OnAddGenericBuffBarButton(self, effectName):
        if effectName not in self.genericBuffBarButtons:
            self.genericBuffBarButtons.add(effectName)
            self.RefreshAllButtonDisplay()

    def OnRemoveGenericBuffBarButton(self, effectName):
        if effectName in self.genericBuffBarButtons:
            self.genericBuffBarButtons.remove(effectName)
            self.RefreshAllButtonDisplay()

    def OnAddFX(self, effectGuid, ballID):
        if ballID == session.shipid and effectGuid in buffBarConst.FX_GUIDS_THAT_UPDATE_BUFF_BAR:
            self.RefreshAllButtonDisplay()

    def OnRemoveFX(self, effectGuid, ballID):
        if ballID == session.shipid and effectGuid in buffBarConst.FX_GUIDS_THAT_UPDATE_BUFF_BAR:
            self.RefreshAllButtonDisplay()

    def OnEwarStartFromTactical(self):
        self.RefreshAllButtonDisplay()

    def OnEwarEndFromTactical(self, jammingType = None, ewarId = None):
        self.RefreshAllButtonDisplay()
        if jammingType and ewarId:
            self.RemoveTimer(jammingType, ewarId)

    def OnRefreshBuffBar(self):
        self.RefreshAllButtonDisplay(False)

    def StartTimer(self, jammingType, _id, duration, *args):
        btnPar = self.btnParByEffectType.get(jammingType, None)
        if btnPar and btnPar.btn:
            timer = btnPar.btn.GetTimer(_id)
            timer.StartTimer(duration)

    def RemoveTimer(self, jammingType, _id):
        btnPar = self.btnParByEffectType.get(jammingType, None)
        if btnPar and btnPar.btn:
            btnPar.btn.RemoveTimer(_id)

    def RefreshAllButtonDisplay(self, doAnimate = True):
        if self.busyRefreshing:
            self.pending = True
            return
        self.pending = False
        self.busyRefreshing = True
        try:
            jammersByType = sm.GetService('tactical').jammersByJammingType
            myShipEffectGuids = sm.GetService('FxSequencer').GetAllBallActivationNames(session.shipid)
            if IsControllingStructure():
                myShipEffectGuids.discard(buffBarConst.FX_GUIDS_BY_SLOT[buffBarConst.Slot_Tethering])
            incomingDbuffTracker = sm.GetService('dbuffClient').incomingDbuffTracker
            incomingDotTracker = sm.GetService('dotWeaponSvc').incomingDotTracker
            for effectType, btnPar in self.btnParByEffectType.iteritems():
                btnPar.UpdateVisibility(jammersByType, myShipEffectGuids, incomingDbuffTracker, incomingDotTracker, self.genericBuffBarButtons, doAnimate)
                btnPar.UpdateDbuffTimer(incomingDbuffTracker)
                btnPar.UpdateDotTimer(incomingDotTracker)

        finally:
            self.busyRefreshing = False

        if self.pending:
            self.RefreshAllButtonDisplay(doAnimate)

    def OnDbuffStateUpdate(self):
        uthread2.StartTasklet(self.RefreshAllButtonDisplay)

    def OnDotWeaponUpdate(self):
        uthread2.StartTasklet(self.RefreshAllButtonDisplay)
