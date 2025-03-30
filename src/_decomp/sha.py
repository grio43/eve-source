#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\sha.py
import warnings
warnings.warn('the sha module is deprecated; use the hashlib module instead', DeprecationWarning, 2)
from hashlib import sha1 as sha
new = sha
blocksize = 1
digest_size = 20
digestsize = 20
