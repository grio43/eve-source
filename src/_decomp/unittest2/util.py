#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\unittest2\util.py


def safe_repr(obj):
    try:
        return repr(obj)
    except Exception:
        return object.__repr__(obj)


def strclass(cls):
    return '%s.%s' % (cls.__module__, cls.__name__)


def sorted_list_difference(expected, actual):
    i = j = 0
    missing = []
    unexpected = []
    while True:
        try:
            e = expected[i]
            a = actual[j]
            if e < a:
                missing.append(e)
                i += 1
                while expected[i] == e:
                    i += 1

            elif e > a:
                unexpected.append(a)
                j += 1
                while actual[j] == a:
                    j += 1

            else:
                i += 1
                try:
                    while expected[i] == e:
                        i += 1

                finally:
                    j += 1
                    while actual[j] == a:
                        j += 1

        except IndexError:
            missing.extend(expected[i:])
            unexpected.extend(actual[j:])
            break

    return (missing, unexpected)
