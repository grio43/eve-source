#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\proper\_impl.py
import abc
import collections
import contextlib
import functools
import weakref
import signals
import uthread2

class _Nothing(object):
    _singleton = None

    def __new__(cls):
        if _Nothing._singleton is None:
            _Nothing._singleton = super(_Nothing, cls).__new__(cls)
        return _Nothing._singleton

    def __repr__(self):
        return 'NOTHING'


NOTHING = _Nothing()

class Factory(object):

    def __init__(self, f, takes_self = False):
        self.f = f
        self.takes_self = takes_self

    def __call__(self, obj):
        if self.takes_self:
            return self.f(obj)
        else:
            return self.f()


def ty(_f = None, default = NOTHING, factory = None, comparator = None, validator = None, coerce = None, before_change = None, after_change = None):
    if factory is not None:
        if default is not NOTHING:
            raise ValueError('The `default` and `factory` arguments are mutually exclusive.')
        if not callable(factory):
            raise ValueError('The `factory` argument must be a callable.')
        default = Factory(factory)
    return Property(default=default, comparator=comparator, validator=validator, coerce=coerce, before_change=before_change, after_change=after_change)


class DependencyTracker(object):

    def __init__(self):
        self.__tracked_stack = []
        self.__dependencies = weakref.WeakKeyDictionary()

    @contextlib.contextmanager
    def track(self, obj, prop):
        if (obj, prop) in self.__tracked_stack:
            raise RuntimeError('Circular dependency chain found')
        self.__tracked_stack.append((obj, prop))
        if obj not in self.__dependencies:
            self.__dependencies[obj] = weakref.WeakKeyDictionary()
        self.__dependencies[obj][prop] = weakref.WeakKeyDictionary()
        try:
            yield self
        finally:
            self.__tracked_stack.pop()

    def get_dependencies(self, obj, prop):
        ret = {}
        if obj not in self.__dependencies or prop not in self.__dependencies[obj]:
            return ret
        deps = self.__dependencies[obj][prop]
        for obj_ref in deps.iterkeyrefs():
            obj = obj_ref()
            if obj is not None:
                ret[obj] = deps[obj]

        return ret

    def mark_dependency(self, obj, prop):
        if not self.__tracked_stack:
            return
        tracked_obj, tracked_prop = self.__tracked_stack[-1]
        if obj not in self.__dependencies[tracked_obj][tracked_prop]:
            self.__dependencies[tracked_obj][tracked_prop][obj] = set()
        self.__dependencies[tracked_obj][tracked_prop][obj].add(prop)


class PropertyChangeTracker(object):

    def __init__(self):
        self._locks = weakref.WeakKeyDictionary()
        self._change_stack = weakref.WeakKeyDictionary()

    @contextlib.contextmanager
    def track_change(self, obj, prop):
        stack = self._get_stack()
        self._check_for_circular_references(obj, prop, stack)
        with self._get_lock(obj, prop):
            stack.append((obj, prop))
            try:
                yield
            finally:
                stack.pop()

    def _get_stack(self):
        current_thread = uthread2.get_current()
        if current_thread not in self._change_stack:
            self._change_stack[current_thread] = []
        return self._change_stack[current_thread]

    def _get_lock(self, obj, prop):
        if obj not in self._locks:
            self._locks[obj] = {}
        if prop not in self._locks[obj]:
            self._locks[obj][prop] = uthread2.Semaphore()
        return self._locks[obj][prop]

    def _check_for_circular_references(self, obj, prop, stack):
        if (obj, prop) not in stack:
            return
        start_index = stack.index((obj, prop))
        chain = []
        for o, p in stack:
            chain.append('  {}.{}\n'.format(o, p.name))

        chain.append('  {}.{}\n'.format(obj, prop.name))
        raise RuntimeError("Circular change chain detected!\nYou've managed to create a circular chain of events which may result in an infinte loop. A change handler for the '{last_prop_name}' property on {last_obj} is attempting to change '{origin_prop_name}' on {origin_obj} which is already being changed earlier in the chain:\n\n{chain}\n\nHave a look at the stacktrace below to figure out which handlers are causing the issue.".format(last_prop_name=stack[-1][1].name, last_obj=stack[-1][0], origin_prop_name=stack[start_index][1].name, origin_obj=stack[start_index][0], chain=''.join(chain)))


