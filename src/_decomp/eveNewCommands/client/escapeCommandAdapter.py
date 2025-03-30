#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveNewCommands\client\escapeCommandAdapter.py
import uthread
from carbonui import uiconst
from carbonui.control.contextMenu.menuUtil import CloseContextMenus, HasContextMenu
from carbonui.uicore import uicore
from eveNewCommands.client.abstractEscapeCommandAdaptor import AbstractEscapeCommandAdapter

class EscapeCommandAdapter(AbstractEscapeCommandAdapter):

    def HasOpenMenuItems(self):
        return HasContextMenu()

    def ClearMenu(self):
        CloseContextMenus()

    def CloseModalWithCancelResult(self):
        modalResult = uicore.registry.GetModalResult(uiconst.ID_CANCEL, 'btn_cancel')
        uicore.registry.GetModalWindow().SetModalResult(modalResult)

    def ShowEscapeMenu(self):
        systemMenu = uicore.layer.systemmenu
        sm.GetService('uipointerSvc').SuppressPointers()
        sm.GetService('heroNotification').hide_notifications(animate=False)
        uthread.new(systemMenu.OpenView)

    def HideEscapeMenu(self):
        systemMenu = uicore.layer.systemmenu
        sm.GetService('uipointerSvc').RevealPointers()
        sm.GetService('heroNotification').show_notifications(animate=False)
        uthread.new(systemMenu.CloseMenu)

    def IsEscapeMenuActive(self):
        systemMenu = uicore.layer.systemmenu
        return systemMenu.isopen

    def HideAllLoading(self):
        uthread.new(sm.GetService('loading').HideAllLoad)

    def IsDisconnectNoticeDisplayed(self):
        return sm.GetService('gameui').HasDisconnectionNotice()

    def HasCancellableModal(self):
        return uicore.registry.GetModalResult(uiconst.ID_CANCEL, 'btn_cancel') is not None

    def HasControl(self):
        return uicore.registry.HasControl()

    def HasActiveLoading(self):
        return uicore.layer.loading.state == uiconst.UI_NORMAL

    def HideElementsUnconditionally(self):
        sm.GetService('helpPointer').HidePointerOverlay()
