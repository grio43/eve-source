#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerSovHub.py
import eveicon
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui import uiconst, TextDetail, TextBody
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from eve.client.script.ui.shared.sov.sovHub.sovHubWnd import OpenSovHubWnd
from carbonui.primitives.base import ScaleDpi
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
import blue
from eveformat.client import solar_system_with_security
from evemap.workforceUtil import GetTexturePathAndColorFromMode
from localization import GetByLabel
from menu import MenuLabel
from sovereignty.client.sovHub.hubUtil import GetTexturePathForWorkforceMode
from sovereignty.workforce.workforceConst import LABELPATH_BY_MODE

class MarkerSovHub(MarkerIconBase):
    texturePath = eveicon.workforce
    distanceFadeAlphaNearFar = (0.0, mapViewConst.MAX_MARKER_DISTANCE)
    isConnected = True

    def __init__(self, *args, **kwds):
        MarkerIconBase.__init__(self, *args, **kwds)
        self.markerID = self.markerID
        self.hubStateConfig = kwds['hubStateConfig']
        self.SetVariables()
        self.projectBracket.offsetY = ScaleDpi(14)

    def SetVariables(self):
        self.hubID = self.hubStateConfig.hubID
        self.solarSystemID = self.hubStateConfig.solarSystemID
        self.sovHubOwnerID = self.hubStateConfig.corporationID
        self.isConnected = self.hubStateConfig.IsConnected()

    def Load(self):
        if self.isLoaded:
            return
        self.texturePath, bgColor = GetTexturePathAndColorFromMode(self.hubStateConfig)
        if not self.IsOwnedByMyCorp():
            bgColor = eveColor.SILVER_GREY
        self.backgroundColor = bgColor
        MarkerIconBase.Load(self)
        self.backgroundSprite.top = 30
        self.backgroundSprite.height = -64
        self.markerContainer.tooltipPanelClassInfo = None
        self.markerContainer.LoadTooltipPanel = self.LoadTooltipPanel
        self.markerContainer.pointerDirection = uiconst.POINT_BOTTOM_2

    def _UpdateSprites(self):
        self.texturePath, bgColor = GetTexturePathAndColorFromMode(self.hubStateConfig)
        if not self.IsOwnedByMyCorp():
            bgColor = eveColor.SILVER_GREY
        self.backgroundColor = bgColor
        self.backgroundSprite.SetRGBA(*self.backgroundColor)
        self.iconSprite.SetTexturePath(self.texturePath)

    def IsOwnedByMyCorp(self):
        isOwnedByMyCorp = self.sovHubOwnerID == session.corpid
        return isOwnedByMyCorp

    def GetBackgroundSpriteIdleOpacity(self):
        modifier = 0.5 if not self.IsOwnedByMyCorp() else 1.0
        if self.isConnected:
            return modifier * 2.0
        return modifier * 1.0

    def GetIconSpriteIdleOpacity(self):
        modifier = 0.5 if not self.IsOwnedByMyCorp() else 1.0
        if self.isConnected:
            return modifier * 1.0
        return modifier * 0.5

    def GetMenu(self):
        m = [MenuEntryData(MenuLabel('UI/Menusvc/OpenSovHubConfigWindow'), func=lambda *args: OpenSovHubWnd(self.hubID, self.solarSystemID), texturePath=eveicon.settings)]
        m += self.GetStateAndConfigProgrammerMenu()
        return m

    def GetStateAndConfigProgrammerMenu(self):
        if not session.role & ROLE_PROGRAMMER:
            return []
        from carbonui.control.contextMenu.menuEntryData import MenuEntryData
        m = [None]
        m += [(str(self.hubID), blue.pyos.SetClipboardData, (str(self.hubID),))]
        try:
            sovHubSvc = sm.GetService('sovHubSvc')
            workforceState = sovHubSvc.GetWorkforceState(self.hubID)
            m.append(MenuEntryData('State : '))
            workforceStateMode = workforceState.get_mode()
            m.append(MenuEntryData(' %s' % GetByLabel(LABELPATH_BY_MODE.get(workforceStateMode))))
            exportState = workforceState.export_state
            if workforceState.import_state:
                for ssID, qty in workforceState.import_state.amount_by_source_system_id.iteritems():
                    m.append(MenuEntryData('  %s: %s ' % (ssID, qty), func=lambda sID = ssID: blue.pyos.SetClipboardData(str(sID))))

            elif exportState:
                destID = exportState.destination_system_id
                m.append(MenuEntryData('  %s: %s ' % (destID, exportState.amount), func=lambda dID = destID: blue.pyos.SetClipboardData(str(dID))))
            workforceConfig = sovHubSvc.GetWorkforceConfiguration(self.hubID)
            m.append(MenuEntryData('Config : '))
            workforceConfigMode = workforceConfig.get_mode()
            m.append(MenuEntryData(' %s' % GetByLabel(LABELPATH_BY_MODE.get(workforceConfigMode))))
            if workforceConfig.import_configuration:
                for ssID in workforceConfig.import_configuration.source_system_ids:
                    m.append(MenuEntryData('  %s' % ssID, func=lambda sID = ssID: blue.pyos.SetClipboardData(str(sID))))

            elif workforceConfig.export_configuration:
                destID = workforceConfig.export_configuration.destination_system_id
                m.append(MenuEntryData('  %s: %s ' % (destID, workforceConfig.export_configuration.amount), func=lambda dID = destID: blue.pyos.SetClipboardData(str(dID))))
        except Exception as e:
            print 'e = ', e

        return m

    def GetDisplayText(self):
        return ''

    def SetMarkerKwds(self, kwds):
        self.hubStateConfig = kwds['hubStateConfig']
        self.SetVariables()
        if not self.isLoaded:
            return
        self._UpdateSprites()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 1
        solarSystemName = solar_system_with_security(self.hubStateConfig.solarSystemID)
        tooltipPanel.AddTextBodyLabel(text=solarSystemName)
        mode = self.hubStateConfig.GetConfigMode()
        texturePath = GetTexturePathForWorkforceMode(mode)
        labelPath = LABELPATH_BY_MODE.get(mode, 'UI/Sovereignty/SovHub/UnknownWorkforceMode')
        modeText = GetByLabel(labelPath)
        text = GetByLabel('UI/Sovereignty/WorforceConfigurationMode', configureMode=modeText)
        modeLabel = TextBody(text=text, align=uiconst.CENTERLEFT, left=24)
        cell = tooltipPanel.AddCell(modeLabel)
        Sprite(parent=cell, align=uiconst.CENTERLEFT, pos=(8, 0, 16, 16), texturePath=texturePath, color=eveColor.SILVER_GREY)
        if self.sovHubOwnerID != session.corpid:
            text = GetByLabel('UI/Sovereignty/SovHubOwnedByDifferentCorp', corpName=cfg.eveowners.Get(self.sovHubOwnerID).name)
            tooltipPanel.AddTextDetailsLabel(text=text, colSpan=2, maxWidth=240)
        importExportText = self.hubStateConfig.GetImportExportInfoForTooltip()
        for path, opacity, text in importExportText:
            modeLabel = TextDetail(text=text, align=uiconst.CENTERLEFT, left=24)
            cell = tooltipPanel.AddCell(modeLabel)
            Sprite(parent=cell, align=uiconst.CENTERLEFT, pos=(8, 0, 16, 16), texturePath=path, color=eveColor.SILVER_GREY)
            cell.opacity = opacity
