#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\postProcessDebugger.py
from carbonui import Density, uiconst
from carbonui.primitives.container import Container
from carbonui.control.window import Window
from carbonui.primitives.gridcontainer import GridContainer
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.control import eveLabel
import blue
from carbonui.primitives.fill import Fill
import uthread2
import trinity
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.line import Line
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.baseScrollContEntry import BaseScrollContEntry

def IsGraphiteAttached():
    try:
        from platformtools.compatibility.exposure.graphite.graphiteutils import IsGraphiteAttached as innerIsGraphiteAttached
        return innerIsGraphiteAttached()
    except ImportError:
        return False


def SetCurrentSelection(selection):
    try:
        from platformtools.compatibility.exposure.graphite.graphiteutils import setCurrentSelection
        setCurrentSelection(selection, True)
    except ImportError:
        pass


def UpdateValueUI(element, attributeName, value):
    if isinstance(value, float):
        element.text = '%.4f' % value
        return
    if isinstance(value, tuple):
        if len(value) == 2:
            element.text = '%.4f, %.4f' % value
            return
        if len(value) == 3:
            element.text = '%.4f, %.4f, %.4f' % value
            return
        if len(value) == 4:
            modifiedValue = (value[0],
             value[1],
             value[2],
             max(value[3], 0.25))
            Fill(bgParent=element, color=modifiedValue)
            return
    if attributeName == 'depthOfFieldShape':
        element.text = trinity.BokehShapeType.GetNameFromValue(value)
        return
    element.text = value


def CreateValueUI(parent, attributeName, value, align = uiconst.TOALL):
    if isinstance(value, float):
        return eveLabel.EveLabelSmall(parent=parent, align=align, text='%.4f' % value)
    if isinstance(value, tuple):
        if len(value) == 2:
            return eveLabel.EveLabelSmall(parent=parent, align=align, text='%.4f, %.4f' % value)
        if len(value) == 3:
            return eveLabel.EveLabelSmall(parent=parent, align=align, text='%.4f, %.4f, %.4f' % value)
        if len(value) == 4:
            container = Container(parent=parent, align=align, width=16, height=16)
            modifiedValue = (value[0],
             value[1],
             value[2],
             max(value[3], 0.25))
            Fill(bgParent=container, color=modifiedValue)
            return container
    if attributeName == 'depthOfFieldShape':
        return eveLabel.EveLabelSmall(parent=parent, align=align, text=trinity.BokehShapeType.GetNameFromValue(value))
    return eveLabel.EveLabelSmall(parent=parent, align=align, text=value)


class Header(Container):
    default_padBottom = 8

    def ApplyAttributes(self, attributes):
        super(Header, self).ApplyAttributes(attributes)
        labels = attributes.labels
        self.container = GridContainer(parent=self, align=uiconst.TOALL, padding=4)
        self.container.columns = len(labels)
        alignments = []
        if attributes.get('equalAlign', False):
            alignments = [uiconst.TOALL] * len(labels)
        else:
            alignments = [uiconst.TOLEFT] + [uiconst.TORIGHT] * (len(labels) - 1)
        for label, alignment in zip(labels, alignments):
            eveLabel.EveHeaderMedium(parent=self.container, align=alignment, text=label)


class WeightRow(BaseScrollContEntry):
    default_name = 'WeightRow'
    default_height = 30
    default_padTop = 8

    def ApplyAttributes(self, attributes):
        super(WeightRow, self).ApplyAttributes(attributes)
        self.attributeName = attributes.attributeName
        self.value = attributes.value
        self.container = GridContainer(parent=self, align=uiconst.TOALL, padding=4)
        self.container.columns = 2
        c1 = Container(parent=self.container, align=uiconst.TOALL)
        c2 = Container(parent=self.container, align=uiconst.TOALL)
        self.attributeNameLabel = eveLabel.EveLabelSmall(parent=c1, text=self.attributeName, align=uiconst.CENTERLEFT)
        self.value = CreateValueUI(c2, self.attributeName, attributes.value, align=uiconst.CENTERLEFT)

    def Update(self, information):
        value = information['value']
        UpdateValueUI(self.value, self.attributeName, value)


class WeightContainer(ScrollContainer):

    def ApplyAttributes(self, attributes):
        super(WeightContainer, self).ApplyAttributes(attributes)
        self.attributes = {}
        self.selectCallback = attributes.selectCallback

    def OnEntrySelected(self, entry):
        self.DeselectAllEntries()
        entry.OnSelect()

    def DeselectAllEntries(self):
        for entry in self.mainCont.children:
            entry.OnDeselect()

    def Update(self, values):
        for attribute, information in iter(values.items()):
            if len(information['influencers']) == 0 and attribute in self.attributes:
                self.attributes[attribute].Close()
                del self.attributes[attribute]
            if len(information['influencers']) == 0:
                continue
            if attribute not in self.attributes:
                row = WeightRow(parent=self, attributeName=attribute, value=information['value'])
                row.on_clicked.connect(self.OnEntrySelected)
                row.on_clicked.connect(self.selectCallback)
                self.attributes[attribute] = row
            else:
                self.attributes[attribute].Update(information)


