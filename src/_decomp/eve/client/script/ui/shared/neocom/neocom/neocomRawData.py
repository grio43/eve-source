#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\neocomRawData.py
import eve.client.script.ui.shared.neocom.neocom.neocomConst as neocomConst
import eve.client.script.ui.shared.neocom.neocom.neocomConstForFeatureFlags as neocomConstForFeatureFlags
from jobboard.client.feature_flag import is_job_board_available, are_missions_in_job_board_available
import neocom2.btnIDs as btnIDs

def GetEveMenuRawData():
    activities_group = neocomConst.RAWDATA_EVEMENU_GROUP_ACTIVITIES
    if is_job_board_available():
        if not are_missions_in_job_board_available():
            activities_group = neocomConstForFeatureFlags.RAWDATA_EVEMENU_GROUP_ACTIVITIES_WITH_BOTH_JOB_BOARD_AND_JOURNAL
    else:
        activities_group = neocomConstForFeatureFlags.RAWDATA_EVEMENU_GROUP_ACTIVITIES_WITHOUT_JOB_BOARD
    raw_data = [activities_group,
     neocomConst.RAWDATA_EVEMENU_GROUP_FINANCE,
     neocomConst.RAWDATA_EVEMENU_GROUP_INDUSTRY,
     neocomConst.RAWDATA_EVEMENU_GROUP_INVENTORY,
     neocomConst.RAWDATA_EVEMENU_GROUP_PERSONAL,
     neocomConst.RAWDATA_EVEMENU_GROUP_SHIP,
     neocomConst.RAWDATA_EVEMENU_GROUP_SOCIAL,
     neocomConst.RAWDATA_EVEMENU_GROUP_PARAGON_SERVICES,
     neocomConst.RAWDATA_EVEMENU_GROUP_UTILITIES]
    raw_data.extend(neocomConst.RAWDATA_EVEMENU_BOTTOM_BUTTONS)
    contacts_data = (neocomConst.BTNTYPE_CMD, btnIDs.ADDRESSBOOK_ID, None)
    locations_data = (neocomConst.BTNTYPE_CMD, btnIDs.LOCATIONS_ID, None)
    for _, button_id, children in raw_data:
        if button_id == btnIDs.GROUP_PERSONAL_ID and locations_data not in children:
            children.insert(1, locations_data)
        if button_id == btnIDs.GROUP_SOCIAL_ID and contacts_data not in children:
            children.insert(0, contacts_data)

    return raw_data


def GetNeocomDefaultRawData():
    if is_job_board_available():
        return neocomConst.RAWDATA_NEOCOMDEFAULT
    return neocomConstForFeatureFlags.RAWDATA_NEOCOMDEFAULT_WITHOUT_JOB_BOARD


def GetAvailableRawData(rawData):
    availableData = rawData if is_job_board_available() else [ button for button in rawData if getattr(button, 'id', None) != btnIDs.JOB_BOARD_ID ]
    return availableData
