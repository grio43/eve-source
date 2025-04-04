#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pympler\django.py
try:
    from debug_toolbar.panels import DebugPanel
except ImportError:

    class DebugPanel(object):
        pass


class MemoryProfilerPanel(DebugPanel):
    name = 'pympler'
    has_content = True
    template = 'templates/django.html'

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def title(self):
        return 'Memory'

    def nav_title(self):
        return 'Memory'

    def url(self):
        return ''

    def get_stats(self):
        pass
