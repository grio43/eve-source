#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\provider.py
import abc
import collections
import threadutils
from eveui.autocomplete.fuzzy import fuzzy_match

class Provider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self, query, previous_suggestions):
        pass


class NameCacheProvider(Provider):

    def __init__(self, cache, suggestion_type, filter = None, score = None):
        self.cache = cache
        self.filter = filter
        self.score = score
        self.suggestion_type = suggestion_type

    def __call__(self, query, previous_suggestions):
        if not query:
            return
        for suggestion in previous_suggestions:
            if not isinstance(suggestion, self.suggestion_type):
                continue
            score = self._calculate_score(query, suggestion.text)
            if score is not None:
                yield (score, suggestion)

        for suggestion_id, name in self.cache.query(query):
            threadutils.be_nice(5)
            if self.filter and not self.filter(suggestion_id):
                continue
            suggestion = self.make_suggestion(suggestion_id)
            if suggestion in previous_suggestions:
                continue
            score = self._calculate_score(query, name)
            if score is not None:
                yield (score, suggestion)

    def make_suggestion(self, suggestion_id):
        return self.suggestion_type(suggestion_id)

    def _calculate_score(self, query, name):
        if self.score:
            return self.score(query, name)
        matched, score, _ = fuzzy_match(query, name)
        if matched:
            return score


class NameCache(object):
    __metaclass__ = abc.ABCMeta
    __instance = None
    use_index = True

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise RuntimeError('Only a single instance of {} allowed'.format(self.__class__.__name__))
        self.__cache = None
        self.__index = None
        self.__prime_cache_thread = None
        self.__prime_index_thread = None

    @abc.abstractmethod
    def prime(self):
        pass

    def query(self, query):
        if not query:
            return
        self._ensure_cache_primed()
        if self.use_index:
            self._ensure_index_primed()
            query = set(query.lower())
            ids = None
            for letter in query:
                if ids is None:
                    ids = self.__index[letter]
                else:
                    ids = ids.intersection(self.__index[letter])

        else:
            ids = self.__cache.iterkeys()
        for id in ids:
            yield (id, self.__cache[id])

    def __iter__(self):
        self._ensure_cache_primed()
        return self.__cache.iteritems()

    def __getitem__(self, index):
        self._ensure_cache_primed()
        return self.__cache[index]

    def _ensure_cache_primed(self):
        if self.__cache is None:
            if self.__prime_cache_thread is None:
                self.__prime_cache_thread = self.__prime_cache()
            self.__prime_cache_thread.get()

    def _ensure_index_primed(self):
        if self.__index is None:
            if self.__prime_index_thread is None:
                self.__prime_index_thread = self.__prime_index()
            self.__prime_index_thread.get()

    @threadutils.threaded
    def __prime_cache(self):
        if self.__cache is not None:
            return
        self.__cache = self.prime()

    @threadutils.threaded
    def __prime_index(self):
        if self.__index is not None:
            return
        self._ensure_cache_primed()
        index = collections.defaultdict(set)
        for id, name in self.__cache.iteritems():
            for letter in name:
                index[letter.lower()].add(id)

        self.__index = index
