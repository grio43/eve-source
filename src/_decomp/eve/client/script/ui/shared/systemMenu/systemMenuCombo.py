#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\systemMenuCombo.py
from carbonui import uiconst, Align
from carbonui.control.combo import Combo
from eve.client.script.ui.shared.systemMenu import systemMenuConst

class SystemMenuCombo(Combo):
    default_align = Align.TOTOP
    default_labelleft = systemMenuConst.LABEL_WIDTH
    default_padBottom = 8
