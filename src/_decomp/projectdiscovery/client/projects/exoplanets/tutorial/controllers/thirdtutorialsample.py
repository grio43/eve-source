#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\tutorial\controllers\thirdtutorialsample.py
from projectdiscovery.client.projects.exoplanets.tutorial.controllers.basecontroller import TutorialController
from projectdiscovery.client.projects.exoplanets.tutorial.tutorialdescriptioncontainer import TutorialDescriptionContainer
from uihighlighting.const import UiHighlightDirections
import localization

class ThirdSampleTutorial(TutorialController):
    __notifyevents__ = TutorialController.__notifyevents__ + ['OnResultScreenShown', 'OnContinueToRewards']
    __highlighted_names__ = ['ExoPlanetsGraph']

    def __init__(self, *args, **kwargs):
        super(ThirdSampleTutorial, self).__init__(*args, **kwargs)
        sm.RegisterNotify(self)
        self.start_tutorial()

    def start_tutorial(self):
        self._highlight_service.custom_highlight_ui_element_by_name(ui_element_name='ExoPlanetsGraph', default_direction=UiHighlightDirections.DOWN, offset=-80, highlight_content=TutorialDescriptionContainer(title=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/HandoffLabel'), description=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/HandoffMessage'), buttonText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/ButtonLabel'), width=400, height=110, buttonFunc=self.explain_handholding_completed))

    def explain_handholding_completed(self, *args, **kwargs):
        self._is_graph_disabled = False
        self._highlight_service.remove_highlight_from_ui_element_by_name('ExoPlanetsGraph')

    def OnResultScreenShown(self, *args, **kwargs):
        self._highlight_service.highlight_ui_element_by_name('ExoPlanetsGraph', localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/NoTransitsBecauseBinary'))

    def OnContinueToRewards(self, *args, **kwargs):
        self._clear_highlights()
