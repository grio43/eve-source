#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\watchdog\utils\echo.py
import inspect
import sys

def name(item):
    return item.__name__


def is_classmethod(instancemethod, klass):
    return inspect.ismethod(instancemethod) and instancemethod.__self__ is klass


def is_static_method(method, klass):
    for c in klass.mro():
        if name(method) in c.__dict__:
            return isinstance(c.__dict__[name(method)], staticmethod)
    else:
        return False


def is_class_private_name(name):
    return name.startswith('__') and not name.endswith('__')


def method_name(method):
    mname = name(method)
    if is_class_private_name(mname):
        mname = '_%s%s' % (name(method.__self__.__class__), mname)
    return mname


def format_arg_value(arg_val):
    arg, val = arg_val
    return '%s=%r' % (arg, val)


def echo(fn, write = sys.stdout.write):
    import functools
    code = fn.__code__
    argcount = code.co_argcount
    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.__defaults__ or list()
    argdefs = dict(list(zip(argnames[-len(fn_defaults):], fn_defaults)))

    @functools.wraps(fn)
    def wrapped(*v, **k):
        positional = list(map(format_arg_value, list(zip(argnames, v))))
        defaulted = [ format_arg_value((a, argdefs[a])) for a in argnames[len(v):] if a not in k ]
        nameless = list(map(repr, v[argcount:]))
        keyword = list(map(format_arg_value, list(k.items())))
        args = positional + defaulted + nameless + keyword
        write('%s(%s)\n' % (name(fn), ', '.join(args)))
        return fn(*v, **k)

    return wrapped


def echo_instancemethod(klass, method, write = sys.stdout.write):
    mname = method_name(method)
    never_echo = ('__str__', '__repr__')
    if mname in never_echo:
        pass
    elif is_classmethod(method, klass):
        setattr(klass, mname, classmethod(echo(method.__func__, write)))
    else:
        setattr(klass, mname, echo(method, write))


def echo_class(klass, write = sys.stdout.write):
    for _, method in inspect.getmembers(klass, inspect.ismethod):
        echo_instancemethod(klass, method, write)

    for _, fn in inspect.getmembers(klass, inspect.isfunction):
        if is_static_method(fn, klass):
            setattr(klass, name(fn), staticmethod(echo(fn, write)))
        else:
            echo_instancemethod(klass, fn, write)


def echo_module(mod, write = sys.stdout.write):
    for fname, fn in inspect.getmembers(mod, inspect.isfunction):
        setattr(mod, fname, echo(fn, write))

    for _, klass in inspect.getmembers(mod, inspect.isclass):
        echo_class(klass, write)


if __name__ == '__main__':
    import doctest
    optionflags = doctest.ELLIPSIS
    doctest.testfile('echoexample.txt', optionflags=optionflags)
    doctest.testmod(optionflags=optionflags)
