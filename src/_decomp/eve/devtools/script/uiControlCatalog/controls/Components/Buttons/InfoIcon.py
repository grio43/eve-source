#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Components\Buttons\InfoIcon.py
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Info icon'
    description = 'Info icons are the standard way of creating clickable links to Show Info windows of the corresponding UI element'

    def sample_code(self, parent):
        from eve.client.script.ui.control.infoIcon import InfoIcon
        InfoIcon(parent=parent, typeID=11387)


class Sample2(Sample):
    name = 'Info'

    def sample_code(self, parent):
        from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
        InfoGlyphIcon(parent=parent)


class Sample3(Sample):
    name = 'Checkmark'

    def sample_code(self, parent):
        from eve.client.script.ui.control.infoIcon import CheckMarkGlyphIcon
        CheckMarkGlyphIcon(parent=parent)


class Sample4(Sample):
    name = 'Play'

    def sample_code(self, parent):
        from eve.client.script.ui.control.infoIcon import PlayGlyphIcon
        PlayGlyphIcon(parent=parent)


class Sample5(Sample):
    name = 'Warning'

    def sample_code(self, parent):
        from eve.client.script.ui.control.infoIcon import WarningGlyphIcon
        WarningGlyphIcon(parent=parent)


class Sample6(Sample):
    name = 'Warning'

    def sample_code(self, parent):
        from eve.client.script.ui.control.infoIcon import QuestionMarkGlyphIcon
        QuestionMarkGlyphIcon(parent=parent)


class Sample7(Sample):
    name = 'Exclamation'

    def sample_code(self, parent):
        from eve.client.script.ui.control.infoIcon import ExclamationMarkGlyphIcon
        ExclamationMarkGlyphIcon(parent=parent)
