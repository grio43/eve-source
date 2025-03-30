#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\codereload\xreload.py
import collections
import gc
import imp
import logging
import marshal
import sys
import types
import weakref
log = logging.getLogger(__name__)

def _expressyourself(obj):
    try:
        return obj.__class__
    except AttributeError:
        return type(obj)


def _safestr(obj):
    try:
        return str(obj)
    except Exception:
        pass

    try:
        return repr(obj)
    except Exception as ex:
        expressedobj = _expressyourself(obj)
        log.warn('Error converting to str. Type: %s Error: %r', expressedobj, ex)
        return '<REPR ERROR> (%s)' % expressedobj


def xreload(mod, code = None):
    modns = mod.__dict__
    if not code:
        modname = mod.__name__
        i = modname.rfind('.')
        if i >= 0:
            pkgname, modname = modname[:i], modname[i + 1:]
        else:
            pkgname = None
        if pkgname:
            pkg = sys.modules[pkgname]
            path = pkg.__path__
        else:
            pkg = None
            path = None
        stream, filename, (suffix, mode, kind) = imp.find_module(modname, path)
        try:
            if kind not in (imp.PY_COMPILED, imp.PY_SOURCE):
                return reload(mod)
            if kind == imp.PY_SOURCE:
                source = stream.read() + '\n'
                code = compile(source, filename, 'exec')
            else:
                code = marshal.load(stream)
        finally:
            if stream:
                stream.close()

    tmpns = modns.copy()
    log.debug('Moving over the following objects: %s', tmpns.keys())
    modns.clear()
    preload = ['__name__',
     '__file__',
     '__path__',
     '__package__',
     '__loader__',
     '__doc__']
    for name in preload:
        if name in tmpns:
            modns[name] = tmpns[name]

    try:
        exec code in modns
    except Exception:
        log.exception('Failed to reload module')
        for name, value in tmpns.iteritems():
            modns[name] = value

        return mod

    for name, ob in tmpns.items():
        if isinstance(ob, types.ModuleType):
            modns[name] = ob

    oldnames = set(tmpns)
    newnames = set(modns)
    for name in oldnames & newnames:
        log.debug('Assigning over %s: %s', name, _safestr(modns[name])[:160])
        modns[name] = _update(tmpns[name], modns[name])

    log.debug('Module already had: %s', oldnames - newnames)
    log.debug('Module has now: %s', mod.__dict__.keys())
    process_deferred_reference_updates()
    if hasattr(mod, '__reload_update__'):
        mod.__reload_update__(tmpns)
    return mod


def _update(oldobj, newobj):
    if oldobj is newobj:
        return newobj
    if type(oldobj) is not type(newobj):
        return newobj
    if hasattr(newobj, '__reload_update__'):
        return newobj.__reload_update__(oldobj)
    if isinstance(newobj, types.ClassType):
        return _update_class(oldobj, newobj)
    if isinstance(newobj, types.TypeType):
        return _update_class(oldobj, newobj)
    if isinstance(newobj, types.FunctionType):
        return _update_function(oldobj, newobj)
    if isinstance(newobj, types.MethodType):
        return _update_method(oldobj, newobj)
    if isinstance(newobj, classmethod):
        return _update_classmethod(oldobj, newobj)
    if isinstance(newobj, staticmethod):
        return _update_staticmethod(oldobj, newobj)
    return newobj


def _update_function(oldfunc, newfunc):
    oldfunc.__doc__ = newfunc.__doc__
    oldfunc.__dict__.update(newfunc.__dict__)
    oldfunc.__defaults__ = newfunc.__defaults__
    if oldfunc.__closure__ != newfunc.__closure__:
        update_global_references(oldfunc, newfunc)
        return newfunc
    if oldfunc.func_code != newfunc.func_code:
        try:
            oldfunc.func_code = newfunc.func_code
        except ValueError:
            update_global_references(oldfunc, newfunc)
            return newfunc

    update_global_references(newfunc, oldfunc)
    return oldfunc


def _update_method(oldmeth, newmeth):
    _update(oldmeth.im_func, newmeth.im_func)
    return oldmeth


def _update_class(oldclass, newclass):
    olddict = oldclass.__dict__
    newdict = newclass.__dict__
    oldnames = set(olddict)
    newnames = set(newdict)
    modified_bases = []
    for new_base in newclass.__bases__:
        for old_base in oldclass.__bases__:
            if old_base is new_base or old_base.__name__ == new_base.__name__:
                modified_bases.append(old_base)
                break
        else:
            modified_bases.append(new_base)

    oldclass.__bases__ = tuple(modified_bases)
    restricted_names = set(['__dict__', '__doc__'])
    for name in newnames - oldnames - restricted_names:
        setattr(oldclass, name, newdict[name])

    for name in oldnames - newnames - restricted_names:
        delattr(oldclass, name)

    for name in oldnames & newnames - restricted_names:
        try:
            setattr(oldclass, name, _update(olddict[name], newdict[name]))
        except AttributeError:
            log.exception('Ignoring exception')

    deferred_update_global_references(newclass, oldclass)
    return oldclass


def _update_classmethod(oldcm, newcm):
    _update(oldcm.__get__(0), newcm.__get__(0))
    return oldcm


def _update_staticmethod(oldsm, newsm):
    _update(oldsm.__get__(0), newsm.__get__(0))
    return oldsm


_deferred_reference_updates = {}

def deferred_update_global_references(oldobj, newobj):
    global _deferred_reference_updates
    _deferred_reference_updates[oldobj] = newobj


def process_deferred_reference_updates():
    while _deferred_reference_updates:
        oldobj, newobj = _deferred_reference_updates.popitem()
        update_global_references(oldobj, newobj, ignore=_deferred_reference_updates)


def update_global_references(oldobj, newobj, ignore = None):
    _update_weak_references(oldobj, newobj)
    _update_references(oldobj, newobj, ignore=ignore)


def _update_references(oldobj, newobj, ignore = None):
    referrers = gc.get_referrers(oldobj)
    for referrer in referrers:
        try:
            if ignore and referrer in ignore:
                continue
        except TypeError:
            continue

        if isinstance(referrer, collections.MutableMapping):
            for k, v in referrer.items():
                if v is oldobj:
                    referrer[k] = newobj

        elif isinstance(referrer, collections.MutableSequence):
            for i in xrange(len(referrer)):
                if referrer[i] is oldobj:
                    referrer[i] = newobj

        elif isinstance(referrer, collections.MutableSet):
            referrer.remove(oldobj)
            referrer.add(newobj)
        elif isinstance(referrer, tuple):
            new_tuple = tuple(((x if x is not oldobj else newobj) for x in referrer))
            _update_references(referrer, new_tuple, ignore=[referrers])
            _update_weak_references(referrer, new_tuple)


def _update_weak_references(old_obj, new_obj):
    weak_refs = list(weakref.getweakrefs(old_obj))
    if len(weak_refs) == 0:
        return
    old_ref = weak_refs.pop()
    while len(weak_refs) > 0:
        new_ref = weakref.ref(new_obj)
        _update_references(old_ref, new_ref, ignore=[weak_refs])
        try:
            old_ref = weak_refs.pop()
        except Exception:
            pass
