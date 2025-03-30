#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\axislabels.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import Label
import carbonui.const as uiconst
from carbonui.graphs import axis
from pool import Pool

class AxisLabels(Container):
    default_clipChildren = True
    default_textAlignment = uiconst.BOTTOMRIGHT
    default_format = str
    default_hints = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.preferredWidth = attributes.width
        self.CreatePools()
        self._labels = []
        self.textAlignment = attributes.get('textAlignment', self.default_textAlignment)
        self._orientation = attributes['orientation']
        self._axis = attributes['axis']
        self._minFactor = attributes.get('minFactor', 0.0)
        self._maxFactor = attributes.get('maxFactor', 1.0)
        self._format = attributes.get('format', self.default_format)
        self._hints = attributes.get('hints', self.default_hints)
        self._prevTicks = None
        self._containers = []
        self._Build()
        self._axis.onChange.connect(self._Build)

    def CreatePools(self):
        self._label_pool = Pool(Label)
        self._container_pool = Pool(Container)

    def _GetTicks(self):
        width, height = self.GetAbsoluteSize()
        size = width if self._orientation == axis.AxisOrientation.HORIZONTAL else height
        ticks = []
        offsets = []
        for tick in self._axis.GetTicks():
            v = self._minFactor + self._axis.MapToView(tick) * (self._maxFactor - self._minFactor)
            offset = v * size
            ticks.append(tick)
            offsets.append(offset)

        return (ticks, offsets)

    def _Build(self, *_):
        containerSize = 16
        width, height = self.GetAbsoluteSize()
        size = width if self._orientation == axis.AxisOrientation.HORIZONTAL else height
        ticks, offsets = self._GetTicks()
        if ticks == self._prevTicks:
            for tick, offset, cont in zip(ticks, offsets, self._containers):
                if offset < 0 or offset >= size:
                    cont.display = False
                else:
                    cont.display = True
                offset -= containerSize / 2
                if offset < 0:
                    offset = 0
                elif offset + containerSize > size:
                    offset = size - containerSize
                if self._orientation == axis.AxisOrientation.HORIZONTAL:
                    cont.left = offset
                else:
                    cont.top = offset

            return
        self.ReturnUIResources()
        self.Flush()
        self._containers = []
        self._labels = []
        self._prevTicks = ticks
        maxLabelWidth = -1
        for tick, offset in zip(ticks, offsets):
            state = uiconst.UI_DISABLED
            if offset < 0 or offset >= size:
                displayState = False
            else:
                displayState = True
            offset -= containerSize / 2
            if offset < 0:
                offset = 0
            elif offset + containerSize > size:
                offset = size - containerSize
            if self._orientation == axis.AxisOrientation.HORIZONTAL:
                cont = self._container_pool.get_instance()
                cont.SetParent(self)
                cont.SetAlign(uiconst.TOPLEFT)
                cont.width = containerSize
                cont.height = self.height
                cont.padding = (3, 0, 3, 0)
                cont.left = offset
            else:
                cont = self._container_pool.get_instance()
                cont.SetParent(self)
                cont.SetAlign(uiconst.TOPLEFT)
                cont.width = self.width
                cont.height = containerSize
                cont.padding = (3, 0, 3, 0)
                cont.top = offset
            cont.state = state
            cont.display = displayState
            self._containers.append(cont)
            label = self.AddLabel(cont, tick)
            maxLabelWidth = max(maxLabelWidth, label.width + 4)
            self._labels.append(label)
            if self._hints:
                label.state = uiconst.UI_NORMAL
                label.hint = self._format(tick)

        self.ResizeWidthIfNeeded(maxLabelWidth)

    def AddLabel(self, cont, tick):
        label = self._label_pool.get_instance()
        label.SetParent(cont)
        label.SetAlign(self.textAlignment)
        label.SetTextColor((1.0, 1.0, 1.0, 0.6))
        label.SetText(self._axis.GetTickLabel(tick))
        return label

    def ResizeWidthIfNeeded(self, maxLabelWidth):
        if self._orientation == axis.AxisOrientation.HORIZONTAL:
            return
        if self.preferredWidth and self.preferredWidth < maxLabelWidth:
            self.width = maxLabelWidth
            for eachCont in self._containers:
                eachCont.width = maxLabelWidth

    def ReturnUIResources(self):
        for label in self._labels:
            self._label_pool.return_instance(label)

        for container in self._containers:
            self._container_pool.return_instance(container)

    def Clear(self):
        self.ReturnUIResources()
        self._prevTicks = None
        self.Flush()

    def Close(self):
        self._container_pool.empty()
        self._label_pool.empty()
        self._container_pool = None
        self._label_pool = None
        super(AxisLabels, self).Close()
