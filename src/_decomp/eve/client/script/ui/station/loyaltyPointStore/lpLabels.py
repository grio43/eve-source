#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\lpLabels.py
from carbonui import uiconst
from eve.client.script.ui.control import eveLabel

class LPStoreLabel(eveLabel.EveLabelMedium):
    default_align = uiconst.TOTOP


class LPStoreEntryLabel(eveLabel.EveLabelMedium):
    default_maxLines = None


class LPStoreHeaderLabel(eveLabel.EveLabelSmall):
    default_align = uiconst.TOTOP
