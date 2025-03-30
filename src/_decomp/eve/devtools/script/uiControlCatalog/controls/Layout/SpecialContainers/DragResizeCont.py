#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\SpecialContainers\DragResizeCont.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import Label
from eve.devtools.script.uiControlCatalog.sample import Sample
TEXT1 = "Some people stand in the darkness\nAfraid to step into the light\nSome people need to help somebody\nWhen the edge of surrender's in sight.."
TEXT2 = "Don't you worry!\nIts gonna be alright\n'cause I'm always ready,\nI won't let you out of my sight."

class Sample1(Sample):
    name = 'Horizontal, proportional'
    description = 'A split container where the divider can be dragged around'

    def sample_code(self, parent):
        from carbonui.control.dragResizeCont import DragResizeCont
        mainCont = Container(parent=parent, align=uiconst.TOPLEFT, width=400, height=250, bgColor=eveColor.MATTE_BLACK, clipChildren=True)
        resizeCont = DragResizeCont(name='resizeCont', parent=mainCont, align=uiconst.TOLEFT_PROP, bgColor=eveColor.GUNMETAL_GREY, minSize=0.1, maxSize=0.9, defaultSize=0.5)
        Label(name='leftLabel', parent=resizeCont.mainCont, align=uiconst.TOTOP, text=TEXT1, padding=8)
        Label(name='rightLabel', parent=mainCont, align=uiconst.TOTOP, text=TEXT2, padding=8)


class Sample2(Sample):
    name = 'Vertical, fixed-size'

    def sample_code(self, parent):
        from carbonui.control.dragResizeCont import DragResizeCont
        mainCont = Container(parent=parent, align=uiconst.TOPLEFT, width=400, height=250, bgColor=eveColor.MATTE_BLACK)
        resizeCont = DragResizeCont(name='resizeCont', parent=mainCont, align=uiconst.TOTOP, bgColor=eveColor.GUNMETAL_GREY, minSize=30, maxSize=170, defaultSize=100, clipChildren=True)
        Label(name='leftLabel', parent=resizeCont.mainCont, align=uiconst.TOTOP, text=TEXT1, padding=8)
        Label(name='rightLabel', parent=mainCont, align=uiconst.TOTOP, text=TEXT2, padding=8)


class Sample3(Sample):
    name = 'Persisting width/height'
    description = "By passing in a 'settingsID' attribute, width and height will be remembered"

    def sample_code(self, parent):
        from carbonui.control.dragResizeCont import DragResizeCont
        mainCont = Container(parent=parent, align=uiconst.TOPLEFT, width=400, height=400, bgColor=eveColor.LED_GREY)
        DragResizeCont(name='resizeCont', parent=mainCont, align=uiconst.TOLEFT_PROP, bgColor=eveColor.MATTE_BLACK, minSize=0.1, maxSize=0.9, defaultSize=0.5, settingsID='MyDragResizeContID')
