#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\moonmining\autoMoonMining\client\auto_moon_miner_window.py
import uthread2
from eve.common.script.sys import idCheckers
import inventorycommon.const as invConst
from appConst import corpRoleStationManager
import localization
import evetypes
import gametime
import trinity
from localization.formatters import FormatTimeIntervalShortWritten
from carbon.common.lib.const import SEC, HOUR
import carbonui
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.itemIcon import ItemIcon
from moonmining.autoMoonMining.common import REAGENT_FUEL_TYPE
from spacecomponents.common.data import get_space_component_for_type
from spacecomponents.common.componentConst import AUTO_MOON_MINER
from dogma.const import attributeServiceModuleFuelAmount
from dogma.data import get_type_attribute
from eve.client.script.ui.control.gauge import Gauge
import eveformat
from evelink.client import location_link, owner_link
from eve.client.script.ui.moonmining import GetPrice
from eve.client.script.ui.shared.ledger.ledgerUtil import GetColorForBaseTypeID
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.line import Line
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
from structures import SETTING_AUTOMOONMINING, GetAccessErrorLabel
from eveexceptions import UserError
DETAILS_UPDATE_INTERVAL = 900

def open_auto_moon_miner(item_id, type_id):
    if not idCheckers.IsAutoMoonMiner(type_id):
        return
    structure_info = sm.GetService('structureDirectory').GetStructureInfo(item_id)
    _check_has_access(structure_info.ownerID, item_id)
    AutoMoonMinerWindow.Open(windowInstanceID=item_id, structure_id=item_id, structure_type_id=type_id, structure_info=structure_info)


def _check_has_access(owner_id, structure_id):
    if session.corpid == owner_id and bool(session.corprole & corpRoleStationManager):
        return
    if sm.GetService('structureSettings').CharacterHasSetting(structure_id, SETTING_AUTOMOONMINING):
        return
    raise UserError(GetAccessErrorLabel(SETTING_AUTOMOONMINING), {'structureName': cfg.evelocations.Get(structure_id).locationName})


