#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\paperDoll\paperDollConfiguration.py
import eve.common.script.paperDoll.paperDollDefinitions as pdDef
from .yamlPreloader import YamlPreloader
import blue
import log

class PerformanceOptions:
    useLodForRedfiles = False
    if hasattr(const, 'PAPERDOLL_LOD_RED_FILES'):
        useLodForRedfiles = const.PAPERDOLL_LOD_RED_FILES
    collapseShadowMesh = False
    if hasattr(const, 'PAPERDOLL_COLLAPSE_SHADOWMESH'):
        collapseShadowMesh = const.PAPERDOLL_COLLAPSE_SHADOWMESH
    collapseMainMesh = False
    if hasattr(const, 'PAPERDOLL_COLLAPSE_MAINMESH'):
        collapseMainMesh = const.PAPERDOLL_COLLAPSE_MAINMESH
    collapsePLPMesh = False
    if hasattr(const, 'PAPERDOLL_COLLAPSE_PLPMESH'):
        collapsePLPMesh = const.PAPERDOLL_COLLAPSE_PLPMESH
    preloadNudeAssets = False
    if hasattr(const, 'PAPERDOLL_PRELOAD_NUDE_ASSETS'):
        preloadNudeAssets = const.PAPERDOLL_PRELOAD_NUDE_ASSETS
    preloadGenericHeadModifiers = False
    shadowLod = 2
    collapseVerbose = False
    lodTextureSizes = [(2048, 1024), (512, 256), (256, 128)]
    textureSizeFactors = {pdDef.DIFFUSE_MAP: 1,
     pdDef.NORMAL_MAP: 1,
     pdDef.SPECULAR_MAP: 1}
    maskMapTextureSize = (1024, 512)
    updateFreq = {}
    useLod2DDS = False
    logLodPerformance = False
    maxLodQueueActiveUp = 3
    maxLodQueueActiveDown = 6
    EnsureCompleteBody = True
    singleBoneLod = 2

    @staticmethod
    def SetEnableYamlCache(enable):
        yamlPreloader = YamlPreloader()
        if enable:
            if blue.paths.exists(pdDef.PAPERDOLL_CACHE_FILE):
                yamlPreloader.LoadCacheFromPickle(pdDef.PAPERDOLL_CACHE_FILE)
            else:
                log.LogWarn('PaperDoll cache file not found')
                extensions = ('.yaml', '.pose', '.type', '.color', '.trif', '.face', 'restrictions')
                yamlPreloader.Preload(rootFolder='res:/graphics/character', extensions=extensions)
                yamlPreloader.SaveCacheAsPickle(pdDef.PAPERDOLL_CACHE_FILE)
        else:
            yamlPreloader.Clear()

    @staticmethod
    def SetEnableLodQueue(enable):
        from eve.client.script.paperDoll.paperDollLOD import LodQueue
        if enable:
            LodQueue.instance = LodQueue()
        else:
            LodQueue.instance = None

    @staticmethod
    def EnableOptimizations():
        PerformanceOptions.collapseShadowMesh = False
        PerformanceOptions.collapseMainMesh = False
        PerformanceOptions.collapsePLPMesh = False
        PerformanceOptions.shadowLod = 1
        PerformanceOptions.singleBoneLod = 1
        PerformanceOptions.updateFreq = {0: 0,
         1: 20,
         2: 8}
        try:
            import trinity
            from eve.client.script.paperDoll.paperDollImpl import Factory
            trinity.settings.SetValue('skinnedLowDetailThreshold', 250)
            trinity.settings.SetValue('skinnedMediumDetailThreshold', 650)
            trinity.settings.SetValue('skinnedMediumLowMargin', 70)
            trinity.settings.SetValue('skinnedHighMediumMargin', 100)
            Factory.PreloadShaders()
        except (ImportError, AttributeError):
            pass

        PerformanceOptions.SetEnableLodQueue(True)
        PerformanceOptions.logLodPerformance = True

    @staticmethod
    def EnableEveOptimizations():
        PerformanceOptions.useLodForRedfiles = True
        PerformanceOptions.useLod2DDS = True
