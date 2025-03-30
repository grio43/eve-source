#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agency\common\contentdata.py
import json
CUSTOM_CONTENT_EXTRA_DATA = ('location_id', 'item_id', 'type_id', 'owner_id', 'enemy_owner_id', 'solar_system_coordinates', 'title_text_id', 'expanded_title_text_id', 'subtitle_text_id', 'expanded_subtitle_text_id', 'blurb_text_id', 'rewards', 'primary_action_id', 'hidden_location_id', 'visibility_at_jump_range_after_minutes')
HIDDEN_EXTRA_DATA = ('hidden_location_id', 'visibility_at_jump_range_after_minutes')

class CustomContentData(object):

    def __init__(self, agency_content_id, source_id, source_content_id, content_type, solar_system_id, creation_date, expiry_date):
        self.agency_content_id = agency_content_id
        self.content_type = content_type
        self.solar_system_id = solar_system_id
        self.creation_date = creation_date
        self.expiry_date = expiry_date
        self.source_id = source_id
        self.source_content_id = source_content_id
        self.location_id = None
        self.item_id = None
        self.type_id = None
        self.owner_id = None
        self.enemy_owner_id = None
        self.solar_system_coordinates = None
        self.title_text_id = None
        self.expanded_title_text_id = None
        self.subtitle_text_id = None
        self.expanded_subtitle_text_id = None
        self.blurb_text_id = None
        self.rewards = []
        self.primary_action_id = None
        self.hidden_location_id = None
        self.visibility_at_jump_range_after_minutes = [(0, None)]

    def update_from_dict(self, content_data):
        for key, value in content_data.iteritems():
            if key in CUSTOM_CONTENT_EXTRA_DATA:
                setattr(self, key, value)

    def __repr__(self):
        return 'CustomContentData(%s)' % ', '.join(('%s=%s' % (k, v) for k, v in sorted(self.__dict__.items()) if '__' not in k))

    def set_visibility(self, jumps, minutes):
        self.visibility_at_jump_range_after_minutes.append((jumps, minutes))
        self.visibility_at_jump_range_after_minutes.sort(reverse=True)

    def get_clean_copy(self):
        content_data_copy = CustomContentData(self.agency_content_id, self.source_id, self.source_content_id, self.content_type, self.solar_system_id, self.creation_date, self.expiry_date)
        content_data_copy.copy_clean_extra_data(self)
        return content_data_copy

    def copy_clean_extra_data(self, content_data):
        for key in CUSTOM_CONTENT_EXTRA_DATA:
            if key in HIDDEN_EXTRA_DATA:
                continue
            setattr(self, key, getattr(content_data, key, None))


def create_custom_content_data(content_row):
    data = create_base_custom_content_data(content_row)
    extra_data = json.loads(content_row.contentData)
    data.update_from_dict(extra_data)
    return data


def create_base_custom_content_data(content_row):
    data = CustomContentData(content_row.customAgencyContentID, content_row.sourceID, content_row.sourceContentID, content_row.contentType, content_row.solarSystemID, content_row.creationDate, content_row.expiryDate)
    return data


def get_custom_content_extra_data(content_data):
    data = {}
    for key in CUSTOM_CONTENT_EXTRA_DATA:
        value = getattr(content_data, key, None)
        if value is not None:
            data[key] = value

    return json.dumps(data)