class AutoMoonMinerWindow(Window):
    __guid__ = 'AutoMoonMinerWindow'
    default_width = 700
    default_height = 450
    default_minSize = [500, 450]
    default_isCompact = True
    default_windowID = 'auto_moon_miner'
    default_captionLabelPath = 'UI/Moonmining/AutoMoonMiner/DetailsWindowName'
    default_iconNum = 'res:/ui/Texture/WindowIcons/moonDrillScheduler.png'
    _structure_id = None
    _structure_type_id = None
    _solar_system_id = None
    _structure_info = None
    _mining_cycle_time = None
    _reagents_per_cycle = None
    _moon_id = None
    _next_harvest_time = None
    _available_fuel = None
    _output_materials = None
    _output_capacity_remaining = None
    _fuel_entries = {}

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self._structure_id = attributes.structure_id
        self._structure_type_id = attributes.structure_type_id
        self._structure_info = attributes.structure_info
        self._solar_system_id = self._structure_info.solarSystemID
        space_component = get_space_component_for_type(self._structure_type_id, AUTO_MOON_MINER)
        self._mining_cycle_time = space_component.miningCycleTime
        self._reagents_per_cycle = space_component.reagentsConsumedPerCycle
        self._main_container = ContainerAutoSize(name='_main_container', parent=self.content, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, minHeight=400)
        LoadingWheel(parent=self._main_container, align=carbonui.Align.CENTER, width=64, height=64)
        uthread2.start_tasklet(self._layout)

    def _layout(self):
        self._update_details()
        self._main_container.Flush()
        self._construct_top()
        self._construct_fuel()
        self._construct_output()
        _, height = self.GetWindowSizeForContentSize(height=self._main_container.height)
        height += self.sr.headerParent.height + self.content_padding[3]
        self.SetMinSize((self.default_minSize[0], height))
        uthread2.start_tasklet(self._update_details_routine)
        uthread2.start_tasklet(self._update_time_routine)

    def _construct_top(self):
        container = Container(name='top_container', parent=self._main_container, height=128, align=carbonui.Align.TOTOP, padBottom=16)
        ItemIcon(parent=container, align=carbonui.Align.TOLEFT, width=128, typeID=invConst.typeMoon, itemID=self._moon_id)
        text_container = Container(parent=container, align=carbonui.Align.TOALL, padLeft=16)
        carbonui.TextBody(parent=text_container, pickState=carbonui.PickState.ON, align=carbonui.Align.TOTOP, text=location_link(self._structure_id))
        carbonui.TextBody(parent=text_container, pickState=carbonui.PickState.ON, align=carbonui.Align.TOTOP, text=owner_link(self._structure_info.ownerID))
        carbonui.TextBody(parent=text_container, align=carbonui.Align.TOTOP, text=cfg.evelocations.Get(self._moon_id).name, color=carbonui.TextColor.SECONDARY)
        container = Container(parent=text_container, align=carbonui.Align.TOTOP, padTop=16, height=24)
        drill_status_container = ContainerAutoSize(parent=container, align=carbonui.Align.TOLEFT, padRight=6)
        self._drill_status = carbonui.TextBody(parent=drill_status_container, align=carbonui.Align.CENTERLEFT)
        self._drill_status_info = InfoGlyphIcon(parent=container, align=carbonui.Align.TOLEFT, hint='')
        self._time_until_output = carbonui.TextBody(parent=text_container, align=carbonui.Align.TOTOP)
        self._remaining_capacity_label = carbonui.TextBody(parent=text_container, align=carbonui.Align.TOTOP)

    def _construct_fuel(self):
        container = ContainerAutoSize(name='fuel_container', parent=self._main_container, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, padBottom=16)
        carbonui.TextBody(parent=container, align=carbonui.Align.TOTOP, text=localization.GetByLabel('UI/Moonmining/AutoMoonMiner/FuelState'), color=carbonui.TextColor.SECONDARY, padBottom=8, bold=True)
        grid_container = GridContainer(parent=container, align=carbonui.Align.TOTOP, height=24, columns=4, lines=1, contentSpacing=(4, 4))
        Line(parent=container, align=carbonui.Align.TOTOP, top=-2, padBottom=4)
        _add_column(localization.GetByLabel('UI/Moonmining/AutoMoonMiner/FuelTypeColumn'), grid_container)
        _add_column(localization.GetByLabel('UI/Moonmining/AutoMoonMiner/QuantityColumn'), grid_container)
        _add_column(localization.GetByLabel('UI/Moonmining/AutoMoonMiner/ExpirationColumn'), grid_container)
        _add_column(localization.GetByLabel('UI/Moonmining/AutoMoonMiner/ConsumptionRateColumn'), grid_container)
        fuel_per_cycle = int(get_type_attribute(invConst.typeStandupMetenoxMoonDrill, attributeServiceModuleFuelAmount))
        self._fuel_entries[invConst.groupFuelBlock] = FuelEntry(parent=container, text=evetypes.GetGroupNameByGroup(invConst.groupFuelBlock), consumption=fuel_per_cycle, cycle_time=3600)
        self._fuel_entries[REAGENT_FUEL_TYPE] = FuelEntry(parent=container, text=evetypes.GetName(REAGENT_FUEL_TYPE), consumption=self._reagents_per_cycle, cycle_time=self._mining_cycle_time)

    def _construct_output(self):
        output_materials_per_cycle = sm.GetService('autoMoonMiner').get_mining_cycle_output(self._solar_system_id, self._structure_id)
        self._output_materials_section = OutputMaterialsSection(parent=self._main_container, materials_per_cycle=output_materials_per_cycle, materials_in_bay=self._output_materials)

    @property
    def _time_until_harvest(self):
        if self._next_harvest_time is None:
            return self._mining_cycle_time * SEC
        time_until_harvest = self._next_harvest_time - gametime.GetSimTime()
        if time_until_harvest < 0:
            time_until_harvest += self._mining_cycle_time * SEC
        return time_until_harvest

    @property
    def _has_reagents(self):
        return self._available_fuel.get(REAGENT_FUEL_TYPE, 0) >= self._reagents_per_cycle

    def _update_details(self):
        try:
            mining_details = sm.GetService('autoMoonMiner').get_mining_details(self._solar_system_id, self._structure_id)
        except:
            self.Close()
            raise

        self._moon_id = mining_details['moonID']
        self._next_harvest_time = mining_details['nextHarvestTime']
        self._available_fuel = mining_details['availableFuel']
        self._output_materials = mining_details['outputMaterials']
        self._output_capacity_remaining = mining_details['remainingOutputBayCapacity']

    def _update_status_text(self):
        if self._next_harvest_time is None:
            status_text = localization.GetByLabel('UI/Moonmining/AutoMoonMiner/StatusInactive')
            status_hint = localization.GetByLabel('UI/Moonmining/AutoMoonMiner/StatusInactiveHint')
            color = carbonui.TextColor.DANGER
        elif not self._has_reagents:
            status_text = localization.GetByLabel('UI/Moonmining/AutoMoonMiner/StatusNoReagents')
            status_hint = localization.GetByLabel('UI/Moonmining/AutoMoonMiner/StatusNoReagentsHint')
            color = carbonui.TextColor.DANGER
        elif self._output_capacity_remaining == 0:
            status_text = localization.GetByLabel('UI/Moonmining/AutoMoonMiner/StatusOutputBayFull')
            status_hint = localization.GetByLabel('UI/Moonmining/AutoMoonMiner/StatusOutputBayFullHint')
            color = carbonui.TextColor.DANGER
        else:
            status_text = localization.GetByLabel('UI/Moonmining/AutoMoonMiner/StatusActive')
            status_hint = localization.GetByLabel('UI/Moonmining/AutoMoonMiner/StatusActiveHint')
            color = carbonui.TextColor.SUCCESS
        self._drill_status.text = u'{} <color={}>{}</color>'.format(localization.GetByLabel('UI/Moonmining/DrillStatus'), color, status_text)
        self._drill_status_info.hint = status_hint
        self._remaining_capacity_label.text = localization.GetByLabel('UI/Moonmining/AutoMoonMiner/RemainingOutputCapacity', volume=eveformat.volume(self._output_capacity_remaining))

    def _update_available_fuel(self):
        fuel_blocks = sum((amount for type_id, amount in self._available_fuel.iteritems() if evetypes.GetGroupID(type_id) == invConst.groupFuelBlock))
        self._fuel_entries[invConst.groupFuelBlock].update_quantity(fuel_blocks)
        self._fuel_entries[REAGENT_FUEL_TYPE].update_quantity(self._available_fuel.get(REAGENT_FUEL_TYPE, 0))

    def _update_details_routine(self):
        self._update_details_components()
        while True:
            uthread2.sleep(min(self._time_until_harvest / SEC, DETAILS_UPDATE_INTERVAL))
            if self.destroyed:
                break
            self._update_details()
            self._update_details_components()

    def _update_details_components(self):
        self._update_status_text()
        self._update_available_fuel()
        self._output_materials_section.update_output_materials(self._output_materials)

    def _update_time_routine(self):
        while not self.destroyed:
            self._time_until_output.text = localization.GetByLabel('UI/Moonmining/AutoMoonMiner/TimeUntilHarvest', time_until=FormatTimeIntervalShortWritten(self._time_until_harvest) if self._next_harvest_time else '-')
            uthread2.sleep(0.5)


