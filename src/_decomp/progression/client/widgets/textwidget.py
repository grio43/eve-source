#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\widgets\textwidget.py
from carbonui import uiconst
from progression.client.const import WIDGET_TEXT_BOLD_WHITE, COLOR_UI_HIGHLIGHTING
from progression.client.widgets.basewidget import BaseWidget

class TextWidget(BaseWidget):

    def ApplyAttributes(self, attributes):
        super(TextWidget, self).ApplyAttributes(attributes)
        self.uiHighlightingService = sm.GetService('uiHighlightingService')
        self.text = attributes.static_data.text
        self.bold = attributes.static_data.bold
        self._ConstructLabel()

    def _ConstructLabel(self):
        self.mainContainer.Flush()
        labelCls = self.GetLabelClass()
        self.label = labelCls(name='textWidget', parent=self.mainContainer, align=uiconst.TOPLEFT, text=self.text, wrapMode=uiconst.WRAPMODE_FORCEWORD, maxWidth=250)
        textWidth, textHeight = self.label.GetAbsoluteSize()
        self.parent.height = textHeight

    def OnMouseEnter(self, *args):
        self.label.SetTextColor(COLOR_UI_HIGHLIGHTING)
        super(TextWidget, self).OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        self.label.SetTextColor(WIDGET_TEXT_BOLD_WHITE)
        super(TextWidget, self).OnMouseExit(*args)
