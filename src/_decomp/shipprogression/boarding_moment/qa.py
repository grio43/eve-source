#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\qa.py
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbonui.services.setting import CharSettingBool
from eve.client.script.ui.control.message import ShowQuickMessage
from .boardingMomentSvc import GetBoardingMomentService
from .const import ShipShape, ShipSize, MomentSteps
overlay_setting = CharSettingBool(settings_key='boarding_moment_qa_ui_enabled', default_value=False)

def clear_data():
    GetBoardingMomentService().Clear()
    ShowQuickMessage('Boarding moment tracking has been reset')


def is_ui_overlay_enabled():
    return settings.char.ui.Get('boarding_moment_qa_ui_enabled', False)


SHAPE_STRINGS = {ShipShape.UNDEFINED: 'UNDEFINED',
 ShipShape.BOX: 'BOX',
 ShipShape.LONG: 'LONG',
 ShipShape.TALL: 'TALL',
 ShipShape.WIDE: 'WIDE'}
SIZE_STRINGS = {ShipSize.SMALL: 'SMALL',
 ShipSize.MEDIUM: 'MEDIUM',
 ShipSize.LARGE: 'LARGE',
 ShipSize.TITAN: 'TITAN'}
MOMENT_STEP_STRINGS = {MomentSteps.TEASE_1: 'TEASE_1',
 MomentSteps.TEASE_2: 'TEASE_2',
 MomentSteps.TEASE_3: 'TEASE_3',
 MomentSteps.BOOSTERS_1: 'BOOSTERS_1',
 MomentSteps.BOOSTERS_2: 'BOOSTERS_2',
 MomentSteps.BOOSTERS_3: 'BOOSTERS_3',
 MomentSteps.REVEAL_1: 'REVEAL_1',
 MomentSteps.REVEAL_2: 'REVEAL_2',
 MomentSteps.REVEAL_3: 'REVEAL_3',
 MomentSteps.CLIMAX_1: 'CLIMAX_1',
 MomentSteps.CLIMAX_2: 'CLIMAX_2',
 MomentSteps.CLIMAX_3: 'CLIMAX_3'}

def get_boarding_moment_ship_info(type_ids = None, separator = '\t', copy_to_clipboard = True, print_to_console = True):
    from shipprogression.boarding_moment import get_ship_shape_group, get_ship_size_group
    from fsdBuiltData.common.graphicIDs import GetSofHullName, GetSofFactionName, GetSofRaceName
    from eve.client.script.environment.sofService import GetSofService
    import evetypes
    import blue
    if not session.role & ROLE_QA:
        print 'not a qa'
        return
    type_id_set = set(type_ids or evetypes.GetTypeIDsByCategory(6))
    result = '{}\n'.format(separator.join((str(i) for i in ('type_id', 'type_name', 'hull_name', 'shape_group', 'size_group'))))
    print 'get_boarding_moment_ship_info starting for {} ships'.format(len(type_id_set))
    for type_id in type_id_set:
        graphic_id = evetypes.GetGraphicID(type_id)
        hull = GetSofHullName(graphic_id)
        faction = GetSofFactionName(graphic_id)
        race = GetSofRaceName(graphic_id)
        dna = '%s:%s:%s' % (hull, faction, race)
        ship_model = GetSofService().spaceObjectFactory.BuildFromDNA(dna)
        shape = SHAPE_STRINGS.get(get_ship_shape_group(type_id, ship_model), 'UNDEFINED')
        if ship_model.dynamicBoundingSphereEnabled:
            shape += '**'
        entry = separator.join((str(i) for i in (type_id,
         evetypes.GetName(type_id, languageID='en-us'),
         hull,
         shape,
         SIZE_STRINGS.get(get_ship_size_group(type_id, ship_model.GetBoundingSphereRadius()), 'UNDEFINED'))))
        if print_to_console:
            print entry
        result += '{}\n'.format(entry)

    if copy_to_clipboard:
        blue.pyos.SetClipboardData(result)
        print 'get_boarding_moment_ship_info copied to clipboard'
    print 'get_boarding_moment_ship_info completed'


