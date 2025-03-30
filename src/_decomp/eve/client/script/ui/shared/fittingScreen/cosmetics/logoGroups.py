#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\cosmetics\logoGroups.py
import evelink
import localization
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.infoNotice import InfoNotice
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst as agencyContentGroupConst
from eve.client.script.ui.shared.fittingScreen.cosmetics.logoEntries import AllianceLogoEntry, CorporationLogoEntry, FRAME_PADDING
from localization import GetByLabel

class LogoGroup(ContainerAutoSize):
    default_labelText = ''
    default_padLeft = 8
    default_padRight = 16
    default_padBottom = 18

    def ApplyAttributes(self, attributes):
        super(LogoGroup, self).ApplyAttributes(attributes)
        self.labelText = attributes.get('labelText', self.default_labelText)
        self._errorCallback = attributes.errorCallback
        self.ConstructLayout()

    def ConstructLayout(self):
        self.label = EveLabelMedium(name='label', parent=self, align=uiconst.TOTOP, text=self.labelText, padding=(FRAME_PADDING,
         0,
         FRAME_PADDING,
         10), opacity=0.7)
        self.notice = InfoNotice(name='notice', parent=self, align=uiconst.TOTOP, padding=(FRAME_PADDING,
         0,
         FRAME_PADDING,
         0), display=False)
        self.entryContainer = ContainerAutoSize(name='entryContainer', parent=self, align=uiconst.TOTOP, padding=(FRAME_PADDING,
         0,
         FRAME_PADDING,
         0))

    def UpdateLayout(self, logoData):
        pass

    def _GetEmblemNotPurchasedText(self):
        link = evelink.local_service_link(text=localization.GetByLabel('UI/Agents/ParagonAgent'), method='AgencyOpenAndShow', contentGroupID=agencyContentGroupConst.contentGroupMissionAgentsHeraldry)
        return GetByLabel('UI/ShipCosmetics/EmblemNotPurchased', link=link)


class AllianceLogoGroup(LogoGroup):
    default_labelText = GetByLabel('UI/ShipCosmetics/AvailableAllianceEmblems')

    def ConstructLayout(self):
        super(AllianceLogoGroup, self).ConstructLayout()
        self.entry = AllianceLogoEntry(parent=self.entryContainer, align=uiconst.TOTOP, errorCallback=self._errorCallback)

    def UpdateLayout(self, logoData):
        super(AllianceLogoGroup, self).UpdateLayout(logoData)
        self.notice.display = self.UpdateNotice(logoData)
        self.entry.logoData = logoData

    def UpdateNotice(self, logoData):
        if not logoData.existence.alliance:
            self.notice.labelText = GetByLabel('UI/ShipCosmetics/EmblemNotReleased')
            return True
        if eve.session.allianceid:
            if not logoData.eligibility.alliance:
                self.notice.labelText = self._GetEmblemNotPurchasedText()
                return True
        else:
            if logoData.eligibility.alliance:
                self.notice.labelText = GetByLabel('UI/ShipCosmetics/EmblemNoAllianceEligible')
            else:
                self.notice.labelText = GetByLabel('UI/ShipCosmetics/EmblemNoAllianceNotEligible')
            return True
        return False


class CorporationLogoGroup(LogoGroup):
    default_labelText = (GetByLabel('UI/ShipCosmetics/AvailableCorporationEmblems'),)

    def ConstructLayout(self):
        super(CorporationLogoGroup, self).ConstructLayout()
        self.entry = CorporationLogoEntry(parent=self.entryContainer, align=uiconst.TOTOP, errorCallback=self._errorCallback)

    def UpdateLayout(self, logoData):
        super(CorporationLogoGroup, self).UpdateLayout(logoData)
        self.notice.display = self.UpdateNotice(logoData)
        self.entry.logoData = logoData

    def UpdateNotice(self, logoData):
        if not logoData.existence.corporation:
            self.notice.labelText = GetByLabel('UI/ShipCosmetics/EmblemNotReleased')
            return True
        if not logoData.eligibility.corporation:
            self.notice.labelText = self._GetEmblemNotPurchasedText()
            return True
        return False
