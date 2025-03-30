#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\systemMenuHeader.py
import carbonui
from carbonui import uiconst, TextColor
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.themeColored import FillThemeColored

class SystemMenuHeader(ContainerAutoSize):
    default_name = 'SystemMenuHeader'
    default_align = uiconst.TOTOP
    default_alignMode = uiconst.TOTOP
    default_padTop = 48
    default_padBottom = 8

    def ApplyAttributes(self, attributes):
        super(SystemMenuHeader, self).ApplyAttributes(attributes)
        carbonui.TextHeader(name='header1', parent=self, align=uiconst.TOTOP, text=attributes.text, color=TextColor.HIGHLIGHT)
