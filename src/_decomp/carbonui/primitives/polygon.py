#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\polygon.py
import math
import carbonui.const as uiconst
from carbonui.primitives.sprite import TexturedBase
from carbonui.util import colorblind
import mathext
import trinity

class Polygon(TexturedBase):
    __renderObject__ = trinity.Tr2Sprite2dPolygon
    default_name = 'polygon'
    default_color = (1, 1, 1, 1)
    default_spriteEffect = trinity.TR2_SFX_FILL
    default_state = uiconst.UI_DISABLED

    def Flush(self):
        ro = self.GetRenderObject()
        del ro.triangles[:]
        del ro.vertices[:]

    def MakeArc(self, radius = 32.0, outerRadius = 66.0, segments = 12, fromDeg = 0.0, toDeg = 90.0, innerColor = default_color, outerColor = default_color, feather = 3.0):
        self.Flush()
        ro = self.GetRenderObject()
        segmentStep = (toDeg - fromDeg) / float(segments)
        TRANSPCOLOR = (0, 0, 0, 0)
        for i in xrange(segments + 1):
            a = math.radians(fromDeg + i * segmentStep)
            x = math.cos(a)
            y = math.sin(a)
            innerVertex = trinity.Tr2Sprite2dVertex()
            innerVertex.position = (x * radius, y * radius)
            innerVertex.color = innerColor
            ro.vertices.append(innerVertex)
            outerVertex = trinity.Tr2Sprite2dVertex()
            outerVertex.position = (x * outerRadius, y * outerRadius)
            outerVertex.color = outerColor
            ro.vertices.append(outerVertex)

        for i in xrange(segments * 2):
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = i
            triangle.index1 = i + 1
            triangle.index2 = i + 2
            ro.triangles.append(triangle)

        if feather:
            shift = len(ro.vertices)
            for i in xrange(segments + 1):
                a = math.radians(fromDeg + i * segmentStep)
                x = math.cos(a)
                y = math.sin(a)
                innerFeatherVertex = trinity.Tr2Sprite2dVertex()
                innerFeatherVertex.position = (x * (radius - feather), y * (radius - feather))
                innerFeatherVertex.color = TRANSPCOLOR
                ro.vertices.append(innerFeatherVertex)
                outerFeatherVertex = trinity.Tr2Sprite2dVertex()
                outerFeatherVertex.position = (x * (outerRadius + feather), y * (outerRadius + feather))
                outerFeatherVertex.color = TRANSPCOLOR
                ro.vertices.append(outerFeatherVertex)

            for i in xrange(segments * 2):
                triangle = trinity.Tr2Sprite2dTriangle()
                triangle.index0 = i
                triangle.index1 = shift + i
                triangle.index2 = shift + i + 2
                ro.triangles.append(triangle)
                triangle = trinity.Tr2Sprite2dTriangle()
                triangle.index0 = shift + i + 2
                triangle.index1 = i + 2
                triangle.index2 = i
                ro.triangles.append(triangle)

    def MakeCircle(self, radius = 64.0, segments = 12, centerColor = default_color, edgeColor = default_color):
        ro = self.GetRenderObject()
        del ro.triangles[:]
        del ro.vertices[:]
        centerVertex = trinity.Tr2Sprite2dVertex()
        centerVertex.position = (radius, radius)
        centerVertex.color = centerColor
        centerVertex.texCoord0 = (0.5, 0.5)
        centerVertex.texCoord1 = (0.5, 0.5)
        ro.vertices.append(centerVertex)
        for i in xrange(segments):
            a = math.pi * 2.0 / float(segments) * float(i)
            x = math.cos(a)
            y = math.sin(a)
            edgeVertex = trinity.Tr2Sprite2dVertex()
            edgeVertex.position = (x * radius + radius, y * radius + radius)
            edgeVertex.color = edgeColor
            edgeVertex.texCoord0 = (x * 0.5 + 0.5, y * 0.5 + 0.5)
            edgeVertex.texCoord1 = edgeVertex.texCoord0
            ro.vertices.append(edgeVertex)

        for i in xrange(segments - 1):
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = 0
            triangle.index1 = i + 1
            triangle.index2 = i + 2
            ro.triangles.append(triangle)

        triangle = trinity.Tr2Sprite2dTriangle()
        triangle.index0 = 0
        triangle.index1 = segments
        triangle.index2 = 1
        ro.triangles.append(triangle)

    def MakeRectangle(self, topLeft = (0, 0), topLeftColor = (1, 1, 1, 1), topRight = (64, 0), topRightColor = (1, 1, 1, 1), bottomRight = (64, 64), bottomRightColor = (1, 1, 1, 1), bottomLeft = (0, 64), bottomLeftColor = (1, 1, 1, 1)):
        ro = self.GetRenderObject()
        del ro.triangles[:]
        del ro.vertices[:]
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = topLeft
        vertex.color = topLeftColor
        vertex.SetTexCoord(0, (0, 0))
        vertex.SetTexCoord(1, (0, 0))
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = topRight
        vertex.color = topRightColor
        vertex.SetTexCoord(0, (1, 0))
        vertex.SetTexCoord(1, (1, 0))
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = bottomRight
        vertex.color = bottomRightColor
        vertex.SetTexCoord(0, (1, 1))
        vertex.SetTexCoord(1, (1, 1))
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = bottomLeft
        vertex.color = bottomLeftColor
        vertex.SetTexCoord(0, (0, 1))
        vertex.SetTexCoord(1, (0, 1))
        ro.vertices.append(vertex)
        triangle = trinity.Tr2Sprite2dTriangle()
        triangle.index0 = 0
        triangle.index1 = 1
        triangle.index2 = 2
        ro.triangles.append(triangle)
        triangle = trinity.Tr2Sprite2dTriangle()
        triangle.index0 = 0
        triangle.index1 = 2
        triangle.index2 = 3
        ro.triangles.append(triangle)

    def MakeTriangle(self, pos1, pos2, pos3, color):
        ro = self.GetRenderObject()
        del ro.triangles[:]
        del ro.vertices[:]
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = pos1
        vertex.color = color
        vertex.SetTexCoord(0, (0, 0))
        vertex.SetTexCoord(1, (0, 0))
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = pos2
        vertex.color = color
        vertex.SetTexCoord(0, (1, 0))
        vertex.SetTexCoord(1, (1, 0))
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = pos3
        vertex.color = color
        vertex.SetTexCoord(0, (1, 1))
        vertex.SetTexCoord(1, (1, 1))
        ro.vertices.append(vertex)
        triangle = trinity.Tr2Sprite2dTriangle()
        triangle.index0 = 0
        triangle.index1 = 1
        triangle.index2 = 2
        ro.triangles.append(triangle)

    def MakeGradient(self, width = 256, height = 256, colorPoints = [(0, (0, 0, 0, 1)), (1, (1, 1, 1, 1))], rotation = 0):
        ro = self.GetRenderObject()
        del ro.triangles[:]
        del ro.vertices[:]
        startPoint = colorPoints[0]
        startValue = startPoint[0]
        startColor = startPoint[1]
        topLeft = (startValue, 0)
        bottomLeft = (startValue, height)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = topLeft
        vertex.color = startColor
        vertex.texCoord0 = (0, 0)
        vertex.texCoord1 = (0, 0)
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = bottomLeft
        vertex.color = startColor
        vertex.texCoord0 = (0, 1)
        vertex.texCoord1 = (0, 1)
        ro.vertices.append(vertex)
        baseIx = 0
        for i in xrange(len(colorPoints) - 1):
            endPoint = colorPoints[i + 1]
            endValue = endPoint[0]
            endColor = endPoint[1]
            topLeft = (endValue * width, 0)
            bottomLeft = (endValue * width, height)
            vertex = trinity.Tr2Sprite2dVertex()
            vertex.position = topLeft
            vertex.color = endColor
            vertex.texCoord0 = (endValue, 0)
            vertex.texCoord1 = (endValue, 0)
            ro.vertices.append(vertex)
            vertex = trinity.Tr2Sprite2dVertex()
            vertex.position = bottomLeft
            vertex.color = endColor
            vertex.texCoord0 = (endValue, 1)
            vertex.texCoord1 = (endValue, 1)
            ro.vertices.append(vertex)
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = baseIx + 0
            triangle.index1 = baseIx + 1
            triangle.index2 = baseIx + 2
            ro.triangles.append(triangle)
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = baseIx + 1
            triangle.index1 = baseIx + 2
            triangle.index2 = baseIx + 3
            ro.triangles.append(triangle)
            baseIx += 2
            startValue = endValue
            startColor = endColor

    def MakeSegmentedRectangle(self, segments, tex):
        ro = self.GetRenderObject()
        del ro.triangles[:]
        del ro.vertices[:]
        self.texture = tex
        width = tex.atlasTexture.width
        height = tex.atlasTexture.height
        step = float(width) / float(segments)
        ustep = 1.0 / float(segments)
        x = 0.0
        u = 0.0
        yTop = 0.0
        yBottom = float(height)
        vTop = 0.0
        vBottom = 1.0
        color = (1, 1, 1, 1)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = (x, yTop)
        vertex.color = color
        vertex.texCoord0 = (u, vTop)
        vertex.texCoord1 = (u, vTop)
        ro.vertices.append(vertex)
        vertex = trinity.Tr2Sprite2dVertex()
        vertex.position = (x, yBottom)
        vertex.color = color
        vertex.texCoord0 = (u, vBottom)
        vertex.texCoord1 = (u, vBottom)
        ro.vertices.append(vertex)
        baseIx = 0
        for i in xrange(segments):
            x += step
            u += ustep
            vertex = trinity.Tr2Sprite2dVertex()
            vertex.position = (x, yTop)
            vertex.color = color
            vertex.texCoord0 = (u, vTop)
            vertex.texCoord1 = (u, vTop)
            ro.vertices.append(vertex)
            vertex = trinity.Tr2Sprite2dVertex()
            vertex.position = (x, yBottom)
            vertex.color = color
            vertex.texCoord0 = (u, vBottom)
            vertex.texCoord1 = (u, vBottom)
            ro.vertices.append(vertex)
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = baseIx + 0
            triangle.index1 = baseIx + 1
            triangle.index2 = baseIx + 2
            ro.triangles.append(triangle)
            triangle = trinity.Tr2Sprite2dTriangle()
            triangle.index0 = baseIx + 1
            triangle.index1 = baseIx + 2
            triangle.index2 = baseIx + 3
            ro.triangles.append(triangle)
            baseIx += 2

    def _ApplyColorblindCorrection(self, colors):
        if colors:
            if isinstance(colors[0], (float, int)):
                colors = colorblind.CheckReplaceColor(colors)
            else:
                colors = [ colorblind.CheckReplaceColor(color) for color in colors ]
        return colors

    def AppendVertices(self, positions, transform, colors, texcoords = None):
        colors = self._ApplyColorblindCorrection(colors)
        if texcoords:
            self.renderObject.AppendVertices(positions, transform, colors, texcoords)
        else:
            self.renderObject.AppendVertices(positions, transform, colors)

    def AddPoint(self, x, y, color):
        positions = [(x, y)]
        transform = None
        colors = self._ApplyColorblindCorrection([color])
        self.renderObject.AppendVertices(positions, transform, colors)

    def UpdatePoint(self, index, x, y):
        positions = []
        transform = None
        colors = []
        for order, vertex in enumerate(self.renderObject.vertices):
            if index == order:
                positions.append((x, y))
            else:
                positions.append((vertex.position[0], vertex.position[1]))
            colors.append(vertex.color)

        self.Flush()
        self.renderObject.AppendVertices(positions, transform, colors)

    def RemovePoint(self, index):
        positions = []
        transform = None
        colors = []
        for order, vertex in enumerate(self.renderObject.vertices):
            if index != order:
                positions.append((vertex.position[0], vertex.position[1]))
                colors.append(vertex.color)

        self.Flush()
        self.renderObject.AppendVertices(positions, transform, colors)

    def _GetIndexedVertices(self):
        return {(int(vertex.position[0]), int(vertex.position[1])):index for index, vertex in enumerate(self.renderObject.vertices)}

    def _GetVertexIndex(self, x, y):
        indexedPoints = self._GetIndexedVertices()
        return indexedPoints[int(x), int(y)]

    def Triangulate(self):
        indexedPoints = self._GetIndexedVertices()
        points = sorted(indexedPoints.keys(), key=lambda point: indexedPoints[point])
        trianglesAsPoints = mathext.triangulate(points)
        trianglesAsIndices = []
        for triangle in trianglesAsPoints:
            p1, p2, p3 = triangle
            i1, i2, i3 = self._GetVertexIndex(*p1), self._GetVertexIndex(*p2), self._GetVertexIndex(*p3)
            trianglesAsIndices.append((i1, i2, i3))

        self.SetTriangles(trianglesAsIndices)

    def SetTriangles(self, triangles):
        del self.renderObject.triangles[:]
        self.renderObject.AppendTriangles(triangles)
