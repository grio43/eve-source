#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\bitmapjob.py
import trinity
import blue

def makeBitmapStep(filePath, scaleToFit = True, color = (1.0, 1.0, 1.0, 1.0), targetSize = None):
    tex = trinity.TriTextureParameter()
    tex.name = 'Texture'
    tex.resourcePath = filePath
    if targetSize is None:
        bb = trinity.device.GetRenderContext().GetDefaultBackBuffer()
        targetSize = (bb.width, bb.height)
    fx = trinity.Tr2Effect()
    fx.effectFilePath = 'res:/Graphics/Effect/Managed/Space/System/ColoredBlit.fx'
    fx.resources.append(tex)
    while tex.resource.isLoading:
        blue.synchro.Yield()

    sw = float(tex.resource.width)
    sh = float(tex.resource.height)
    tw = float(targetSize[0])
    th = float(targetSize[1])
    v = trinity.Tr2Vector4Parameter()
    v.name = 'Color'
    v.value = color
    fx.parameters.append(v)
    v = trinity.Tr2Vector4Parameter()
    v.name = 'SourceUVs'
    fx.parameters.append(v)
    sourceAspect = sw / sh
    targetAspect = tw / th
    if scaleToFit:
        if targetAspect > sourceAspect:
            span = targetAspect / sourceAspect
            v.value = (0.5 - 0.5 * span,
             0.0,
             0.5 + 0.5 * span,
             1.0)
        else:
            span = sourceAspect / targetAspect
            v.value = (0,
             0.5 - 0.5 * span,
             1.0,
             0.5 + 0.5 * span)
    elif targetAspect > sourceAspect:
        d = 1.0 - sw * th / (sh * tw)
        d *= 0.5
        v.value = (0.0,
         d,
         1.0,
         1.0 - d)
    else:
        d = 1.0 - tw * sh / (th * sw)
        d *= 0.5
        v.value = (d,
         0.0,
         1.0 - d,
         1.0)
    return trinity.TriStepRenderEffect(fx)


def addBitmapRenderJob(filePath, scaleToFit = True, color = (1.0, 1.0, 1.0, 1.0), targetSize = None):
    rj = trinity.CreateRenderJob('Background bitmap')
    step = makeBitmapStep(filePath, scaleToFit=scaleToFit, color=color, targetSize=targetSize)
    rj.steps.append(step)
    rj.ScheduleRecurring()


def makeCubemapStep(filePath, scaleToFit = True, color = (1.0, 1.0, 1.0, 1.0), cubeFace = 0, targetSize = None):
    tex = trinity.TriTextureParameter()
    tex.name = 'BlitSource'
    tex.resourcePath = filePath
    if targetSize is None:
        bb = trinity.device.GetRenderContext().GetDefaultBackBuffer()
        targetSize = (bb.width, bb.height)
    targetAspect = float(targetSize[0]) / float(targetSize[1])
    fx = trinity.Tr2Effect()
    fx.effectFilePath = 'res:/Graphics/Effect/Managed/Space/System/ColoredBlitCube.fx'
    fx.effectResource.Reload()
    fx.resources.append(tex)
    v = trinity.Tr2Vector4Parameter()
    v.name = 'Color'
    v.value = color
    fx.parameters.append(v)
    v = trinity.Tr2FloatParameter()
    v.name = 'cubeFace'
    v.value = cubeFace
    fx.parameters.append(v)
    v = trinity.Tr2Vector4Parameter()
    v.name = 'ScaleXY'
    fx.parameters.append(v)
    if scaleToFit:
        if targetAspect >= 1.0:
            v.value = (targetAspect,
             1.0,
             1.0,
             1.0)
        else:
            v.value = (1.0,
             1.0 / targetAspect,
             1.0,
             1.0)
    elif targetAspect < 1.0:
        v.value = (targetAspect,
         1.0,
         1.0,
         1.0)
    else:
        v.value = (1.0,
         1.0 / targetAspect,
         1.0,
         1.0)
    return trinity.TriStepRenderEffect(fx)


def addCubemapRenderJob(filePath, scaleToFit = True, color = (1.0, 1.0, 1.0, 1.0), cubeFace = 0, targetSize = None):
    rj = trinity.CreateRenderJob('Background cubemap')
    step = makeCubemapStep(filePath, scaleToFit=scaleToFit, color=color, cubeFace=cubeFace, targetSize=targetSize)
    rj.steps.append(step)
    rj.ScheduleRecurring()
