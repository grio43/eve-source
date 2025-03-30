#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\graphicEffects\texture.py
import trinity
import logging
from brennivin import nicenum
log = logging.getLogger(__name__)

def LinearToSrgb(value):
    if value < 0.0031308:
        return value * 12.92
    return value ** (1 / 2.4) * 1.055 - 0.055


class TextureInfo:

    def __init__(self, texture):
        self.texture = texture
        self.textureType = getattr(texture, 'type', trinity.TEXTURE_TYPE.TEX_TYPE_2D)
        minArraySize = 6 if self.textureType == trinity.TEXTURE_TYPE.TEX_TYPE_CUBE else 1
        arraySize = getattr(texture, 'arraySize', minArraySize)
        self.textureTypeName = trinity.TEXTURE_TYPE.GetNameFromValue(self.textureType)
        self.isArray = arraySize > minArraySize or self.textureType == trinity.TEXTURE_TYPE.TEX_TYPE_3D
        self.arraySize = arraySize / minArraySize - 1
        self.format = trinity.PIXEL_FORMAT.GetNameFromValue(texture.format)
        self.colorSpace = 'Linear'
        if 'UNORM' in self.format:
            self.colorSpace = 'SRGB'
        elif isinstance(texture, trinity.Tr2DepthStencil):
            self.format = trinity.DEPTH_STENCIL_FORMAT.GetNameFromValue(texture.format)
            self.colorSpace = 'Logarithmic'
        self.width = texture.width
        self.height = texture.height
        self.depth = getattr(texture, 'depth', 1)
        self.mips = texture.mipCount
        self.msaa = getattr(texture, 'multiSampleType', 1)
        self.path = getattr(texture, 'path', texture.__bluetype__)
        self.gpuMip = getattr(texture, 'gpuMip', 0)
        self.cpuMip = getattr(texture, 'cpuMip', 0)
        self.lodEnabled = getattr(texture, 'lodEnabled', False)
        self.memory = nicenum.format_memory(texture.GetMemoryUsage()) if hasattr(texture, 'GetMemoryUsage') else 'N/A'
        self.effect = CreatePreviewEffect(texture)
        self._minValue = 0.0
        self._maxValue = 1.0
        self.SetColorSpace(self.colorSpace)

    def __del__(self):
        self.texture = None
        self.effect = None

    def RefreshInfo(self):
        self.gpuMip = getattr(self.texture, 'gpuMip', 0)
        self.cpuMip = getattr(self.texture, 'cpuMip', 0)

    def GetMipOptions(self):
        mipLevels = [(-1, 'Auto Mip')]
        width = self.width
        height = self.height
        for mip in range(0, self.mips):
            mipLevels.append((mip, 'Mip %d (%d x %d)' % (mip, width, height)))
            width = max(width / 2, 1)
            height = max(height / 2, 1)

        return mipLevels

    def GetColorSpaceOptions(self):
        return ['Linear', 'SRGB', 'Logarithmic']

    def IsCube(self):
        return self.textureType == trinity.TEXTURE_TYPE.TEX_TYPE_CUBE

    def Is3D(self):
        return self.textureType == trinity.TEXTURE_TYPE.TEX_TYPE_3D

    def IsSRGB(self):
        return self.colorSpace == 'SRGB'

    def SetMinValue(self, value):
        self._minValue = value
        if self.IsSRGB():
            value = LinearToSrgb(value)
        self._SetEffectValue('MinValue', (value,
         value,
         value,
         value))

    def SetMaxValue(self, value):
        self._maxValue = value
        if self.IsSRGB():
            value = LinearToSrgb(value)
        self._SetEffectValue('MaxValue', (value,
         value,
         value,
         value))

    def SetSlice(self, index):
        if not self.isArray:
            return
        attribute = 'ArraySlice'
        if self.textureType == trinity.TEXTURE_TYPE.TEX_TYPE_3D:
            attribute = 'VolumeSlice'
        self._SetEffectValue(attribute, index)

    def ShowAllChannels(self):
        self._SetChannels(((1, 0, 0, 0),
         (0, 1, 0, 0),
         (0, 0, 1, 0),
         (0, 0, 0, 1)))

    def ShowRedChannel(self):
        self._SetChannels(((1, 1, 1, 1),
         (0, 0, 0, 0),
         (0, 0, 0, 0),
         (0, 0, 0, 0)))

    def ShowGreenChannel(self):
        self._SetChannels(((0, 0, 0, 0),
         (1, 1, 1, 1),
         (0, 0, 0, 0),
         (0, 0, 0, 0)))

    def ShowBlueChannel(self):
        self._SetChannels(((0, 0, 0, 0),
         (0, 0, 0, 0),
         (1, 1, 1, 1),
         (0, 0, 0, 0)))

    def ShowAlphaChannel(self):
        self._SetChannels(((0, 0, 0, 0),
         (0, 0, 0, 0),
         (0, 0, 0, 0),
         (1, 1, 1, 1)))

    def SetMipLevel(self, mip):
        self._SetEffectValue('UseForceMipMap', 0 if mip is -1 else 1)
        if mip > -1:
            self._SetEffectValue('ForceMipMap', mip)

    def SetViewMode(self, viewMode):
        for i, each in enumerate(self.effect.options):
            if each[0] == 'CUBE_RENDERING_MODE':
                self.effect.options[i] = ('CUBE_RENDERING_MODE', viewMode.upper())

        self.effect.RebuildCachedData()

    def SetColorSpace(self, colorSpace):
        lookup = {'srgb': 'SRGB_SPACE',
         'linear': 'LINEAR_SPACE',
         'logarithmic': 'LOGARITHMIC_SPACE'}
        self.SetMinValue(self._minValue)
        self.SetMaxValue(self._maxValue)
        for i, each in enumerate(self.effect.options):
            if each[0] == 'COLOR_SPACE':
                self.effect.options[i] = ('COLOR_SPACE', lookup[colorSpace.lower()])

        self.colorSpace = colorSpace
        self.effect.RebuildCachedData()

    def _SetChannels(self, transform):
        for i, row in enumerate(transform):
            self._SetEffectValue('ColorTransform%s' % i, row)

    def _SetEffectValue(self, paramName, value):
        p = self.effect.parameters.FindByName(paramName)
        if p is None:
            log.error("parameter '%s' not found" % paramName)
            return
        p.value = value


