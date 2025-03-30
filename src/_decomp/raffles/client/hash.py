#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\hash.py
import random
import math
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

class HashGenerator(object):

    def __init__(self, seed, count, alphabet = None):
        self.seed = seed
        self.bits = int(math.ceil(math.log(count) / math.log(2)))
        self.alphabet = alphabet or ALPHABET
        self._random = random.Random(seed)
        self.alphabet = ''.join(self._random.sample(self.alphabet, len(self.alphabet)))
        self._hashes = []
        self._map = {}

    def __getitem__(self, index):
        while len(self._hashes) <= index:
            self._add(self._next_hash())

        return self._hashes[index]

    def _add(self, hash_value):
        if hash_value not in self._map:
            self._map[hash_value] = len(self._hashes)
            self._hashes.append(hash_value)

    def _next_hash(self):
        return ''.join([ self._random.choice(self.get_available_options(i)) for i in range(4) ])

    def get_available_options(self, index):
        return self.alphabet[index * self.bits % 20:index * self.bits % 20 + self.bits]
