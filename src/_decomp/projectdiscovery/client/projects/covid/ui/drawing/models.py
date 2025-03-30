#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\models.py
import enum
import uuid
import decimal
import math
import logging
log = logging.getLogger('projectdiscovery.covid.models')

class Coord(object):
    __slots__ = ('right', 'up')

    def __init__(self, right = 0, up = 0):
        self.right = right
        self.up = up

    @property
    def as_tuple(self):
        return (self.right, self.up)

    @classmethod
    def from_args(cls, param1, param2 = None):
        if isinstance(param1, cls):
            return param1
        if isinstance(param1, (list, tuple)):
            if len(param1) != 2:
                raise ValueError('expected two values for x and y, got %s' % len(param1))
            return cls(*param1)
        if isinstance(param1, dict):
            x = None
            if 'x' in param1:
                x = param1.get('x')
            elif 'right' in param1:
                x = param1.get('right')
            y = None
            if 'y' in param1:
                y = param1.get('y')
            elif 'up' in param1:
                y = param1.get('up')
            if x is not None and y is not None:
                return cls(x, y)
            raise ValueError('expected x and y keys')
        elif isinstance(param1, (int, long, float)):
            if isinstance(param2, (int, long, float)):
                return cls(param1, param2)
            raise ValueError('expected two scalar arguments for x and y')
        else:
            raise ValueError('unknown argument type')

    @property
    def x(self):
        return self.right

    @x.setter
    def x(self, value):
        self.right = value

    @property
    def y(self):
        return self.up

    @y.setter
    def y(self, value):
        self.up = value

    def __str__(self):
        return '(%s, %s)' % self.as_tuple

    def __repr__(self):
        return '<Coord right=%s, up=%s>' % self.as_tuple

    def __eq__(self, other):
        if isinstance(other, Coord):
            return other.right == self.right and other.up == self.up
        if isinstance(other, (tuple, list)) and len(other) == 2:
            return other[0] == self.right and other[1] == self.up
        return False

    def __add__(self, other):
        if isinstance(other, Coord):
            return Coord(other.right + self.right, other.up + self.up)
        if isinstance(other, (list, tuple)) and len(other) == 2:
            return Coord(other[0] + self.right, other[1] + self.up)
        raise TypeError('dont know how to add Coord and %s' % type(other))

    def __iadd__(self, other):
        if isinstance(other, Coord):
            self.right += other.right
            self.up += other.up
        elif isinstance(other, (list, tuple)) and len(other) == 2:
            self.right += other[0]
            self.up += other[1]
        else:
            raise TypeError('dont know how to add Coord and %s' % type(other))

    def scale(self, ratio):
        self.right = int(self.right * ratio + 0.5)
        self.up = int(self.up * ratio + 0.5)

    def delta(self, to_other):
        return Coord(to_other.right - self.right, to_other.up - self.up)

    def dist_squared(self, other):
        if not isinstance(other, Coord):
            other = Coord.from_args(other)
        a = abs(other.right - self.right)
        b = abs(other.up - self.up)
        return a * a + b * b

    def is_within_dist(self, other, dist):
        sq = self.dist_squared(other)
        return sq <= dist * dist

    @property
    def as_copy(self):
        return Coord(self.right, self.up)

    @property
    def as_sign_tuple(self):
        return (1 if self.right > 0 else (-1 if self.right < 0 else 0), 1 if self.up > 0 else (-1 if self.up < 0 else 0))


