#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\numRunsIndicator.py
import eveformat
import eveicon
from carbonui import TextBody, Align, PickState, uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from eve.client.script.ui import eveColor
from localization import GetByLabel

class NumRunsIndicator(ContainerAutoSize):
    default_minHeight = 30
    default_minWidth = 30
    default_state = uiconst.UI_NORMAL

    def __init__(self, num_runs, licence_type, **kw):
        super(NumRunsIndicator, self).__init__(**kw)
        self.license_type = licence_type
        self.num_runs = num_runs
        StretchSpriteHorizontal(name='runs_icon', bgParent=self, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/overlays/runs_remaining_bg.png', leftEdgeSize=15, rightEdgeSize=15)
        if licence_type == ComponentLicenseType.LIMITED:
            TextBody(name='runs_remaining_label', parent=self, align=Align.CENTER, text=eveformat.number_readable_short(num_runs), padding=(9, 0, 9, 0), color=eveColor.WHITE)
        else:
            Sprite(parent=self, align=Align.CENTER, pos=(0, 0, 16, 16), texturePath=eveicon.infinity, pickState=PickState.OFF)

    def GetHint(self):
        if self.license_type == ComponentLicenseType.UNLIMITED:
            return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/UnlimitedDesignElement')
        else:
            return u'{}\n{} X {}'.format(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/LimitedDesignElement'), self.num_runs, GetByLabel('UI/Personalization/ShipSkins/SKINR/Sequencing/SequencingRuns'))
