#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\skill_scroll_cont.py
from carbonui.control.scrollContainer import ScrollContainer

class SkillScrollCont(ScrollContainer):

    def __init__(self, **kwargs):
        super(SkillScrollCont, self).__init__(**kwargs)
        self.copyCallback = kwargs['copyCallback']
        self.selectAllCallback = kwargs['selectAllCallback']

    def Copy(self, *_args):
        self.copyCallback()

    def SelectAll(self, *_args):
        self.selectAllCallback()
