#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\controller\feedback.py
from projectdiscovery.client.projects.covid.ui.drawing import models
from projectdiscovery.client.projects.covid.ui.drawing.controller import update

class FeedbackController(object):
    TYPES = models.FeedbackType

    def __init__(self):
        self.feedback = None
        self.updater = update.UpdateController()

    def clear(self):
        if self.feedback:
            self.feedback = None
            self.updater.tick()

    def _message(self, slug, feedback_type, default_text, **kwargs):
        if self.feedback:
            if self.feedback.slug != slug:
                self.updater.tick()
            elif self.feedback.feedback_type != feedback_type:
                self.updater.tick()
            elif self.feedback.kwargs != kwargs:
                self.updater.tick()
        self.feedback = models.Feedback(slug=slug, feedback_type=feedback_type, default_text=default_text, **kwargs)

    def info(self, slug, default_text = None, **kwargs):
        self._message(slug=slug, feedback_type=models.FeedbackType.INFO, default_text=default_text, **kwargs)

    def warning(self, slug, default_text = None, **kwargs):
        self._message(slug=slug, feedback_type=models.FeedbackType.WARNING, default_text=default_text, **kwargs)

    def error(self, slug, default_text = None, **kwargs):
        self._message(slug=slug, feedback_type=models.FeedbackType.ERROR, default_text=default_text, **kwargs)

    @property
    def feedback_type(self):
        if self.feedback:
            return self.feedback.feedback_type
        return models.FeedbackType.NOTHING

    @property
    def formatted(self):
        return unicode(repr(self))

    def __repr__(self):
        return repr(self.feedback)

    def __nonzero__(self):
        return self.feedback is not None
