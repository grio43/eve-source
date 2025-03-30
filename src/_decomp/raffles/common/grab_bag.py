#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\common\grab_bag.py
from bisect import bisect_left
from contextlib import contextmanager
import logging
import random
logger = logging.getLogger(__name__)

class GrabBag(object):

    def __init__(self, random_generator = None):
        if random_generator is None:
            random_generator = random.random
        self._weights = []
        self._keys = []
        self._weight_index = []
        self._random = random_generator
        self._is_batched = False
        self._lowest_changed_index = None

    @property
    def total_weight(self):
        if self._weight_index:
            return self._weight_index[-1]
        return 0

    def grab(self, count):
        if not len(self):
            return []
        if count >= len(self):
            return self._keys[:]
        result = []
        for _ in xrange(count):
            number = self._random() * self.total_weight
            index = bisect_left(self._weight_index, number)
            result.append(self._keys[index])

        return result

    def filter(self, keys):
        filtered_bag = GrabBag()
        filtered_bag.insert_all(((self._keys[i], self._weights[i]) for i in xrange(len(self)) if self._keys[i] in keys))
        return filtered_bag

    def insert(self, key, weight):
        if weight <= 0:
            logger.warning('Ignoring raffle {} with score {}'.format(key, weight))
            return
        with self.batch():
            self._insert(key, weight)

    def insert_all(self, seq):
        with self.batch():
            for key, weight in seq:
                self._insert(key, weight)

    def remove(self, key):
        with self.batch():
            index = self._keys.index(key)
            self._remove(index)

    def discard(self, key):
        try:
            self.remove(key)
        except ValueError:
            pass

    @contextmanager
    def batch(self):
        if self._is_batched:
            yield
            return
        self._is_batched = True
        self._lowest_changed_index = len(self)
        try:
            yield
        finally:
            self._is_batched = False
            self._update_weight_index(start=self._lowest_changed_index)

    def _insert(self, key, weight):
        index = bisect_left(self._weights, weight)
        self._weights.insert(index, weight)
        self._keys.insert(index, key)
        self._weight_index.insert(index, None)
        self._lowest_changed_index = min(index, self._lowest_changed_index)
        return index

    def _remove(self, index):
        self._weights.pop(index)
        self._keys.pop(index)
        self._weight_index.pop(index)
        self._lowest_changed_index = min(index, self._lowest_changed_index)

    def _update_weight_index(self, start = 0):
        for i in xrange(start, len(self)):
            weight = self._weights[i]
            if i > 0:
                weight += self._weight_index[i - 1]
            self._weight_index[i] = weight

    def __len__(self):
        return len(self._keys)
