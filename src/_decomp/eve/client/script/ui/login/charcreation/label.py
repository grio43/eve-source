#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\label.py
from carbonui import uiconst
from eve.client.script.ui.control import eveLabel
import charactercreator.const

class CCLabel(eveLabel.Label):
    default_bold = 1
    default_color = charactercreator.const.COLOR
    default_letterspace = 1
    default_state = uiconst.UI_DISABLED
