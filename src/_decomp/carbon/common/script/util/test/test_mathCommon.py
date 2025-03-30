#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\test\test_mathCommon.py
from math import pi, pow, sqrt
from mock import patch
from testsuites.testcases import ServerClientTestCase
from unittest import main

class Geo2Mock(object):

    def Vec3Length(self, v):
        return sqrt(sum([ pow(v[i], 2) for i in xrange(3) ]))

    def Vec3Subtract(self, v1, v2):
        return [ v1[i] - v2[i] for i in xrange(3) ]

    def MatrixMultiply(self, m1, m2):
        return [ [ sum((a * b for a, b in zip(m1_row, m2_col))) for m2_col in zip(*m2) ] for m1_row in m1 ]


class GetAngleBetweenTwoVectorsTestCase(ServerClientTestCase):

    def setUp(self):
        super(GetAngleBetweenTwoVectorsTestCase, self).setUp()
        with patch.dict('sys.modules', self._mock_imported_modules()):
            from carbon.common.script.util.mathCommon import FloatCloseEnough, GetAngleBetweenTwoVectors
            from carbon.common.script.util.mathErrors import InvalidInput
            self.get_angle_between_two_vectors = GetAngleBetweenTwoVectors
            self.is_float_close_enough = FloatCloseEnough
            self.invalid_input = InvalidInput

    def _mock_imported_modules(self):
        imported_modules = {'geo2': Geo2Mock()}
        return imported_modules

    def _test_angle_is_as_expected(self, v1, v2, expected_angle):
        test_angle = self.get_angle_between_two_vectors(v1, v2)
        self.assertTrue(expr=self.is_float_close_enough(test_angle, expected_angle), msg='Result: {test} vs Expected: {expected}'.format(test=test_angle, expected=expected_angle))

    def _test_exception_raised_when_calculating_angle(self, v1, v2):
        self.assertRaises(self.invalid_input, self.get_angle_between_two_vectors, v1, v2)

    def test_angle_between_two_vectors_1(self):
        v1 = (4.0, 0.0, 7.0)
        v2 = (-2.0, 1.0, 3.0)
        self._test_angle_is_as_expected(v1, v2, expected_angle=1.12525242)

    def test_angle_between_two_vectors_2(self):
        v1 = (3.0, 4.0, -7.0)
        v2 = (-2.0, 1.0, 3.0)
        self._test_angle_is_as_expected(v1, v2, expected_angle=2.36681159)

    def test_angle_between_two_vectors_parallel(self):
        v1 = (1.0, 0.0, 0.0)
        v2 = (2.0, 0.0, 0.0)
        self._test_angle_is_as_expected(v1, v2, expected_angle=0.0)

    def test_angle_between_two_vectors_opposite(self):
        v1 = (1.0, 0.0, 0.0)
        v2 = (-2.0, 0.0, 0.0)
        self._test_angle_is_as_expected(v1, v2, expected_angle=pi)

    def test_angle_between_two_vectors_perpendicular(self):
        v1 = (1.0, 0.0, 0.0)
        v2 = (0.0, -1.0, 0.0)
        self._test_angle_is_as_expected(v1, v2, expected_angle=pi / 2.0)

    def test_angle_between_vector_and_zero_vector(self):
        v1 = (1.0, 0.0, 0.0)
        v2 = (0.0, 0.0, 0.0)
        self._test_exception_raised_when_calculating_angle(v1, v2)

    def test_angle_between_two_zero_vectors(self):
        v1 = (0.0, 0.0, 0.0)
        v2 = (0.0, 0.0, 0.0)
        self._test_exception_raised_when_calculating_angle(v1, v2)

    def test_angle_between_two_same_vectors(self):
        v1 = (1.0, 0.0, 0.0)
        v2 = (1.0, 0.0, 0.0)
        self._test_angle_is_as_expected(v1, v2, expected_angle=0.0)


