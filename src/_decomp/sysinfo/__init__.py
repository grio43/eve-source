#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sysinfo\__init__.py
import blue
import logging
import sys
logger = logging.getLogger('sysinfo')
PLATFORM_WINDOWS = 2
PLATFORM_MACOS = 1
PLATFORM_UNKNOWN = 0
PLATFORM_MACOS_WINE = -3
PLATFORM_LINUX_WINE = -4
HUMAN_PLATFORMS = {PLATFORM_WINDOWS: 'Windows',
 PLATFORM_MACOS: 'macOS',
 PLATFORM_UNKNOWN: 'Unknown',
 PLATFORM_MACOS_WINE: 'macOS',
 PLATFORM_LINUX_WINE: 'Linux'}

def get_device_id():
    device_id = blue.os.GetStartupArgValue('deviceID')
    if not device_id and blue.sysinfo.os.platform == blue.OsPlatform.WINDOWS:
        try:
            device_id = blue.win32.RegistryGetValue('HKEY_CURRENT_USER\\SOFTWARE\\CCP\\EVE', 'DeviceIdV2', 1)
        except WindowsError:
            logger.error('Failed to get deviceID')

    return device_id


def get_pdm_byte_data():
    memStream = blue.GetPDMByteData()
    contents = memStream.Read()
    return contents


def get_os_platform_information():
    if blue.sysinfo.isWine:
        hostVersion = blue.sysinfo.wineHostOs
        platform = PLATFORM_UNKNOWN
        osMajor, osMinor, osPatch = (0, 0, 0)
        try:
            if hostVersion.startswith('Darwin'):
                platform = PLATFORM_MACOS_WINE
                components = hostVersion.replace('Darwin', '').strip().split('.')
                osMajor, osMinor, osPatch = int(components[0]), int(components[1]), components[2]
            elif hostVersion.startswith('Linux'):
                platform = PLATFORM_LINUX_WINE
                components = hostVersion.replace('Linux', '').strip().split('.')
                osMajor, osMinor, osPatch = int(components[0]), int(components[1]), components[2]
        except Exception:
            logger.exception('Failed getting platform (major, minor, patch) for a wine system.')

    else:
        if sys.platform.startswith('darwin'):
            platform = PLATFORM_MACOS
        else:
            platform = PLATFORM_WINDOWS
        hostVersion = '%s %s.%s.%s' % (HUMAN_PLATFORMS[platform],
         blue.sysinfo.os.majorVersion,
         blue.sysinfo.os.minorVersion,
         blue.sysinfo.os.buildNumber)
        osMajor = blue.sysinfo.os.majorVersion
        osMinor = blue.sysinfo.os.minorVersion
        osPatch = blue.sysinfo.os.patch
    osName = HUMAN_PLATFORMS[platform]
    return {'hostOsName': osName,
     'hostOsVersion': hostVersion,
     'osBit': blue.sysinfo.systemBitCount,
     'wineVersion': blue.sysinfo.wineVersion,
     'osPlatform': platform,
     'osMajor': osMajor,
     'osMinor': osMinor,
     'osPatch': osPatch}


def getProcessorInfo():
    results = {'processor': {}}
    results['processor']['Architecture'] = 'x86' if blue.sysinfo.cpu.bitCount == 32 else 'AMD64'
    results['processor']['Level'] = blue.sysinfo.cpu.family
    results['processor']['Revision'] = blue.sysinfo.cpu.revision
    results['processor']['Count'] = blue.sysinfo.cpu.logicalCpuCount
    results['processor']['MHz'] = blue.sysinfo.cpu.frequency
    results['processor']['BitCount'] = blue.sysinfo.cpu.bitCount
    results['processor']['Identifier'] = blue.sysinfo.cpu.identifier
    return results
