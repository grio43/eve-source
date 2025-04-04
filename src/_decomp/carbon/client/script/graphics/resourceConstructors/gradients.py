#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\client\script\graphics\resourceConstructors\gradients.py
import blue
import trinity
import struct
import math

def isVector(a):
    return hasattr(a, '__iter__')


def Lerp(a, b, u):

    def LerpValue(x, y):
        return x * (1.0 - u) + y * u

    if not isVector(a):
        return LerpValue(a, b)
    else:
        return map(LerpValue, a, b)


def Cosine(a, b, u):

    def CosValue(x, y):
        cosU = math.cos(u * math.pi * 0.5)
        return x * cosU * cosU + y * (1.0 - cosU * cosU)

    if not isVector(a):
        return CosValue(a, b)
    else:
        return map(CosValue, a, b)


def v_op(a, b, op):
    if isVector(a):
        if isVector(b):
            return map(op, a, b)
        return map(lambda x: op(x, b), a)
    elif isVector(b):
        return map(lambda x: op(a, x), b)
    else:
        return op(a, b)


def v_add(a, b):
    return v_op(a, b, lambda x, y: x + y)


def v_sub(a, b):
    return v_op(a, b, lambda x, y: x - y)


def v_mul(a, b):
    return v_op(a, b, lambda x, y: x * y)


def v_div(a, b):
    return v_op(a, b, lambda x, y: x / y)


def v_dot(a, b):
    return reduce(lambda x, y: x + y, v_mul(a, b))


def v_len(a):
    if isVector(a):
        return math.sqrt(v_dot(a, a))
    return a


def v_unit(a):
    l = v_len(a)
    if -1e-05 < abs(l) < 1e-05:
        l = 1.0
    return v_div(a, l)


def Bezier(a, b, c, d, u):
    inVal = v_sub(b, a)
    tweenVal = v_sub(c, b)
    outVal = v_sub(d, c)
    tanIn = v_mul(v_add(inVal, tweenVal), 0.5)
    tanOut = v_mul(v_add(tweenVal, outVal), 0.5)
    b1 = v_add(b, v_mul(tanIn, 0.33))
    c1 = v_sub(c, v_mul(tanOut, 0.33))
    v = 1.0 - u
    return v_add(v_add(v_mul(b, math.pow(v, 3)), v_mul(b1, u * 3.0 * math.pow(v, 2))), v_add(v_mul(c1, v * 3.0 * math.pow(u, 2)), v_mul(c, math.pow(u, 3))))


def SampleGradient(divs, points, x, interpMode = 'linear'):
    if x < divs[0]:
        return points[0]
    elif x >= divs[-1]:
        return points[-1]
    n = len(points)
    minX, maxX = (0, 1)
    index = 0
    for i, xPrev, xNext in zip(range(n), divs, divs[1:]):
        if xPrev <= x < xNext:
            minX = xPrev
            maxX = xNext
            index = i
            break
        minX = xPrev
        index = 1

    u = (x - minX) / (maxX - minX) if maxX != minX else 0.0

    def fetch(i):
        return points[min(n - 1, max(0, i))]

    if interpMode == 'bezier':
        return Bezier(fetch(index - 1), fetch(index), fetch(index + 1), fetch(index + 2), u)
    elif interpMode == 'cosine':
        return Cosine(fetch(index), fetch(index + 1), u)
    else:
        return Lerp(fetch(index), fetch(index + 1), u)


def ColourByteClamp(r, g, b, a):
    r = int(min(255, max(0, r * 255)))
    g = int(min(255, max(0, g * 255)))
    b = int(min(255, max(0, b * 255)))
    a = int(min(255, max(0, a * 255)))
    return (r,
     g,
     b,
     a)