def play_cinematic_for_ships(type_ids = None, skip_unpublished = True, skip_duplicate_hulls = False, only_unseen = False):
    import evetypes
    import uthread2
    from fsdBuiltData.common.graphicIDs import GetSofHullName
    from inventorycommon.util import IsModularShip
    from ballparkCommon.docking import CanDock
    from eve.client.script.ui.services.menuSvcExtras import invItemFunctions
    from nodegraph.client.getters.inventory import GetInventoryItem
    from nodegraph.client.actions.qa import SlashCommand
    from nodegraph.client.util import wait_for_session
    from shipprogression.boarding_moment import is_excluded_from_boarding_moment
    if not session.role & ROLE_QA:
        print 'not a qa'
        return
    get_ship = GetInventoryItem()
    slash_command = SlashCommand(wait_for_session=True)
    if session.structureid:
        structure_type_id = sm.GetService('invCache').GetInventoryFromId(session.structureid).typeID
    else:
        structure_type_id = None
    type_id_list = type_ids or evetypes.GetTypeIDsByCategory(6)
    hulls_played = set()
    was_naming_suppressed = settings.user.suppress.Get('suppress.ShipNameChangeOnAssemble', False)
    settings.user.suppress.Set('suppress.ShipNameChangeOnAssemble', True)
    bm_svc = GetBoardingMomentService()
    print 'play_cinematic_for_ships starting for {} ships'.format(len(type_id_list))

    def the_action(type_id):
        print 'starting', type_id, evetypes.GetName(type_id, languageID='en-us')
        get_ship.type_id = type_id
        item_info = get_ship.get_values()
        if not item_info:
            slash_command.slash_command = u'/create {} 1'.format(type_id)
            slash_command.start()
            uthread2.sleep(0.5)
        item_info = get_ship.get_values()
        if not item_info:
            print 'skipping - failed to create item', type_id,
            print evetypes.GetName(type_id, languageID='en-us')
            return
        bm_svc.SetSeen(type_id)
        item = item_info['inventory_item']
        if not item.singleton:
            invItemFunctions.AssembleAndBoardShip(item)
        else:
            sm.GetService('station').TryActivateShip(item)
        uthread2.sleep(0.5)
        wait_for_session()
        uthread2.sleep(1)
        wait_for_session()
        counter = 0
        while True:
            current_view = sm.GetService('viewState').GetCurrentView()
            if current_view and current_view.activeShipModel and current_view._vfxMultiEffect and current_view.GetActiveShipTypeID() == type_id:
                break
            uthread2.sleep(0.1)
            counter += 1
            if not bool(counter % 10):
                print 'waiting for hangar - has activeShipModel {} - is correct ship type {}'.format(bool(current_view.activeShipModel), current_view.GetActiveShipTypeID() == type_id)

        current_view.on_first_boarding()
        uthread2.sleep(0.5)
        while bm_svc.IsPlaying():
            uthread2.sleep(0.1)

        uthread2.sleep(0.5)

    def the_loop():
        for type_id in type_id_list:
            if skip_unpublished and not evetypes.IsPublished(type_id):
                continue
            if is_excluded_from_boarding_moment(type_id):
                print 'skipping - excluded from boarding moments', type_id,
                print evetypes.GetName(type_id, languageID='en-us')
                continue
            if IsModularShip(type_id):
                print 'skipping - modular ship', type_id,
                print evetypes.GetName(type_id, languageID='en-us')
                continue
            if structure_type_id and not CanDock(structure_type_id, type_id):
                print 'skipping - not allowed to dock', type_id,
                print evetypes.GetName(type_id, languageID='en-us')
                continue
            if only_unseen and bm_svc.HasSeen(type_id):
                print 'skipping - has seen', type_id,
                print evetypes.GetName(type_id, languageID='en-us')
                continue
            if skip_duplicate_hulls:
                graphic_id = evetypes.GetGraphicID(type_id)
                hull = GetSofHullName(graphic_id)
                if hull in hulls_played:
                    print 'skipping - duplicate hull', type_id,
                    print evetypes.GetName(type_id, languageID='en-us')
                    continue
                hulls_played.add(hull)
            the_action(type_id)

        settings.user.suppress.Set('suppress.ShipNameChangeOnAssemble', was_naming_suppressed)
        print 'play_cinematic_for_ships completed'

    tasklet = uthread2.start_tasklet(the_loop)
    return tasklet
