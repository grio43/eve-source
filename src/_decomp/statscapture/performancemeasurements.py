#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\statscapture\performancemeasurements.py
import json
import os
import shutil
import tempfile
import time
import blue
import evegraphics.settings as gfxsettings
import trinity
import uthread2
PERFMEASUREMENTS_URL = 'http://trilambda-ws:8088/'
PERFMEASUREMENTS_UPLOAD_URL = PERFMEASUREMENTS_URL + 'measurement/'

def _CaptureRenderSteps():
    steps = []
    for rjIndex, rj in enumerate(trinity.renderJobs.recurring):
        for stepIndex, step in enumerate(rj.steps):
            step.statName = 'Trinity/RenderJobs/Recurring/%s/%s' % (rj.name or 'RJ%s' % (stepIndex + 1), step.name or 'Step%s' % (stepIndex + 1))
            step.debugCaptureCpuTime = True
            step.debugCaptureGpuTime = True
            steps.append(step)

    return steps


def _GetRenderTargetBitmap():
    rt = trinity.device.GetRenderContext().GetDefaultBackBuffer()
    if not rt.isReadable:
        readable = trinity.Tr2RenderTarget(rt.width, rt.height, 1, rt.format)
        rt.Resolve(readable)
        return trinity.Tr2HostBitmap(readable)
    else:
        return trinity.Tr2HostBitmap(rt)


def _GetMemoryUsage():
    try:
        meg = 1.0 / 1024.0 / 1024.0
        return blue.pyos.cpuUsage[-1].virtualMemory * meg
    except:
        return 0


class _FrameTimeInfo(object):

    def __init__(self, frameTimes):
        times = sorted(frameTimes)
        self.median = frameTimes[len(times) / 2]
        self.min = times[0]
        self.max = times[-1]
        summed = reduce(lambda x, y: x + y, times)
        self.avg = summed / len(times)


