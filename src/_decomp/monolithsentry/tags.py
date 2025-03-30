#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\tags.py
import datetime
import re
import logging
import monolithconfig
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

def get_tags():
    if monolithconfig.on_server():
        return get_server_tags()
    if monolithconfig.on_proxy():
        return get_proxy_tags()
    return get_client_tags()


def get_common_tags():
    import blue
    import sysinfo
    import carbonversion
    os_info = sysinfo.get_os_platform_information()
    refresh_token = monolithconfig.get_refresh_token()
    refresh_token_on_start = True
    if not refresh_token:
        refresh_token_on_start = False
    cv = carbonversion.get_carbon_version()
    tags = {'branch': monolithconfig.get_value('codename', 'boot'),
     'role': monolithconfig.get_value('role', 'boot'),
     'version': monolithconfig.get_value('version', 'boot'),
     'sync': monolithconfig.get_value('sync', 'boot'),
     'build': monolithconfig.get_value('build', 'boot'),
     'app': monolithconfig.get_value('appname', 'boot'),
     'host_os_name': os_info['hostOsName'],
     'host_os_version': os_info['hostOsVersion'],
     'os_bit': os_info['osBit'],
     'wine_version': os_info['wineVersion'],
     'process_bit': blue.sysinfo.processBitCount,
     'refresh_token_on_start': refresh_token_on_start}
    carbon_tags = {lib_name:cv.get_library_tag(lib_name) for lib_name in cv.get_libraries()}
    carbon_tags['carbon_version'] = cv.get_version()
    tags.update(carbon_tags)
    return tags


def get_server_tags():
    cluster_mode = monolithconfig.get_value('clusterMode', 'prefs')
    cluster_name = monolithconfig.get_value('clusterName', 'prefs')
    tags = {'cluster_mode': cluster_mode,
     'cluster_name': cluster_name}
    tags.update(get_common_tags())
    return tags


def get_proxy_tags():
    return get_server_tags()


def _get_driver_age(date_string):
    match = re.match('.*?(\\d+)$', date_string)
    if not match:
        raise ValueError()
    year = int(match.group(1))
    if year < 100:
        year += 2000
    year -= datetime.datetime.today().year
    return year


def _get_settings_tags():
    import trinity
    import evegraphics.settings as gfxsettings
    tags = {'window_mode': 'fullscreen' if trinity.mainWindow.GetWindowState().windowMode == trinity.Tr2WindowMode.FULL_SCREEN else 'windowed',
     'upscaling': trinity.UPSCALING_TECHNIQUE.GetNameFromValue(gfxsettings.Get(gfxsettings.GFX_UPSCALING_TECHNIQUE, trinity.UPSCALING_TECHNIQUE.NONE)),
     'raytracing': 'Enabled' if gfxsettings.Get(gfxsettings.GFX_SHADOW_QUALITY) == 3 else 'Disabled'}
    return tags


def get_client_tags():
    tags = {}
    try:
        import gpuinfo
        gpu = gpuinfo.getGpuInfo()
        gpu_tags = {'gpu_api': gpu['gpu']['TrinityPlatform'],
         'gpu_driver_vendor': gpu['gpu']['driver'].get('Vendor', ''),
         'gpu': gpu['gpu']['Description']}
        try:
            gpu_tags['gpu_driver_age_years'] = _get_driver_age(gpu['gpu']['driver'].get('Date', ''))
        except (KeyError, ValueError):
            gpu_tags['gpu_driver_age_years'] = -1

        tags.update(gpu_tags)
    except Exception:
        log.warning('Failed to get GPU info for Sentry client', exc_info=1)

    try:
        tags.update(_get_settings_tags())
    except Exception:
        pass

    tags.update(get_common_tags())
    return tags
