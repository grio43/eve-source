#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\signatureContentPiece.py
from carbonui.uicore import uicore
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.siteContentPiece import SiteContentPiece
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.comtool.constants import CHANNEL_SCANNING
import inventorycommon.const as invConst
from eve.client.script.ui.shared.mapView.markers.mapMarkerUtil import ICONS_BY_SCANGROUP, GetResultColor
from localization import GetByLabel

class SignatureContentPiece(SiteContentPiece):
    contentType = agencyConst.CONTENTTYPE_SIGNATURES

    def GetSiteName(self):
        return self.site.GetName()

    def GetBracketIconTexturePath(self):
        if self.site.scanStrengthAttribute in ICONS_BY_SCANGROUP:
            return ICONS_BY_SCANGROUP.get(self.site.scanStrengthAttribute, None)
        else:
            return 'res:/UI/Texture/classes/MapView/scanResultLocation.png'

    def IsAccurate(self):
        return self.site.IsAccurate()

    def GetColor(self):
        return GetResultColor(self.site.signalStrength)

    def GetSubSolarSystemPosition(self):
        return self.site.position

    def GetModulesRequiredTypeIDs(self):
        return (invConst.typeCoreScannerProbe, invConst.typeCoreProbeLauncher)

    def GetChatChannelID(self):
        return CHANNEL_SCANNING

    def GetMenu(self):
        return sm.GetService('scanSvc').GetScanResultMenuWithoutIgnore(self.site)

    def _ExecuteWarpTo(self):
        sm.GetService('menu').WarpToScanResult(self.site.siteID)

    def IsWarpableTo(self):
        return self.IsAccurate()

    def _GetButtonState(self):
        if not self.IsAccurate():
            return agencyUIConst.ACTION_OPENPROBESCANNER
        return super(SiteContentPiece, self)._GetButtonState()

    def GetButtonLabel(self):
        if not self.IsAccurate():
            return GetByLabel('UI/Inflight/Scanner/ProbeScanner')
        return super(SiteContentPiece, self).GetButtonLabel()

    def GetButtonTexturePath(self):
        if not self.IsAccurate():
            return 'res:/UI/Texture/Icons/probe_scan.png'
        return super(SiteContentPiece, self).GetButtonTexturePath()

    def _ExecutePrimaryFunction(self, actionID):
        if actionID == agencyUIConst.ACTION_OPENPROBESCANNER:
            uicore.cmd.OpenProbeScanner()
        return super(SignatureContentPiece, self)._ExecutePrimaryFunction(actionID)
