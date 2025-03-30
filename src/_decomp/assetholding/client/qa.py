#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\assetholding\client\qa.py
import blue

def get_entitlement_qa_menu_entries(asset_ids, goal_id, is_daily_goal = False):
    menu_entries = (('QA - Expire Entitlement', lambda : _request_expire_entitlement(asset_ids, goal_id, is_daily_goal)), ('QA - Copy Goal ID {goal_id}'.format(goal_id=goal_id), lambda : blue.pyos.SetClipboardData(str(goal_id))))
    return menu_entries


def _request_expire_entitlement(asset_ids, goal_id, is_daily_goal):
    if is_daily_goal:
        return
    group_name = 'eve-organization-goals'
    for asset_id in asset_ids:
        command = '/assetholding expire {asset_id} {external_id} {group_name}'.format(asset_id=asset_id, external_id=goal_id, group_name=group_name)
        sm.RemoteSvc('slash').SlashCmd(command)


def get_insider_qa_menu():
    return ('Asset Holding', [get_toggle_entry('Bypass validation when consuming items', sm.GetService('assetHoldingSvc').toggle_item_validation, not sm.GetService('assetHoldingSvc').is_item_validation_enabled), get_toggle_entry('Simulate failures in hold and spawn', sm.GetService('assetHoldingSvc').toggle_item_failure, sm.GetService('assetHoldingSvc').is_item_failure_enabled)])


def get_toggle_entry(label, callback, enabled):
    texture = {True: 'res:/UI/Texture/classes/insider/toggle_on_18.png',
     False: 'res:/UI/Texture/classes/insider/toggle_off_18.png'}[enabled]
    return ('{} ({})'.format(label, '<color=green>on</color>' if enabled else '<color=red>off</color>'),
     callback,
     (),
     (texture, 18))
