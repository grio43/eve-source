#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\local_chat\validators\paste.py
from carbon.common.script.util.commonutils import StripTags

class PasteValidator(object):

    def validate(self, text):
        return NotImplementedError

    @property
    def identifier(self):
        return self.__class__.__name__


class DefaultValidator(PasteValidator):

    def validate(self, text):
        text = text.replace('<t>', '  ')
        ignored_tags = ['b', 'i', 'u']
        ignored_tags += sm.GetService('helpPointer').FindTagToIgnore(text)
        return StripTags(text, ignored_tags)
