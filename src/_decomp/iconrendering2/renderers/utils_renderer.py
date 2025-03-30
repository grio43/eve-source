#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\renderers\utils_renderer.py
import trinity
import blue
import os
from trinity.sceneRenderJobSpaceJessica import CreateJessicaSpaceRenderJob
from trinity.renderJob import RenderJob
from iconrendering2.utils import Pump, IsExeFile
_RENDERJOBS_CACHE = {}

def RenderToBitmapFromScene(renderInfo, scene, view, projection, postProcessingQuality = 0, supersampleQuality = 1, useRenderjobCache = False, waitTime = 0):
    return _RenderToBitmap(renderInfo, scene, view, projection, None, postProcessingQuality, supersampleQuality, useRenderjobCache, waitTime)


def RenderToBitmapFromIcon(renderInfo):
    if renderInfo.backgroundTransparent:
        transparent = True
        backgroundPath = ''
    else:
        transparent = False
        backgroundPath = renderInfo.background
    renderJob, rt = CreateRenderJobFromIconPath(renderInfo.renderSize, renderInfo.inputIcon, backgroundPath, renderInfo.foreground, renderInfo.overlay, renderInfo.backgroundColor, transparent)
    blue.resMan.Wait()
    renderJob.ScheduleOnce()
    renderJob.WaitForFinish()
    return trinity.Tr2HostBitmap(rt)


def _RenderToBitmap(renderInfo, scene, view = None, projection = None, iconPath = None, postProcessingQuality = 0, supersampleQuality = 1, useRenderjobCache = False, waitTime = 0):
    size = renderInfo.renderSize
    size *= 2 ** supersampleQuality
    transparent = renderInfo.backgroundTransparent
    renderJob = CreateRenderJob(size, view, projection, renderInfo.backgroundColor, transparent, postProcessingQuality, supersampleQuality, useRenderjobCache)
    renderJob.SetScene(scene)
    backgroundPath = renderInfo.background
    if backgroundPath or transparent:
        scene.backgroundRenderingEnabled = False
        if backgroundPath:
            renderJob.backgroundTexture.resPath = backgroundPath
    if renderInfo.overlay:
        renderJob.overlayTexture.resPath = renderInfo.overlay
    if renderInfo.foreground:
        renderJob.techTexture.resPath = renderInfo.foreground
    if iconPath:
        renderJob.iconTexture.resPath = iconPath
    renderJob.SetSettingsBasedOnPerformancePreferences()
    blue.resMan.Wait()
    renderJob.RemoveStep('FPS_COUNTER')
    trinity.renderJobs.UnscheduleByName('FPS')
    if not IsExeFile():
        trinity.renderJobs.recurring.removeAt(-1)
    time = blue.os.GetSimTime()
    if waitTime > 0:
        renderJob.Start()
        s = blue.os.GetSimTime()
        wait = waitTime * 1000
        while blue.os.TimeDiffInMs(s, blue.os.GetSimTime()) < wait:
            time = blue.os.GetSimTime()
            scene.UpdateScene(time)
            Pump()

        renderJob.UnscheduleRecurring()
        renderJob.WaitForFinish()
    else:
        time = blue.os.GetSimTime()
        scene.UpdateScene(time)
        renderJob.ScheduleOnce()
        renderJob.WaitForFinish()
        Pump()
    scene.UpdateScene(time)
    Pump()
    blue.resMan.Wait()
    renderJob.ScheduleOnce()
    renderJob.WaitForFinish()
    Pump()
    hostBitmap = trinity.Tr2HostBitmap(renderJob.renderTarget)
    for _ in range(supersampleQuality):
        hostBitmap.Downsample2x2()

    if useRenderjobCache:
        renderJob.status = trinity.RJ_INIT
    renderJob.SetScene(None)
    return hostBitmap


