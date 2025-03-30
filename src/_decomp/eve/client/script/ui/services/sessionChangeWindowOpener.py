#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\sessionChangeWindowOpener.py
import logging
import inventorycommon.const as invConst
from carbonui import uiconst
from carbonui.control.window import Window
from carbonui.window.settings import GetRegisteredState
from eve.client.script.ui.inflight.scannerFiles import scannerUtil
from eve.client.script.ui.inflight.scannerFiles.moonScanner import MoonScanner
from eve.client.script.ui.shared import dockedUI
from eve.client.script.ui.shared.addressBookWindow import AddressBookWindow
from eve.client.script.ui.shared.assetsWindow import AssetsWindow
from eve.client.script.ui.shared.bookmarks.standaloneBookmarkWnd import StandaloneBookmarkWnd
from eve.client.script.ui.shared.inventory import invWindow
from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
from eve.client.script.ui.shared.market.marketbase import RegionalMarket
from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
from eve.client.script.ui.shared.neocom.evemail import MailWindow
from eve.client.script.ui.shared.neocom.journal import JournalWindow
from eve.client.script.ui.shared.neocom.locations.window import LocationsWindow
from eve.client.script.ui.shared.neocom.notepad import NotepadWindow
from eve.client.script.ui.shared.neocom.wallet.walletWnd import WalletWindow
from eve.client.script.ui.shared.uilog import LoggerWindow
from eve.common.lib import appConst
from eve.common.script.sys.eveCfg import IsControllingStructure
from eveuniverse.solar_systems import is_directional_scanner_suppressed, is_scanning_suppressed, is_solarsystem_map_suppressed
from xmppchatclient.xmppchatchannels import XmppChatChannels
from carbonui.uicore import uicore
logger = logging.getLogger(__name__)

def OnSessionChanged():
    _CheckAlways()
    if session.stationid:
        CloseOutOfScopeWindows(uiconst.SCOPE_DOCKED)
        _CheckStation()
    elif session.structureid and session.structureid != session.shipid:
        CloseOutOfScopeWindows(uiconst.SCOPE_DOCKED)
        _CheckStructure()
    elif session.solarsystemid and session.shipid:
        CloseOutOfScopeWindows(uiconst.SCOPE_INFLIGHT)
        _CheckSpace()
    else:
        CloseOutOfScopeWindows(uiconst.SCOPE_INGAME)
    dockedUI.ReloadLobbyWnd()


def CloseOutOfScopeWindows(scope):
    for window in uicore.registry.GetWindows()[:]:
        if window.destroyed:
            continue
        windowScope = _GetWindowScope(window)
        logger.info('ScopeCheck on %s with scope %s', window.name, windowScope)
        if not windowScope or windowScope == uiconst.SCOPE_ALL:
            continue
        if windowScope & scope:
            continue
        try:
            closeMethod = getattr(window, 'Close', getattr(window, 'CloseByUser', None))
            logger.info('ScopeCheck on %s - Closing window via %s', window.name, closeMethod)
            closeMethod()
        except TypeError:
            logger.exception('ScopeCheck: Failed to find a Close* method for window %s', window.name)
        except StandardError:
            logger.exception('ScopeCheck: Close* method for window %s raised an error', window.name)


def _GetWindowScope(window):
    if hasattr(window, 'content') and hasattr(window.content, 'scope'):
        return window.content.scope
    else:
        return getattr(window, 'scope', None)


def _TryOpenWnd(cls, windowID = None, windowInstanceID = None, **kwargs):
    try:
        windowID = windowID or cls.default_windowID
        windowInstanceID = windowInstanceID or cls.default_windowInstanceID
        if Window.GetIfOpen(windowID, windowInstanceID):
            return
        isRegisteredAsOpen = GetRegisteredState(windowID, 'open', False)
        if not isRegisteredAsOpen:
            return
        cls.OpenBehindFullscreenViews(windowID=windowID, windowInstanceID=windowInstanceID, **kwargs)
    except StandardError as e:
        logger.exception('Failed at opening window')


