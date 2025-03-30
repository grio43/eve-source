#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\geometry\rect.py
import mathext

class Rect(object):
    __slots__ = ('_left', '_top', '_width', '_height')

    def __init__(self, left, top, width, height):
        self._left = left
        self._top = top
        self._width = width
        self._height = height

    @property
    def left(self):
        return self._left

    @property
    def top(self):
        return self._top

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def right(self):
        return self.left + self.width

    @property
    def center(self):
        return (self.left + self.width / 2.0, self.top + self.height / 2.0)

    @property
    def is_empty(self):
        return self.left >= self.right or self.top >= self.bottom

    def contains(self, x, y):
        return self.left <= x < self.right and self.top <= y < self.bottom

    def overlaps(self, other):
        if self.right <= other.left or other.right <= self.left:
            return False
        if self.bottom <= other.top or other.bottom <= self.top:
            return False
        return True

    def envelops(self, other):
        return self.right > other.right and self.left <= other.left and self.bottom > other.bottom and self.top <= other.top

    def inflate(self, delta):
        return Rect(self.left - delta, self.top - delta, self.width + 2.0 * delta, self.height + 2.0 * delta)

    def deflate(self, delta):
        return self.inflate(-delta)

    def distance_from_point(self, x, y):
        dy = max(self.top - y, 0.0, y - self.bottom)
        dx = max(self.left - x, 0.0, x - self.right)
        return mathext.sqrt(dx * dx + dy * dy)

    @staticmethod
    def lerp(a, b, t):
        if b is None:
            if a is None:
                return
            else:
                k = 1 - t
                return Rect(a.left * k, a.top * k, a.width * k, a.height * k)
        else:
            if a is None:
                return Rect(b.left * t, b.top * t, b.width * t, b.height * t)
            return Rect(left=mathext.lerp(a.left, b.left, t), top=mathext.lerp(a.top, b.top, t), width=mathext.lerp(a.width, b.width, t), height=mathext.lerp(a.height, b.height, t))

    @staticmethod
    def zero():
        return Rect(0, 0, 0, 0)

    def __eq__(self, other):
        return self is other or isinstance(other, Rect) and self.left == other.left and self.top == other.top and self.width == other.width and self.height == other.height

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.left,
         self.top,
         self.width,
         self.height))

    def __repr__(self):
        return 'Rect(left={}, top={}, width={}, height={})'.format(self.left, self.top, self.width, self.height)