def Gradient(paramString):
    params = {'rgbInterp': 'linear',
     'rgbDivs': [0.0,
                 0.33,
                 0.66,
                 1.0],
     'rgbPoints': [(0, 0, 1),
                   (0, 1, 0),
                   (1, 0, 0),
                   (0, 0.5, 0.5)],
     'alphaInterp': 'linear',
     'alphaDivs': [0, 1],
     'alphaPoints': [1.0, 1.0],
     'textureSize': 256}
    if paramString.endswith('}atlas'):
        paramString = paramString[:-5]
    try:
        if paramString:
            params.update(eval(paramString))
    except:
        pass

    textureSize = params['textureSize']
    texture = trinity.textureAtlasMan.atlases[0].CreateTexture(textureSize, 1)
    locked = texture.LockBufferAndMargin(None, False)
    if locked:
        buf = locked[0]
        width = locked[1]
        height = locked[2]
        pitch = locked[3]
        margin = locked[4]
        try:
            for y in range(height):
                for xi in range(width):
                    x = (xi - margin) / float(textureSize - 1)
                    x = max(0.0, min(1.0, x))
                    r, g, b = SampleGradient(params['rgbDivs'], params['rgbPoints'], x, params['rgbInterp'])
                    a = SampleGradient(params['alphaDivs'], params['alphaPoints'], x, params['alphaInterp'])
                    r, g, b, a = ColourByteClamp(r, g, b, a)
                    buf[y * pitch + xi * 4 + 0] = struct.pack('B', b)
                    buf[y * pitch + xi * 4 + 1] = struct.pack('B', g)
                    buf[y * pitch + xi * 4 + 2] = struct.pack('B', r)
                    buf[y * pitch + xi * 4 + 3] = struct.pack('B', a)

        finally:
            texture.UnlockBuffer()

    return texture


def GradientRadial(paramString):
    params = {'toCorners': True,
     'rgbInterp': 'linear',
     'rgbDivs': [0.0,
                 0.33,
                 0.66,
                 1.0],
     'rgbPoints': [(0, 0, 1),
                   (0, 1, 0),
                   (1, 0, 0),
                   (0, 0.5, 0.5)],
     'alphaInterp': 'linear',
     'alphaDivs': [0, 1],
     'alphaPoints': [1.0, 1.0],
     'textureSize': (256, 256)}
    if paramString.endswith('}atlas'):
        paramString = paramString[:-5]
    try:
        if paramString:
            params.update(eval(paramString))
    except:
        pass

    textureSize = params['textureSize']
    if not hasattr(textureSize, '__iter__'):
        textureSize = (textureSize, textureSize)
    texture = trinity.textureAtlasMan.atlases[0].CreateTexture(textureSize[0], textureSize[1])
    locked = texture.LockBufferAndMargin(None, False)
    if locked:
        buf = locked[0]
        width = locked[1]
        height = locked[2]
        pitch = locked[3]
        margin = locked[4]
        try:
            for yi in range(height):
                y = 2.0 * ((yi - margin) / float(height - 1) - 0.5)
                y = max(-1.0, min(y, 1.0))
                for xi in range(width):
                    x = 2.0 * ((xi - margin) / float(width - 1) - 0.5)
                    x = max(-1.0, min(x, 1.0))
                    rad = math.sqrt(x * x + y * y)
                    if params['toCorners']:
                        rad /= 1.41421
                    r, g, b = SampleGradient(params['rgbDivs'], params['rgbPoints'], rad, params['rgbInterp'])
                    a = SampleGradient(params['alphaDivs'], params['alphaPoints'], rad, params['alphaInterp'])
                    r, g, b, a = ColourByteClamp(r, g, b, a)
                    buf[yi * pitch + xi * 4 + 0] = struct.pack('B', b)
                    buf[yi * pitch + xi * 4 + 1] = struct.pack('B', g)
                    buf[yi * pitch + xi * 4 + 2] = struct.pack('B', r)
                    buf[yi * pitch + xi * 4 + 3] = struct.pack('B', a)

        finally:
            texture.UnlockBuffer()

    return texture


