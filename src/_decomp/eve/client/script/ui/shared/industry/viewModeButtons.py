#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\viewModeButtons.py
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.shared.industry.industryUIConst import VIEWMODE_ICONLIST, VIEWMODE_LIST
import localization
import carbonui.const as uiconst

class ViewModeButtons(ContainerAutoSize):
    default_name = 'ViewModeButtons'
    default_viewMode = VIEWMODE_ICONLIST
    default_height = 16

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.settingsID = attributes.settingsID
        self.controller = attributes.controller
        self.viewMode = settings.user.ui.Get(self.settingsID, VIEWMODE_ICONLIST)
        self.btnViewModeIconList = ButtonIcon(texturePath='res:/UI/Texture/Icons/38_16_189.png', parent=self, align=uiconst.TOLEFT, width=self.height, func=self.SetViewModeIconList, hint=localization.GetByLabel('UI/Inventory/Details'))
        self.btnViewModeList = ButtonIcon(texturePath='res:/UI/Texture/Icons/38_16_190.png', parent=self, align=uiconst.TOLEFT, width=self.height, func=self.SetViewModeList, hint=localization.GetByLabel('UI/Inventory/List'))
        self.SetViewMode(self.viewMode)

    def SetViewModeIconList(self):
        self.SetViewMode(VIEWMODE_ICONLIST)
        self.controller.OnViewModeChanged(VIEWMODE_ICONLIST)

    def SetViewModeList(self):
        self.SetViewMode(VIEWMODE_LIST)
        self.controller.OnViewModeChanged(VIEWMODE_LIST)

    def SetViewMode(self, viewMode):
        self.viewMode = viewMode
        self.UpdateButtons(viewMode)
        settings.user.ui.Set(self.settingsID, viewMode)

    def GetViewMode(self):
        return self.viewMode

    def UpdateButtons(self, viewMode):
        if viewMode == VIEWMODE_ICONLIST:
            self.btnViewModeIconList.SetSelected()
        else:
            self.btnViewModeIconList.SetDeselected()
        if viewMode == VIEWMODE_LIST:
            self.btnViewModeList.SetSelected()
        else:
            self.btnViewModeList.SetDeselected()
