#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\plexPanel.py
import carbonui.const as uiconst
import uthread
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLargeBold, EveLabelMediumBold
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.cloneGrade import ORIGIN_CHARACTERSHEET
from eve.client.script.ui.shared.cloneGrade.cloneStateIcon import CloneStateIcon
from eve.client.script.ui.shared.inventory.plexVault import Vault, PlexVaultActions, PlexVaultController
from eve.client.script.ui.shared.monetization.events import LogCharacterSheetPilotLicenseImpression
from eve.common.lib import appConst as const
from localization import GetByLabel
from fastcheckout.const import FROM_CHARACTER_SHEET

class PLEXPanel(Container):
    default_name = 'PLEXPanel'
    __notifyevents__ = ['OnMultipleCharactersTrainingRefreshed', 'OnSubscriptionTimeUpdateServer']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.isConstructed = False

    def LoadPanel(self, *args):
        self.ConstructLayout()
        self.multipleQueueLabel1.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueNotActive')
        self.multipleQueueLabel1.color = Color.GRAY5
        self.multipleQueueExpiryLabel1.state = uiconst.UI_HIDDEN
        self.multipleQueueIcon1.opacity = 0.3
        self.multipleQueueLabel2.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueNotActive')
        self.multipleQueueLabel2.color = Color.GRAY5
        self.multipleQueueExpiryLabel2.state = uiconst.UI_HIDDEN
        self.multipleQueueIcon2.opacity = 0.3
        for index, (trainingID, trainingExpiry) in enumerate(sorted(sm.GetService('skillqueue').GetMultipleCharacterTraining().iteritems())):
            if index == 0:
                self.multipleQueueLabel1.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueActive')
                self.multipleQueueLabel1.color = (0.0, 1.0, 0.0, 0.8)
                self.multipleQueueExpiryLabel1.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueExpires', expiryDate=trainingExpiry)
                self.multipleQueueExpiryLabel1.state = uiconst.UI_DISABLED
                self.multipleQueueIcon1.opacity = 1.0
            elif index == 1:
                self.multipleQueueLabel2.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueActive')
                self.multipleQueueLabel2.color = (0.0, 1.0, 0.0, 0.8)
                self.multipleQueueExpiryLabel2.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueExpires', expiryDate=trainingExpiry)
                self.multipleQueueExpiryLabel2.state = uiconst.UI_DISABLED
                self.multipleQueueIcon2.opacity = 1.0

        self.RefreshOmegaTime(self.GetOmegaTime())

    def ConstructLayout(self):
        if self.isConstructed:
            return
        self.isConstructed = True
        controller = PlexVaultController()
        Vault(parent=self, align=uiconst.TOTOP, controller=controller)
        scrollContainer = ScrollContainer(name='plexScroll', parent=self, align=uiconst.TOALL)
        scrollMainCont = ContainerAutoSize(parent=scrollContainer, align=uiconst.TOTOP, padding=(10, 10, 10, 10))
        PlexVaultActions(parent=scrollMainCont, align=uiconst.TOTOP, logContext=FROM_CHARACTER_SHEET, controller=controller)
        EveLabelLargeBold(parent=scrollMainCont, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/CloneState'), padding=(10, 25, 0, 0))
        EveLabelMedium(parent=scrollMainCont, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/PlexDescription'), padding=(10, 10, 0, 10), color=Color.GRAY5)
        subscription = ContainerAutoSize(parent=scrollMainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0, 0, 0, 0.3))
        self.subscriptionHeaderLabel = EveLabelLargeBold(parent=subscription, align=uiconst.TOTOP, text=None, padding=(75, 15, 0, 8))
        self.subscriptionDescriptionLabel = EveLabelMedium(parent=subscription, align=uiconst.TOTOP, text=None, padding=(75, 0, 0, 15))
        self.cloneState = CloneStateIcon(parent=subscription, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, pos=(10, 0, 55, 55), origin=ORIGIN_CHARACTERSHEET)
        EveLabelLargeBold(parent=scrollMainCont, align=uiconst.TOTOP, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/MultipleCharacterTitle'), padding=(10, 25, 0, 0))
        EveLabelMedium(parent=scrollMainCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/MultipleCharacterDescription', typeID=const.typeMultiTrainingToken), padding=(10, 2, 0, 10), color=Color.GRAY5)
        multipleQueue1 = ContainerAutoSize(parent=scrollMainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0, 0, 0, 0.3))
        self.multipleQueueLabel1 = EveLabelMediumBold(parent=multipleQueue1, align=uiconst.TOTOP, text='', padding=(35, 8, 0, 8))
        self.multipleQueueExpiryLabel1 = EveLabelMediumBold(parent=multipleQueue1, align=uiconst.TOPRIGHT, text='', pos=(10, 8, 0, 0), color=Color.GRAY5)
        self.multipleQueueIcon1 = Icon(parent=multipleQueue1, align=uiconst.TOPLEFT, icon='res:/UI/Texture/Icons/additional_training_queue.png', pos=(10, 7, 17, 17))
        multipleQueue2 = ContainerAutoSize(parent=scrollMainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0, 0, 0, 0.3))
        self.multipleQueueLabel2 = EveLabelMediumBold(parent=multipleQueue2, align=uiconst.TOTOP, text='', padding=(35, 8, 0, 8))
        self.multipleQueueExpiryLabel2 = EveLabelMediumBold(parent=multipleQueue2, align=uiconst.TOPRIGHT, text='', pos=(10, 8, 0, 0), color=Color.GRAY5)
        self.multipleQueueIcon2 = Icon(parent=multipleQueue2, align=uiconst.TOPLEFT, icon='res:/UI/Texture/Icons/additional_training_queue.png', pos=(10, 7, 17, 17))

    def OnMultipleCharactersTrainingRefreshed(self):
        if self.display:
            self.LoadPanel()

    def GetOmegaTime(self):
        return sm.RemoteSvc('subscriptionMgr').GetSubscriptionTime()

    def RefreshOmegaTime(self, omegaTime):
        if omegaTime:
            text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/CurrentCloneStateOmega')
            self.subscriptionHeaderLabel.SetText(text)
            text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/DaysLeft', expireDate=omegaTime)
            self.subscriptionDescriptionLabel.SetText(text)
        else:
            text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/CurrentCloneStateAlpha')
            self.subscriptionHeaderLabel.SetText(text)
            self.subscriptionDescriptionLabel.SetText(None)

    def OnSubscriptionTimeUpdateServer(self, omegaTime):
        if self.isConstructed:
            self.RefreshOmegaTime(omegaTime)


def LogOpenPilotLicense():
    uthread.new(LogCharacterSheetPilotLicenseImpression())
