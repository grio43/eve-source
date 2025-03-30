#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelContainer.py
import logging
import blue
import telemetry
import carbonui.const as uiconst
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import uthread
import uthread2
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.shared.infoPanels import infoPanelSettingsController
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst, infoPanelClassConst, infoPanelUIConst
from eve.client.script.ui.shared.infoPanels.infoPanelDragData import InfoPanelDragData
from operations.common.util import get_tutorial_category_id
from uihider import get_ui_hider, UiHiderMixin
logger = logging.getLogger(__name__)

class InfoPanelContainer(UiHiderMixin, ContainerAutoSize):
    default_name = 'InfoPanelContainer'
    uniqueUiName = pConst.UNIQUE_NAME_INFO_PANEL
    ICONSIZE = 16
    __notifyevents__ = ['OnOperationsInitialized', 'OnUIScalingChange']
    default_performFitsCheck = True

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.panelClasses = []
        settingsID = attributes.get('settingsID', None)
        self.performFitsCheck = attributes.get('performFitsCheck', self.default_performFitsCheck)
        self.infoPanelsByTypeID = {}
        self.infoPanelButtonsByTypeID = {}
        self.isDraggingButton = False
        self.ConstructLayout()
        self.ReconstructPanels(settingsID, False)
        sm.RegisterNotify(self)

    def ConstructLayout(self):
        self.topCont = Container(name='topCont', parent=self, align=uiconst.TOTOP, height=self.ICONSIZE, padding=(infoPanelUIConst.LEFTPAD,
         0,
         0,
         5))
        self.dropIndicatorLine = Line(name='dropIndicatorLine', parent=self.topCont, align=uiconst.TOLEFT_NOPUSH, state=uiconst.UI_HIDDEN, color=Color.GetGrayRGBA(1.0, 0.6), padding=(0, 2, 0, 2))
        self.iconCont = ContainerAutoSize(name='iconCont', parent=self.topCont, state=uiconst.UI_NORMAL, align=uiconst.TOLEFT, uniqueUiName=pConst.UNIQUE_NAME_INFO_PANEL_BTNS)
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self, align=uiconst.TOTOP)

    def ReconstructPanels(self, settingsID, animate = True):
        self.settingsID = settingsID
        if settingsID:
            self._ReconstructPanels(animate)

    def _GetCurrentlyAvailableInfoPanelClasses(self):
        panelIDs = infoPanelConst.PANELS_BY_SETTINGSID.get(self.settingsID, [])
        infoPanelClasses = [ infoPanelClassConst.PANEL_TYPE_ID_TO_CLASS[panelID] for panelID in panelIDs ]
        return [ infoPanelClass for infoPanelClass in infoPanelClasses if infoPanelClass.IsAvailable() ]

    def IsPanelTypeAllowedInView(self, panelTypeID):
        return panelTypeID in infoPanelConst.PANELS_BY_SETTINGSID.get(self.settingsID, [])

    def SortPanelClasses(self):
        if infoPanelSettingsController.get_all_info_panel_settings(self.settingsID):
            self.panelClasses = sorted(self.panelClasses, key=self.GetInfoPanelClassKey)

    def GetInfoPanelClassKey(self, infoPanelClass):
        panelSettings = infoPanelSettingsController.get_all_info_panel_settings(self.settingsID)
        for index, entry in enumerate(panelSettings):
            if entry[0] == infoPanelClass.panelTypeID:
                return index

        if infoPanelClass in self.panelClasses:
            return self.panelClasses.index(infoPanelClass)

    def OnOperationsInitialized(self, categoryID, operationID):
        if categoryID == get_tutorial_category_id():
            self.ConstructTopIcons()

    def OnUIScalingChange(self, *args):
        self._ReconstructPanels()

    @telemetry.ZONE_FUNCTION
    def ConstructTopIcons(self):
        self.iconCont.Flush()
        self.infoPanelButtonsByTypeID.clear()
        for infoPanelCls in self.panelClasses:
            self.ConstructTopIcon(infoPanelCls)

    def ConstructTopIcon(self, infoPanelCls):
        if infoPanelCls.panelTypeID in self.infoPanelButtonsByTypeID:
            return
        if not infoPanelCls.IsAvailable() or get_ui_hider().is_ui_element_hidden(infoPanelCls.uniqueUiName):
            return
        try:
            button = ButtonIconInfoPanel(infoPanelCls=infoPanelCls, parent=self.iconCont, controller=self, texturePath=infoPanelCls.GetTexturePath(), func=self.OnPanelContainerIconPressed, align=uiconst.TOLEFT, width=self.ICONSIZE)
        except:
            logger.exception('InfoPanelContainer::ConstructTopIcons - Unable to construct top icon for info panel class: %s' % infoPanelCls)
        else:
            self.infoPanelButtonsByTypeID[infoPanelCls.panelTypeID] = button

    def OnPanelContainerIconPressed(self, panelTypeID):
        panel = self.GetPanelByTypeID(panelTypeID)
        if panel:
            if panel.isInModeTransition:
                return
            if panel.mode == infoPanelConst.MODE_HIDDEN:
                panel.mode = infoPanelConst.MODE_NORMAL
            elif panel.isCollapsable:
                panel.mode = infoPanelConst.MODE_HIDDEN
            elif panel.mode == infoPanelConst.MODE_NORMAL:
                panel.mode = infoPanelConst.MODE_COMPACT
            else:
                panel.mode = infoPanelConst.MODE_NORMAL

    @telemetry.ZONE_FUNCTION
    def _ConstructInfoPanels(self):
        for infoPanelCls in self.panelClasses:
            if not session.charid:
                return
            self.ConstructInfoPanel(infoPanelCls)

        if self.performFitsCheck:
            self.CheckAllPanelsFit()

    def CheckAllPanelsFit(self, triggeredByPanel = None):
        uthread2.StartTasklet(self._CheckAllPanelsFit, triggeredByPanel)

    @telemetry.ZONE_FUNCTION
    def _CheckAllPanelsFit(self, triggeredByPanel = None):
        for mode in (infoPanelConst.MODE_COMPACT, infoPanelConst.MODE_HIDDEN):
            for panelTypeID, panel in self.infoPanelsByTypeID.iteritems():
                if panel.mode == infoPanelConst.MODE_HIDDEN:
                    continue
                if not self.IsLastPanelClipped():
                    return
                if panelTypeID == triggeredByPanel:
                    continue
                panel.mode = mode
                logger.info("InfoPanelContainer::_CheckAllPanelsFit - Panels don't fit, setting panelTypeID %s mode to %s", panelTypeID, mode)

    def ConstructInfoPanel(self, infoPanelClass):
        if infoPanelClass not in self.panelClasses:
            self.panelClasses.append(infoPanelClass)
        mode = infoPanelSettingsController.get_panel_mode(self.settingsID, infoPanelClass.panelTypeID)
        try:
            panel = infoPanelClass(parent=self.mainCont, mode=mode, settingsID=self.settingsID)
        except:
            logger.exception('InfoPanelContainer::ConstructInfoPanels - Unable to construct info panel: %s' % infoPanelClass)
        else:
            panel.onModeTransitionToNormalSignal.connect(self.CheckAllPanelsFit)
            self.infoPanelsByTypeID[infoPanelClass.panelTypeID] = panel
            if not infoPanelClass.IsAvailable():
                panel.Hide()
            self.ConstructTopIcon(infoPanelClass)
        finally:
            blue.synchro.Yield()

    def UpdatePanel(self, panelTypeID, ignoreViewSettings = True):
        panel = self.GetPanelByTypeID(panelTypeID)
        if not panel or panel.destroyed:
            panelCls = infoPanelClassConst.PANEL_TYPE_ID_TO_CLASS.get(panelTypeID, None)
            if panelCls.IsAvailable():
                if ignoreViewSettings or self.IsPanelTypeAllowedInView(panelTypeID):
                    self.ConstructInfoPanel(panelCls)
        elif panel and not panel.IsAvailable():
            self.ClosePanel(panelTypeID)

    @telemetry.ZONE_FUNCTION
    def _ReconstructPanels(self, animate = False):
        uthread.Lock(self)
        self.panelClasses = self._GetCurrentlyAvailableInfoPanelClasses()
        try:
            self.SortPanelClasses()
            if animate:
                self.mainCont.opacity = 0.0
            if not session.charid:
                return
            self.mainCont.Flush()
            self._ConstructInfoPanels()
            if not session.charid:
                return
            self.ConstructTopIcons()
            uicore.animations.FadeIn(self.mainCont, duration=0.6)
        finally:
            uthread.UnLock(self)

    @telemetry.ZONE_FUNCTION
    def ClosePanel(self, panelTypeID):
        panel = self.GetPanelByTypeID(panelTypeID)
        button = self.GetPanelButtonByTypeID(panelTypeID)
        if panel:
            self.infoPanelsByTypeID.pop(panelTypeID)
            panel.Close()
        if button:
            self.infoPanelButtonsByTypeID.pop(panelTypeID)
            button.Close()

    def GetPanelByTypeID(self, panelTypeID):
        return self.infoPanelsByTypeID.get(panelTypeID, None)

    def GetPanelButtonByTypeID(self, panelTypeID):
        return self.infoPanelButtonsByTypeID.get(panelTypeID, None)

    def OnButtonDragStart(self, infoPanelCls):
        self.isDraggingButton = infoPanelCls
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.OnButtonDragMove)

    def OnButtonDragEnd(self, infoPanelCls):
        self.dropIndicatorLine.Hide()
        self.isDraggingButton = False
        if self.IsDraggingOverIcons():
            idx = self.GetDropIconIdx()
            dragId = self.GetCurrentPanelTypes().index(infoPanelCls.panelTypeID)
            if dragId < idx:
                idx -= 1
            if idx < len(self.mainCont.children):
                currAtIdx = self.mainCont.children[idx]
                oldTypeID = currAtIdx.panelTypeID
            else:
                oldTypeID = None
            self.MovePanelInFrontOf(infoPanelCls, oldTypeID)

    @telemetry.ZONE_FUNCTION
    def MovePanelInFrontOf(self, infoPanelCls, oldTypeID = None):
        panelSettings = infoPanelSettingsController.get_all_info_panel_settings(self.settingsID)
        entry = infoPanelSettingsController.get_panel_settings_entry_by_type(panelSettings, infoPanelCls.panelTypeID)
        if oldTypeID:
            idx = panelSettings.index(infoPanelSettingsController.get_panel_settings_entry_by_type(panelSettings, oldTypeID))
        else:
            idx = len(self.mainCont.children)
        oldIdx = panelSettings.index(infoPanelSettingsController.get_panel_settings_entry_by_type(panelSettings, infoPanelCls.panelTypeID))
        if oldIdx == idx:
            return
        panelSettings.pop(oldIdx)
        panelSettings.insert(idx, entry)
        infoPanelSettingsController.save_info_panel_setting(self.settingsID, panelSettings)
        self._ReconstructPanels(animate=True)

    def OnButtonDragMove(self, *args):
        if not self.isDraggingButton:
            return False
        if self.IsDraggingOverIcons():
            self.dropIndicatorLine.state = uiconst.UI_DISABLED
            self.SetDropIndicatorLinePosition()
        else:
            self.dropIndicatorLine.Hide()
        return True

    def IsDraggingOverIcons(self):
        return uicore.uilib.mouseOver.IsUnder(self.iconCont) or uicore.uilib.mouseOver == self.iconCont

    def GetCurrentPanelTypes(self):
        return [ panel.panelTypeID for panel in self.panelClasses ]

    def SetDropIndicatorLinePosition(self):
        idx = self.GetDropIconIdx()
        dragIdx = self.GetCurrentPanelTypes().index(self.isDraggingButton.panelTypeID)
        if idx in (dragIdx, dragIdx + 1):
            self.dropIndicatorLine.Hide()
        else:
            self.dropIndicatorLine.Show()
        numIcons = self.GetNumVisible()
        left, _, width, _ = self.iconCont.GetAbsolute()
        self.dropIndicatorLine.left = idx * (width / numIcons) - 2

    def GetDropIconIdx(self):
        numIcons = self.GetNumVisible()
        left, _, width, _ = self.iconCont.GetAbsolute()
        x = uicore.uilib.x - left
        numSlots = numIcons * 2
        pos = max(0, min(x / float(width), 1.0))
        idx = numSlots * pos
        idx = int(float(idx) / 2 + 0.5)
        return idx

    def GetNumVisible(self):
        return len([ child for child in self.iconCont.children if child.display ])

    def IsLastPanelClipped(self):
        if self.destroyed:
            return False
        if not self.mainCont.children:
            return False
        lastChild = self.GetLastVisiblePanel()
        if not lastChild:
            return False
        _, pt, _, ph = self.parent.GetAbsolute()
        if ph <= 0:
            logger.warn("InfoPanelContainer::IsLastPanelClipped: Container parent height is %s (zero or less) so don't collapse any panels", ph)
            return False
        _, t, _, h = lastChild.GetAbsolute()
        return t - pt + h > ph

    def GetLastVisiblePanel(self):
        children = self.mainCont.children[:]
        children.reverse()
        for child in children:
            if child.mode != infoPanelConst.MODE_HIDDEN:
                return child


