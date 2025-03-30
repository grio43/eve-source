#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\metadata\common\content_tags\content_tags_data.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import contentTagsLoader
except ImportError:
    contentTagsLoader = None

try:
    import contentTagTypesLoader
except ImportError:
    contentTagTypesLoader = None

class ContentTagsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/contentTags.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/contentTags.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/contentTags.fsdbinary'
    __loader__ = contentTagsLoader


class ContentTagTypesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/contentTagTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/contentTagTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/contentTagTypes.fsdbinary'
    __loader__ = contentTagTypesLoader


def get_content_tags():
    return ContentTagsLoader.GetData()


def get_content_tag_types():
    return ContentTagTypesLoader.GetData()


def get_content_tag(content_tag_id):
    return get_content_tags().get(content_tag_id, None)


def get_content_tag_type(content_tag_type_id):
    return get_content_tag_types().get(content_tag_type_id, None)


def get_content_tag_type_id(content_tag_id):
    content_tag = get_content_tag(content_tag_id)
    if content_tag:
        return content_tag.contentTagType
