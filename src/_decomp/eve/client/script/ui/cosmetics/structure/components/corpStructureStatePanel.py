#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\corpStructureStatePanel.py
from carbonui import uiconst, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from cosmetics.common.structures.exceptions import LicenseNotFoundException
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.loadingContainer import LoadingContainer, LoadingSpriteSize
from localization import GetByLabel
from structures import UPKEEP_STATE_FULL_POWER
from eve.client.script.ui.cosmetics.structure import const as paintToolConst, paintToolSignals
STATUS_ICON_SIZE = 32

class CorpStructureStatePanelLoadingContainer(LoadingContainer):

    def _ConstructFailureState(self, failureStateMessage, failureStateSubtext, retryBtnLabel):
        icon_cont = Container(parent=self._failureStateCont, name='iconCont', align=uiconst.TOLEFT, width=STATUS_ICON_SIZE, left=2)
        Sprite(parent=icon_cont, name='icon', align=uiconst.CENTER, width=STATUS_ICON_SIZE, height=STATUS_ICON_SIZE, texturePath='res:/UI/Texture/classes/paintTool/low_power.png')
        EveLabelMedium(parent=self._failureStateCont, align=uiconst.CENTERLEFT, left=STATUS_ICON_SIZE, text=GetByLabel('UI/Personalization/PaintTool/StructureStates/ErrorLoading'))


class CorpStructureStatePanel(Container):
    default_state = uiconst.UI_NORMAL

    def __init__(self, structure_data, **kw):
        self._structure_data = structure_data
        super(CorpStructureStatePanel, self).__init__(**kw)
        self._construct_layout()

    def Close(self):
        super(CorpStructureStatePanel, self).Close()

    def _construct_layout(self):
        self._loading_container = CorpStructureStatePanelLoadingContainer(parent=self, loadingSpriteSize=LoadingSpriteSize.SMALL)
        self._loading_container.loadingSpriteFadeDelay = 0.5
        self._loading_container.LoadContent(loadCallback=self._load)

    def _load(self):
        try:
            license_id = sm.GetService('cosmeticsSvc').get_structure_cosmetic_license_id_from_state(self._structure_data.instance_id, self._structure_data.location_id, True)
        except LicenseNotFoundException:
            license_id = None

        has_license = license_id is not None
        is_eligible = self._structure_data.is_eligible_for_painting()
        full_power = self._structure_data.upkeep_state == UPKEEP_STATE_FULL_POWER
        self._structure_data.license_id = license_id
        self.hint = ''
        if not is_eligible:
            icon_path = 'res:/UI/Texture/classes/paintTool/low_power.png'
            text = GetByLabel('UI/Personalization/PaintTool/StructureStates/Ineligible')
        elif has_license:
            icon_path = 'res:/UI/Texture/classes/paintTool/low_power.png'
            text = GetByLabel('UI/Personalization/PaintTool/StructureStates/HasLicense')
            license_data = sm.GetService('cosmeticsLicenseSvc').get_structure_paintwork_license(self._structure_data.instance_id, license_id)
            remaining_seconds = max(0, license_data.get_remaining_time())
            self.hint = GetByLabel('UI/Personalization/PaintTool/StructureStates/LicenseDurationHint', numDays=int(remaining_seconds / 86400))
        elif full_power:
            icon_path = 'res:/UI/Texture/classes/paintTool/full_power.png'
            text = GetByLabel(paintToolConst.UPKEEP_STATE_NAMES[self._structure_data.upkeep_state])
        else:
            icon_path = 'res:/UI/Texture/classes/paintTool/low_power.png'
            text = GetByLabel(paintToolConst.UPKEEP_STATE_NAMES[self._structure_data.upkeep_state])
        icon_cont = Container(parent=self, name='iconCont', align=uiconst.TOLEFT, width=STATUS_ICON_SIZE, left=2)
        Sprite(parent=icon_cont, name='icon', align=uiconst.CENTER, width=STATUS_ICON_SIZE, height=STATUS_ICON_SIZE, texturePath=icon_path)
        self._state_label = EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, text=text, left=STATUS_ICON_SIZE, color=TextColor.NORMAL, autoFadeSides=paintToolConst.LABEL_FADEOUT)
        paintToolSignals.on_structure_state_loaded(self._structure_data.instance_id)

    @staticmethod
    def get_size(structure_data, label_params):
        text = GetByLabel(paintToolConst.UPKEEP_STATE_NAMES[structure_data.upkeep_state])
        alt_text = GetByLabel('UI/Personalization/PaintTool/StructureStates/ErrorLoading')
        length = uicore.font.MeasureTabstops([(text,) + label_params])[0]
        alt_length = uicore.font.MeasureTabstops([(alt_text,) + label_params])[0]
        return max(length, alt_length) + STATUS_ICON_SIZE
