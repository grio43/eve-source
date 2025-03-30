#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\ghostFittingHelpers.py


def TryPreviewFitItemOnMouseAction(node, oldWindow = True, force = False):
    from eve.client.script.ui.shared.fittingScreen.fittingWnd import FittingWindow
    fittingWnd = FittingWindow.GetIfOpen()
    if fittingWnd is not None:
        fittingWnd.PreviewFitItem(node, force)