class Rect(object):
    __slots__ = ('bottom_left', 'size')

    def __init__(self, bottom_left, size):
        self.bottom_left = bottom_left
        self.size = size

    @property
    def upper_right(self):
        return self.bottom_left + self.size

    @property
    def as_tuple(self):
        return (self.bottom_left.right,
         self.bottom_left.up,
         self.size.right,
         self.size.up)

    def __contains__(self, item):
        if isinstance(item, Coord):
            ur = self.upper_right
            if not self.bottom_left.right <= item.right <= ur.right:
                return False
            if not self.bottom_left.up <= item.up <= ur.up:
                return False
            return True
        if isinstance(item, Rect):
            return item.bottom_left in self and item.upper_right in self

    @staticmethod
    def bounding_rect(list_of_coords):
        if list_of_coords:
            min_x = list_of_coords[0].right
            min_y = list_of_coords[0].up
            max_x = list_of_coords[0].right
            max_y = list_of_coords[0].up
            if len(list_of_coords) > 1:
                for c in list_of_coords[1:]:
                    min_x = min(min_x, c.right)
                    min_y = min(min_y, c.up)
                    max_x = max(max_x, c.right)
                    max_y = max(max_y, c.up)

                return Rect(Coord(min_x, min_y), Coord(max_x - min_x, max_y - min_y))
            else:
                return Rect(Coord(min_x, min_y), Coord(0, 0))
        return Rect(Coord(0, 0), Coord(0, 0))

    @property
    def as_copy(self):
        return Rect(self.bottom_left.as_copy, self.size.as_copy)

    def scale(self, ratio):
        self.bottom_left.scale(ratio)
        self.size.scale(ratio)

    def __str__(self):
        return '%s' % self.as_tuple

    def __repr__(self):
        return '<Rect %s>' % str(self.as_tuple)


class Segment(object):
    __slots__ = ('_start', '_end')

    def __init__(self, start, end):
        self._start = start
        self._end = end

    def __str__(self):
        return '[%s, %s]' % (self._start.as_tuple, self._end.as_tuple)

    def __repr__(self):
        return '<Segment start=%s, end=%s>' % (self._start.as_tuple, self._end.as_tuple)

    def __eq__(self, other):
        if isinstance(other, Segment):
            return self._start == other._start and self._end == other._end
        return False

    def __ne__(self, other):
        if isinstance(other, Segment):
            return not (self._start == other._start and self._end == other._end)
        return True

    def scale(self, ratio):
        self._start.scale(ratio)
        self._end.scale(ratio)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        if isinstance(value, Coord):
            self._start.x = value.x
            self._start.y = value.y
        elif isinstance(value, (list, tuple)) and len(value) == 2:
            self._start.x = value[0]
            self._start.y = value[1]
        elif isinstance(value, dict) and 'x' in value and 'y' in value:
            self._start.x = value['x']
            self._start.y = value['y']
        else:
            ValueError('start value must be a Coord, 2-tuple/list or a dict with x and y but was: %r' % value)

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        if isinstance(value, Coord):
            self._end.x = value.x
            self._end.y = value.y
        elif isinstance(value, (list, tuple)) and len(value) == 2:
            self._end.x = value[0]
            self._end.y = value[1]
        elif isinstance(value, dict) and 'x' in value and 'y' in value:
            self._end.x = value['x']
            self._end.y = value['y']
        else:
            ValueError('end value must be a Coord, 2-tuple/list or a dict with x and y but was: %r' % value)

    @property
    def as_tuples(self):
        return (self._start.as_tuple, self._end.as_tuple)

    @property
    def slope(self):
        delta = self._start.delta(self._end)
        if delta.x:
            return decimal.Decimal(delta.y) / decimal.Decimal(delta.x)
        else:
            return decimal.Decimal('inf')

    @property
    def as_vector(self):
        return self._start.delta(self._end)

    @property
    def as_reversed(self):
        return Segment(start=self._end.as_copy, end=self._start.as_copy)

    def intersects(self, other_segment):
        a = self._start
        b = self._end
        c = other_segment._start
        d = other_segment._end
        return self._is_clockwise_oriented(a, c, d) != self._is_clockwise_oriented(b, c, d) and self._is_clockwise_oriented(a, b, c) != self._is_clockwise_oriented(a, b, d)

    @staticmethod
    def _is_clockwise_oriented(a, b, c):
        return (c.y - a.y) * (b.x - a.x) < (b.y - a.y) * (c.x - a.x)