def RenderToSurface(scene, view, projection, size = 128, bgColor = None, transparent = False, backgroundPath = None, overlayPath = None, techPath = None, iconPath = None, postProcessingQuality = 0, supersampleQuality = 1, useRenderjobCache = False):
    size *= 2 ** supersampleQuality
    renderJob = CreateRenderJob(size, view, projection, bgColor, transparent, postProcessingQuality, supersampleQuality, useRenderjobCache)
    if scene:
        renderJob.SetScene(scene)
    else:
        renderJob.SetScene(trinity.EveSpaceScene())
    if backgroundPath:
        scene.backgroundRenderingEnabled = False
        renderJob.backgroundTexture.resPath = backgroundPath
    if overlayPath:
        renderJob.overlayTexture.resPath = overlayPath
    if iconPath:
        renderJob.iconTexture.resPath = iconPath
    if techPath:
        renderJob.techTexture.resPath = techPath
    renderJob.SetSettingsBasedOnPerformancePreferences()
    blue.resMan.Wait()
    renderJob.ScheduleOnce()
    renderJob.WaitForFinish()
    hostBitmap = trinity.Tr2HostBitmap(renderJob.renderTarget)
    for _ in range(supersampleQuality):
        hostBitmap.Downsample2x2()

    if useRenderjobCache:
        renderJob.status = trinity.RJ_INIT
    renderJob.SetScene(None)
    return hostBitmap


def ApplyOutline(outPath, size, outlineColor, thickness, hardlines, backgroundPath):
    if thickness <= 0:
        return
    if not os.path.exists(outPath):
        return
    color = (outlineColor[0], outlineColor[1], outlineColor[2])
    alpha = float(outlineColor[3] if len(outlineColor) > 3 else 255) / 255.0
    from PIL import Image, ImageFilter
    n = 0.5
    o = 0

    class CustomBlurFilter(ImageFilter.BuiltinFilter):
        name = 'CustomBlur'
        filterargs = ((5, 5),
         16,
         0,
         (o,
          o,
          o,
          o,
          o,
          o,
          n,
          n,
          n,
          o,
          o,
          n,
          1,
          n,
          o,
          o,
          n,
          n,
          n,
          o,
          o,
          o,
          o,
          o,
          o))

    bigImg = Image.open(outPath).convert('RGBA')
    bigAlphaData = bigImg.tostring('raw', 'A')
    bigAlphaImg = Image.fromstring('L', bigImg.size, bigAlphaData)
    bigAlphaBlur = Image.fromstring('L', bigImg.size, bigAlphaData)
    for i in range(0, int(thickness)):
        bigAlphaBlur = bigAlphaBlur.filter(CustomBlurFilter)
        bigAlphaBlur = Image.eval(bigAlphaBlur, lambda px: (255 if px > 0 else 0))

    mainImg = bigImg.resize((size, size), Image.ANTIALIAS)
    alphaBlur = bigAlphaBlur.resize((size, size), Image.ANTIALIAS)
    alphaImg = bigAlphaImg.resize((size, size), Image.ANTIALIAS)
    if backgroundPath:
        backgroundImg = Image.open(backgroundPath).convert('RGBA')
        backgroundImg = backgroundImg.resize((size, size), Image.ANTIALIAS)
    else:
        backgroundImg = Image.new('RGBA', mainImg.size, (0, 0, 0, 0))
    outlineImg = Image.new('RGBA', mainImg.size, color)
    if alpha < 1.0:
        alphaBlur = Image.eval(alphaBlur, lambda px: alpha * px)
    finalImg = Image.composite(outlineImg, backgroundImg, alphaBlur)
    if not hardlines:
        finalImg = finalImg.filter(ImageFilter.BLUR).filter(ImageFilter.BLUR)
    finalImg = Image.composite(mainImg, finalImg, alphaImg)
    finalImg.save(outPath)


