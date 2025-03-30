#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\boundingboxbracket.py
import trinity
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.util.dpi import reverse_scale_dpi, scale_dpi

class BoundingBoxBracket(Container):
    default_name = 'boundingboxBracket'
    default_align = uiconst.TOPLEFT
    default_minWidth = 0.0
    default_minHeight = 0.0
    default_maxWidth = 0.0
    default_maxHeight = 0.0
    default_screenMargin = 32.0

    def ApplyAttributes(self, attributes):
        proj = trinity.Tr2ProjectBoundingBoxBracket()
        self.projectBracket = proj
        cs = uicore.uilib.bracketCurveSet
        cs.curves.append(self.projectBracket)
        self.leftBinding = trinity.CreatePythonBinding(cs, proj, 'projectedX', self, 'scaledLeft')
        self.topBinding = trinity.CreatePythonBinding(cs, proj, 'projectedY', self, 'scaledTop')
        self.widthBinding = trinity.CreatePythonBinding(cs, proj, 'projectedWidth', self, 'scaledWidth')
        self.heightBinding = trinity.CreatePythonBinding(cs, proj, 'projectedHeight', self, 'scaledHeight')
        Container.ApplyAttributes(self, attributes)
        self.trackObject = attributes.get('trackObject', None)
        self.screenMargin = attributes.get('screenMargin', self.default_screenMargin)
        pb = self.projectBracket
        if self.width:
            pb.minProjectedWidth = pb.maxProjectedWidth = self.width
        else:
            pb.minProjectedWidth = attributes.get('minWidth', self.default_minWidth)
            pb.maxProjectedWidth = attributes.get('maxWidth', self.default_maxWidth)
        if self.height:
            pb.minProjectedHeight = pb.maxProjectedHeight = self.height
        else:
            pb.minProjectedHeight = attributes.get('minHeight', self.default_minHeight)
            pb.maxProjectedHeight = attributes.get('maxHeight', self.default_maxHeight)

    def Close(self):
        Container.Close(self)
        cs = uicore.uilib.bracketCurveSet
        cs.curves.fremove(self.projectBracket)
        cs.bindings.fremove(self.leftBinding)
        cs.bindings.fremove(self.topBinding)
        cs.bindings.fremove(self.widthBinding)
        cs.bindings.fremove(self.heightBinding)
        self.leftBinding = None
        self.topBinding = None
        self.widthBinding = None
        self.heightBinding = None
        self.projectBracket = None

    @property
    def name(self):
        return Container.name.fget(self)

    @name.setter
    def name(self, name):
        Container.name.fset(self, name)
        self.projectBracket.name = unicode(name)

    @property
    def trackObject(self):
        return self.projectBracket.object

    @trackObject.setter
    def trackObject(self, value):
        self.projectBracket.object = value

    @property
    def screenMargin(self):
        return self.projectBracket.screenMargin

    @screenMargin.setter
    def screenMargin(self, value):
        self.projectBracket.screenMargin = value

    @property
    def scaledLeft(self):
        return scale_dpi(self.left)

    @scaledLeft.setter
    def scaledLeft(self, value):
        self.left = reverse_scale_dpi(value)

    @property
    def scaledTop(self):
        return scale_dpi(self.top)

    @scaledTop.setter
    def scaledTop(self, value):
        self.top = reverse_scale_dpi(value)

    @property
    def scaledWidth(self):
        return scale_dpi(self.width)

    @scaledWidth.setter
    def scaledWidth(self, value):
        self.width = reverse_scale_dpi(value)

    @property
    def scaledHeight(self):
        return scale_dpi(self.height)

    @scaledHeight.setter
    def scaledHeight(self, value):
        self.height = reverse_scale_dpi(value)
