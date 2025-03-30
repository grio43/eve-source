#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\workforce\client\data_types.py
import sovereignty.workforce.workforceConst as workforceConst

class WorkforceConfiguration(object):
    _hub_id = None
    _inactive = None
    _import_configuration = None
    _export_configuration = None
    _transit = None

    def __init__(self, hub_id, inactive = False, import_configuration = None, export_configuration = None, transit = False):
        self._hub_id = hub_id
        self._inactive = inactive
        self._import_configuration = import_configuration
        self._export_configuration = export_configuration
        self._transit = transit

    @property
    def hub_id(self):
        return self._hub_id

    @property
    def inactive(self):
        return self._inactive

    @property
    def import_configuration(self):
        return self._import_configuration

    @property
    def export_configuration(self):
        return self._export_configuration

    @property
    def transit(self):
        return self._transit

    @classmethod
    def create_from_proto(cls, hub_id, workforce_configuration):
        if workforce_configuration.WhichOneof('mode') == 'inactive':
            return WorkforceConfiguration(hub_id, inactive=True)
        if workforce_configuration.WhichOneof('mode') == 'transit':
            return WorkforceConfiguration(hub_id, transit=True)
        if workforce_configuration.WhichOneof('mode') == 'export_settings':
            if workforce_configuration.export_settings.WhichOneof('export_destination') == 'destination_system':
                destination_system_id = workforce_configuration.export_settings.destination_system.sequential
            elif workforce_configuration.export_settings.WhichOneof('export_destination') == 'no_destination':
                destination_system_id = None
            amount = workforce_configuration.export_settings.amount
            export_config = WorkforceExportConfiguration(hub_id, destination_system_id, amount)
            return WorkforceConfiguration(hub_id, export_configuration=export_config)
        if workforce_configuration.WhichOneof('mode') == 'import_settings':
            source_system_ids = {x.source.sequential for x in workforce_configuration.import_settings.sources}
            import_config = WorkforceImportConfiguration(hub_id, source_system_ids)
            return WorkforceConfiguration(hub_id, import_configuration=import_config)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.hub_id == other.hub_id and self.inactive == other.inactive and self.import_configuration == other.import_configuration and self.export_configuration == other.export_configuration and self.transit == other.transit

    def __repr__(self):
        return '<ImportConfiguration %s>' % self.__dict__

    def get_mode(self):
        if self.inactive:
            return workforceConst.MODE_IDLE
        if self.transit:
            return workforceConst.MODE_TRANSIT
        if self.import_configuration:
            return workforceConst.MODE_IMPORT
        if self.export_configuration:
            return workforceConst.MODE_EXPORT


class WorkforceImportConfiguration(object):
    _hub_id = None
    _source_system_ids = set()

    def __init__(self, hub_id, source_system_ids):
        self._hub_id = hub_id
        self._source_system_ids = source_system_ids

    @property
    def hub_id(self):
        return self._hub_id

    @property
    def source_system_ids(self):
        return self._source_system_ids

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.hub_id == other.hub_id and self.source_system_ids == other.source_system_ids

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<WorkforceImportConfiguration %s>' % self.__dict__


class WorkforceExportConfiguration(object):
    _hub_id = None
    _source_system_ids = set()

    def __init__(self, hub_id, destination_system_id, amount):
        self._hub_id = hub_id
        self._destination_system_id = destination_system_id
        self._amount = amount

    @property
    def hub_id(self):
        return self._hub_id

    @property
    def destination_system_id(self):
        return self._destination_system_id

    @property
    def amount(self):
        return self._amount

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.hub_id == other.hub_id and self.destination_system_id == other.destination_system_id and self.amount == other.amount

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<WorkforceExportConfiguration %s>' % self.__dict__


