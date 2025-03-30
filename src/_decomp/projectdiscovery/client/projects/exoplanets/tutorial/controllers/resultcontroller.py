#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\tutorial\controllers\resultcontroller.py
from projectdiscovery.client.projects.exoplanets.tutorial.controllers.basecontroller import TutorialController
import localization

class GraphResultTutorialController(TutorialController):
    __notifyevents__ = TutorialController.__notifyevents__ + ['OnResultScreenShown', 'OnContinueToRewards']
    __highlighted_names__ = ['ExoPlanetsGraph']

    def __init__(self, result_description, result_title = None, *args, **kwargs):
        super(GraphResultTutorialController, self).__init__(*args, **kwargs)
        self._description = result_description
        self._title = result_title
        sm.RegisterNotify(self)
        self.start_tutorial()

    def start_tutorial(self):
        pass

    def OnResultScreenShown(self, *args, **kwargs):
        self._highlight_service.highlight_ui_element_by_name('ExoPlanetsGraph', title=self._title, message=self._description)

    def OnContinueToRewards(self, *args, **kwargs):
        self._clear_highlights()


class SingleTransitResultTutorialController(GraphResultTutorialController):
    __highlighted_names__ = ['HighlightSprite']

    def __init__(self, *args, **kwargs):
        super(SingleTransitResultTutorialController, self).__init__(*args, **kwargs)

    def OnResultScreenShown(self, *args, **kwargs):
        self._transit_message = self._description
        self._transit_title = self._transit_title
        sm.ScatterEvent('OnDisplayTutorialGraph', self._correct_markers[0], hide_graphs=True)
        self._highlight_transit_location('HighlightSprite', self._transit_message, title=self._transit_title)


class DummyResultTutorialController(GraphResultTutorialController):

    def __init__(self, *args, **kwargs):
        super(DummyResultTutorialController, self).__init__('Missing Description', 'Missing Title', *args, **kwargs)


class FourthSampleController(SingleTransitResultTutorialController):

    def __init__(self, *args, **kwargs):
        super(FourthSampleController, self).__init__(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/FourthSampleText'), None, *args, **kwargs)


class FifthSampleController(SingleTransitResultTutorialController):

    def __init__(self, *args, **kwargs):
        super(FifthSampleController, self).__init__(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/FifthSampleText'), None, *args, **kwargs)


class SixthSampleController(GraphResultTutorialController):

    def __init__(self, *args, **kwargs):
        super(SixthSampleController, self).__init__(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/SixthSampleText'), None, *args, **kwargs)


class SeventhSampleController(GraphResultTutorialController):

    def __init__(self, *args, **kwargs):
        super(SeventhSampleController, self).__init__(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/SeventhSampleText'), None, *args, **kwargs)


class EighthSampleController(SingleTransitResultTutorialController):

    def __init__(self, *args, **kwargs):
        super(EighthSampleController, self).__init__(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/EighthSampleText'), None, *args, **kwargs)


class TenthSampleTutorial(GraphResultTutorialController):

    def __init__(self, *args, **kwargs):
        super(TenthSampleTutorial, self).__init__(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/Tutorial/TenthSampleText'), None, *args, **kwargs)
