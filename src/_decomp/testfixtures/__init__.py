#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\testfixtures\__init__.py


class singleton(object):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<%s>' % self.name

    __str__ = __repr__


not_there = singleton('not_there')
from testfixtures.comparison import Comparison, StringComparison, RoundComparison, compare, diff
from testfixtures.tdatetime import test_datetime, test_date, test_time
from testfixtures.logcapture import LogCapture, log_capture
from testfixtures.outputcapture import OutputCapture
from testfixtures.resolve import resolve
from testfixtures.replace import Replacer, replace
from testfixtures.shouldraise import ShouldRaise, should_raise
from testfixtures.tempdirectory import TempDirectory, tempdir
from testfixtures.utils import wrap, generator
