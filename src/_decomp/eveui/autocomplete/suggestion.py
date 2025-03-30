#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\suggestion.py
import abc
import itertools

class SuggestionMeta(abc.ABCMeta):

    def __new__(cls, name, bases, dct):
        klass = super(SuggestionMeta, cls).__new__(cls, name, bases, dct)
        key_attributes = dct['key_attributes']
        if isinstance(key_attributes, abc.abstractproperty):
            key_attributes = []
        attributes = getattr(klass, '_Suggestion__attributes', ())
        klass._Suggestion__attributes = tuple(itertools.chain(attributes, key_attributes))
        return klass


class Suggestion(object):
    __metaclass__ = SuggestionMeta
    __slots__ = ()

    @abc.abstractproperty
    def key_attributes(self):
        pass

    @abc.abstractproperty
    def text(self):
        pass

    @property
    def name(self):
        return self.text

    @property
    def subtext(self):
        return ''

    def render_icon(self, size):
        return None

    def get_drag_data(self):
        return None

    def get_menu(self):
        return None

    def has_show_info(self):
        return False

    def show_info(self):
        pass

    def __getstate__(self):
        return tuple((getattr(self, attr) for attr in self.key_attributes))

    def __setstate__(self, state):
        for attr, value in zip(self.key_attributes, state):
            setattr(self, attr, value)

    def __eq__(self, other):
        return isinstance(other, type(self)) and all((getattr(self, a) == getattr(other, a) for a in self.__attributes))

    def __hash__(self):
        return hash(tuple((getattr(self, a) for a in self.__attributes)))

    def __str__(self):
        return self.text

    def __unicode__(self):
        return unicode(self.text)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, ', '.join(('{}={}'.format(a, getattr(self, a)) for a in self.__attributes)))