class PropertyBase(object):
    __metaclass__ = abc.ABCMeta
    _dependency_tracker = DependencyTracker()
    _change_tracker = PropertyChangeTracker()
    name = '<unknown property>'

    def __init__(self, comparator = None, validator = None, coerce = None):
        if comparator and not callable(comparator):
            raise ValueError('The `comparator` argument must be a callable.')
        if validator and not callable(validator):
            raise ValueError('The `validator` argument must be a callable.')
        if coerce and not callable(coerce):
            raise ValueError('The `coerce` argument must be a callable.')
        self._comparator = comparator
        self._validator = validator
        self._coerce = coerce
        self._signals = weakref.WeakKeyDictionary()
        self._dep_signals = weakref.WeakKeyDictionary()
        self._deferred_dispatch = {}

        def reload_hook(old):
            self._signals = old._signals
            self._dep_signals = old._dep_signals
            self._deferred_dispatch = old._deferred_dispatch
            return self

        self.__reload_update__ = reload_hook

    @property
    def validator(self, f = None):

        def wrapper(f):
            if self._validator:
                raise TypeError('Property already has a validator defined')
            self._validator = f
            return f

        if f is None:
            return wrapper
        return wrapper(f)

    def get_default_value(self, obj):
        return NOTHING

    def bind(self, obj, handler):
        self._get_signal(obj).connect(handler)

    def unbind(self, obj, handler):
        self._get_signal(obj).disconnect(handler)

    def unbind_all(self, obj):
        if obj in self._signals:
            self._signals[obj].clear()

    @abc.abstractmethod
    def get(self, obj):
        pass

    def set(self, obj, value):
        raise AttributeError('Cannot set attribute')

    def dispatch(self, obj):
        if obj in self._dep_signals:
            self._dep_signals[obj](obj, self)
        if obj in self._deferred_dispatch:
            self._deferred_dispatch[obj] = True
            return
        value = self.get(obj)
        if obj in self._signals:
            self._signals[obj](obj, value)
        default_handler_name = 'on_{}'.format(self.name)
        default_handler = getattr(obj, default_handler_name, None)
        if default_handler:
            default_handler(value)

    def bind_dependency(self, obj, handler):
        self._get_dependency_signal(obj).connect(handler)

    def unbind_dependency(self, obj, handler):
        self._get_dependency_signal(obj).disconnect(handler)

    def init_storage(self, obj, value):
        pass

    def post_initialize(self, obj):
        pass

    def defer(self, obj):
        self._deferred_dispatch[obj] = False

    def resume(self, obj):
        should_dispatch = self._deferred_dispatch.pop(obj, False)
        if should_dispatch:
            with self._change_tracker.track_change(obj, self):
                self.dispatch(obj)

    def _get_signal(self, obj):
        if obj not in self._signals:
            self._signals[obj] = signals.Signal()
        return self._signals[obj]

    def _get_dependency_signal(self, obj):
        if obj not in self._dep_signals:
            self._dep_signals[obj] = signals.Signal()
        return self._dep_signals[obj]

    def _is_change(self, obj, new_value):
        current = self.__get__(obj)
        if self._comparator is not None:
            is_equal = self._comparator(obj, current, new_value)
            if is_equal is not NotImplemented:
                return not is_equal
        return current != new_value

    def _coerce_value(self, value):
        if self._coerce:
            return self._coerce(value)
        return value

    def _validate_value(self, obj, value):
        if self._validator is None:
            return value
        else:
            return self._validator(obj, value)

    def __call__(self, f):
        return self

    def __delete__(self, obj):
        raise AttributeError('Cannot delete attribute')

    def __get__(self, obj, obj_type = None):
        if obj is None:
            return self
        return self.get(obj)

    def __set__(self, obj, value):
        return self.set(obj, value)

    def __repr__(self):
        return "<proper.{}, name='{}'>".format(self.__class__.__name__, self.name)