class ButtonIconInfoPanel(ButtonIcon):
    __notifyevents__ = ['OnInfoPanelSettingChanged']
    default_padRight = 4
    default_iconSize = 18
    isDragObject = True

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.controller = attributes.controller
        self.infoPanelCls = attributes.infoPanelCls
        self.UpdateMode(self.GetInfoPanelMode())

    def OnClick(self, *args):
        self.func(self.infoPanelCls.panelTypeID)

    def GetHint(self):
        return self.infoPanelCls.GetClassHint()

    def OnInfoPanelSettingChanged(self, panelTypeID, mode):
        if panelTypeID == self.infoPanelCls.panelTypeID:
            self.UpdateMode(mode)

    def UpdateMode(self, mode):
        if mode == infoPanelConst.MODE_HIDDEN:
            self.SetSelected()
        else:
            self.SetDeselected()

    def GetInfoPanelMode(self):
        return infoPanelSettingsController.get_panel_mode(self.controller.settingsID, self.infoPanelCls.panelTypeID)

    def GetDragData(self):
        self.controller.OnButtonDragStart(self.infoPanelCls)
        return (InfoPanelDragData(self.infoPanelCls),)

    def OnEndDrag(self, *args):
        ButtonIcon.OnEndDrag(self, *args)
        self.controller.OnButtonDragEnd(self.infoPanelCls)

    def OnDblClick(self, *args):
        pass
