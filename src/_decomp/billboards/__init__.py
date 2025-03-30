#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\billboards\__init__.py
import logging
from billboardsystem import BillboardSystem
from fsdBuiltData.client.billboards import GetVideoSpecificationsIterator, GetResourcesForView
logger = logging.getLogger(__name__)

def get_billboard_system():
    try:
        return get_billboard_system._system
    except AttributeError:
        system = BillboardSystem()
        get_billboard_system._system = system
        return system


def load_billboard_playlist_for_view(viewName, locale, **kwargs):
    from videoplayer import playlistresource
    videoSpecIterator = GetVideoSpecificationsIterator(viewName, locale, **kwargs)
    for resourceName, folders, size, fallbackImage, sound in videoSpecIterator:
        playlistresource.register_resource_constructor(resourceName, size.width, size.height, playlistresource.shuffled_videos(*folders), fallbackImage, withSound=sound)


def unload_billboard_playlist_for_view(viewName):
    from videoplayer import playlistresource
    for resourceName in GetResourcesForView(viewName):
        playlistresource.unregister_resource_constructor(resourceName)
