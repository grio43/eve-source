#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\linkLabel.py
from carbonui import const as uiconst
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label

class LinkLabel(Label):
    default_state = uiconst.UI_CLICK
    default_color = (1, 0.65, 0, 1)
    default_highlight = Color.WHITE

    def ApplyAttributes(self, attributes):
        super(LinkLabel, self).ApplyAttributes(attributes)
        self.baseColor = attributes.get('baseColor', self.default_color)
        self.highlightColor = attributes.get('highlightColor', self.default_highlight)
        self.function = attributes.get('function', None)
        self.SetTextColor(self.baseColor)

    def OnMouseEnter(self, *args):
        self.SetTextColor(self.highlightColor)

    def OnMouseExit(self, *args):
        self.SetTextColor(self.baseColor)

    def OnClick(self, *args):
        self.function()
