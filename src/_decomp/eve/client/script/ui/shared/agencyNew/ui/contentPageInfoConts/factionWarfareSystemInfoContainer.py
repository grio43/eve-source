#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\factionWarfareSystemInfoContainer.py
from carbonui.control.scrollContainer import ScrollContainer
from eve.common.lib import appConst
import inventorycommon.const as invConst
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.agencyNew.contentPieces.controlBunkerContentPiece import ControlBunkerContentPiece
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.jobInfoContainer import JobContentPageInfoContainer
from eve.client.script.ui.shared.factionalWarfare.fwSystemBenefitIcon import FWSystemBenefitIcon
from jobboard.client import get_factional_warfare_job
from localization import GetByLabel
ICON_SIZE = 64
LABEL_WIDTH = 220

class FactionWarfareSystemInfoContainer(JobContentPageInfoContainer):
    default_name = 'FactionWarfareSystemInfoContainer'
    default_scroll_container_height = 110
    default_headerText = GetByLabel('UI/Agency/FactionWarfare/sitesInSystem')
    __notifyevents__ = ['OnClientEvent_DestinationSet']

    def __init__(self, *args, **kwargs):
        super(FactionWarfareSystemInfoContainer, self).__init__(*args, **kwargs)
        sm.RegisterNotify(self)

    def Close(self):
        sm.UnregisterNotify(self)
        super(FactionWarfareSystemInfoContainer, self).Close()

    def ConstructScrollEntries(self, contentPieces):
        super(FactionWarfareSystemInfoContainer, self).ConstructScrollEntries(contentPieces)
        if session.solarsystemid and session.solarsystemid == self.contentPiece.solarSystemID:
            self.AddInfrastructureHubToScroll()

    def AddInfrastructureHubToScroll(self):
        ballpark = sm.GetService('michelle').GetBallpark(doWait=True)
        if ballpark is None:
            return
        controlBunkerID = sm.GetService('facwar').facWarMgr.GetControlBunkerIDInSystem()
        controlBunkerItem = ballpark.GetInvItem(controlBunkerID)
        if not controlBunkerItem:
            return
        controlBunkerBall = ballpark.GetBall(controlBunkerID)
        controlBunkerContentPiece = ControlBunkerContentPiece(solarSystemID=self.contentPiece.solarSystemID, typeID=controlBunkerItem.typeID, itemID=controlBunkerID, slimItem=controlBunkerItem, ball=controlBunkerBall)
        self.ConstructScrollEntry(controlBunkerContentPiece)

    def ConstructLayout(self):
        self.ConstructOccupierContainer()
        self.ConstructSystemLevelContainer()
        self.ConstructScroll()

    def ConstructScroll(self):
        scrollParent = Container(name='scrollParent', parent=self, top=10)
        self.scrollCont = ScrollContainer(name='scrollCont', parent=scrollParent, align=uiconst.TOALL, showUnderlay=True)
        self.scrollLoadingWheel = LoadingWheel(name='infoContLoadingWheel', parent=scrollParent, align=uiconst.CENTER)

    def ConstructSystemLevelContainer(self):
        systemLevelContainer = ContainerAutoSize(name='systemLevelContainer', parent=self, align=uiconst.TOTOP)
        progressGaugeLabelCont = Container(name='progressGaugeLabelCont', parent=systemLevelContainer, align=uiconst.TOTOP, height=20, top=5)
        self.currentLPInSystemLabel = EveLabelMedium(name='currentLPInSystemLabel', parent=progressGaugeLabelCont, align=uiconst.CENTERLEFT)
        self.LPNeededForNextSystemUpgradeLabel = EveLabelMedium(name='LPNeededForNextSystemUpgradeLabel', parent=progressGaugeLabelCont, align=uiconst.CENTERRIGHT)
        self.systemUpgradeProgressGauge = Gauge(name='systemUpgradeProgressGauge', parent=systemLevelContainer, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        systemBenefitsContainer = Container(name='systemBenefitsContainer', parent=systemLevelContainer, align=uiconst.TOTOP, height=42, top=10)
        self.currentBenefitsIconCont = ContainerAutoSize(name='currentBenefitsIconCont', parent=systemBenefitsContainer, align=uiconst.TOLEFT)
        self.nextBenefitsIconCont = ContainerAutoSize(name='nextBenefitsIconCont', parent=systemBenefitsContainer, align=uiconst.TORIGHT)

    def ConstructOccupierContainer(self):
        occupierContainer = Container(name='occupierContainer', parent=self, align=uiconst.TOTOP, height=ICON_SIZE)
        occupierIconContainer = Container(name='occupierIconContainer', parent=occupierContainer, align=uiconst.TOLEFT, width=ICON_SIZE)
        self.occupierIcon = OwnerIcon(name='occupierIcon', parent=occupierIconContainer, align=uiconst.TOALL)
        occupierLabelContainer = Container(name='occupierLabelContainer', parent=occupierContainer, align=uiconst.TOALL, left=10)
        labelCont = ContainerAutoSize(parent=occupierLabelContainer, align=uiconst.CENTERLEFT, width=LABEL_WIDTH)
        self.adjacencyLabel = EveLabelMedium(name='adjacencyLabel', parent=labelCont, align=uiconst.TOTOP)
        self.occupierNameLabel = EveLabelMedium(name='occupierNameLabel', parent=labelCont, align=uiconst.TOTOP, width=LABEL_WIDTH, state=uiconst.UI_NORMAL)
        self.systemStatusLabel = EveLabelMedium(name='systemStatusLabel', parent=labelCont, align=uiconst.TOTOP, width=LABEL_WIDTH, state=uiconst.UI_NORMAL)
        self.systemLevelLabel = EveLabelMedium(name='systemLevelLabel', parent=labelCont, align=uiconst.TOTOP)

    def _UpdateContentPiece(self, contentPiece):
        super(FactionWarfareSystemInfoContainer, self)._UpdateContentPiece(contentPiece)
        self.UpdateOccupierIcon()
        self.UpdateOccupierNameLabel()
        self.UpdateSystemStatusLabel()
        self.UpdateSystemLevelContainer()
        self.UpdateSystemBenefitsIcons()
        self.UpdateAdjacencyLabel()

    def UpdateSystemLevelContainer(self):
        self.systemLevelLabel.SetText(GetByLabel('UI/Agency/FactionWarfare/systemUpgradeLevel', level=self.contentPiece.GetSystemUpgradeLevel()))
        currentLPsInSystem = self.contentPiece.GetCurrentLPsInSystem()
        self.currentLPInSystemLabel.SetText(GetByLabel('UI/LPStore/AmountLP', lpAmount=FmtAmt(currentLPsInSystem)))
        LPsNeededForNextLevel = self.contentPiece.GetLPRequiredForNextSystemLevel()
        self.LPNeededForNextSystemUpgradeLabel.SetText(GetByLabel('UI/LPStore/AmountLP', lpAmount=FmtAmt(LPsNeededForNextLevel)))
        self.UpdateSystemUpgradeProgressGauge(currentLPsInSystem)

    def UpdateSystemBenefitsIcons(self):
        self.currentBenefitsIconCont.Flush()
        self.nextBenefitsIconCont.Flush()
        currentUpgradeLevel = self.contentPiece.GetSystemUpgradeLevel()
        currentBenefits = self.contentPiece.GetSystemUpgradeBenefitsForLevel(currentUpgradeLevel)
        for i, (benefitType, benefitValue) in enumerate(reversed(currentBenefits)):
            FWSystemBenefitIcon(parent=self.currentBenefitsIconCont, align=uiconst.TOLEFT, left=10 if i else 0, benefitType=benefitType, benefitValue=benefitValue, opacity=1.0, width=26)

        nextBenefits = self.contentPiece.GetSystemUpgradeBenefitsForLevel(level=currentUpgradeLevel + 1)
        for i, (benefitType, benefitValue) in enumerate(nextBenefits):
            FWSystemBenefitIcon(parent=self.nextBenefitsIconCont, align=uiconst.TORIGHT, benefitType=benefitType, benefitValue=benefitValue, opacity=0.5, width=26, left=10 if i else 0)

    def UpdateSystemUpgradeProgressGauge(self, currentLPsInSystem):
        LPsNeededForNextLevel = self.contentPiece.GetLPRequiredForNextSystemLevel()
        LPsNeededForLastLevel = self.contentPiece.GetLPRequiredForLastSystemLevel()
        LPsOverLastLevel = currentLPsInSystem - LPsNeededForLastLevel
        totalLPsNeededToUpgrade = LPsNeededForNextLevel - LPsNeededForLastLevel
        proportionAcquired = LPsOverLastLevel / float(totalLPsNeededToUpgrade)
        self.systemUpgradeProgressGauge.SetValueInstantly(max(0.0, min(proportionAcquired, 1.0)))
        if currentLPsInSystem < appConst.facwarSolarSystemMaxLPPool:
            progressGaugeHint = GetByLabel('UI/FactionWarfare/IHub/LevelUnlockHint', num=LPsOverLastLevel, numTotal=totalLPsNeededToUpgrade)
            self.systemUpgradeProgressGauge.SetHint(progressGaugeHint)

    def UpdateSystemStatusLabel(self):
        newStatusText = GetByLabel('UI/Agency/FactionWarfare/systemStatusLabel', systemStatusText=self.contentPiece.GetSystemStatusText(), color=Color.RGBtoHex(*self.contentPiece.GetSystemCaptureStatusColor()))
        self.systemStatusLabel.SetText(newStatusText)
        self.systemStatusLabel.SetHint(self.contentPiece.GetSystemCaptureStatusHint())

    def UpdateOccupierNameLabel(self):
        newText = GetByLabel('UI/Agency/FactionWarfare/systemOccupierLabel', factionID=self.contentPiece.ownerID, typeID=invConst.typeFaction)
        self.occupierNameLabel.SetText(newText)

    def UpdateOccupierIcon(self):
        self.occupierIcon.SetOwnerID(self.contentPiece.ownerID)

    def UpdateAdjacencyLabel(self):
        adjacencyText = self.contentPiece.GetAdjacencyText(longText=True)
        self.adjacencyLabel.SetText(adjacencyText)

    def GetEntryContentPieces(self):
        return self.contentPiece.contentPieces

    def _GetJob(self, instanceID):
        return get_factional_warfare_job(instanceID)

    def OnClientEvent_DestinationSet(self, *args, **kwargs):
        self.OnScrollEntryClicked(self.clickedEntry)
