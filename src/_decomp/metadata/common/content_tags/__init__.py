#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\metadata\common\content_tags\__init__.py
from collections import OrderedDict
import localization
from metadata.common.content_tags.content_tags_data import get_content_tag, get_content_tag_type, ContentTagsLoader
from metadata.common.content_tags.content_tags_enum import ContentTags, ContentTagTypes
from signals import Signal
import eveicon
on_content_tags_reloaded = Signal('on_content_tags_reloaded')

def get_content_tag_as_object(content_tag_id):
    content_tag_objects = getattr(get_content_tag_as_object, '_content_tag_objects', {})
    if content_tag_id not in content_tag_objects:
        content_tag_data = get_content_tag(content_tag_id)
        content_tag_objects[content_tag_id] = ContentTag(content_tag_id, content_tag_data)
        get_content_tag_as_object._content_tag_objects = content_tag_objects
    return content_tag_objects.get(content_tag_id, None)


def get_content_tags_as_objects(content_tag_ids):
    if not content_tag_ids:
        return {}
    result = OrderedDict()
    for content_tag_id in content_tag_ids:
        content_tag = get_content_tag_as_object(content_tag_id)
        if content_tag:
            result[content_tag_id] = content_tag

    return result


def _on_content_tags_reloaded():
    if hasattr(get_content_tag_as_object, '_content_tag_objects'):
        delattr(get_content_tag_as_object, '_content_tag_objects')
    on_content_tags_reloaded()


ContentTagsLoader.ConnectToOnReload(_on_content_tags_reloaded)

class ContentTag(object):

    def __init__(self, content_tag_id, content_tag_data):
        self._content_tag_id = content_tag_id
        self._data = content_tag_data

    @property
    def id(self):
        return self._content_tag_id

    @property
    def data(self):
        return self._data

    @property
    def type_data(self):
        return get_content_tag_type(self.tag_type)

    @property
    def tag_type(self):
        return self.data.contentTagType

    @property
    def title(self):
        return localization.GetByMessageID(self.data.title)

    @property
    def description(self):
        return localization.GetByMessageID(self.data.description)

    @property
    def icon(self):
        if not self._data.icon:
            return ''
        return eveicon.get(self._data.icon)

    @property
    def tag_type_title(self):
        return localization.GetByMessageID(self.type_data.title)