class WorkforceState(object):
    amount_per_period = None
    period = None
    min_quantity = None
    max_quantity = None

    def __init__(self, hub_id, inactive = False, import_state = None, export_state = None, transit_state = None):
        self._hub_id = hub_id
        self._inactive = inactive
        self._import_state = import_state
        self._export_state = export_state
        self._transit_state = transit_state

    @property
    def hub_id(self):
        return self._hub_id

    @property
    def inactive(self):
        return self._inactive

    @property
    def import_state(self):
        return self._import_state

    @property
    def export_state(self):
        return self._export_state

    @property
    def transit_state(self):
        return self._transit_state

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.hub_id == other.hub_id and self.inactive == other.inactive and self.import_state == other.import_state and self.export_state == other.export_state and self.transit_state == other.transit_state

    def __repr__(self):
        return '<WorkforceState %s>' % self.__dict__

    @classmethod
    def create_from_proto(cls, hub_id, workforce_state):
        if workforce_state.WhichOneof('mode') == 'inactive':
            return WorkforceState(hub_id, inactive=True)
        if workforce_state.WhichOneof('mode') == 'transit':
            return WorkforceState(hub_id, transit_state=WorkforceTransitState(hub_id))
        if workforce_state.WhichOneof('mode') == 'export_state':
            export_state = workforce_state.export_state
            if export_state.WhichOneof('exporting') == 'connected':
                destination_system_id = export_state.connected.destination_system.sequential
                amount = workforce_state.export_state.connected.exported_quantity
            elif export_state.WhichOneof('exporting') == 'disconnected':
                destination_system_id = None
                amount = workforce_state.export_state.disconnected.local_reserve
            export_state = WorkforceExportState(hub_id, destination_system_id, amount)
            return WorkforceState(hub_id, export_state=export_state)
        if workforce_state.WhichOneof('mode') == 'import_state':
            amount_by_source_system_id = {x.source.sequential:x.amount for x in workforce_state.import_state.sources}
            import_state = WorkforceImportState(hub_id, amount_by_source_system_id)
            return WorkforceState(hub_id, import_state=import_state)

    def get_mode(self):
        if self.inactive:
            return workforceConst.MODE_IDLE
        if self.transit_state:
            return workforceConst.MODE_TRANSIT
        if self.import_state:
            return workforceConst.MODE_IMPORT
        if self.export_state:
            return workforceConst.MODE_EXPORT


class WorkforceImportState(object):
    _hub_id = None
    _source_system_ids = set()

    def __init__(self, hub_id, amount_by_source_system_id):
        self._hub_id = hub_id
        self._amount_by_source_system_id = amount_by_source_system_id

    @property
    def hub_id(self):
        return self._hub_id

    @property
    def amount_by_source_system_id(self):
        return self._amount_by_source_system_id

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.hub_id == other.hub_id and self.amount_by_source_system_id == other.amount_by_source_system_id

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<WorkforceImportState %s>' % self.__dict__


class WorkforceExportState(object):
    _hub_id = None
    _source_system_ids = set()

    def __init__(self, hub_id, destination_system_id, amount):
        self._hub_id = hub_id
        self._destination_system_id = destination_system_id
        self._amount = amount

    @property
    def hub_id(self):
        return self._hub_id

    @property
    def destination_system_id(self):
        return self._destination_system_id

    @property
    def amount(self):
        return self._amount

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.hub_id == other.hub_id and self.destination_system_id == other.destination_system_id and self.amount == other.amount

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<WorkforceExportState %s>' % self.__dict__


class WorkforceTransitState(object):
    _hub_id = None

    def __init__(self, hub_id):
        self._hub_id = hub_id

    @property
    def hub_id(self):
        return self._hub_id

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.hub_id == other.hub_id

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<WorkforceTransitState %s>' % self.__dict__


class WorkforceNetworkedHub(object):
    _hub_id = None
    _system_id = None
    _configuration = None
    _state = None

    def __init__(self, hub_id, system_id, configuration, state):
        self._hub_id = hub_id
        self._system_id = system_id
        self._configuration = configuration
        self._state = state

    @property
    def hub_id(self):
        return self._hub_id

    @property
    def system_id(self):
        return self._system_id

    @property
    def configuration(self):
        return self._configuration

    @property
    def state(self):
        return self._state

    @classmethod
    def create_from_proto(cls, hub_id, solar_system, configuration, state):
        workforceConfiguration = WorkforceConfiguration.create_from_proto(hub_id, configuration)
        workforceState = WorkforceState.create_from_proto(hub_id, state)
        return WorkforceNetworkedHub(hub_id, solar_system, workforceConfiguration, workforceState)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.hub_id == other.hub_id and self.system_id == other.system_id and self.configuration == other.configuration and self.state == other.state

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<WorkforceNetworkedHub %s>' % self.__dict__
