#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\voidspace\util\client_helper.py


def send_void_space_expiry_time_to_character(macho_net, character_id, end_time):
    macho_net.SinglecastByCharID(character_id, 'OnAddExpiryDurationForVoidSpaceContent', end_time)


def send_on_void_space_relog_to_character(macho_net, character_id, client_data):
    macho_net.SinglecastByCharID(character_id, 'OnVoidSpaceRelog', client_data)