class _MemoryInfo(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end


class _DrawPrimitivesInfo(object):

    def __init__(self, drawPrimitives):
        if drawPrimitives:
            self.min = int(min(drawPrimitives.values()))
            self.max = int(max(drawPrimitives.values()))
            self.avg = sum(drawPrimitives.values()) / len(drawPrimitives)
        else:
            self.min = 0
            self.max = 0
            self.avg = 0


class _MeasurementInfo(object):

    def __init__(self, frameTimes, startSysMem, endSysMem, startGpuMem, endGpuMem, drawPrimitives):
        self.frameTime = _FrameTimeInfo(frameTimes)
        self.systemMemory = _MemoryInfo(startSysMem, endSysMem)
        self.gpuMemory = _MemoryInfo(startGpuMem, endGpuMem)
        self.drawPrimitives = _DrawPrimitivesInfo(drawPrimitives)


class Measurement(object):
    STATE_NOT_STARTED = 0
    STATE_RUNNING = 1
    STATE_FINISHED = 2

    def __init__(self, captureRenderSteps = True, perFrameCapture = True, statFilter = ()):
        self._steps = []
        self._captureRenderSteps = captureRenderSteps
        self._perFrameCapture = perFrameCapture
        self._startTime = 0L
        self._endTime = time.localtime()
        self._statistics = []
        self._state = self.STATE_NOT_STARTED
        self._frameTimes = {}
        self._drawPrimitives = {}
        self._screenshots = []
        self._startSysMem = 0
        self._endSysMem = 0
        self._startGpuMem = 0
        self._endGpuMem = 0
        self._statFilter = statFilter

    def _Ticker(self):
        self._startTime = blue.os.GetWallclockTime()
        t0 = self._startTime
        dp = blue.statistics.Find('Trinity/AL/sceneDrawcallCount')
        while self._state == self.STATE_RUNNING:
            uthread2.Yield()
            if self._state != self.STATE_RUNNING:
                break
            t1 = blue.os.GetWallclockTime()
            ms = float(blue.os.TimeDiffInUs(t0, t1)) / 1000.0
            t0 = t1
            timeFromStartInMs = float(blue.os.TimeDiffInUs(self._startTime, t1)) / 1000.0
            self._frameTimes[timeFromStartInMs] = ms
            self._drawPrimitives[timeFromStartInMs] = int(dp.value) if dp else 0

    def GetState(self):
        return self._state

    def Begin(self):
        if self._state == self.STATE_RUNNING:
            raise RuntimeError('already started')
        if self._captureRenderSteps:
            self._steps = _CaptureRenderSteps()
            uthread2.Yield()
            uthread2.Yield()
        self._startTime = blue.os.GetWallclockTime()
        self._frameTimes.clear()
        self._drawPrimitives.clear()
        del self._screenshots[:]
        blue.statistics.BeginCapture()
        self._startSysMem = _GetMemoryUsage()
        self._startGpuMem = getattr(blue.statistics.Find('Trinity/AL/gpuMemoryEst/total'), 'value', 0) / 1024.0 / 1024.0
        self._state = self.STATE_RUNNING
        uthread2.StartTasklet(self._Ticker)

    def End(self):
        if self._state != self.STATE_RUNNING:
            raise RuntimeError('measurement is not running')
        try:
            self._endTime = time.localtime()
            self._endSysMem = _GetMemoryUsage()
            self._endGpuMem = getattr(blue.statistics.Find('Trinity/AL/gpuMemoryEst/total'), 'value', 0) / 1024.0 / 1024.0
            statistics = blue.statistics.EndCapture()
            types = {0: 0,
             1: 0,
             2: 1,
             3: 2}
            self._statistics = [ {'name': name,
             'type': types.get(getattr(blue.statistics.Find(name), 'type', 0), 0),
             'perFrame': values} for name, values in statistics.items() if not self._statFilter or name in self._statFilter ]
            for step in self._steps:
                step.debugCaptureCpuTime = False
                step.debugCaptureGpuTime = False
                step.statName = ''

            del self._steps[:]
        finally:
            self._state = self.STATE_FINISHED

    def GetEndTime(self):
        if self._state != self.STATE_FINISHED:
            raise RuntimeError('measurement data is not available')
        return self._endTime

    def GetInfo(self):
        if self._state != self.STATE_FINISHED:
            raise RuntimeError('measurement data is not available')
        return _MeasurementInfo(self._frameTimes.values(), self._startSysMem, self._endSysMem, self._startGpuMem, self._endGpuMem, self._drawPrimitives)

    def GetFrameTimes(self):
        if self._state != self.STATE_FINISHED:
            raise RuntimeError('measurement data is not available')
        return self._frameTimes

    def TakeScreenshot(self):
        if self._state != self.STATE_RUNNING:
            raise RuntimeError('measurement is not running')
        screenshot = _GetRenderTargetBitmap()
        screenshotTime = float(blue.os.TimeDiffInUs(self._startTime, blue.os.GetWallclockTime())) / 1000.0
        self.AddScreenshot(screenshotTime, screenshot)

    def AddScreenshot(self, screenshotTime, screenshot):
        self._screenshots.append((screenshotTime, screenshot))

    def ExportCsv(self, path):
        if self._state != self.STATE_FINISHED:
            raise RuntimeError('measurement data is not available')
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        dataTable = [','.join(map(str, sorted(self._frameTimes.keys()))),
         ','.join([ str(self._frameTimes[k]) for k in sorted(self._frameTimes.keys()) ]),
         ','.join((str(self._drawPrimitives.get(k, '')) for k in sorted(self._frameTimes.keys()))),
         '%s' % self._endSysMem]
        data = '\n'.join(dataTable)
        with open(path, 'w') as f:
            f.write(data)

    def GetData(self, name, appData, benchmarkData = None):
        import socket
        aaLabels = {gfxsettings.AA_QUALITY_DISABLED: 'Disabled',
         gfxsettings.AA_QUALITY_TAA_LOW: 'Low',
         gfxsettings.AA_QUALITY_TAA_MEDIUM: 'Medium',
         gfxsettings.AA_QUALITY_TAA_HIGH: 'High'}
        if blue.sysinfo.isWine:
            osLabel = blue.sysinfo.wineHostOs
        elif blue.sysinfo.os.platform == blue.OsPlatform.OSX:
            osLabel = 'macOS %s.%s.%s' % (blue.sysinfo.os.majorVersion, blue.sysinfo.os.minorVersion, blue.sysinfo.os.buildNumber)
        else:
            osLabel = 'Windows %s.%s' % (blue.sysinfo.os.majorVersion, blue.sysinfo.os.minorVersion)

        def yesNo(value):
            if value:
                return 'Yes'
            return 'No'

        arch = blue.sysinfo.cpu.architecture
        if blue.sysinfo.isRosetta:
            arch = 'x64 (Rosetta)'
        data = {'machine': {'name': socket.gethostname(),
                     'cpu': blue.sysinfo.cpu.brand,
                     'memory': blue.sysinfo.GetMemory().totalPhysical,
                     'gpu': trinity.adapters.GetAdapterInfo(trinity.device.adapter).description,
                     'os': osLabel},
         'app': {'trinityPlatform': trinity.platform,
                 'architecture': arch,
                 'settings': {'FullScreen': trinity.mainWindow.GetWindowState().windowMode == trinity.Tr2WindowMode.FULL_SCREEN,
                              'Size': '%s x %s' % (trinity.device.width, trinity.device.height),
                              'Present Interval': trinity.PRESENT_INTERVAL.GetNameFromValue(trinity.device.presentationInterval),
                              'Anti-Aliasing': aaLabels.get(gfxsettings.Get(gfxsettings.GFX_ANTI_ALIASING), '?'),
                              'Post Processing': ['None', 'Low', 'High'][gfxsettings.Get(gfxsettings.GFX_POST_PROCESSING_QUALITY)],
                              'Shader Quality': ['',
                                                 'Low',
                                                 'Medium',
                                                 'High'][gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY)],
                              'Texture Quality': ['High', 'Medium', 'Low'][gfxsettings.Get(gfxsettings.GFX_TEXTURE_QUALITY)],
                              'LOD Quality': ['',
                                              'Low',
                                              'Medium',
                                              'High'][gfxsettings.Get(gfxsettings.GFX_LOD_QUALITY)],
                              'Shadow Quality': ['Disabled',
                                                 'Low',
                                                 'High',
                                                 'Raytraced'][gfxsettings.Get(gfxsettings.GFX_SHADOW_QUALITY)],
                              'Reflection Quality': ['Disabled',
                                                     'Low',
                                                     'Medium',
                                                     'High',
                                                     'Highest'][gfxsettings.Get(gfxsettings.GFX_REFLECTION_QUALITY)],
                              'AO Quality': ['Disabled',
                                             'Low',
                                             'Medium',
                                             'High'][gfxsettings.Get(gfxsettings.GFX_AO_QUALITY)],
                              'Volumetric Quality': ['Low',
                                                     'Medium',
                                                     'High',
                                                     'Ultra'][gfxsettings.Get(gfxsettings.GFX_VOLUMETRIC_QUALITY)],
                              'Upscaling Technique': trinity.UPSCALING_TECHNIQUE.GetNameFromValue(trinity.device.upscalingTechnique).lower(),
                              'Upscaling Setting': trinity.UPSCALING_SETTING.GetNameFromValue(trinity.device.upscalingSetting).lower(),
                              'Framegeneration': yesNo(gfxsettings.Get(gfxsettings.GFX_FRAMEGENERATION_ENABLED)),
                              'Turrets Enabled': yesNo(gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED)),
                              'Effects': yesNo(gfxsettings.Get(gfxsettings.UI_EFFECTS_ENABLED)),
                              'Missile Effects': yesNo(gfxsettings.Get(gfxsettings.UI_MISSILES_ENABLED)),
                              'Ship Explosions': yesNo(gfxsettings.Get(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED)),
                              'Drone Models': yesNo(gfxsettings.Get(gfxsettings.UI_DRONE_MODELS_ENABLED)),
                              'Trails': yesNo(gfxsettings.Get(gfxsettings.UI_TRAILS_ENABLED)),
                              'GPU Particles': yesNo(gfxsettings.Get(gfxsettings.UI_GPU_PARTICLES_ENABLED)),
                              'Asteroid Environments': yesNo(gfxsettings.Get(gfxsettings.UI_ASTEROID_ATMOSPHERICS)),
                              'Inspace Skinning Effect': yesNo(gfxsettings.Get(gfxsettings.UI_MODELSKINSINSPACE_ENABLED)),
                              'DOF Enabled': yesNo(gfxsettings.Get(gfxsettings.GFX_DOF_POSTPROCESS_ENABLED)),
                              'GDPR Enabled': yesNo(trinity.settings.GetValue('gdrEnabled'))}},
         'benchmark': {'name': name,
                       'timestamp': time.mktime(self._endTime) * 1000},
         'frameTimes': sorted(self._frameTimes.keys()),
         'stats': self._statistics}
        data['app'].update(appData)
        if benchmarkData:
            data['benchmark'].update(benchmarkData)
        try:
            driverInfo = trinity.adapters.GetAdapterInfo(trinity.device.adapter).GetDriverInfo()
            data['machine']['gpu driver'] = '%s %s' % (driverInfo.driverVersionString, driverInfo.driverDate)
        except trinity.ALError:
            pass

        return data

    def Export(self, name, path, appData, benchmarkData = None):
        if self._state != self.STATE_FINISHED:
            raise RuntimeError('measurement data is not available')
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        exportName = os.path.splitext(os.path.basename(path))[0]
        exportFolderPath = os.path.dirname(path)
        data = self.GetData(name, appData, benchmarkData)
        if self._screenshots:
            data['screenshots'] = [ {'time': s[0] / 1000,
             'href': '%s-%s.png' % (exportName, i)} for i, s in enumerate(self._screenshots) ]
        outPaths = []
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
            outPaths.append(path)
        for i, each in enumerate(self._screenshots):
            screenPath = os.path.abspath(os.path.join(exportFolderPath, '%s-%s.png' % (exportName, i)))
            each[1].Save(screenPath)
            outPaths.append(screenPath)

        return outPaths

    def Upload(self, name, appData, benchmarkData = None, tags = '', saveDir = ''):
        import requests
        if saveDir:
            try:
                os.makedirs(saveDir)
            except OSError:
                pass

        tempDir = saveDir if saveDir else tempfile.mkdtemp()
        try:
            paths = self.Export(name, os.path.join(tempDir, 'measurement.json'), appData, benchmarkData)
            files = [ (os.path.basename(x), open(x, 'rb')) for x in paths ]
            try:
                ret = requests.request('POST', PERFMEASUREMENTS_UPLOAD_URL, data={'tags': tags}, files={str(i):v for i, v in enumerate(files)}).json()
                result = bool(ret['success'])
            finally:
                for each in files:
                    each[1].close()

            if not result:
                raise RuntimeError('failed to upload')
        finally:
            if not saveDir:
                shutil.rmtree(tempDir)

    def GetAggregatedStats(self, statsFilter):
        aggregatedStats = {}
        for statistic in self._statistics:
            if statistic['name'] in statsFilter and len(statistic['perFrame']):
                mean = sum(statistic['perFrame']) / len(statistic['perFrame'])
                aggregatedStats[statistic['name']] = mean

        return aggregatedStats
