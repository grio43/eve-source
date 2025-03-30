#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\gpumemory.py
from nicenum import FormatMemory
import trinity

class ResourceFilters(object):

    @staticmethod
    def IsTexture(name, _):
        return name == 'Tr2TextureAL'

    @staticmethod
    def IsRenderTarget(name, value):
        return name == 'Tr2TextureAL' and int(value.get('gpuUsage', 0)) & 4 != 0

    @staticmethod
    def IsDepthStencil(name, value):
        return name == 'Tr2TextureAL' and int(value.get('gpuUsage', 0)) & 8 != 0

    @staticmethod
    def IsImmutable(_, value):
        return int(value.get('gpuUsage', 0)) & (4 | 8 | 32 | 64) == 0 and int(value.get('cpuUsage', 0)) & 2 == 0

    @staticmethod
    def IsBuffer(name, _):
        return name == 'Tr2BufferAL'

    @staticmethod
    def IsDynamic(_, value):
        return int(value.get('cpuUsage', 0)) & 8 != 0


_COLUMN_ORDER = ['size',
 'texType',
 'width',
 'height',
 'depth',
 'mipLevels',
 'format']

def GetResourceListColumns(resources):
    keys = set()
    for item in resources:
        for key in item:
            keys.add(key)

    if 'type' in keys and len(keys) > 1:
        keys.remove('type')

    def keyCmp(x, y):
        try:
            i0 = _COLUMN_ORDER.index(x)
        except ValueError:
            i0 = None

        try:
            i1 = _COLUMN_ORDER.index(y)
        except ValueError:
            i1 = None

        if i0 is not None and i1 is not None:
            return cmp(i0, i1)
        if i0 is not None and i1 is None:
            return -1
        if i0 is None and i1 is not None:
            return 1
        return cmp(x, y)

    return sorted(keys, cmp=keyCmp)


def FormatCpuUsage(value):
    if value == 0:
        return 'None'
    result = []
    READ = 1
    WRITE = 2
    READ_OFTEN = READ | 4
    WRITE_OFTEN = WRITE | 8
    if value & WRITE_OFTEN == WRITE_OFTEN:
        result.append('WriteOften')
    elif value & WRITE == WRITE:
        result.append('Write')
    if value & READ_OFTEN == READ_OFTEN:
        result.append('ReadOften')
    elif value & READ == READ:
        result.append('Read')
    return ' '.join(result)


_GPU_USAGE = ((1, 'VB'),
 (2, 'IB'),
 (4, 'RT'),
 (8, 'DS'),
 (16, 'SRV'),
 (32, 'UAV'),
 (64, 'CopyDest'),
 (128, 'IndirectArgs'),
 (512, 'Shared'))

def FormatGpuUsage(value):
    if value == 0:
        return 'None'
    return ' '.join((v for k, v in _GPU_USAGE if k & value == k))


def FormatField(key, value):
    if key == 'format':
        value = trinity.PIXEL_FORMAT.GetNameFromValue(int(value))
        return (value, value)
    if key == 'texType':
        return (int(value), {1: '1D',
          2: '2D',
          3: '3D',
          4: 'Cube'}.get(int(value), value))
    if key == 'cpuUsage':
        return (int(value), FormatCpuUsage(int(value)))
    if key == 'gpuUsage':
        return (int(value), FormatGpuUsage(int(value)))
    if key == 'size':
        return (int(value), FormatMemory(int(value)))
    try:
        return (int(value), value)
    except ValueError:
        return (value, value)


def GetResourceRow(resource, columns):
    row = [ '' for _ in range(len(columns)) ]
    for item in resource:
        value = resource[item]
        if item not in columns:
            continue
        col = columns[item]
        row[col] = FormatField(item, value)

    return tuple(row)