def CreateRenderJobFromIconPath(size, iconPath, backgroundPath, foregroundPath, overlayPath, bgColor = None, transparent = False):
    if transparent:
        clearColor = bgColor or (0.0, 0.0, 0.0, 0.0)
        pixelFormat = trinity.PIXEL_FORMAT.B8G8R8A8_UNORM
    else:
        clearColor = bgColor or (0.0, 0.0, 0.0, 1.0)
        pixelFormat = trinity.PIXEL_FORMAT.B8G8R8X8_UNORM
    rt = trinity.Tr2RenderTarget(size, size, 1, pixelFormat)
    rt.name = 'MyRT'
    renderjob = RenderJob()
    renderjob.steps.append(trinity.TriStepPushRenderTarget(rt))
    renderjob.steps.append(trinity.TriStepPushDepthStencil(None))
    renderjob.steps.append(trinity.TriStepClear(clearColor))
    bgSprite1 = CreateSprite(1.0, size)
    bgSprite2 = CreateSprite(1.0, size)
    bgSpriteScene = trinity.Tr2Sprite2dScene()
    bgSpriteScene.children.append(bgSprite1)
    bgSpriteScene.children.append(bgSprite2)
    renderjob.steps.append(trinity.TriStepRenderScene(bgSpriteScene))
    setattr(renderjob, 'iconTexture', bgSprite1.texturePrimary)
    setattr(renderjob, 'backgroundTexture', bgSprite2.texturePrimary)
    oSprite1 = CreateSprite(1.0, size)
    oSprite1.blendMode = 2
    oSprite2 = CreateSprite(1.0, size)
    oSprite2.blendMode = 1
    oSpriteScene = trinity.Tr2Sprite2dScene()
    oSpriteScene.children.append(oSprite2)
    oSpriteScene.children.append(oSprite1)
    renderjob.steps.append(trinity.TriStepRenderScene(oSpriteScene))
    renderjob.steps.append(trinity.TriStepPopDepthStencil())
    renderjob.steps.append(trinity.TriStepPopRenderTarget())
    setattr(renderjob, 'overlayTexture', oSprite1.texturePrimary)
    setattr(renderjob, 'techTexture', oSprite2.texturePrimary)
    setattr(renderjob, 'renderTarget', rt)
    setattr(renderjob, 'scaledSprite', oSprite2)
    scale = 16.0 / size
    oSprite2.displayHeight = scale
    oSprite2.displayWidth = scale
    oSprite1.texturePrimary.resPath = overlayPath or 'res:/Texture/Global/blackAlpha.dds'
    bgSprite1.texturePrimary.resPath = iconPath or 'res:/Texture/Global/blackAlpha.dds'
    bgSprite1.texturePrimary.atlasTexture.isStandAlone = True
    bgSprite2.texturePrimary.resPath = backgroundPath or 'res:/Texture/Global/blackAlpha.dds'
    oSprite2.texturePrimary.resPath = foregroundPath or 'res:/Texture/Global/blackAlpha.dds'
    return (renderjob, rt)


