#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\d3dinfo\availablePlatforms.py
import sys
import os
import blue
import logging
logger = logging.getLogger(__name__)
try:
    d3dinfo = blue.LoadExtension('_d3dinfo')
except ImportError:
    d3dinfo = None

def IsD3D11Valid():
    if not d3dinfo:
        return True
    isOK = False
    d3d = d3dinfo.D3D11Info()
    try:
        d3d.InitializeD3D()
        adapterCount = d3d.GetAdapterCount()
        if adapterCount > 0:
            isOK = True
        d3d.ShutdownD3D()
    except RuntimeError:
        pass

    return isOK


_INTEL_ONBOARD_DEVICE_IDS = [42880,
 42881,
 42888,
 42889,
 42890,
 42882,
 42891,
 42883,
 42912,
 42913,
 42920,
 42922,
 42923,
 42924,
 42925,
 42921,
 42785,
 18693,
 18695,
 18696,
 18697,
 18048,
 4690,
 18056,
 18058,
 18059,
 18050,
 4692,
 18067,
 18131,
 18132,
 18128,
 18129,
 18130,
 17958,
 17960,
 17962,
 18082,
 18099,
 18114,
 18083,
 18098,
 18115,
 18080,
 18096,
 18112,
 18086,
 18090,
 18088,
 18081,
 18097,
 18113,
 19594,
 19595,
 19600,
 19610,
 20081,
 20065,
 20055,
 20053,
 20049,
 17751,
 17749,
 17777,
 17745,
 17729,
 39513,
 39544,
 39520,
 39536,
 39528,
 39488,
 39497,
 35440,
 35441,
 35414,
 35416,
 35419,
 35421,
 35412,
 35418,
 35420,
 35415,
 35417,
 35408,
 35409,
 35410,
 35411,
 16037,
 16040,
 16038,
 16039,
 16034,
 16016,
 16019,
 16025,
 16028,
 16033,
 39845,
 39848,
 16036,
 39713,
 39840,
 39842,
 39844,
 39850,
 39851,
 39852,
 34762,
 16035,
 39745,
 39872,
 39874,
 39876,
 39882,
 39883,
 39884,
 16017,
 16018,
 16024,
 16027,
 39877,
 39880,
 16022,
 16026,
 16020,
 39878,
 39910,
 39926,
 16041,
 16032,
 22843,
 22819,
 22822,
 22823,
 22807,
 22802,
 22811,
 22806,
 22817,
 22810,
 22813,
 22814,
 22812,
 34752,
 22803,
 22805,
 22786,
 22790,
 22795,
 22794,
 22792,
 22798,
 12677,
 12676,
 6789,
 23173,
 2692,
 6788,
 23172,
 6442,
 6450,
 6459,
 6458,
 6461,
 6435,
 6438,
 6439,
 6443,
 6445,
 6418,
 6427,
 6419,
 6421,
 6423,
 6426,
 6422,
 6433,
 6429,
 6430,
 6402,
 6406,
 6411,
 6410,
 6414,
 5693,
 5690,
 5682,
 5694,
 5691,
 5686,
 5666,
 5670,
 5674,
 5675,
 5677,
 5678,
 5650,
 5654,
 5658,
 5659,
 5661,
 5662,
 5634,
 5638,
 5642,
 5643,
 5645,
 5646,
 8880,
 8882,
 8883,
 8881]
_INTEL_VENDOR_ID = 32902

def IsIntelOnBoardGpu(adapterInfo):
    return adapterInfo.vendorID == _INTEL_VENDOR_ID and adapterInfo.deviceID in _INTEL_ONBOARD_DEVICE_IDS


def IsD3D12Valid():
    if not d3dinfo:
        return True
    isOK = False
    d3d = d3dinfo.D3D12Info()
    try:
        d3d.InitializeD3D()
        adapterCount = d3d.GetAdapterCount()
        if adapterCount > 0:
            isOK = True
            try:
                if IsIntelOnBoardGpu(d3d.GetAdapterInfo(0)):
                    logger.info('Intel on-board GPU detected, assuming D3D12 is not supported')
                    isOK = False
            except:
                pass

        d3d.ShutdownD3D()
    except RuntimeError:
        pass

    return isOK


def GetAvailablePlatforms():
    platforms = []
    if sys.platform.startswith('darwin'):
        platforms.append('metal')
    else:
        if IsD3D11Valid():
            platforms.append('dx11')
        if IsD3D12Valid():
            platforms.append('dx12')
    platforms.append('stub')
    return platforms


def InstallSystemBinaries(fileName):
    installMsg = 'Executing %s ...' % fileName
    print installMsg
    logger.info(installMsg)
    oldDir = os.getcwdu()
    os.chdir(blue.paths.ResolvePath(u'bin:/'))
    exitStatus = os.system(fileName)
    os.chdir(oldDir)
    retString = 'Execution of ' + fileName
    if exitStatus:
        retString += ' failed (exit code %d)' % exitStatus
        logger.error(retString)
    else:
        retString += ' succeeded'
        logger.info(retString)


def InstallDirectXIfNeeded():
    if not IsD3D11Valid():
        import imp
        if imp.get_suffixes()[0][0] == '_d.pyd':
            InstallSystemBinaries('DirectXRedistForDebug.exe')
        else:
            InstallSystemBinaries('DirectXRedist.exe')