def CreatePreviewEffect(texture):
    effect = trinity.Tr2Effect()
    effect.effectFilePath = 'res:/Graphics/Effect/Utility/TextureViewer.fx'
    msaaType = getattr(texture, 'multiSampleType', 1)
    MinValue = trinity.Tr2Vector4Parameter()
    MinValue.name = 'MinValue'
    MinValue.value = (0, 0, 0, 0)
    effect.parameters.append(MinValue)
    MaxValue = trinity.Tr2Vector4Parameter()
    MaxValue.name = 'MaxValue'
    MaxValue.value = (1, 1, 1, 1)
    effect.parameters.append(MaxValue)
    ColorTransform0 = trinity.Tr2Vector4Parameter()
    ColorTransform0.name = 'ColorTransform0'
    ColorTransform0.value = (1, 0, 0, 0)
    effect.parameters.append(ColorTransform0)
    ColorTransform1 = trinity.Tr2Vector4Parameter()
    ColorTransform1.name = 'ColorTransform1'
    ColorTransform1.value = (0, 1, 0, 0)
    effect.parameters.append(ColorTransform1)
    ColorTransform2 = trinity.Tr2Vector4Parameter()
    ColorTransform2.name = 'ColorTransform2'
    ColorTransform2.value = (0, 0, 1, 0)
    effect.parameters.append(ColorTransform2)
    ColorTransform3 = trinity.Tr2Vector4Parameter()
    ColorTransform3.name = 'ColorTransform3'
    ColorTransform3.value = (0, 0, 0, 1)
    effect.parameters.append(ColorTransform3)
    UseForceMipMap = trinity.Tr2FloatParameter()
    UseForceMipMap.name = 'UseForceMipMap'
    UseForceMipMap.value = 0
    effect.parameters.append(UseForceMipMap)
    ForceMipMap = trinity.Tr2FloatParameter()
    ForceMipMap.name = 'ForceMipMap'
    ForceMipMap.value = 0
    effect.parameters.append(ForceMipMap)
    VolumeSlice = trinity.Tr2FloatParameter()
    VolumeSlice.name = 'VolumeSlice'
    VolumeSlice.value = 0
    effect.parameters.append(VolumeSlice)
    ArraySlice = trinity.Tr2FloatParameter()
    ArraySlice.name = 'ArraySlice'
    ArraySlice.value = 0
    effect.parameters.append(ArraySlice)
    MsaaType = trinity.Tr2FloatParameter()
    MsaaType.name = 'MsaaType'
    MsaaType.value = msaaType
    effect.parameters.append(MsaaType)
    if isinstance(texture, (trinity.TriTextureRes, trinity.Tr2DepthStencil)):
        param = trinity.TriTextureParameter()
        param.name = 'Texture'
        param.SetResource(texture)
    else:
        param = trinity.Tr2RuntimeTextureParameter()
        param.name = 'Texture'
        param.texture = texture
    effect.resources.append(param)
    minArraySize = 1
    textureType = getattr(texture, 'type', trinity.TEXTURE_TYPE.TEX_TYPE_2D)
    if textureType == trinity.TEXTURE_TYPE.TEX_TYPE_CUBE:
        effect.options.append(('TEXTURE_TYPE', 'TEXTURE_CUBE'))
        effect.options.append(('CUBE_RENDERING_MODE', 'CUBE'))
        minArraySize = 6
    elif textureType == trinity.TEXTURE_TYPE.TEX_TYPE_3D:
        effect.options.append(('TEXTURE_TYPE', 'TEXTURE_3D'))
    else:
        effect.options.append(('TEXTURE_TYPE', 'TEXTURE_2D'))
    effect.options.append(('TEXTURE_ARRAY', 'ARRAY_YES' if getattr(texture, 'arraySize', minArraySize) > minArraySize else 'ARRAY_NO'))
    effect.options.append(('TEXTURE_MSAA', 'MSAA_YES' if msaaType > 1 else 'MSAA_NO'))
    try:
        name = trinity.PIXEL_FORMAT.GetNameFromValue(texture.format)
    except AttributeError:
        name = ''

    if name.endswith('_UINT'):
        effect.options.append(('TEXTURE_FORMAT', 'FORMAT_UINT'))
    elif name.endswith('_INT'):
        effect.options.append(('TEXTURE_FORMAT', 'FORMAT_INT'))
    else:
        effect.options.append(('TEXTURE_FORMAT', 'FORMAT_FLOAT'))
    effect.options.append(('COLOR_SPACE', 'SRGB_SPACE' if 'UNORM' in name else 'LINEAR_SPACE'))
    effect.RebuildCachedData()
    return effect