class FuelEntry(GridContainer):
    default_align = carbonui.Align.TOTOP
    default_height = 24
    default_lines = 1
    default_columns = 4
    default_contentSpacing = (4, 4)

    def __init__(self, text, consumption, cycle_time, *args, **kwargs):
        super(FuelEntry, self).__init__(*args, **kwargs)
        self._consumption_per_cycle = consumption
        self._consumption_per_hour = self._consumption_per_cycle / (cycle_time / 3600)
        text_color = carbonui.TextColor.NORMAL
        _add_column(text, parent=self, color=text_color)
        self._quantity = _add_column('', parent=self, color=text_color)
        self._expiration = _add_column('', parent=self, color=text_color)
        _add_column(localization.GetByLabel('UI/Sovereignty/AmountPerHour', value=consumption), parent=self, color=text_color)

    def update_quantity(self, quantity):
        self._quantity.text = localization.GetByLabel('UI/PI/Common/UnitsAmount', amount=quantity)
        if quantity < self._consumption_per_cycle:
            time_remaining = 0
        else:
            time_remaining = int(quantity / float(self._consumption_per_hour) * HOUR)
        self._expiration.text = FormatTimeIntervalShortWritten(time_remaining, showTo='hour')


class OutputMaterialsSection(ContainerAutoSize):
    default_name = 'OutputMaterialsSection'
    default_align = carbonui.Align.TOTOP
    default_alignMode = carbonui.Align.TOTOP

    def __init__(self, materials_in_bay, materials_per_cycle, *args, **kwargs):
        super(OutputMaterialsSection, self).__init__(*args, **kwargs)
        self._entries = {}
        self._materials_per_cycle = materials_per_cycle
        carbonui.TextBody(parent=self, align=carbonui.Align.TOTOP, text=localization.GetByLabel('UI/Moonmining/Output'), color=carbonui.TextColor.SECONDARY, padBottom=8, bold=True)
        grid_container = GridContainer(parent=self, align=carbonui.Align.TOTOP, height=24, columns=5, lines=1, contentSpacing=(4, 4))
        Line(parent=self, align=carbonui.Align.TOTOP, top=-2, padBottom=4)
        _add_column(localization.GetByLabel('UI/Moonmining/MoonProductHeader'), grid_container)
        _add_column(localization.GetByLabel('UI/Moonmining/AutoMoonMiner/UnitsPerCycle'), grid_container)
        _add_column(localization.GetByLabel('UI/Moonmining/AutoMoonMiner/EstPricePerCycle'), grid_container)
        _add_column(localization.GetByLabel('UI/Generic/Units'), grid_container)
        _add_column(localization.GetByLabel('UI/Moonmining/EstPriceHeader'), grid_container)
        total_units_per_cycle = 0
        total_volume_per_cycle = 0
        total_price_per_cycle = 0
        entries = []
        for type_id, units_per_cycle in materials_per_cycle.iteritems():
            price = GetPrice(type_id, 1)
            total_units_per_cycle += units_per_cycle
            total_volume_per_cycle += evetypes.GetVolume(type_id) * units_per_cycle
            total_price_per_cycle += price * units_per_cycle
            entries.append({'type_id': type_id,
             'price': price,
             'units': materials_in_bay.get(type_id, 0),
             'units_per_cycle': units_per_cycle,
             'gauge_color': GetColorForBaseTypeID(type_id)[:3] + (0.6,)})

        for entry in sorted(entries, key=lambda x: evetypes.GetName(x['type_id'])):
            entry['price_percentage'] = entry['price'] * entry['units_per_cycle'] / float(total_price_per_cycle)
            entry['units_percentage'] = entry['units_per_cycle'] / float(total_units_per_cycle)
            self._entries[entry['type_id']] = OutputMaterialEntry(parent=self, **entry)

        Line(parent=self, align=carbonui.Align.TOTOP, padTop=4)
        grid_container = GridContainer(parent=self, align=carbonui.Align.TOTOP, height=24, columns=5, lines=1, padBottom=4, contentSpacing=(4, 4))
        _add_column(localization.GetByLabel('UI/Moonmining/Total'), grid_container)
        _add_column(u'{} ({})'.format(total_units_per_cycle, eveformat.volume(total_volume_per_cycle)), grid_container)
        _add_column(eveformat.isk(total_price_per_cycle), grid_container)
        self._total_units_label = _add_column('', grid_container)
        self._total_price_label = _add_column('', grid_container)
        grid_container.GetAbsoluteSize()
        self.update_output_materials(materials_in_bay)

    def update_output_materials(self, materials_in_bay):
        total_price = 0
        total_units = 0
        total_volume = 0
        for type_id in self._materials_per_cycle:
            units = materials_in_bay.get(type_id, 0)
            self._entries[type_id].update_units(units)
            total_units += units
            total_volume += evetypes.GetVolume(type_id) * units
            total_price += self._entries[type_id].price * units

        self._total_units_label.text = u'{} ({})'.format(total_units, eveformat.volume(total_volume))
        self._total_price_label.text = eveformat.isk(total_price)