class SegmentChain(object):
    __slots__ = ('verticies',)

    def __init__(self, list_of_verticies = None):
        self.verticies = list_of_verticies or []

    def __len__(self):
        return len(self.verticies)

    def scale(self, ratio):
        for v in self.verticies:
            v.scale(ratio)

    @property
    def last_vertex(self):
        if self.verticies:
            return self.verticies[-1]

    @property
    def first_vertex(self):
        if self.verticies:
            return self.verticies[0]

    def add_vertex(self, new_vertex):
        self.verticies.append(new_vertex)

    @property
    def segments(self):
        buf = []
        if len(self.verticies) > 1:
            last = None
            for i in xrange(len(self.verticies)):
                if last is not None:
                    buf.append(Segment(last.as_copy, self.verticies[i].as_copy))
                last = self.verticies[i]

        return buf

    @property
    def as_tuple_list(self):
        return [ v.as_tuple for v in self.verticies ]

    def __str__(self):
        return '%s' % self.as_tuple_list

    def __repr__(self):
        return '<SegmentChain %s>' % self.as_tuple_list

    def __contains__(self, item):
        if isinstance(item, (Coord, list, tuple)):
            for c in self.verticies:
                if c == item:
                    return True

        return False


class Polygon(SegmentChain):
    __slots__ = ('verticies',)

    def add_vertex(self, new_vertex):
        raise ValueError('cant add vertex to complete polygon')

    def __str__(self):
        return '%s' % self.as_tuple_list

    def __repr__(self):
        return '<Polygon %s>' % self.as_tuple_list

    @property
    def segments(self):
        segs = super(Polygon, self).segments
        segs.append(Segment(self.last_vertex.as_copy, self.first_vertex.as_copy))
        return segs


class TrackedPolygon(Polygon):
    __slots__ = ('uuid', 'verticies', 'drawing_started_at', 'drawing_duration', 'is_selected', 'is_targeted', 'is_moving', 'is_invalid', 'is_adjusting', 'bounding_rect')

    def __init__(self, list_of_verticies, drawing_started_at, drawing_duration):
        super(TrackedPolygon, self).__init__(list_of_verticies)
        self.uuid = uuid.uuid4()
        self.drawing_started_at = drawing_started_at
        self.drawing_duration = drawing_duration
        self.bounding_rect = Rect.bounding_rect(self.verticies)
        self.is_selected = False
        self.is_targeted = False
        self.is_moving = False
        self.is_adjusting = False
        self.is_invalid = False

    def translate(self, translation):
        for v in self.verticies:
            v += translation

        self.bounding_rect.bottom_left = self.bounding_rect.bottom_left + translation

    def adjust(self, vertex_index, new_pos):
        self.verticies[vertex_index].right = new_pos.right
        self.verticies[vertex_index].up = new_pos.up
        self.bounding_rect = Rect.bounding_rect(self.verticies)

    def scale(self, ratio):
        super(TrackedPolygon, self).scale(ratio)
        self.bounding_rect = Rect.bounding_rect(self.verticies)

    def __str__(self):
        return '%s' % self.as_tuple_list

    def __repr__(self):
        return '<TrackedPolygon[{u}]{inv}{mov}{adj}{tar}{sel} {p}>'.format(u=self.uuid, sel=' select' if self.is_selected else '', tar=' target' if self.is_targeted else '', mov=' move' if self.is_moving else '', adj=' adjust' if self.is_adjusting else '', inv=' invalid' if self.is_invalid else '', p=self.as_tuple_list)


class FeedbackType(enum.IntEnum):
    NOTHING = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class Feedback(object):
    __slots__ = ('slug', 'feedback_type', 'default_text', 'kwargs')

    def __init__(self, slug, feedback_type = FeedbackType.INFO, default_text = None, **kwargs):
        self.slug = slug
        self.feedback_type = feedback_type
        self.default_text = default_text
        self.kwargs = kwargs or {}
        log.info('created: %r', self)

    def __repr__(self):
        return '<Feedback:{t}="{s}" kw={kw!r}>'.format(t=self.feedback_type.name, s=self.slug, kw=self.kwargs)