class GetSignedDistanceFromPointToPlaneTestCase(ServerClientTestCase):

    def setUp(self):
        super(GetSignedDistanceFromPointToPlaneTestCase, self).setUp()
        with patch.dict('sys.modules', self._mock_imported_modules()):
            from carbon.common.script.util.mathCommon import FloatCloseEnough, GetSignedDistanceFromPointToPlane
            from carbon.common.script.util.mathErrors import InvalidInput
            self.get_signed_distance_from_point_to_plane = GetSignedDistanceFromPointToPlane
            self.is_float_close_enough = FloatCloseEnough
            self.invalid_input = InvalidInput

    def _mock_imported_modules(self):
        imported_modules = {'geo2': Geo2Mock()}
        return imported_modules

    def _test_distance_is_as_expected(self, point, plane, expected_distance):
        test_distance = self.get_signed_distance_from_point_to_plane(point, plane)
        self.assertTrue(expr=self.is_float_close_enough(test_distance, expected_distance), msg='Result: {test} vs Expected: {expected}'.format(test=test_distance, expected=expected_distance))

    def _test_exception_raised_when_calculating_distance(self, point, plane):
        self.assertRaises(self.invalid_input, self.get_signed_distance_from_point_to_plane, point, plane)

    def test_distance_0_between_point_0_and_plane_z0(self):
        point = (0.0, 0.0, 0.0)
        plane = (0.0, 0.0, 1.0, 0.0)
        self._test_distance_is_as_expected(point, plane, expected_distance=0.0)

    def test_distance_0_between_point_z0_and_plane_z0(self):
        point = (22.0, -30.0, 0.0)
        plane = (0.0, 0.0, 1.0, 0.0)
        self._test_distance_is_as_expected(point, plane, expected_distance=0.0)

    def test_distance_1_between_point_z1_and_plane_z0(self):
        point = (0.0, 0.0, 1.0)
        plane = (0.0, 0.0, 1.0, 0.0)
        self._test_distance_is_as_expected(point, plane, expected_distance=1.0)

    def test_distance_10_between_point_z10_and_plane_z0(self):
        point = (0.0, 0.0, 10.0)
        plane = (0.0, 0.0, 1.0, 0.0)
        self._test_distance_is_as_expected(point, plane, expected_distance=10.0)

    def test_distance_between_point_and_not_a_plane(self):
        point = (0.0, 0.0, 10.0)
        plane = (0.0, 0.0, 0.0, 0.0)
        self._test_exception_raised_when_calculating_distance(point, plane)


class IsWithinFrustumTestCase(ServerClientTestCase):

    def setUp(self):
        super(IsWithinFrustumTestCase, self).setUp()
        with patch.dict('sys.modules', self._mock_imported_modules()):
            from carbon.common.script.util.mathCommon import IsWithinFrustum
            self.is_within_frustum = IsWithinFrustum

    def _mock_imported_modules(self):
        imported_modules = {'geo2': Geo2Mock()}
        return imported_modules

    def _test_is_in_view_as_expected(self, point, view_matrix, projection_matrix, expected_is_in_view):
        test_is_in_view = self.is_within_frustum(point, view_matrix, projection_matrix)
        self.assertTrue(expr=test_is_in_view == expected_is_in_view, msg='Result: {test} vs Expected: {expected}'.format(test=test_is_in_view, expected=expected_is_in_view))

    def test_point_is_in_view(self):
        point = (-46147.09375, 1563.0390625, -4425.38671875)
        view_matrix = ((0.025582458823919296, -0.10342695564031601, 0.9943079352378845, 0.0),
         (0.0, 0.9946334362030029, 0.10346081852912903, 0.0),
         (-0.9996727108955383, -0.0026467822026461363, 0.02544517070055008, 0.0),
         (-0.3162713050842285, 0.028678221628069878, -17.96691131591797, 1.0))
        projection_matrix = ((1.8118325471878052, 0.0, 0.0, 0.0),
         (0.0, 3.0685949325561523, 0.0, 0.0),
         (0.0, 0.0, -1.0000005960464478, -1.0),
         (0.0, 0.0, -6.000003337860107, 0.0))
        self._test_is_in_view_as_expected(point, view_matrix, projection_matrix, expected_is_in_view=True)

    def test_point_is_not_in_view(self):
        point = (-46147.09375, 1563.0390625, -4425.38671875)
        view_matrix = ((-0.639927864074707, -0.07032500207424164, 0.7652102112770081, 0.0),
         (0.0, 0.9958034753799438, 0.09151717275381088, 0.0),
         (-0.768435001373291, 0.05856438726186752, -0.6372423768043518, 0.0),
         (-0.23369121551513672, 0.014873266220092773, -18.198253631591797, 1.0))
        projection_matrix = ((1.8118325471878052, 0.0, 0.0, 0.0),
         (0.0, 3.0685951709747314, 0.0, 0.0),
         (0.0, 0.0, -1.0000005960464478, -1.0),
         (0.0, 0.0, -6.000003337860107, 0.0))
        self._test_is_in_view_as_expected(point, view_matrix, projection_matrix, expected_is_in_view=False)


if __name__ == '__main__':
    main()
