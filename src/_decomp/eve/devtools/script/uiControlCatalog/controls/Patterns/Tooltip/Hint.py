#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Patterns\Tooltip\Hint.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = "To give any ui Object a simple tooltip, just pass in a 'hint' argument (text)"

    def sample_code(self, parent):
        cont = Container(name='myCont', parent=parent, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, width=100, height=100, bgColor=eveColor.MATTE_BLACK, hint='This container has a hint')
        eveLabel.EveLabelMedium(parent=cont, align=uiconst.CENTER, text='Hover me plz')


class Sample2(Sample):
    name = 'GetHint Method'
    description = 'Alternatively, you can define a GetHint method on your objects'

    def sample_code(self, parent):

        class MyContainerWithHint(Container):
            default_state = uiconst.UI_NORMAL
            default_bgColor = eveColor.MATTE_BLACK

            def GetHint(self):
                import random
                return 'A random number: %s' % random.randint(0, 10)

        cont = MyContainerWithHint(name='myCont', parent=parent, align=uiconst.TOPLEFT, width=100, height=100)
        eveLabel.EveLabelMedium(parent=cont, align=uiconst.CENTER, text='Hover me plz')
