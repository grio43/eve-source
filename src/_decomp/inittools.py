#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\inittools.py
import blue
import bluepy
import logmodule
import os
import site
import sys
import traceback
import platform

def gettool():
    args = blue.pyos.GetArg()[1:]
    for each in iter(args):
        split = each.split('=')
        if split[0].strip() == '/tools' and len(split) > 1:
            tool = split[1].strip()
            return tool


def run_(tool):
    isWin32 = blue.sysinfo.processBitCount == 32
    isOSX = platform.system().lower() == 'darwin'
    join = os.path.join
    binstr = 'win32' if isWin32 else 'x64'
    carbonTools = blue.paths.ResolvePath(u'root:/../carbon/tools')
    platformTools = blue.paths.ResolvePath(u'root:/../platformtools')
    site.addsitedir(blue.paths.ResolvePath(u'root:/../packages'))
    sys.path.append(blue.paths.ResolvePath(u'root:/..'))
    eveTools = blue.paths.ResolvePath(u'root:/tools')
    carbonToolsLib = os.path.join(carbonTools, 'lib')
    sys.path.append(carbonToolsLib)
    if isOSX:
        sys.path.append(join(platformTools, 'external', 'macOS', binstr, 'AppleClang'))
    else:
        sys.path.append(join(platformTools, 'external', binstr))

    def execIfExists(toolPath):
        path = '%s/startup/%s.py' % (toolPath, tool)
        if os.path.exists(path):
            _ExecScript(path, tool)
            return True
        return False

    if os.path.exists(tool):
        _ExecScript(tool, tool)
    elif execIfExists(eveTools):
        pass
    elif execIfExists(carbonTools):
        pass
    elif execIfExists(platformTools):
        pass
    else:
        errStr = 'The following file was not found on your machine: /tools/startup/%s.py' % tool
        _LogAndTerm(errStr, tool)


def _LogAndTerm(errstr, tool):
    silent = '/silent' in blue.pyos.GetArg()
    if not silent:
        blue.os.ShowErrorMessageBox('Failed to initialize %s' % tool, errstr)
        bluepy.Terminate(1, errstr)


def _ExecScript(path, tool):
    try:
        rf = blue.classes.CreateInstance('blue.ResFile')
        rf.OpenAlways(path)
        try:
            data = rf.Read()
        finally:
            rf.Close()

        data = data.replace('\r\n', '\n')
        codeObject = compile(data, path, 'exec')
        eval(codeObject, globals())
        runFunc = globals().get('run', None)
        if runFunc is not None:
            runFunc()
    except Exception as e:
        traceback.print_exc()
        logmodule.LogException()
        _LogAndTerm(str(e), tool)
