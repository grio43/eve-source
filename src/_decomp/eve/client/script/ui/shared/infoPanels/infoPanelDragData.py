#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelDragData.py


class InfoPanelDragData:

    def __init__(self, infoPanelCls):
        self.infoPanelCls = infoPanelCls

    def LoadIcon(self, icon, dragContainer, iconSize):
        icon.LoadIcon(self.infoPanelCls.default_iconTexturePath)
        icon.width = icon.height = 32
