#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\planet\surfacePoint.py
import math
MATH_2PI = math.pi * 2

class SurfacePoint:

    def __init__(self, x = 0.0, y = 0.0, z = 0.0, radius = 1.0, theta = None, phi = None):
        if theta is not None and phi is not None:
            self.SetRadThPhi(radius, theta, phi)
        else:
            self.SetXYZ(x, y, z)

    def SetXYZ(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self._CalcRadThPhi()

    def Copy(self, surfacePoint):
        self.x = surfacePoint.x
        self.y = surfacePoint.y
        self.z = surfacePoint.z
        self.radius = surfacePoint.radius
        self.theta = surfacePoint.theta
        self.phi = surfacePoint.phi

    def SetRadThPhi(self, radius, theta, phi):
        self.radius = radius
        self.theta = theta
        self.phi = phi
        self._CalcXYZ()

    def _CalcRadThPhi(self):
        self.radius = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        if self.radius == 0.0:
            self.theta = self.phi = 0.0
            return
        self.phi = math.acos(self.y / self.radius)
        self.theta = math.atan2(self.z, self.x)
        self._CheckTheta()

    def _CheckTheta(self):
        while self.theta >= MATH_2PI:
            self.theta -= MATH_2PI

        while self.theta < 0.0:
            self.theta += MATH_2PI

    def _CalcXYZ(self):
        radSinPhi = self.radius * math.sin(self.phi)
        self.x = radSinPhi * math.cos(self.theta)
        self.z = radSinPhi * math.sin(self.theta)
        self.y = self.radius * math.cos(self.phi)

    def SetX(self, x):
        self.x = x
        self._CalcRadThPhi()

    def SetY(self, y):
        self.y = y
        self._CalcRadThPhi()

    def SetZ(self, z):
        self.z = z
        self._CalcRadThPhi()

    def SetRadius(self, radius):
        self.radius = radius
        self._CalcXYZ()

    def SetTheta(self, theta):
        self.theta = theta
        self._CheckTheta()
        self._CalcXYZ()

    def SetPhi(self, phi):
        self.phi = phi
        self._CalcXYZ()

    def GetAsXYZTuple(self):
        return (self.x, self.y, self.z)

    def GetAsRadThPhiTuple(self):
        return (self.radius, self.theta, self.phi)

    def GetAsXYZString(self):
        return '(%6.2f, %6.2f, %6.2f) = (x,y,z)' % self.GetAsXYZTuple()

    def GetAsRadThPhiString(self):
        return '(%6.2f, %6.2f, %6.2f) = (rad,theta,phi)' % self.GetAsRadThPhiTuple()

    def GetAngleBetween(self, other):
        dotProduct = (self.x * other.x + self.y * other.y + self.z * other.z) / self.radius / other.radius
        if dotProduct > 1.0:
            dotProduct = 1.0
        return math.acos(dotProduct)

    def GetDistanceToOther(self, other):
        return self.radius * self.GetAngleBetween(other)

    def GetRotatedSurfacePoint(self, alpha, beta, gamma):
        alpha = math.radians(alpha)
        beta = math.radians(beta)
        gamma = math.radians(gamma)
        point = [[self.x], [self.y], [self.z]]
        R_x = [[1, 0, 0], [0, math.cos(alpha), -math.sin(alpha)], [0, math.sin(alpha), math.cos(alpha)]]
        R_y = [[math.cos(beta), 0, math.sin(beta)], [0, 1, 0], [-math.sin(beta), 0, math.cos(beta)]]
        R_z = [[math.cos(gamma), -math.sin(gamma), 0], [math.sin(gamma), math.cos(gamma), 0], [0, 0, 1]]
        result = self._matrix_multiply(R_z, point)
        result = [[result[0]], [result[1]], [result[2]]]
        result = self._matrix_multiply(R_x, result)
        result = [[result[0]], [result[1]], [result[2]]]
        result = self._matrix_multiply(R_y, result)
        return SurfacePoint(x=result[0], y=result[1], z=result[2])

    def _matrix_multiply(self, A, B):
        result = [ [ sum((A[i][k] * B[k][j] for k in range(len(B)))) for j in range(len(B[0])) ] for i in range(len(A)) ]
        if len(B[0]) == 1:
            return [ row[0] for row in result ]
        return result
