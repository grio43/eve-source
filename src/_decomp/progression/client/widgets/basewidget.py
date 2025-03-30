#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\widgets\basewidget.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelMedium

class BaseWidget(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(BaseWidget, self).ApplyAttributes(attributes)
        self.bold = attributes.static_data.bold
        self.mainContainer = Container(name='mainContainer', parent=self, align=uiconst.TOLEFT, width=250)
        self.uiHighlightingService = sm.GetService('uiHighlightingService')
        self._static_highlighted_space_object_ids = getattr(attributes.static_data, 'highlight_space_object_ids', [])
        self._static_highlighted_type_ids = getattr(attributes.static_data, 'highlight_type_ids', [])

    def GetLabelClass(self):
        if self.bold:
            return EveLabelMediumBold
        else:
            return EveLabelMedium

    def GetDynamicHighlightedObjectIDs(self):
        return []

    def GetDynamicHighlightedTypeIDs(self):
        return []

    def GetDynamicHighlightedItemIDs(self):
        return []

    def OnMouseEnter(self, *args):
        for type_id in self._static_highlighted_type_ids + self.GetDynamicHighlightedTypeIDs():
            self.uiHighlightingService.highlight_space_object_by_type(type_id, '', '', show_box=False)

        for space_object_id in self._static_highlighted_space_object_ids + self.GetDynamicHighlightedObjectIDs():
            self.uiHighlightingService.highlight_space_object_by_dungeon_object_id(space_object_id, '', '', None, None, False)

        for item_id in self.GetDynamicHighlightedItemIDs():
            self.uiHighlightingService.highlight_space_object_by_item_id(item_id, '', '', None, None, False)

    def OnMouseExit(self, *args):
        self.uiHighlightingService.clear_space_object_highlighting()
