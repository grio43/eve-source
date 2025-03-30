#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\paintToolWnd.py
import launchdarkly
import eve.client.script.ui.cosmetics.structure.const as paintToolConst
from cosmetics.common.structures.const import FLAG_PAINTWORK_SKINR_KILLSWITCH, FLAG_PAINTWORK_SKINR_KILLSWITCH_DEFAULT
from eve.client.script.ui.shared.mapView.dockPanel import DockablePanel
from eve.client.script.ui.cosmetics.structure import paintToolSelections
from eve.client.script.ui.cosmetics.structure.pages.structureSelectionPage import StructureSelectionPage
from eve.client.script.ui.cosmetics.structure.pages.designCreationPage import DesignCreationPage
from eve.client.script.ui.cosmetics.structure.pages.designApplicationPage import DesignApplicationPage
from eve.client.script.ui.cosmetics.structure.pages.summaryPage import SummaryPage
from eve.client.script.ui.cosmetics.structure.paintToolSignals import on_close_window_requested
from eve.client.script.ui.view.viewStateConst import ViewState
from carbonui.primitives.container import Container
from eve.common.lib import appConst

class PaintToolWnd(DockablePanel):
    __guid__ = 'PainToolDockablePanel'
    __notifyevents__ = ['OnSessionChanged']
    default_captionLabelPath = 'UI/Personalization/PaintTool/TrySKINRTitle'
    default_descriptionLabelPath = 'UI/Personalization/PaintToolDescription'
    default_name = 'Paint Tool'
    default_windowID = 'PaintTool'
    default_iconNum = 'res:/UI/Texture/WindowIcons/paint_tool.png'
    default_minSize = paintToolConst.WINDOW_MIN_SIZE
    panelID = default_windowID
    viewState = ViewState.PaintTool

    def __init__(self, **kwargs):
        super(PaintToolWnd, self).__init__(**kwargs)
        sm.RegisterNotify(self)
        ld_client = launchdarkly.get_client()
        ld_client.notify_flag(FLAG_PAINTWORK_SKINR_KILLSWITCH, FLAG_PAINTWORK_SKINR_KILLSWITCH_DEFAULT, self._on_killswitch_changed)
        self._create_pages()
        paintToolSelections.SELECTED_PAGE.set(paintToolConst.STRUCTURE_SELECTION_PAGE_ID)
        on_close_window_requested.connect(self._on_close_requested)

    def _on_killswitch_changed(self, ld_client, feature_key, fallback, _flagDeleted):
        killswitch = ld_client.get_bool_variation(feature_key=feature_key, fallback=fallback)
        if killswitch:
            self.CloseIfOpen()

    def OnSessionChanged(self, _is_remote, _session, change):
        if 'corprole' in change:
            if not session.corprole & appConst.corpRoleBrandManager:
                eve.Message('InsufficientRolesForSKINR')
                self.Close()

    @classmethod
    def Open(cls, *args, **kwds):
        if not session.corprole & appConst.corpRoleBrandManager:
            eve.Message('InsufficientRolesForSKINR')
        else:
            return super(PaintToolWnd, cls).Open(*args, **kwds)

    def Close(self, setClosed = False, *args, **kwds):
        on_close_window_requested.disconnect(self._on_close_requested)
        paintToolSelections.SELECTED_PAGE.set(paintToolConst.STRUCTURE_SELECTION_PAGE_ID)
        super(PaintToolWnd, self).Close(setClosed, *args, **kwds)

    def _create_pages(self):
        main_cont = Container(name='mainCont', parent=self.content, padTop=self.toolbarContainer.height)
        self._pages = {paintToolConst.STRUCTURE_SELECTION_PAGE_ID: StructureSelectionPage(name='structureSelectionPage', parent=main_cont, page_id=paintToolConst.STRUCTURE_SELECTION_PAGE_ID),
         paintToolConst.DESIGN_CREATION_PAGE_ID: DesignCreationPage(name='designCreationPage', parent=main_cont, page_id=paintToolConst.DESIGN_CREATION_PAGE_ID),
         paintToolConst.DESIGN_APPLICATION_PAGE_ID: DesignApplicationPage(name='designApplicationPage', parent=main_cont, page_id=paintToolConst.DESIGN_APPLICATION_PAGE_ID),
         paintToolConst.SUMMARY_PAGE_ID: SummaryPage(name='summaryPage', parent=main_cont, page_id=paintToolConst.SUMMARY_PAGE_ID)}

    def _on_close_requested(self):
        self.Close()