class InfluencerContainer(DragResizeCont):
    default_maxSize = 500
    default_minSize = 150
    default_defaultSize = 175

    def ApplyAttributes(self, attributes):
        super(InfluencerContainer, self).ApplyAttributes(attributes)
        self.attributeName = None
        self.showInspect = IsGraphiteAttached()
        headers = ['Influencer',
         'Value',
         'Weight',
         'Priority']
        header = Container(parent=self, align=uiconst.TOTOP, height=36)
        self.title = eveLabel.EveHeaderLarge(parent=header, align=uiconst.CENTER, text='', padTop=16)
        self.header = Header(parent=self, labels=headers, align=uiconst.TOTOP, height=36)
        self.scroller = ScrollContainer(parent=self, align=uiconst.TOALL)
        self.influencers = []

    def Update(self, values):
        if self.attributeName is None:
            return
        attributes = [ i['attributes'] for i in values[self.attributeName]['influencers'] ]
        for influencer, row, value, weight, priority in self.influencers[:]:
            if influencer['attributes'] not in attributes:
                row.Close()
                self.influencers.remove((influencer,
                 row,
                 value,
                 weight,
                 priority))

        existingAttributes = [ i[0]['attributes'] for i in self.influencers ]
        for influencer in values[self.attributeName]['influencers']:
            if influencer['attributes'] not in existingAttributes:
                self.AddRow(influencer)

        existingAttributes = [ i[0]['attributes'] for i in self.influencers ]
        for influencer in values[self.attributeName]['influencers']:
            index = existingAttributes.index(influencer['attributes'])
            _, row, value, weight, priority = self.influencers[index]
            w = influencer['weight']
            attrValue = getattr(influencer['attributes'], self.attributeName)
            UpdateValueUI(value, self.attributeName, attrValue)
            weight.text = '%.2f' % w
            priority.text = trinity.Tr2PostProcessPriority.GetNameFromValue(influencer['attributes'].priority)

    def AddRow(self, influencer):
        attr = influencer['attributes']
        value = getattr(attr, self.attributeName)
        weight = influencer['weight']
        row = GridContainer(parent=self.scroller, align=uiconst.TOTOP, height=30)
        row.columns = 4
        c1 = Container(parent=row, align=uiconst.TOALL)
        if self.showInspect:
            buttonContainer = Container(parent=c1, align=uiconst.TOLEFT, width=70, height=24, padding=2)
            Button(parent=buttonContainer, label='Inspect', density=Density.COMPACT, func=self.SetGraphiteSelection(influencer['attributes']))
        labelContainer = Container(parent=c1, align=uiconst.TOALL)
        eveLabel.EveLabelSmall(parent=labelContainer, text=('%s' % attr).replace('>', '').replace('<', ''), align=uiconst.CENTERLEFT)
        c2 = Container(parent=row, align=uiconst.TOALL)
        value = CreateValueUI(c2, self.attributeName, value, align=uiconst.CENTERRIGHT)
        c3 = Container(parent=row, align=uiconst.TOALL)
        weight = eveLabel.EveLabelSmall(parent=c3, text='%.2f' % weight, align=uiconst.CENTERRIGHT)
        c4 = Container(parent=row, align=uiconst.TOALL)
        priority = eveLabel.EveLabelSmall(parent=c4, text=trinity.Tr2PostProcessPriority.GetNameFromValue(attr.priority), align=uiconst.CENTERRIGHT)
        self.influencers.append((influencer,
         row,
         value,
         weight,
         priority))

    def SetGraphiteSelection(self, selection):

        def inner(_):
            ShowQuickMessage('Selected in Graphite')
            SetCurrentSelection(selection)

        return inner

    def Select(self, attributeName):
        self.attributeName = attributeName
        self.title.text = 'Influencers for ' + attributeName
        self.scroller.Flush()
        self.influencers = []


class PostProcessingDebugger(Window):
    default_windowID = 'postProcessingDebugger'

    def __init__(self, **kwargs):
        super(PostProcessingDebugger, self).__init__(**kwargs)
        self.name = 'Post Processing Debugger'
        self.windowID = 'postProcessingDebugger' + self.name
        self.running = True

    def Close(self, *args, **kwargs):
        Window.Close(self, *args, **kwargs)
        trinity.settings.SetValue('enablePostProcessDebugging', False)
        self.running = False

    def ShowUI(self):
        wnd = Window.Open(windowID=self.windowID)
        wnd.SetMinSize([400, 200])
        wnd.SetCaption(self.name)
        self.scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        self.topContainer = Container(name='top', parent=wnd.GetMainArea(), align=uiconst.TOALL, padBottom=10, padLeft=10)
        header = Container(parent=self.topContainer, align=uiconst.TOTOP, height=36)
        eveLabel.EveHeaderLarge(parent=header, align=uiconst.CENTER, text='Active Post Process Attributes', padTop=16)
        self.influencerContainer = InfluencerContainer(name='influencerContainer', parent=self.topContainer, align=uiconst.TOBOTTOM, width=250)
        Line(parent=self.topContainer, align=uiconst.TOBOTTOM, padTop=4, padBottom=4)
        Header(parent=self.topContainer, labels=['Attribute', 'Value'], equalAlign=True, align=uiconst.TOTOP, height=36)
        self.weightContainer = WeightContainer(name='weightContainer', parent=self.topContainer, align=uiconst.TOALL, selectCallback=self.SelectAttribute)
        self.running = True
        self.rows = []
        self.activeInfluencers = []
        self.values = {}
        uthread2.start_tasklet(self.UpdateRows)

    def SelectAttribute(self, entry):
        attribute = entry.attributeName
        self.influencerContainer.Select(attribute)

    def GetValues(self):
        trinity.settings.SetValue('enablePostProcessDebugging', True)
        return self.scene.GetPostProcessDebug()

    def UpdateRows(self):
        while self.running:
            values = self.GetValues()
            if values is not None:
                self.weightContainer.Update(values)
                self.influencerContainer.Update(values)
            blue.synchro.Sleep(250)


def OpenPostProcessDebugger():
    PostProcessingDebugger().ShowUI()
