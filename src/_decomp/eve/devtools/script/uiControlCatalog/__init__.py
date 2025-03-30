#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\__init__.py
import inspect
import pkgutil
import os
import imp

def Test():
    path = os.path.dirname(__file__) + '/controls'
    ret = walk_modules(path)
    print 'RETURNING', ret
    return ret


def walk_modules(path):
    for module_loader, name, ispkg in pkgutil.iter_modules([path]):
        print name, ispkg
        if ispkg:
            return walk_modules(path + '/' + name)
        module = get_module(module_loader, name)
        print module.__file__
        for n, val in inspect.getmembers(module):
            if n == 'CLASS':
                print 'YES', val


def get_module(module_loader, name):
    module_path = module_loader.path + '/%s.py' % name
    module = imp.load_source(name, module_path)
    return module


if __name__ == '__main__':
    Test()
