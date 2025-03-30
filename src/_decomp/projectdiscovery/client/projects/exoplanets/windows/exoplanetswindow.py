#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\windows\exoplanetswindow.py
import carbonui.const as uiconst
from projectdiscovery.client.ui.projectdiscoverywindow import BaseProjectDiscoveryWindow
from projectdiscovery.client.projects.exoplanets.gameplaymodes.exoplanetsproject import ExoPlanetsProject
from projectdiscovery.client.projects.exoplanets.gameplaymodes.exoplanetstutorial import ExoPlanetsTutorial
from projectdiscovery.client.util.spacescene import SpaceScene

class ExoPlanetsWindow(BaseProjectDiscoveryWindow):

    def set_project(self):
        self._project_container = ExoPlanetsProject(name='exoplanets_project', parent=self.project_container, align=uiconst.TOALL, bottomContainer=self._bottom_container, clipChildren=False, opacity=0, padTop=20, scale=self.get_scale())

    def set_tutorial(self):
        self._project_container = ExoPlanetsTutorial(name='exoplanets_tutorial', parent=self.project_container, align=uiconst.TOALL, bottomContainer=self._bottom_container, clipChildren=False, opacity=0, padTop=20, scale=self.get_scale(), playerStatistics=self.player_statistics if 'message' not in self.player_statistics else None, playerState=self.player_exp_state)

    def set_background(self):
        self._background_scene = SpaceScene(name='SpaceScene', parent=self.sr.main, align=uiconst.TOALL, padLeft=2, padRight=2, padBottom=2)
