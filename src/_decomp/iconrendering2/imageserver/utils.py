#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\imageserver\utils.py
import os
import shutil
import json

def CopyFile(src, dst):
    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))
    shutil.copyfile(src, dst)


def GetFolder(root, name):
    folder = os.path.join(root, name)
    if not os.path.exists(folder):
        os.mkdir(folder)
    return folder


def ReadMapping(folder, name):
    path = os.path.join(folder, '%s.json' % name)
    with open(path, 'r') as fp:
        return json.load(fp)


def WriteMapping(mapping, folder, name):
    path = os.path.join(folder, '%s.json' % name)
    with open(path, 'w') as fp:
        json.dump(mapping, fp)
    return path
