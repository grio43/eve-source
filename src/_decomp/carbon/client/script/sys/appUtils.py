#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\client\script\sys\appUtils.py
import blue
import carbon.client.script.util.lg as lg
import bluepy
from eveprefs import prefs

def CanReboot():
    for arg in blue.pyos.GetArg()[1:]:
        if arg.startswith('/ssoToken'):
            return False

    return True


def Reboot(reason = ''):
    if not CanReboot():
        lg.Info('appUtils.Reboot', 'suppressing reboot due to single sign-on')
        lg.Info('appUtils.Reboot', 'rebooting due to ' + reason)
        bluepy.Terminate(0, reason)
    lg.Info('appUtils.Reboot', 'About to reboot the client because:' + reason)
    prefs.SetValue('rebootReason', reason)
    prefs.SetValue('rebootTime', blue.os.GetWallclockTime())
    allargs = blue.pyos.GetArg()
    cmd = allargs[0]
    args = []
    for arg in allargs[1:]:
        arg = arg.strip()
        if arg.find(' ') >= 0 or arg.find('\t') >= 0:
            arg = '"""' + arg + '"""'
        args.append(arg)

    args = ' '.join(args)
    lg.Info('appUtils.Reboot', 'About to reboot the client with:' + str((0,
     None,
     cmd,
     args)))
    try:
        blue.os.ShellExecute(cmd, args)
    except Exception as e:
        lg.Error('appUtils.Reboot', 'Failed with: ' + str(e))
        raise

    bluepy.Terminate(0, reason)


exports = {'appUtils.Reboot': Reboot}
