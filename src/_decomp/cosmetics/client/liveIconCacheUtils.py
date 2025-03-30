#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\liveIconCacheUtils.py
import trinity
import blue
import os
import hashlib
import evegraphics.settings as gfxsettings
MAP_CACHE_PATH = u'cache:/SKINR/icons'

def is_low_spec():
    return gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY) == gfxsettings.SHADER_MODEL_LOW


def open_cache_directory_in_explorer():
    fileSystemPath = blue.paths.ResolvePath(MAP_CACHE_PATH)
    os.startfile(fileSystemPath)


def create_cache_directory():
    cachePath = blue.paths.ResolvePathForWriting(MAP_CACHE_PATH)
    if not os.path.exists(cachePath):
        os.makedirs(cachePath)


def clear_all_cached_maps():
    fileSystemPath = blue.paths.ResolvePath(MAP_CACHE_PATH)
    for root, dirs, files in os.walk(fileSystemPath):
        for f in files:
            os.remove(os.path.join(root, f))


def get_cache_file_path(cachePath, hashKey):
    hashKey = str(hashKey).replace('-', '_')
    return u'{0}/{1}.dds'.format(cachePath, hashKey)


def get_unique_filename(skin_design, bg_texture_path):
    uniqueString = skin_design.design_hex + bg_texture_path + str(gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY))
    h = hashlib.new('sha256')
    h.update(uniqueString.encode())
    hex = h.hexdigest()
    hex = str(skin_design.ship_type_id) + hex
    path = blue.paths.ResolvePathForWriting(get_cache_file_path(MAP_CACHE_PATH, hex))
    path.encode('utf-8', 'ignore')
    return path


def cached_render_available(skin_design, bg_texture_path):
    filePath = get_unique_filename(skin_design, bg_texture_path)
    fileExists = os.path.isfile(filePath)
    return fileExists
