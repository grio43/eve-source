#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\structureCosmetics.py
import evetypes
import uthread
import random
import carbonui.const as uiconst
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from cosmetics.common.structures.const import PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS, StructurePaintSlot
from cosmetics.common.structures.exceptions import LicenseNotFoundException
from cosmetics.common.structures.fitting import StructurePaintwork
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.entries.generic import Generic
from cosmetics.client.messengers.cosmetics.structures.requestMessenger import PublicRequestsMessenger
from carbon.common.script.sys.serviceConst import ROLE_GML
from structures import UPKEEP_STATE_FULL_POWER

class StructurePaintsTable(Window):
    __guid__ = 'StructurePaintsTable'
    default_width = 600
    default_height = 600
    default_windowID = 'structurePaintsWindow'
    default_minSize = [default_width, default_height]

    def ApplyAttributes(self, attributes):
        super(StructurePaintsTable, self).ApplyAttributes(attributes)
        self.SetCaption('Structure Nanocoating Licenses')
        self.scroll = Scroll(name='scroll', parent=self.sr.maincontainer, align=uiconst.TOALL)
        self.scroll.LoadHeaders(self._get_headers())
        self._fetch_and_populate()

    def _fetch_and_populate(self):
        publicGatewaySvc = sm.GetService('publicGatewaySvc')
        if publicGatewaySvc.is_available():
            cosmetic_states_messenger = PublicRequestsMessenger(publicGatewaySvc)
            structures = self._get_structures_list()
            structure_licenses = sm.GetService('cosmeticsLicenseSvc').get_structure_licenses_for_corporation()
            for structure in structures:
                uthread.new(self._fetch_and_populate_thread, cosmetic_states_messenger, structure_licenses, structure)

    def _fetch_and_populate_thread(self, cosmetic_states_messenger, structure_licenses, structure):
        type_id = structure['typeID']
        upkeep_state = structure['upkeepState']
        structure_id = structure['structureID']
        solar_system_id = structure['solarSystemID']
        license_data = structure_licenses.get(structure_id, None)
        cosmetic_state = None
        if type_id in PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS:
            _, cosmetic_state = cosmetic_states_messenger.get_request(structure_id, solar_system_id)
        license_error = False
        disabled_license = license_data is not None and upkeep_state is not UPKEEP_STATE_FULL_POWER
        if license_data:
            remaining_seconds = license_data.get_remaining_time()
            remaining_days = int(remaining_seconds / 86400)
            remaining_seconds = remaining_seconds - remaining_days * 86400
            remaining_hours = int(remaining_seconds / 3600)
            remaining_seconds = remaining_seconds - remaining_hours * 3600
            remaining_minutes = int(remaining_seconds / 60)
            remaining_seconds = int(remaining_seconds - remaining_minutes * 60)
            remaining_time = '%s days %s hours %s min %s sec' % (remaining_days,
             remaining_hours,
             remaining_minutes,
             remaining_seconds)
        else:
            remaining_time = '-'
        data = [ str(x) or '' for x in [structure_id,
         cfg.evelocations.Get(structure_id).name,
         evetypes.GetName(type_id),
         solar_system_id,
         'Yes' if upkeep_state == UPKEEP_STATE_FULL_POWER else 'No',
         license_data.id if license_data else None,
         'ERROR' if license_error else (license_data.activation_timestamp if license_data else '-'),
         'ERROR' if license_error else ('%s days' % int(license_data.duration / 86400) if license_data else '-'),
         'ERROR' if license_error else remaining_time,
         cosmetic_state.get_slot(StructurePaintSlot.PRIMARY) or '-' if cosmetic_state else ('disabled' if disabled_license else '-'),
         cosmetic_state.get_slot(StructurePaintSlot.SECONDARY) or '-' if cosmetic_state else ('disabled' if disabled_license else '-'),
         cosmetic_state.get_slot(StructurePaintSlot.DETAILING) or '-' if cosmetic_state else ('disabled' if disabled_license else '-')] ]
        node = GetFromClass(StructureEntry, {'label': '<t>'.join(data),
         'structure': structure,
         'state': cosmetic_state})
        self.scroll.AddEntries(-1, [node])

    def _add_entry(self, data):
        pass

    def _get_headers(self):
        return ['structure id',
         'structure name',
         'structure type',
         'solar system id',
         'full power',
         'license id',
         'issued date',
         'duration',
         'remaining duration',
         'primary slot',
         'secondary slot',
         'detailing slot']

    def _get_structures_list(self):
        structures = sm.GetService('structureDirectory').GetCorporationStructures()
        return structures.values()


class StructureEntry(Generic):
    __guid__ = 'listentry.StructureEntry'
    __nonpersistvars__ = []

    def __init__(self, **kw):
        self.structure_id = None
        super(StructureEntry, self).__init__(**kw)

    def GetMenu(self):
        if session and session.role & ROLE_GML:
            menu = [['Issue License', self._admin_issue_license]]
            return menu

    def Load(self, node):
        super(StructureEntry, self).Load(node)
        self.structure_id = node['structure'].structureID

    def _admin_issue_license(self, *args):
        paintwork = StructurePaintwork()
        paintwork.set_slot(StructurePaintSlot.PRIMARY, random.randint(1, 99))
        paintwork.set_slot(StructurePaintSlot.SECONDARY, random.randint(1, 99))
        paintwork.set_slot(StructurePaintSlot.DETAILING, random.randint(1, 99))
        wnd = AdminIssueLicenseWnd()
        result = wnd.ShowModal()
        if result == uiconst.ID_OK:
            duration = wnd.duration.GetValue() * 60
            cost = wnd.cost.GetValue()
            sm.GetService('cosmeticsLicenseSvc').admin_request_license_for_structures([self.structure_id], paintwork, duration, cost)


class AdminIssueLicenseWnd(Window):
    default_width = 400
    default_height = 300

    def __init__(self, *args, **kwargs):
        super(AdminIssueLicenseWnd, self).__init__(*args, **kwargs)
        self.MakeUnResizeable()
        self.DefineButtons(buttons=uiconst.OK, okLabel='OK')
        self._construct_layout()

    def _construct_layout(self):
        EveLabelMedium(parent=self.content, align=uiconst.TOTOP, text='Duration (in minutes)')
        self.duration = SingleLineEditInteger(parent=self.content, align=uiconst.TOTOP)
        EveLabelMedium(parent=self.content, align=uiconst.TOTOP, text='EM Cost')
        self.cost = SingleLineEditInteger(parent=self.content, align=uiconst.TOTOP)
        EveLabelMedium(parent=self.content, align=uiconst.TOTOP, text="Notes: <br>- Paints are selected randomly.<br>- License expiry isn't processed instantly, it can take up to 5 minutes for an expired license to be reflected on the structure.")