def _CheckAlways():
    _TryOpenWnd(cls=MailWindow)
    _TryOpenWnd(cls=WalletWindow)
    _TryOpenWnd(cls=AssetsWindow)
    _TryOpenWnd(cls=XmppChatChannels)
    _TryOpenWnd(cls=JournalWindow)
    _TryOpenWnd(cls=LoggerWindow)
    _TryOpenWnd(cls=CharacterSheetWindow)
    _TryOpenWnd(cls=AddressBookWindow)
    _TryOpenWnd(cls=LocationsWindow)
    _TryOpenWnd(cls=RegionalMarket)
    _TryOpenWnd(cls=NotepadWindow)
    _TryOpenWnd(cls=StandaloneBookmarkWnd)


def _CheckStation():
    (_TryOpenWnd(cls=invWindow.InventoryPrimary, windowID=invConst.INVENTORY_ID_STATION),)
    (_TryOpenWnd(cls=invWindow.StationItems, windowInstanceID=session.stationid),)
    (_TryOpenWnd(cls=invWindow.StationShips, windowInstanceID=session.stationid),)
    if session.corpid:
        _TryOpenWnd(cls=invWindow.StationCorpDeliveries, windowInstanceID=session.stationid)
        office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
        if office:
            _TryOpenWnd(cls=invWindow.StationCorpHangars, windowID=invConst.INVENTORY_ID_STATION_CORP_HANGARS, windowInstanceID=office.officeID)
            _CheckCorpHangarDivisionInvWnds(invIdName='StationCorpHangar', locationID=office.officeID)


def _CheckStructure():
    _CheckInventoryWndForStructure()
    if session.corpid:
        _TryOpenWnd(cls=invWindow.StationCorpDeliveries, windowInstanceID=session.structureid)
        office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
        if office:
            _TryOpenWnd(cls=invWindow.StationCorpHangars, windowID=invConst.INVENTORY_ID_STRUCTURE_CORP_HANGARS, windowInstanceID=office.officeID)
            _CheckCorpHangarDivisionInvWnds(invIdName='StructureCorpHangar', locationID=office.officeID)


def _CheckSpace():
    from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
    from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
    if IsControllingStructure():
        _CheckInventoryWndForStructure()
    currentSystemID = session.solarsystemid2
    _TryOpenWnd(cls=invWindow.InventoryPrimary, windowID=invConst.INVENTORY_ID_SPACE)
    _TryOpenWnd(cls=MoonScanner)
    if not scannerUtil.IsDirectionalScanPanelEmbedded() and not is_directional_scanner_suppressed(currentSystemID):
        _TryOpenWnd(cls=DirectionalScanner)
    if not scannerUtil.IsProbeScanPanelEmbedded() and not is_scanning_suppressed(currentSystemID):
        _TryOpenWnd(cls=ProbeScannerWindow)
    if not scannerUtil.IsSolarSystemMapFullscreen() and not is_solarsystem_map_suppressed(currentSystemID):
        _TryOpenWnd(cls=SolarSystemViewPanel)


def _CheckInventoryWndForStructure():
    _TryOpenWnd(cls=invWindow.InventoryPrimary, windowID=invConst.INVENTORY_ID_STRUCTURE)
    _TryOpenWnd(cls=invWindow.StationItems, invID=(invConst.INVENTORY_ID_STRUCTURE_ITEMS, session.structureid))
    _TryOpenWnd(cls=invWindow.StationShips, invID=(invConst.INVENTORY_ID_STRUCTURE_SHIPS, session.structureid))


def _CheckCorpHangarDivisionInvWnds(invIdName, locationID):
    for flagID in appConst.flagCorpSAGs:
        divisionID = appConst.corpDivisionsByFlag[flagID]
        invID = ('%s' % invIdName, locationID, divisionID)
        windowID = '%s_%s' % (invIdName, divisionID)
        windowInstanceID = '%s_%s' % (locationID, divisionID)
        _TryOpenWnd(cls=invWindow.Inventory, windowID=windowID, windowInstanceID=windowInstanceID, invID=invID)
