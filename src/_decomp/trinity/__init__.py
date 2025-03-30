#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\__init__.py
import logging
import blue
import _utils
_utils.AssertNotOnProxyOrServer()
from d3dinfo import availablePlatforms
from ._singletons import *
from ._trinity import *
from .renderJob import CreateRenderJob
from .renderJobUtils import *
logger = logging.getLogger(__name__)

def GetEnumValueName(enumName, value):
    if enumName in globals():
        enum = globals()[enumName]
        result = ''
        for enumKeyName, (enumKeyValue, enumKeydocString) in enum.values.iteritems():
            if enumKeyValue == value:
                if result != '':
                    result += ' | '
                result += enumKeyName

        return result


def GetEnumValueNameAsBitMask(enumName, value):
    if enumName in globals():
        enum = globals()[enumName]
        result = ''
        for enumKeyName, (enumKeyValue, enumKeydocString) in enum.values.iteritems():
            if enumKeyValue & value == enumKeyValue:
                if result != '':
                    result += ' | '
                result += enumKeyName

        return result


def ConvertTriFileToGranny(path):
    helper = TriGeometryRes()
    return helper.ConvertTriFileToGranny(path)


def LoadDone(evt):
    evt.isDone = True


def WaitForResourceLoads():
    blue.resMan.Wait()


def WaitForUrgentResourceLoads():
    blue.resMan.WaitUrgent()


def LoadUrgent(path):
    blue.resMan.SetUrgentResourceLoads(True)
    obj = Load(path)
    blue.resMan.SetUrgentResourceLoads(False)
    return obj


def GetResourceUrgent(path, extra = ''):
    blue.resMan.SetUrgentResourceLoads(True)
    obj = blue.resMan.GetResource(path, extra)
    blue.resMan.SetUrgentResourceLoads(False)
    return obj


def Save(obj, path):
    blue.motherLode.Delete(path)
    return blue.resMan.SaveObject(obj, path)


def SaveRenderTarget(filename, rt = None):
    if rt is None:
        rt = device.GetRenderContext().GetDefaultBackBuffer()
    if not rt.isReadable:
        readable = Tr2RenderTarget(rt.width, rt.height, 1, rt.format)
        rt.Resolve(readable)
        return Tr2HostBitmap(readable).Save(filename)
    else:
        return Tr2HostBitmap(rt).Save(filename)


def _StoreGPUInfoInCrashHeaders():
    try:
        adapterInfo = adapters.GetAdapterInfo(adapters.DEFAULT_ADAPTER)
        blue.SetCrashKeyValues('GPU_Description', adapterInfo.description)
        blue.SetCrashKeyValues('GPU_Driver', adapterInfo.driver)
        blue.SetCrashKeyValues('GPU_VendorId', str(adapterInfo.vendorID))
        blue.SetCrashKeyValues('GPU_DeviceId', str(adapterInfo.deviceID))
        blue.SetCrashKeyValues('trinityPlatform', platform)
        try:
            driverInfo = adapterInfo.GetDriverInfo()
            blue.SetCrashKeyValues('GPU_Driver_Version', driverInfo.driverVersionString)
            blue.SetCrashKeyValues('GPU_Driver_Date', driverInfo.driverDate)
            blue.SetCrashKeyValues('GPU_Driver_Vendor', driverInfo.driverVendor)
            blue.SetCrashKeyValues('GPU_Driver_Is_Optimus', 'Yes' if driverInfo.isOptimus else 'No')
            blue.SetCrashKeyValues('GPU_Driver_Is_Amd_Switchable', 'Yes' if driverInfo.isAmdDynamicSwitchable else 'No')
        except RuntimeError:
            blue.SetCrashKeyValues('GPU_Driver_Version', str(adapterInfo.driverVersion))

    except RuntimeError:
        pass


def IsFpsEnabled():
    return bool('FPS' in (j.name for j in renderJobs.recurring))


def SetFpsEnabled(enable, viewPort = None):
    if enable:
        if IsFpsEnabled():
            return
        fpsJob = CreateRenderJob('FPS')
        fpsJob.SetViewport(viewPort)
        fpsJob.RenderFps()
        fpsJob.ScheduleRecurring(insertFront=False)
    else:
        renderJobs.UnscheduleByName('FPS')


def AddRenderJobText(text, x, y, renderJob, color = 4278255360L):
    steps = [ step for step in renderJob.steps if step.name == 'RenderDebug' ]
    if len(steps) > 0:
        step = steps[0]
    else:
        return
    step.Print2D(x, y, color, text)
    return renderJob


def CreateDebugRenderJob(renderJobName, viewPort, renderJobIndex = -1):
    renderJob = CreateRenderJob(renderJobName)
    renderJob.SetViewport(viewPort)
    step = renderJob.RenderDebug()
    step.name = 'RenderDebug'
    step.autoClear = False
    if renderJobIndex is -1:
        renderJob.ScheduleRecurring()
    else:
        renderJobs.recurring.insert(renderJobIndex, renderJob)
    return renderJob


def SetupDefaultGraphs():
    graphs.Clear()
    graphs.AddGraph('frameTime')
    graphs.AddGraph('devicePresent')
    graphs.AddGraph('primitiveCount')
    graphs.AddGraph('batchCount')
    graphs.AddGraph('pendingLoads')
    graphs.AddGraph('pendingPrepares')
    graphs.AddGraph('textureResBytes')


def AddFrameTimeMarker(name):
    line = GetLineGraphFrameTime()
    if line is not None:
        line.AddMarker(name)


class FrameTimeMarkerStopwatch(object):

    def __init__(self, stopwatchName):
        self.started = blue.os.GetCycles()[0]
        self.stopwatchName = stopwatchName

    def __str__(self):
        return '%s %i ms' % (self.stopwatchName, int(1000 * ((blue.os.GetCycles()[0] - self.started) / float(blue.os.GetCycles()[1]))))

    def __del__(self):
        AddFrameTimeMarker(str(self))


def CreateBinding(cs, src, srcAttr, dst, dstAttr):
    binding = TriValueBinding()
    binding.sourceObject = src
    binding.sourceAttribute = srcAttr
    binding.destinationObject = dst
    binding.destinationAttribute = dstAttr
    if cs:
        cs.bindings.append(binding)
    return binding


def CreatePythonBinding(cs, src, srcAttr, dst, dstAttr):
    binding = Tr2PyValueBinding()
    binding.sourceObject = src
    binding.sourceAttribute = srcAttr
    binding.destinationObject = dst
    binding.destinationAttribute = dstAttr
    if cs:
        cs.bindings.append(binding)
    return binding


def _init():
    _StoreGPUInfoInCrashHeaders()
    device.SetRenderJobs(renderJobs)


_init()
