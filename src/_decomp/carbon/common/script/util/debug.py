#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\debug.py
import pdb
import sys

def startDebugging():
    pdb.post_mortem(sys.exc_info()[2])
