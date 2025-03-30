#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\essContentCard.py
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetESSBountyColor
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from localization import GetByLabel

class ESSContentCard(BaseContentCard):
    default_name = 'ESSContentCard'

    def Update(self):
        super(ESSContentCard, self).Update()
        self.UpdateReserveBankAmountLabel()
        self.UpdateMainBankAmountLabel()
        self.UpdateReserveBankFrame()
        self.UpdateBountiesOutputLabel()
        self.UpdateReserveBankLockIcon()

    def ConstructBottomCont(self):
        pass

    def ConstructContent(self):
        self.ConstructBankAmountContainer()
        self.ConstructTitleLabel()
        self.ConstructSubtitleLabel()
        self.ConstructMainBankAmountContainer()
        self.ConstructReserveBankAmountContainer()
        self.ConstructBountiesOutputLabel()
        self.ConstructBankLockIcon()

    def ConstructBountiesOutputLabel(self):
        self.bountiesOutputLabel = EveLabelLarge(name='bountiesOutputLabel', parent=self, align=uiconst.TOPRIGHT, top=4, left=4)

    def ConstructBankAmountContainer(self):
        self.bankAmountContainer = Container(name='bankAmountContainer', parent=self, padTop=-3)

    def ConstructMainBankAmountContainer(self):
        self.mainBankAmountContainer = Container(name='mainBankAmountContainer', parent=self.bankAmountContainer, align=uiconst.TOLEFT_PROP, width=0.45, padding=(0, 0, 4, 0))
        EveLabelMedium(parent=self.mainBankAmountContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/ESS/MainBank'))
        mainBankAmountLabelContainer = Container(name='mainBankAmountLabelContainer', parent=self.mainBankAmountContainer, padding=(0, 0, 0, 5))
        self.mainBankAmountLabel = EveLabelMedium(parent=mainBankAmountLabelContainer, align=uiconst.CENTER, left=5, top=-1)
        Frame(bgParent=mainBankAmountLabelContainer, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=agencyUIConst.COLOR_BG)

    def ConstructReserveBankAmountContainer(self):
        self.reserveBankAmountContainer = Container(name='reserveBankAmountContainer', parent=self.bankAmountContainer, align=uiconst.TORIGHT_PROP, width=0.55, padding=(4, 0, 4, 4))
        Frame(bgParent=self.reserveBankAmountContainer, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=agencyUIConst.COLOR_BG, opacity=0.3)
        EveLabelMedium(parent=self.reserveBankAmountContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/ESS/ReserveBank'), maxLines=1, left=5)
        reserveBankAmountLabelContainer = Container(name='reserveBankAmountLabelContainer', parent=self.reserveBankAmountContainer, padding=(5, 0, 0, 3))
        self.reserveBankAmountLabel = EveLabelMedium(parent=reserveBankAmountLabelContainer, align=uiconst.CENTER)
        self.reserveBankFrame = Frame(bgParent=reserveBankAmountLabelContainer, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=(1.0, 1.0, 1.0, 0.5))

    def ConstructBankLockIcon(self):
        self.reserveBankLockIcon = Sprite(name='reserveBankLockIcon', parent=Container(parent=self.reserveBankAmountContainer, align=uiconst.TORIGHT, width=20, left=2, idx=0), align=uiconst.CENTER, width=20, height=20, hint=GetByLabel('UI/Agency/ESS/ReserveBankUnlocked'))

    def UpdateReserveBankAmountLabel(self):
        self.reserveBankAmountLabel.SetText('%s %s' % (FmtAmt(self.contentPiece.reserveBankAmount, fmt='sn'), GetByLabel('UI/Wallet/WalletWindow/ISK')))

    def UpdateMainBankAmountLabel(self):
        self.mainBankAmountLabel.SetText('%s %s' % (FmtAmt(self.contentPiece.mainBankAmount, fmt='sn'), GetByLabel('UI/Wallet/WalletWindow/ISK')))

    def UpdateReserveBankFrame(self):
        if self.contentPiece.reserveBankUnlocked:
            color = agencyConst.ESS_HIGH_PAYOUT_COLOR
        else:
            color = agencyConst.ESS_LOW_PAYOUT_COLOR
        self.reserveBankFrame.SetRGBA(*color)
        self.reserveBankFrame.SetAlpha(0.75)

    def UpdateReserveBankLockIcon(self):
        if self.contentPiece.reserveBankUnlocked:
            texturePath = 'res:/UI/Texture/classes/agency/Icon_unlock.png'
            hint = GetByLabel('UI/Agency/ESS/ReserveBankUnlocked')
        else:
            texturePath = 'res:/UI/Texture/classes/agency/Icon_lock.png'
            hint = GetByLabel('UI/Agency/ESS/ReserveBankLocked')
        self.reserveBankLockIcon.SetHint(hint)
        self.reserveBankLockIcon.SetTexturePath(texturePath)

    def UpdateBountiesOutputLabel(self):
        bountiesOutput = self.contentPiece.bountiesOutput
        self.bountiesOutputLabel.SetText('%s%%' % (round(bountiesOutput, 4) * 100))
        dynamicResourceSettings = self.contentPiece.GetDynamicResourceSettings()
        newColor = self.GetBountyColor(bountiesOutput, dynamicResourceSettings)
        self.bountiesOutputLabel.SetRGBA(*newColor)

    def GetBountyColor(self, bountiesOutput, dynamicResourceSettings):
        minBountyOutput = dynamicResourceSettings['minOutput']
        maxBountyOutput = dynamicResourceSettings['maxOutput']
        equilibriumValue = dynamicResourceSettings['equilibriumValue']
        return GetESSBountyColor(minBountyOutput, maxBountyOutput, equilibriumValue, bountiesOutput)
