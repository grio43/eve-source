#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controlCatalogWindow.py
import uthread2
from carbonui import fontconst, uiconst, IdealSize
from carbonui.button.group import ButtonGroup
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.tabGroup import TabGroup
from carbonui.control.window import Window
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.treeViewEntry import TreeViewEntryHeader
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.devtools.script.uiControlCatalog import samplesChangedEventHandler, samplePage

class ControlCatalogWindow(Window):
    default_windowID = 'ControlCatalogWindow'
    default_caption = 'UI Control Catalog'
    default_width = IdealSize.SIZE_1200
    default_height = IdealSize.SIZE_960
    default_minSize = (IdealSize.SIZE_720, IdealSize.SIZE_480)

    def ApplyAttributes(self, attributes):
        self._panels = []
        super(ControlCatalogWindow, self).ApplyAttributes(attributes)
        ControlCataLogPanel(parent=self.sr.main, folderName='controls', content_padding=self.content_padding)


class ControlCataLogPanel(Container):

    def ApplyAttributes(self, attributes):
        super(ControlCataLogPanel, self).ApplyAttributes(attributes)
        self.folderName = attributes.folderName
        self.entriesByID = {}
        self.samplePageData = None
        self.currSample = None
        self._content_padding = attributes.get('content_padding', (0, 0, 0, 0))
        self._left_side_fill = None
        self.constructThread = None
        self.populate_scroll_tasklet = None
        self._selected_node_id = None
        self.ConstuctLayout()
        samplesChangedEventHandler.register_for_sample_modified_event(self.OnSampleModified)
        samplesChangedEventHandler.register_for_sample_added_or_removed(self.OnSampleAddedOrRemoved)
        self.filterEdit.SetFocus()

    @property
    def content_padding(self):
        return self._content_padding

    @content_padding.setter
    def content_padding(self, value):
        if self._content_padding != value:
            self._content_padding = value
            self._update_content_padding()

    def ConstuctLayout(self):
        self.leftCont = DragResizeCont(name='leftCont', parent=self, align=uiconst.TOLEFT, defaultSize=260, minSize=200, maxSize=400, padRight=8)
        self.mainButtonGroup = ButtonGroup(name='mainButtonGroup', parent=self, padTop=16)
        self.bottomCont = DragResizeCont(name='topCont', parent=self, align=uiconst.TOBOTTOM_PROP, settingsID='ControlCatalogWindowSampleCont', minSize=0.1, maxSize=0.9, defaultSize=0.5, clipChildren=True, show_line=True)
        tabCont = ContainerAutoSize(name='tabCont', parent=self, align=uiconst.TOTOP)
        self._left_side_fill = PanelUnderlay(bgParent=self.leftCont.mainCont, padding=self._get_left_side_fill_padding())
        self.filterEdit = QuickFilterEdit(parent=self.leftCont.mainCont, align=uiconst.TOTOP, callback=self.OnFilterEdit, padding=(0, 16, 16, 0))
        self.controlScroll = ScrollContainer(parent=self.leftCont.mainCont, innerPadding=(0, 16, 0, 0))
        self.PopulateScroll()
        self.tabGroup = TabGroup(parent=tabCont, align=uiconst.TOTOP, callback=self.OnTabSelected, padBottom=0)
        self.sampleDescriptionLabel = eveLabel.EveLabelMedium(name='sampleDescriptionLabel', parent=tabCont, align=uiconst.TOTOP, padding=(32, 32, 32, 0))
        sampleParent = ScrollContainer(name='sampleParent', parent=self, innerPadding=16, padTop=16, centerContent=True)
        self.sampleCont = ContainerAutoSize(name='sampleCont', parent=sampleParent, align=uiconst.CENTERTOP)
        self.codeSnippetPanel = EditPlainText(name='codeSnippetPanel', parent=self.bottomCont, align=uiconst.TOALL, ignoreTags=True, readonly=True, fontPath=fontconst.CONSOLA_PATH, fontsize=14)
        self.ConstructMainButtonGroup()

    def OnFilterEdit(self, *args):
        self.PopulateScroll()

    def OnSampleModified(self, event):
        self.samplePageData.ParseDataFromFile()
        self.SetSelectedControl(self.samplePageData)

    def OnSampleAddedOrRemoved(self, event):
        self.PopulateScroll()

    def ConstructMainButtonGroup(self):
        self.mainButtonGroup.AddButton('Open in editor', self.OpenSampleCodeInEditor, hint='Open sample code in editor. Samples are live-reloaded as changes are made to code.')

    def OpenSampleCodeInEditor(self, *args):
        self.samplePageData.OpenSampleCodeInEditor()

    def BrowseControls(self, *args):
        samplePage.browse_controls()

    def PopulateScroll(self):
        if self.populate_scroll_tasklet:
            self.populate_scroll_tasklet.kill()
        self.populate_scroll_tasklet = uthread2.start_tasklet(self._PopulateScroll)

    def _PopulateScroll(self):
        self.controlScroll.Flush()
        for data in self._GetNodesToConstruct():
            TreeViewEntryHeader(parent=self.controlScroll, data=data)
            if self.samplePageData and self.samplePageData.GetID() == data.GetID():
                self.SetSamplePageData(data)

    def _GetNodesToConstruct(self):
        filterTxt = self.filterEdit.GetValue()
        root_node = samplePage.get_control_data(self.folderName, filterTxt)
        root_node.on_click.connect(self.OnNodeClicked)
        if self._selected_node_id:
            self._UpdateSelectedNode(root_node)
        return root_node.children

    def OnNodeExpanded(self, node, animate = True):
        root_node = node.GetRootNode()
        for top_node in root_node.children:
            if not node.IsAncestor(top_node) and not node == top_node:
                top_node.SetCollapsed()

    def _UpdateSelectedNode(self, root_node):
        node = root_node.GetChildByID(self._selected_node_id)
        if node:
            node.SetSelected(animate=False)
        else:
            self._selected_node_id = None

    def RegisterID(self, entry, entryID):
        if entryID in self.entriesByID:
            raise ValueError('Same entry registered again: %s' % entryID)
        self.entriesByID[entryID] = entry

    def UnregisterID(self, entryID):
        self.entriesByID.pop(entryID, None)

    def OnNodeClicked(self, node):
        if node.children:
            node.ToggleExpanded()
        else:
            root_node = node.GetRootNode()
            root_node.DeselectAll()
            node.SetSelected()
            self._selected_node_id = node.GetID()
            self.tabGroup.SelectByID(0, silent=True)
            self.SetSelectedControl(node)

    def SetSelectedControl(self, data):
        self.SetSamplePageData(data)
        self.codeSnippetPanel.Clear()
        self.sampleCont.Flush()
        self.ReloadSamples()
        self.UpdateCodeEdit()

    def SetSamplePageData(self, data):
        self.samplePageData = data
        self.SetCurrSample(self.GetCurrSampleNum())

    def GetCurrSampleNum(self):
        return self.tabGroup.GetSelectedID() or 0

    def UpdateCodeEdit(self):
        code = self.currSample.get_snippet()
        self.bottomCont.display = bool(code)
        self.codeSnippetPanel.SetText(code.strip(), html=False)

    def GetCodeText(self):
        return self.codeSnippetPanel.GetAllText()

    def ReloadSamples(self, *args):
        sampleNum = self.GetCurrSampleNum()
        self.ReconstructTabs()
        self.tabGroup.SelectByID(sampleNum)

    def ReconstructTabs(self):
        self.tabGroup.Flush()
        num_samples = self.samplePageData.GetNumSamples()
        for i in range(num_samples):
            sample = self.samplePageData.GetSample(i)
            tabName = sample.get_name()
            self.tabGroup.AddTab(tabName, tabID=i)

    def OnTabSelected(self, sampleNum, *args):
        self.SetCurrSample(sampleNum)
        self.ReloadCurrentSample()
        self.UpdateCodeEdit()

    def SetCurrSample(self, sampleNum):
        if self.currSample:
            self.currSample.on_code_changed.disconnect(self.OnSampleCodeChanged)
        self.currSample = self.samplePageData.GetSample(sampleNum)
        self.currSample.on_code_changed.connect(self.OnSampleCodeChanged)

    def OnSampleCodeChanged(self):
        self.UpdateCodeEdit()

    def ReloadCurrentSample(self):
        self.sampleCont.Flush()
        uicore.animations.FadeTo(self.sampleCont, 0.0, 1.0, 0.1)
        if self.samplePageData.GetNumSamples():
            self.ExecuteCode(self.GetCurrSampleNum())

    def ExecuteCode(self, sampleNum):
        if self.constructThread:
            self.constructThread.kill()
        self.constructThread = uthread2.start_tasklet(self._ConstructSample)
        self.UpdateSampleDescriptionLabel(self.currSample.get_description())

    def _ConstructSample(self):
        self.currSample.construct_sample(self.sampleCont)
        self.constructThread = None

    def UpdateSampleDescriptionLabel(self, sampleName):
        if sampleName:
            self.sampleDescriptionLabel.Show()
            self.sampleDescriptionLabel.text = '<center>' + sampleName
        else:
            self.sampleDescriptionLabel.Hide()
            self.sampleDescriptionLabel.text = ''

    def _update_content_padding(self):
        if self._left_side_fill is not None:
            self._left_side_fill.padding = self._get_left_side_fill_padding()

    def _get_left_side_fill_padding(self):
        pad_left, pad_top, pad_right, pad_bottom = self._content_padding
        return (-pad_left,
         0,
         0,
         -pad_bottom)