class OutputMaterialEntry(GridContainer):
    default_align = carbonui.Align.TOTOP
    default_height = 32
    default_lines = 1
    default_columns = 5
    default_contentSpacing = (4, 4)

    def __init__(self, type_id, units, units_per_cycle, units_percentage, price, price_percentage, gauge_color, *args, **kwargs):
        super(OutputMaterialEntry, self).__init__(*args, **kwargs)
        self.type_id = type_id
        self.price = price
        self.units = None
        container = Container(parent=self, clipChildren=True)
        ItemIcon(name='typeIcon', parent=container, align=carbonui.Align.CENTERLEFT, typeID=type_id)
        carbonui.TextBody(name='typeLabel', parent=container, left=40, align=carbonui.Align.CENTERLEFT, text=evetypes.GetName(type_id))
        container = Container(parent=self, clipChildren=True, padRight=6)
        gauge = OutputMaterialGauge(parent=container, name='units_gauge', value=units_percentage, color=gauge_color, pos=(0, 6, 0, 0), gradientBrightnessFactor=1.5)
        gauge.SetValueText(_get_volume_text(type_id, units_per_cycle))
        container = Container(parent=self, clipChildren=True, padRight=6)
        gauge = OutputMaterialGauge(parent=container, name='price_gauge', value=price_percentage, color=gauge_color, pos=(0, 6, 0, 0), gradientBrightnessFactor=1.5)
        gauge.SetValueText(eveformat.isk(price * units_per_cycle))
        self._units_label = _add_column('', self, color=carbonui.TextColor.HIGHLIGHT)
        self._price_label = _add_column('', self, color=carbonui.TextColor.HIGHLIGHT)
        self.update_units(units)

    def update_units(self, units):
        if units == self.units:
            return
        self.units = units
        self._units_label.text = _get_volume_text(self.type_id, units)
        self._price_label.text = eveformat.isk(self.price * units)