def CreateRenderJob(size, view, projection, bgColor = None, transparent = False, postProcessingQuality = 2, supersampleQuality = 1, useRenderjobCache = False):
    global _RENDERJOBS_CACHE
    if transparent:
        clearColor = bgColor or (0.0, 0.0, 0.0, 0.0)
        format = trinity.PIXEL_FORMAT.B8G8R8A8_UNORM
    else:
        clearColor = bgColor or (0.0, 0.0, 0.0, 1.0)
        format = trinity.PIXEL_FORMAT.B8G8R8X8_UNORM
    if not useRenderjobCache or GetRenderjob(size, transparent) is None:

        def _GetRenderStepPosition(rj, name):
            for i, each in enumerate(rj.steps):
                if each.name == name:
                    return i

            return -1

        rt = trinity.Tr2RenderTarget(size, size, 1, format)
        rt.name = 'MyRT'
        ds = trinity.Tr2DepthStencil(size, size, trinity.DEPTH_STENCIL_FORMAT.D24S8)
        ds.name = 'MyDS'
        vp = trinity.TriViewport()
        vp.width = size
        vp.height = size
        renderjob = CreateJessicaSpaceRenderJob()
        renderjob.updateJob = None
        renderjob.CreateBasicRenderSteps()
        settings = renderjob.GetSettings()
        settings['aaQuality'] = 0
        renderjob.SetSettings(settings)
        renderjob.SetViewport(vp)
        renderjob.OverrideBuffers(rt, ds)
        bgStep = trinity.TriStepRenderScene()
        bgStep.name = 'BACKGROUND_SPRITE'
        bgSprite1 = CreateSprite(1.0, size)
        bgSprite2 = CreateSprite(1.0, size)
        bgSpriteScene = trinity.Tr2Sprite2dScene()
        bgSpriteScene.children.append(bgSprite1)
        bgSpriteScene.children.append(bgSprite2)
        bgStep.scene = bgSpriteScene
        pos = _GetRenderStepPosition(renderjob, 'CLEAR')
        renderjob.steps.insert(pos + 1, bgStep)
        setattr(renderjob, 'iconTexture', bgSprite1.texturePrimary)
        setattr(renderjob, 'backgroundTexture', bgSprite2.texturePrimary)
        oStep = trinity.TriStepRenderScene()
        oStep.name = 'OVERLAY_SPRITES'
        oSprite1 = CreateSprite(1.0, size)
        oSprite1.blendMode = 2
        oSprite2 = CreateSprite(1.0, size)
        oSprite2.blendMode = 1
        oSpriteScene = trinity.Tr2Sprite2dScene()
        oSpriteScene.children.append(oSprite2)
        oSpriteScene.children.append(oSprite1)
        oStep.scene = oSpriteScene
        pos2 = _GetRenderStepPosition(renderjob, 'END_RENDERING')
        renderjob.steps.insert(pos2 + 1, oStep)
        setattr(renderjob, 'overlayTexture', oSprite1.texturePrimary)
        setattr(renderjob, 'techTexture', oSprite2.texturePrimary)
        setattr(renderjob, 'renderTarget', rt)
        setattr(renderjob, 'scaledSprite', oSprite2)
        _RENDERJOBS_CACHE[size, format] = renderjob
    renderjob = GetRenderjob(size, transparent)
    settings = renderjob.GetSettings()
    settings['postProcessingQuality'] = postProcessingQuality
    renderjob.SetSettings(settings)
    renderjob.SetActiveCamera(view=view, projection=projection)
    renderjob.Enable(False)
    scale = 16.0 * 2 ** supersampleQuality / size
    renderjob.scaledSprite.displayHeight = scale
    renderjob.scaledSprite.displayWidth = scale
    renderjob.renderTarget.Create(size, size, 1, format)
    renderjob.OverrideSettings('bbFormat', format)
    renderjob.SetClearColor(clearColor)
    renderjob.overlayTexture.resPath = 'res:/Texture/Global/blackAlpha.dds'
    renderjob.iconTexture.resPath = 'res:/Texture/Global/blackAlpha.dds'
    renderjob.backgroundTexture.resPath = 'res:/Texture/Global/blackAlpha.dds'
    renderjob.techTexture.resPath = 'res:/Texture/Global/blackAlpha.dds'
    return renderjob


def GetRenderjob(size, transparent):
    if transparent:
        return _RENDERJOBS_CACHE.get((size, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM), None)
    return _RENDERJOBS_CACHE.get((size, trinity.PIXEL_FORMAT.B8G8R8X8_UNORM), None)


def CreateSprite(scale, size):
    sprite = trinity.Tr2Sprite2d()
    sprite.texturePrimary = trinity.Tr2Sprite2dTexture()
    sprite.texturePrimary.resPath = 'res:/Texture/Global/blackAlpha.dds'
    sprite.displayHeight = scale
    sprite.displayWidth = scale
    sprite.displayX = 0
    sprite.displayY = 0
    return sprite
