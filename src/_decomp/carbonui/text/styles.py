#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\text\styles.py
from carbonui.text.const import FontSizePreset
from carbonui.text.custom import TextCustom

class TextFixedStyleBase(TextCustom):
    _FIXED_PROPERTIES = {'fontFamily',
     'fontPath',
     'fontStyle',
     'fontsize',
     'letterspace',
     'lineSpacing'}

    def __init__(self, **kwargs):
        for name in self._FIXED_PROPERTIES:
            if name in kwargs:
                raise TypeError("You're not allowed to change {name} on a {klass}".format(name=name, klass=self.__class__.__name__))

        super(TextFixedStyleBase, self).__init__(fontsize=self.default_fontsize, **kwargs)


class TextDisplay(TextFixedStyleBase):
    default_fontsize = FontSizePreset.DISPLAY


class TextHeadline(TextFixedStyleBase):
    default_fontsize = FontSizePreset.HEADLINE


class TextHeader(TextFixedStyleBase):
    default_fontsize = FontSizePreset.HEADER


class TextBody(TextFixedStyleBase):
    default_fontsize = FontSizePreset.BODY


class TextDetail(TextFixedStyleBase):
    default_fontsize = FontSizePreset.DETAIL
