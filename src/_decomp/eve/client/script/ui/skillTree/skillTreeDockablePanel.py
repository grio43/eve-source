#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillTree\skillTreeDockablePanel.py
from eve.client.script.ui.shared.mapView.dockPanel import DockablePanel
from eve.client.script.ui.skillTree.skillTreeDataProvider import GetSkillTreeDataProvider
from eve.client.script.ui.skillTree.skillTreeMapView import SkillTreeMapView
from eve.client.script.ui.view.viewStateConst import ViewState

class SkillTreeDockablePanel(DockablePanel):
    default_windowID = 'skillTreeDockablePanel'
    panelID = default_windowID
    default_caption = 'Skill Tree Map'
    viewState = ViewState.SkillTree

    def ApplyAttributes(self, attributes):
        super(SkillTreeDockablePanel, self).ApplyAttributes(attributes)
        self.skillTreeDataProvider = GetSkillTreeDataProvider()
        SkillTreeMapView(parent=self.sr.main)
