#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\cosmetics\logos.py
from carbonui import const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.loadingContainer import LoadingContainer, LoadingSpriteSize
from eve.client.script.ui.shared.fittingScreen.cosmetics.logoGroups import AllianceLogoGroup, CorporationLogoGroup
from shipcosmetics.common.const import CosmeticsType
from shipcosmetics.client.fittingsgateway.fittingsSignals import on_ship_cosmetics_changed
from shipcosmetics.client.licensegateway.licenseSignals import on_ship_cosmetics_license_change
from localization import GetByLabel

class LogoSelectionPanel(Container):
    __notifyevents__ = ['ProcessActiveShipChanged', 'OnSessionChanged', 'OnCorporationChanged']

    def ApplyAttributes(self, attributes):
        self._fittingErrorCallback = attributes.fittingErrorCallback
        self.cosmeticController = attributes.controller
        super(LogoSelectionPanel, self).ApplyAttributes(attributes)
        self.loadingCont = None
        self._ConstructContents()
        sm.RegisterNotify(self)
        on_ship_cosmetics_changed.connect(self.OnShipCosmeticsChanged)
        on_ship_cosmetics_license_change.connect(self.OnLicenseStatusChanged)
        self.cosmeticController.on_new_itemID.connect(self.OnNewItem)

    def Close(self, *args):
        sm.UnregisterNotify(self)
        on_ship_cosmetics_changed.disconnect(self.OnShipCosmeticsChanged)
        on_ship_cosmetics_license_change.disconnect(self.OnLicenseStatusChanged)
        self.cosmeticController.on_new_itemID.disconnect(self.OnNewItem)
        super(LogoSelectionPanel, self).Close()

    def _ConstructContents(self):
        self.loadingCont = LoadingContainer(parent=self, name='loadingCont', align=uiconst.TOALL, loadingSpriteSize=LoadingSpriteSize.LARGE, failureStateMessage=GetByLabel('UI/Fitting/FittingWindow/Cosmetic/FetchLicensesFailedErrorMessage'), retryBtnLabel=GetByLabel('UI/Fitting/FittingWindow/Cosmetic/FetchingFailedButton'))
        scrollCont = ScrollContainer(parent=self.loadingCont, name='scrollCont', align=uiconst.TOALL)
        self.noLogosLabel = EveLabelMedium(parent=self.loadingCont, align=uiconst.CENTER, text=GetByLabel('UI/ShipCosmetics/LogoSelectionUnavailable'))
        self.noLogosLabel.display = False
        self.allianceLogoGroup = AllianceLogoGroup(name='allianceLogoGroup', parent=scrollCont, align=uiconst.TOTOP, padTop=12, errorCallback=self._fittingErrorCallback)
        self.allianceLogoGroup.display = False
        self.corporationLogoGroup = CorporationLogoGroup(name='corporationLogoGroup', parent=scrollCont, align=uiconst.TOTOP, errorCallback=self._fittingErrorCallback)
        self.corporationLogoGroup.display = False
        self.loadingCont.LoadContent(loadCallback=self._LoadDataCallback)

    def _LoadDataCallback(self):
        logoData = self.FetchLogoData(True)
        self.UpdateLogoEntries(logoData)

    def _QuickLoadDataCallback(self):
        logoData = self.FetchLogoData(False)
        self.UpdateLogoEntries(logoData)

    def QuickContentReload(self):
        self.loadingCont.LoadContent(loadCallback=self._QuickLoadDataCallback)

    def UpdateLogoEntries(self, logoData):
        self.noLogosLabel.display = logoData is None
        self.allianceLogoGroup.display = logoData is not None
        self.corporationLogoGroup.display = logoData is not None
        if logoData is not None:
            self.allianceLogoGroup.UpdateLayout(logoData)
            self.corporationLogoGroup.UpdateLayout(logoData)

    def FetchLogoData(self, forceRefresh = False):
        existingLicenses = sm.GetService('cosmeticsLicenseSvc').get_ship_licenses_for_ship_type(sm.GetService('godma').GetItem(session.shipid).typeID)
        ownedLicenses = sm.GetService('cosmeticsLicenseSvc').get_owned_ship_licenses_for_ship(session.shipid, force_refresh=forceRefresh)
        selectedCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(session.shipid, forceRefresh=forceRefresh, raises=True)
        existing_alliance_license = None
        existing_corp_license = None
        for license in existingLicenses:
            if license.cosmeticType == CosmeticsType.ALLIANCE_LOGO:
                existing_alliance_license = license
            elif license.cosmeticType == CosmeticsType.CORPORATION_LOGO:
                existing_corp_license = license

        owned_alliance_license = None
        owned_corp_license = None
        for license in ownedLicenses:
            if license.cosmeticType == CosmeticsType.ALLIANCE_LOGO:
                owned_alliance_license = license
            elif license.cosmeticType == CosmeticsType.CORPORATION_LOGO:
                owned_corp_license = license

        logoData = LogoData(existence=LogoProperties(alliance=existing_alliance_license, corporation=existing_corp_license), eligibility=LogoProperties(alliance=owned_alliance_license, corporation=owned_corp_license), selection=LogoProperties(alliance=owned_alliance_license if CosmeticsType.ALLIANCE_LOGO in selectedCosmetics else None, corporation=owned_corp_license if CosmeticsType.CORPORATION_LOGO in selectedCosmetics else None))
        return logoData

    def OnSessionChanged(self, _isremote, _session, change):
        if 'corpid' in change.keys() or 'allianceid' in change.keys():
            self.QuickContentReload()

    def OnShipCosmeticsChanged(self, _ship_id, _cosmetics_types):
        self.QuickContentReload()

    def OnLicenseStatusChanged(self, _cosmeticsLicenseID, _enable):
        self.QuickContentReload()

    def ProcessActiveShipChanged(self, _shipID, _oldShipID):
        self.QuickContentReload()

    def OnCorporationChanged(self, _corpID, _change):
        self.QuickContentReload()

    def OnNewItem(self, *args):
        self.QuickContentReload()


class LogoProperties(object):

    def __init__(self, alliance = None, corporation = None):
        self.alliance = alliance
        self.corporation = corporation


class LogoData(object):

    def __init__(self, existence = LogoProperties(), eligibility = LogoProperties(), selection = LogoProperties()):
        self.existence = existence
        self.eligibility = eligibility
        self.selection = selection
