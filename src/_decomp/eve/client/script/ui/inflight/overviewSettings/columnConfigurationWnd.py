#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\columnConfigurationWnd.py
from carbonui import uiconst
from carbonui.control.window import Window
from eve.client.script.ui.inflight.overviewSettings.columnsPanel import ColumnsPanel
import localization

class ColumnConfigurationWindow(Window):
    default_minSize = (400, 440)
    default_windowID = 'OverviewTabColumnConfig'

    def ApplyAttributes(self, attributes):
        super(ColumnConfigurationWindow, self).ApplyAttributes(attributes)
        self.tabID = attributes.tabID
        tabName = sm.GetService('overviewPresetSvc').GetTabName(self.tabID)
        self.SetCaption(localization.GetByLabel('UI/Overview/TabColumnsCaption', tabName=tabName))
        ColumnsPanel(parent=self.content, tabID=self.tabID, state=uiconst.UI_PICKCHILDREN).LoadColumns()
