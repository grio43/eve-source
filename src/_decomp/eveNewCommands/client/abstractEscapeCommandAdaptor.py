#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveNewCommands\client\abstractEscapeCommandAdaptor.py


class AbstractEscapeCommandAdapter(object):

    def IsDisconnectNoticeDisplayed(self):
        return False

    def HasCancellableModal(self):
        return False

    def HasOpenMenuItems(self):
        return False

    def ClearMenu(self):
        pass

    def CloseModalWithCancelResult(self):
        pass

    def HasActiveLoading(self):
        return False

    def HideAllLoading(self):
        pass

    def IsEscapeMenuActive(self):
        return False

    def HideEscapeMenu(self):
        pass

    def ShowEscapeMenu(self):
        pass

    def HasControl(self):
        return True

    def HideElementsUnconditionally(self):
        pass