def SampleGradient2D(subdivsX, subdivsY, pointsX, pointsY, x, y, interpMode = 'linear'):
    indexX, indexY = (0, 0)
    minX, minY, maxX, maxY = (0, 0, 1, 1)
    found = False
    for idx, xCurr, xNext in zip(range(len(subdivsX)), subdivsX, subdivsX[1:]):
        if xCurr <= x < xNext:
            indexX = idx
            minX = xCurr
            maxX = xNext
            found = True
            break

    if found:
        u = (x - minX) / (maxX - minX)
    else:
        indexX = len(pointsX) - 1
        u = 1
    found = False
    for idx, yCurr, yNext in zip(range(len(subdivsY)), subdivsY, subdivsY[1:]):
        if yCurr <= y < yNext:
            indexY = idx
            minY = yCurr
            maxY = yNext
            found = True
            break

    if found:
        v = (y - minY) / (maxY - minY)
    else:
        indexY = len(pointsY) - 1
        v = 1

    def fetch(i, points):
        i = min(len(points) - 1, max(0, i))
        return points[i]

    if interpMode == 'bezier':
        colorX = Bezier(fetch(indexX - 1, pointsX), fetch(indexX, pointsX), fetch(indexX + 1, pointsX), fetch(indexX + 2, pointsX), u)
        colorY = Bezier(fetch(indexY - 1, pointsY), fetch(indexY, pointsY), fetch(indexY + 1, pointsY), fetch(indexY + 2, pointsY), v)
    elif interpMode == 'cosine':
        colorX = Cosine(fetch(indexX, pointsX), fetch(indexX + 1, pointsX), u)
        colorY = Cosine(fetch(indexY, pointsY), fetch(indexY + 1, pointsY), v)
    else:
        colorX = Lerp(fetch(indexX, pointsX), fetch(indexX + 1, pointsX), u)
        colorY = Lerp(fetch(indexY, pointsY), fetch(indexY + 1, pointsY), v)
    if isVector(colorX):
        color = (colorX[0] * colorY[0], colorX[1] * colorY[1], colorX[2] * colorY[2])
    else:
        color = colorX * colorY
    return color


def Gradient2D(paramString):
    params = {'rgbHorizontal': [0, 1],
     'rgbVertical': [0, 1],
     'rgbDataHorizontal': [(1, 1, 1), (0, 0, 0)],
     'rgbDataVertical': [(1, 1, 1), (0, 0, 0)],
     'alphaHorizontal': [0, 1],
     'alphaVertical': [0, 1],
     'alphaDataHorizontal': [1, 0],
     'alphaDataVertical': [1, 0],
     'textureSize': (256, 256),
     'rgbInterp': 'linear',
     'alphaInterp': 'linear'}
    if paramString.endswith('}atlas'):
        paramString = paramString[:-5]
    try:
        if paramString:
            params.update(eval(paramString))
    except:
        pass

    textureSize = params['textureSize']
    if not hasattr(textureSize, '__iter__'):
        textureSize = (textureSize, textureSize)
    texture = trinity.textureAtlasMan.atlases[0].CreateTexture(textureSize[0], textureSize[1])
    locked = texture.LockBufferAndMargin(None, False)
    if locked:
        buf = locked[0]
        width = locked[1]
        height = locked[2]
        pitch = locked[3]
        margin = locked[4]
        try:
            rgbHorizontal = params['rgbHorizontal']
            rgbVertical = params['rgbVertical']
            rgbDataHorizontal = params['rgbDataHorizontal']
            rgbDataVertical = params['rgbDataVertical']
            rgbInterp = params['rgbInterp']
            alphaHorizontal = params['alphaHorizontal']
            alphaVertical = params['alphaVertical']
            alphaDataHorizontal = params['alphaDataHorizontal']
            alphaDataVertical = params['alphaDataVertical']
            alphaInterp = params['alphaInterp']
            for yi in xrange(height):
                y = (yi - margin) / float(textureSize[1] - 1)
                y = max(0.0, min(y, 1.0))
                for xi in xrange(width):
                    x = (xi - margin) / float(textureSize[0] - 1)
                    x = max(0.0, min(x, 1.0))
                    r, g, b = SampleGradient2D(rgbHorizontal, rgbVertical, rgbDataHorizontal, rgbDataVertical, x, y, rgbInterp)
                    a = SampleGradient2D(alphaHorizontal, alphaVertical, alphaDataHorizontal, alphaDataVertical, x, y, alphaInterp)
                    r, g, b, a = ColourByteClamp(r, g, b, a)
                    buf[yi * pitch + xi * 4 + 0] = struct.pack('B', b)
                    buf[yi * pitch + xi * 4 + 1] = struct.pack('B', g)
                    buf[yi * pitch + xi * 4 + 2] = struct.pack('B', r)
                    buf[yi * pitch + xi * 4 + 3] = struct.pack('B', a)

        finally:
            texture.UnlockBuffer()

    return texture
