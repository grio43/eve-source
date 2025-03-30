#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\sample.py
import inspect
import linecache
import textwrap
from signals import Signal

class Sample(object):
    name = None
    description = None
    cls = None
    on_code_changed = Signal('on_code_changed')

    def get_name(self):
        if self.name:
            return self.name
        elif self.cls:
            return self.cls.__name__
        else:
            return self.__class__.__name__

    def get_description(self):
        if self.description:
            return self.description
        if self.cls:
            return self.cls.__doc__

    def construct_sample(self, parent):
        self.sample_code(parent)

    def sample_code(self, parent):
        pass

    def get_snippet(self):
        linecache.checkcache(filename=inspect.getfile(self.__class__))
        method = self.sample_code
        if method.func_code == Sample.sample_code.func_code:
            return ''
        lines = inspect.getsourcelines(method)[0][1:]
        ret = ''
        for line in lines:
            ret += line

        return textwrap.dedent(ret)
