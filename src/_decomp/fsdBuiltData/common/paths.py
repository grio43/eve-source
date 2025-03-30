#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\paths.py
try:
    import blue
except ImportError:
    blue = None

def resolve_path(res_path):
    return blue.paths.ResolvePath(res_path)


def get_file_contents_with_yield(path):
    return blue.paths.GetFileContentsWithYield(path)