class Property(PropertyBase):

    def __init__(self, default = NOTHING, before_change = None, after_change = None, **kwargs):
        if before_change and not callable(before_change):
            raise ValueError('The `before_change` argument must be a callable.')
        if after_change and not callable(after_change):
            raise ValueError('The `after_change` argument must be a callable.')
        super(Property, self).__init__(**kwargs)
        self._default = default
        self._before_change = before_change
        self._after_change = after_change
        self._values = weakref.WeakKeyDictionary()
        parent_reload_hook = self.__reload_update__

        def reload_hook(old):
            self._values = old._values
            return parent_reload_hook(old)

        self.__reload_update__ = reload_hook

    @property
    def default(self, f = None):

        def wrapper(f):
            if self._default is not NOTHING:
                raise TypeError('Property already has a default value defined.')
            self._default = Factory(f, takes_self=True)
            return f

        if f is None:
            return wrapper
        return wrapper(f)

    @property
    def before_change(self, f = None):

        def wrapper(f):
            if self._before_change is not None:
                raise TypeError('Property already has a before_change handler defined.')
            self._before_change = f
            return f

        if f is None:
            return wrapper
        return wrapper(f)

    @property
    def after_change(self, f = None):

        def wrapper(f):
            if self._after_change is not None:
                raise TypeError('Property already has a after_change handler defined.')
            self._after_change = f
            return f

        if f is None:
            return wrapper
        return wrapper(f)

    def get_default_value(self, obj):
        if isinstance(self._default, Factory):
            return self._default(obj)
        else:
            return self._default

    def get(self, obj):
        self._dependency_tracker.mark_dependency(obj, self)
        try:
            value = self._values[obj]
            if isinstance(value, Uninitialized):
                value = self._initialize_value(obj, value)
            return value
        except KeyError:
            return NOTHING

    def set(self, obj, value):
        with self._change_tracker.track_change(obj, self):
            value = self._coerce_value(value)
            value = self._validate_value(obj, value)
            if self._is_change(obj, value):
                if self._before_change:
                    self._before_change(obj, value)
                self._values[obj] = value
                if self._after_change:
                    self._after_change(obj, value)
                self.dispatch(obj)

    def init_storage(self, obj, value):
        self._values[obj] = Uninitialized(value)

    def _initialize_value(self, obj, uninitialized):
        value = uninitialized.value
        if isinstance(value, LazyDefaultValue):
            value = value()
        if value is not NOTHING:
            value = self._coerce_value(value)
            value = self._validate_value(obj, value)
        self._values[obj] = value
        return value


class Uninitialized(object):

    def __init__(self, value):
        self.value = value


class AliasProperty(PropertyBase):

    def __init__(self, getter, setter = None, **kwargs):
        super(AliasProperty, self).__init__(**kwargs)
        self._getter = getter
        self._setter = setter
        self.__echo_handlers = set()
        self.__bound_dependencies = weakref.WeakKeyDictionary()
        self.__cached_values = weakref.WeakKeyDictionary()
        self.__previous_cached_values = weakref.WeakKeyDictionary()

    def setter(self, func):
        self._setter = func
        return self

    def dispatch(self, obj):
        self._clear_cached_value(obj)
        current_value = self.get(obj)
        if obj in self.__previous_cached_values:
            previous_value = self.__previous_cached_values[obj]
            if current_value == previous_value:
                return
        super(AliasProperty, self).dispatch(obj)

    def _handle_dependency_change(self, obj, obj_dep, prop):
        self._clear_cached_value(obj)
        self.__bound_dependencies.pop(obj).drop()
        prop.bind(obj_dep, self._get_echo_handler(obj, prop))

    def _get_echo_handler(self, obj, prop):
        handler = TransientAliasEchoHandler(obj, self, prop, self._drop_echo_handler)
        self.__echo_handlers.add(handler)
        return handler

    def _drop_echo_handler(self, handler):
        self.__echo_handlers.remove(handler)

    def get(self, obj):
        self._dependency_tracker.mark_dependency(obj, self)
        if obj not in self.__cached_values:
            if obj in self.__bound_dependencies:
                self.__bound_dependencies.pop(obj).drop()
            with self._dependency_tracker.track(obj, self):
                self.__cached_values[obj] = self._getter(obj)
            self.__bound_dependencies[obj] = BoundDependenciesCookie(obj=obj, handler=self._handle_dependency_change, dependencies=self._dependency_tracker.get_dependencies(obj, self))
        return self.__cached_values[obj]

    def set(self, obj, value):
        if self._setter is None:
            raise AttributeError('Cannot set attribute')
        with self._change_tracker.track_change(obj, self):
            value = self._coerce_value(value)
            value = self._validate_value(obj, value)
            self._setter(obj, value)

    def init_storage(self, obj, value):
        self.set(obj, value)

    def post_initialize(self, obj):
        self.get(obj)

    def _clear_cached_value(self, obj):
        if obj in self.__cached_values:
            value = self.__cached_values.pop(obj)
            self.__previous_cached_values[obj] = value


class TransientAliasEchoHandler(object):

    def __init__(self, obj, alias_prop, prop, drop):
        self._obj_ref = weakref.ref(obj)
        self._alias_prop = alias_prop
        self._prop = prop
        self._drop = drop
        self._dropped = False

    def __call__(self, obj, value):
        if self._dropped:
            return
        self._prop.unbind(obj, self)
        self._drop(self)
        self._dropped = True
        alias_obj = self._obj_ref()
        if alias_obj:
            self._alias_prop.dispatch(alias_obj)


