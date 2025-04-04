#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinutils\sceneutils.py
import blue
import trinity
from caching.memoize import Memoize
try:
    from carbon.tools.jessica import jessica
except ImportError:
    jessica = None

def FindScene(useDeviceSceneIfFound = True, types = None):
    if types is None:
        types = (trinity.Tr2InteriorScene, trinity.EveSpaceScene)

    def RecursiveSearch(rj):
        for step in rj.steps:
            if hasattr(step, 'object') and isinstance(step.object, types):
                return step.object
            if isinstance(step, trinity.TriStepRunJob):
                scene = RecursiveSearch(step.job)
                if scene:
                    return scene

    scene = None
    if useDeviceSceneIfFound and trinity.device.scene:
        return trinity.device.scene
    for rj in trinity.renderJobs.recurring:
        scene = RecursiveSearch(rj)
        if scene:
            break

    return scene


@Memoize
def GetSceneTypes():
    sceneClasses = []
    classInfo = trinity.GetClassInfo()
    for key, value in classInfo.iteritems():
        if 'ITr2Scene' in value[1] or 'ITr2LightPrePassScene' in value[1]:
            sceneClasses.append('trinity.' + key)

    return sceneClasses


def FindAllScenes():
    results = []
    sceneTypes = GetSceneTypes()
    for each in trinity.renderJobs.Find(sceneTypes):
        if blue.objectMetadata.Get(each, 'JessicaHidden', ''):
            continue
        results.append(each)

    return results


def GetOrCreateScene():
    scene = FindScene()
    if scene is None or not isinstance(scene, trinity.EveSpaceScene):
        scene = trinity.EveSpaceScene()
    if trinity.device.scene != scene:
        trinity.device.scene = scene
    return scene


def CreateFisRenderJob(scene):
    jessica.GetGlobalJessicaModel().SetRenderInfo(scene)


def CreateBackgroundLandscape(scene, medDetailThreshold = 0.0001, lowDetailThreshold = 0.0001, shaderModel = 'SM_3_0_DEPTH'):
    m10 = trinity.Load('res:/dx9/scene/universe/m10_cube.red')
    scene.backgroundEffect = m10.backgroundEffect
    scene.envMapResPath = m10.envMapResPath
    scene.envMap1ResPath = m10.envMap1ResPath
    scene.envMap2ResPath = m10.envMap2ResPath
    scene.envMap3ResPath = m10.envMap3ResPath
    scene.backgroundEffect = scene.backgroundEffect
    scene.sunDiffuseColor = (1.5, 1.5, 1.5, 1.0)
    trinity.settings.SetValue('eveSpaceSceneVisibilityThreshold', 3.0)
    trinity.settings.SetValue('eveSpaceSceneMediumDetailThreshold', medDetailThreshold)
    trinity.settings.SetValue('eveSpaceSceneLowDetailThreshold', lowDetailThreshold)
    trinity.SetShaderModel(shaderModel)
    scene.starfield = trinity.Load('res:/dx9/scene/starfield/spritestars.red')
    scene.starfield.minDist = 40
    scene.starfield.maxDist = 80
    scene.starfield.numStars = 500
    universe = [ stars for stars in scene.backgroundObjects if stars.name == 'Neighboring Stars' ]
    if not universe:
        universe = trinity.Load('res:/dx9/scene/starfield/universe.red')
        scene.backgroundObjects.append(universe)
        systemX = -20474870.72500089
        systemY = 4023837.993657142
        systemZ = 5762127.890242104
        universe.children[0].translation = (systemX, systemY, systemZ)
    scene.backgroundRenderingEnabled = True
    if jessica:
        CreateFisRenderJob(scene)


def LoadObjectFromPath(path):
    blue.motherLode.Delete(path)
    return trinity.Load(path, True)