class OutputMaterialGauge(Gauge):
    __guid__ = 'OutputMaterialGauge'
    default_gaugeHeight = 20
    default_align = carbonui.Align.TOALL
    default_state = carbonui.uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        Gauge.ApplyAttributes(self, attributes)
        self.valueText = carbonui.TextBody(parent=self.gaugeCont, align=carbonui.Align.CENTER, idx=0, color=carbonui.TextColor.HIGHLIGHT)
        self.shadowLabel = carbonui.TextBody(parent=self.gaugeCont, text='', align=carbonui.Align.CENTER, color=(0, 0, 0, 1), idx=1)
        self.shadowLabel.renderObject.spriteEffect = trinity.TR2_SFX_BLUR

    def SetValueText(self, text):
        Gauge.SetValueText(self, text)
        if self.shadowLabel.text != text:
            self.shadowLabel.text = text


def _get_volume_text(type_id, units):
    return u'{} ({})'.format(units, eveformat.volume(evetypes.GetVolume(type_id) * units))


def _add_column(text, parent, align = carbonui.Align.CENTERLEFT, color = carbonui.TextColor.SECONDARY):
    container = Container(parent=parent, clipChildren=True)
    return carbonui.TextBody(parent=container, align=align, text=text, color=color, autoFadeSides=16)
