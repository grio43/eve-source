#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\drawingpolygon\operations.py


def do_any_segments_intersect(vertices):
    if len(vertices) <= 3:
        return False
    segments = _get_segments(vertices)
    for index_1, segment_1 in enumerate(segments):
        for index_2, segment_2 in enumerate(segments):
            should_check_this_segment_pair = index_1 + 1 < index_2 and (index_1 != 0 or index_2 != len(segments) - 1)
            if should_check_this_segment_pair and do_segments_intersect(segment_1, segment_2):
                return True

    return False


def do_polygons_intersect(vertices_1, vertices_2):
    if len(vertices_1) <= 2 or len(vertices_2) <= 2:
        return False
    segments_1 = _get_segments(vertices_1)
    segments_2 = _get_segments(vertices_2)
    for segment_1 in segments_1:
        for segment_2 in segments_2:
            if do_segments_intersect(segment_1, segment_2):
                return True

    return False


def is_point_inside_polygon(x, y, vertices):
    number_of_intersections = 0
    polygon_segments = _get_segments(vertices)
    for polygon_segment in polygon_segments:
        test_segment = [[0, 0], [x, y]]
        if do_segments_intersect(test_segment, polygon_segment):
            number_of_intersections += 1

    return bool(number_of_intersections % 2)


def _get_segments(vertices):
    all_segments = []
    first_point = vertices[0]
    for second_point in vertices[1:] + [vertices[0]]:
        all_segments.append([first_point, second_point])
        first_point = second_point

    return all_segments


def do_segments_intersect(segment_1, segment_2):
    a, b = segment_1
    c, d = segment_2
    return _is_clockwise_oriented(a, c, d) != _is_clockwise_oriented(b, c, d) and _is_clockwise_oriented(a, b, c) != _is_clockwise_oriented(a, b, d)


def _is_clockwise_oriented(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) < (b[1] - a[1]) * (c[0] - a[0])


def are_points_within_distance(point_1, point_2, max_distance):
    a = abs(point_1[0] - point_2[0])
    b = abs(point_1[1] - point_2[1])
    square_distance = a * a + b * b
    return square_distance <= max_distance * max_distance
