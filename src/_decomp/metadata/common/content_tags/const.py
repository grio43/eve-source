#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\metadata\common\content_tags\const.py
from characterdata import careerpathconst
from metadata.common.content_tags import ContentTags
CAREER_PATH_TO_CONTENT_TAG_ID = {careerpathconst.career_path_enforcer: ContentTags.career_path_enforcer,
 careerpathconst.career_path_explorer: ContentTags.career_path_explorer,
 careerpathconst.career_path_industrialist: ContentTags.career_path_industrialist,
 careerpathconst.career_path_soldier_of_fortune: ContentTags.career_path_soldier_of_fortune}
CONTENT_TAG_TO_CAREER_PATH = {value:key for key, value in CAREER_PATH_TO_CONTENT_TAG_ID.iteritems()}