class BoundDependenciesCookie(object):

    def __init__(self, obj, handler, dependencies):
        self._obj_ref = weakref.ref(obj)
        self._handler = handler
        self._dependencies = dependencies
        for obj, props in dependencies.items():
            for prop in props:
                prop.bind_dependency(obj, self._on_dependency_changed)

    def drop(self):
        for obj, props in self._dependencies.items():
            for prop in props:
                prop.unbind_dependency(obj, self._on_dependency_changed)

        self._dependencies = None

    def _on_dependency_changed(self, obj_dep, prop):
        obj = self._obj_ref()
        if obj is not None:
            self._handler(obj, obj_dep, prop)


def alias(func):
    return AliasProperty(func)


class PropertyCache(collections.defaultdict):

    def __missing__(self, key):
        props = {}
        for name in dir(key):
            prop = getattr(key, name, None)
            if isinstance(prop, PropertyBase):
                prop.name = name
                props[name] = prop

        return props


class PropertyHandlerCache(collections.defaultdict):

    def __missing__(self, key):
        handlers = {}
        for func_name in dir(key):
            if not func_name.startswith('on_'):
                continue
            prop_name = func_name[3:]
            try:
                key.property(prop_name)
                handlers[prop_name] = func_name
            except KeyError:
                continue

        return handlers


class LazyDefaultValue(object):

    def __init__(self, prop, obj):
        self.prop = prop
        self.obj_ref = weakref.ref(obj)

    def __call__(self):
        obj = self.obj_ref()
        value = getattr(obj, 'default_{}'.format(self.prop.name), NOTHING)
        if value is NOTHING:
            value = self.prop.get_default_value(obj)
        return value


class Observable(object):
    __properties = PropertyCache()
    __handlers = PropertyHandlerCache()
    __getters = weakref.WeakKeyDictionary()
    __setters = weakref.WeakKeyDictionary()
    __deferred_objs = weakref.WeakKeyDictionary()

    @classmethod
    def properties(cls):
        return cls.__properties[cls].values()

    @classmethod
    def property(cls, name):
        return cls.__properties[cls][name]

    def __init__(self, **kwargs):
        for prop in self.properties():
            if isinstance(prop, AliasProperty):
                continue
            value = NOTHING
            if prop.name in kwargs:
                value = kwargs.pop(prop.name)
            if value is NOTHING:
                value = LazyDefaultValue(prop, self)
            if value is not NOTHING:
                prop.init_storage(self, value)

        super(Observable, self).__init__(**kwargs)
        for prop in self.properties():
            prop.post_initialize(self)

    def bind(self, **kwargs):
        for name, handler in kwargs.items():
            try:
                self.__bind(name, handler)
            except KeyError:
                raise TypeError('No attribute with name {}'.format(name))

    def unbind(self, **kwargs):
        for name, handler in kwargs.items():
            self.property(name).unbind(self, handler)

    def unbind_all(self):
        for prop in self.properties():
            prop.unbind_all(self)

    def dispatch(self, prop_name):
        self.property(prop_name).dispatch(self)

    def getter(self, name):
        if self not in self.__getters:
            self.__getters[self] = {}
        storage = self.__getters[self]
        if name not in storage:
            storage[name] = functools.partial(self.__getter_proxy, weakref.ref(self), name)
        return storage[name]

    def setter(self, name):
        if self not in self.__setters:
            self.__setters[self] = {}
        storage = self.__setters[self]
        if name not in storage:
            storage[name] = functools.partial(self.__setter_proxy, weakref.ref(self), name)
        return storage[name]

    @contextlib.contextmanager
    def deferred_dispatch(self):
        already_deferred = self.__defer_dispatch()
        try:
            yield self
        finally:
            if not already_deferred:
                self.__resume_dispatch()

    def __defer_dispatch(self):
        if self in self.__deferred_objs:
            return True
        self.__deferred_objs[self] = True
        for prop in self.properties():
            prop.defer(self)

        return False

    def __resume_dispatch(self):
        del self.__deferred_objs[self]
        for prop in self.properties():
            prop.resume(self)

    @staticmethod
    def __getter_proxy(self_ref, name, instance):
        self = self_ref()
        return self.property(name).__get__(self)

    @staticmethod
    def __setter_proxy(self_ref, name, instance, value):
        self = self_ref()
        self.property(name).__set__(self, value)

    def __bind(self, name, handler):
        self.property(name).bind(self, handler)
