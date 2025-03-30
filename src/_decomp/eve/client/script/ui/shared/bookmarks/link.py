#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\bookmarks\link.py
import evelink.client
from carbon.common.lib.const import maxInt
SCHEME = 'bookmarkFolder'

def register_link_handlers(registry):
    registry.register(SCHEME, handle_bookmark_folder_link, hint='UI/AclBookmarks/BookmarkFolderLinkHint', color_info=evelink.settings_link_color_info)


def handle_bookmark_folder_link(url):
    folder_id = parse_bookmark_folder_url(url)
    sm.GetService('bookmarkSvc').ShowBookmarkFolderInfo(folder_id)


def parse_bookmark_folder_url(url):
    folder_id = int(url.split(':')[1])
    if maxInt < folder_id < 1:
        raise ValueError('Bookmark folder ID out of range')
    return folder_id


def bookmark_folder_link(folder_id, name):
    return evelink.Link(url=format_bookmark_folder_url(folder_id), text=name)


def format_bookmark_folder_url(folder_id):
    return u'{}:{}'.format(SCHEME, folder_id)
