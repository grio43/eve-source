#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\various_unsorted.py
import logging
import sys
from functools import wraps
import blue
import mathext
from stringutil import strx
from carbonui.uicore import uicore
from carbonui.util import sortUtil
log = logging.getLogger(__name__)

def GetBuffersize(size):
    if size <= 8:
        return 8
    if size <= 16:
        return 16
    if size <= 32:
        return 32
    if size <= 64:
        return 64
    if size <= 128:
        return 128
    if size <= 256:
        return 256
    if size <= 512:
        return 512
    if size <= 1024:
        return 1024
    if size <= 2048:
        return 2048
    return 128


def StringColorToHex(color):
    colors = {'Black': '0xff000000',
     'Green': '0xff008000',
     'Silver': '0xffC0C0C0',
     'Lime': '0xff00FF00',
     'Gray': '0xff808080',
     'Grey': '0xff808080',
     'Olive': '0xff808000',
     'White': '0xffFFFFFF',
     'Yellow': '0xffFFFF00',
     'Maroon': '0xff800000',
     'Navy': '0xff000080',
     'Red': '0xffFF0000',
     'Blue': '0xff0000FF',
     'Purple': '0xff800080',
     'Teal': '0xff008080',
     'Fuchsia': '0xffFF00FF',
     'Aqua': '0xff00FFFF',
     'Orange': '0xffFF8000',
     'Transparent': '0x00000000',
     'Lightred': '0xffcc3333',
     'Lightblue': '0xff7777ff',
     'Lightgreen': '0xff80ff80'}
    return colors.get(color.capitalize(), None)


def Sort(lst):
    return sortUtil.Sort(lst)


def SortListOfTuples(lst, reverse = 0):
    return sortUtil.SortListOfTuples(lst, reverse)


def Flush(parent):
    parent.Flush()


def FlushList(lst):
    for each in lst[:]:
        if each is not None and not getattr(each, 'destroyed', 0):
            each.Close()

    del lst[:]


def GetWindowAbove(item):
    if item == uicore.desktop:
        return None
    if uicore.registry.IsWindow(item):
        return item
    if item.parent and not item.parent.destroyed:
        return GetWindowAbove(item.parent)


def IsUnderActiveWindow(item):
    if IsUnder(item, uicore.layer.modal):
        return True
    active_window = uicore.registry.GetActive()
    return active_window and active_window == GetWindowAbove(item)


def GetDesktopObject(item):
    if not item.parent:
        if item.destroyed:
            return None
        else:
            return item
    else:
        return GetDesktopObject(item.parent)


def GetBrowser(item):
    if item == uicore.desktop:
        return
    if getattr(item, 'IsBrowser', None):
        return item
    from carbonui.control.edit import EditCore
    if isinstance(item, EditCore):
        return item
    if item.parent:
        return GetBrowser(item.parent)


def GetAttrs(obj, *names):
    for name in names:
        obj = getattr(obj, name, None)
        if obj is None:
            return

    return obj


def Transplant(wnd, newParent, idx = None):
    if wnd is None or wnd.destroyed or newParent is None or newParent.destroyed:
        return
    if idx in (-1, None):
        idx = len(newParent.children)
    wnd.SetParent(newParent, idx)


def IsUnder(child, ancestor_maybe, retfailed = False):
    return child.IsUnder(ancestor_maybe, retfailed)


def MapIcon(sprite, iconPath, ignoreSize = 0):
    if hasattr(sprite, 'LoadIcon'):
        return sprite.LoadIcon(iconPath, ignoreSize)
    import warnings
    warnings.warn('Called MapIcon for an instance of a non-icon class. Implement LoadIcon on the relevant class instead.', DeprecationWarning)
    from eve.client.script.ui.control import eveIcon
    return eveIcon.Icon.LoadIcon(sprite, iconPath, ignoreSize)


def ConvertDecimal(qty, fromChar, toChar, numDecimals = None):
    import types
    ret = qty
    if type(ret) in [types.IntType, types.FloatType, types.LongType]:
        if numDecimals is not None:
            ret = '%.*f' % (numDecimals, qty)
        else:
            ret = repr(qty)
    ret = ret.replace(fromChar, toChar)
    return ret


def GetClipboardData():
    try:
        return blue.clipboard.GetClipboardUnicode()
    except (blue.error, WindowsError):
        return ''


def GetTrace(item, trace = '', div = '/'):
    trace = div + item.name + trace
    if getattr(item, 'parent', None) is None:
        return trace
    return GetTrace(item.parent, trace, div)


def ParseHTMLColor(colorstr, asTuple = 0, error = 0):
    colors = {'Black': '0x000000',
     'Green': '0x008000',
     'Silver': '0xC0C0C0',
     'Lime': '0x00FF00',
     'Gray': '0x808080',
     'Grey': '0x808080',
     'Olive': '0x808000',
     'White': '0xFFFFFF',
     'Yellow': '0xFFFF00',
     'Maroon': '0x800000',
     'Navy': '0x000080',
     'Red': '0xFF0000',
     'Blue': '0x0000FF',
     'Purple': '0x800080',
     'Teal': '0x008080',
     'Fuchsia': '0xFF00FF',
     'Aqua': '0x00FFFF',
     'Transparent': '0x00000000'}
    try:
        colorstr = colors.get(colorstr.capitalize(), colorstr).lower()
    except:
        sys.exc_clear()
        return colorstr

    if colorstr.startswith('#'):
        colorstr = colorstr.replace('#', '0x')
    r, g, b, a = (0.0, 255.0, 0.0, 255.0)
    if colorstr.startswith('0x'):
        try:
            if len(colorstr) == 8:
                r = eval('0x' + colorstr[2:4])
                g = eval('0x' + colorstr[4:6])
                b = eval('0x' + colorstr[6:8])
            elif len(colorstr) == 10:
                a = eval('0x' + colorstr[2:4])
                r = eval('0x' + colorstr[4:6])
                g = eval('0x' + colorstr[6:8])
                b = eval('0x' + colorstr[8:10])
            else:
                log.warning('Invalid color string, has to be in form of 0xffffff or 0xffffffff (with alpha). 0x can be replaced with # (%s)' % colorstr)
                if error:
                    return
        except:
            log.warning('Invalid color string, has to be in form of 0xffffff or 0xffffffff (with alpha). 0x can be replaced with # (%s)' % colorstr)
            if error:
                return

    else:
        log.error('Unknown color (' + colorstr + '), I only know: ' + strx(', '.join(colors.keys())))
        if error:
            return
    col = (r / 255.0,
     g / 255.0,
     b / 255.0,
     a / 255.0)
    if asTuple:
        return col
    import trinity
    return trinity.TriColor(*col)


def ParanoidDecoMethod(fn, attrs):
    check = []
    if attrs is None:
        check = ['sr']
    else:
        check.extend(attrs)

    @wraps(fn)
    def deco(self, *args, **kw):
        if GetAttrs(self, *check) is None:
            return
        if self.destroyed:
            return
        return fn(self, *args, **kw)

    return deco


def NiceFilter(func, list):
    ret = []
    for x in list:
        if func(x):
            ret.append(x)
        blue.pyos.BeNice()

    return ret


def divide_evenly(value, index, total_count):
    remainder = value % total_count
    fraction = remainder / float(total_count)
    if (index + 1) / float(total_count) > fraction:
        return int(mathext.floor(value / float(total_count)))
    else:
        return int(mathext.ceil(value / float(total_count)))
