#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\skyhookTheftUI\infoPanelSkyhookTheft.py
import localization
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from spacecomponents.common.components.linkWithShip import LINKSTATE_IDLE, LINKSTATE_RUNNING, LINKSTATE_DISABLED
from eve.client.script.ui.shared.infoPanels.skyhookTheftUI.infoPanelSkyhookTheftTimerContainer import InfoPanelSkyhookTheftTimerContainer
from spacecomponents.common.componentConst import SKYHOOK_REAGENT_SILO, ORBITAL_SKYHOOK
import eveicon
import logging
log = logging.getLogger(__name__)

class InfoPanelSkyhookTheft(InfoPanelBase):
    default_name = 'InfoPanelSkyhookTheft'
    panelTypeID = infoPanelConst.PANEL_SKYHOOK_THEFT
    label = 'UI/OrbitalSkyhook/SkyhookInfoPanel/SkyhookTheftTitle'
    default_iconTexturePath = eveicon.reagents_skyhook
    default_isModeFixed = False
    hasSettings = False
    isAvailable = True
    __notifyevents__ = InfoPanelBase.__notifyevents__ + ['OnLinkedWithShipSiloItemUpdated']

    @staticmethod
    def IsAvailable():
        skyhookSvc = sm.GetService('skyhookSvc')
        return skyhookSvc.HasOnGoingTheft()

    def ApplyAttributes(self, attributes):
        super(InfoPanelSkyhookTheft, self).ApplyAttributes(attributes)
        self.titleCaption = EveCaptionSmall(parent=self.headerCont, text=localization.GetByLabel('UI/OrbitalSkyhook/SkyhookInfoPanel/SkyhookTheftTitle'), align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        self.bodyCont = ContainerAutoSize(name='bodyCont', align=uiconst.TOTOP, parent=self.mainCont)
        self.collapsedStateCont = None
        self.onGoingTheftItems = {}
        self.skyhookSvc = sm.GetService('skyhookSvc')
        self.onGoingTheft = self.skyhookSvc.GetOnGoingTheft()
        for theft, timeValues in self.onGoingTheft.iteritems():
            self.CreateNewTheftTimerItem(theft, timeValues[0], timeValues[1])

    def ConstructHeaderButton(self):
        ButtonIcon(parent=self.headerBtnCont, align=uiconst.TOPRIGHT, pos=(0,
         0,
         self.topCont.height,
         self.topCont.height), texturePath=self.default_iconTexturePath, iconSize=18, showIcon=True)

    def OnLinkedWithShipSiloItemUpdated(self, itemID, solarsystemID, completeAtTime, state, duration):
        if solarsystemID != session.solarsystemid2:
            return
        if state in (LINKSTATE_IDLE, LINKSTATE_DISABLED):
            theftContainer = self.onGoingTheftItems.get(itemID, None)
            if theftContainer:
                if completeAtTime is not None:
                    theftContainer.LinkSuccess()
                else:
                    theftContainer.LinkFailed()
                self.onGoingTheftItems.pop(itemID)
                self.skyhookSvc.UpdatePanelContainer()
        elif state == LINKSTATE_RUNNING:
            startTime = completeAtTime - duration
            self.CreateNewTheftTimerItem(itemID, startTime, completeAtTime)

    def CreateNewTheftTimerItem(self, itemID, startTime, endTime):
        ballpark = sm.GetService('michelle').GetBallpark()
        siloComponent = ballpark.componentRegistry.GetComponentForItem(itemID, SKYHOOK_REAGENT_SILO)
        skyhookComponent = ballpark.componentRegistry.GetComponentForItem(siloComponent.skyhookID, ORBITAL_SKYHOOK)
        planetName = cfg.evelocations.Get(skyhookComponent.planetID).name
        timerItem = InfoPanelSkyhookTheftTimerContainer(parent=self.bodyCont, name='skyhookTheftTimer', padTop=13, startTime=startTime, endTime=endTime, planetName=planetName)
        self.onGoingTheftItems[itemID] = timerItem

    def ConstructHiddenCollpsedState(self):
        if self.collapsedStateCont and not self.collapsedStateCont.destroyed:
            self.collapsedStateCont.Flush()
        else:
            self.collapsedStateCont = ContainerAutoSize(parent=self.headerCont, align=uiconst.TOLEFT)
        if self.mode != infoPanelConst.MODE_COMPACT:
            self.collapsedStateCont.Hide()

    def ConstructCompact(self):
        if self.collapsedStateCont:
            self.collapsedStateCont.Show()

    def ConstructNormal(self):
        if self.collapsedStateCont:
            self.collapsedStateCont.Hide()
