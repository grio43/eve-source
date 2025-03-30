#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\writebuffer.py
__all__ = ['WriteBuffer']

class WriteBuffer:

    def __init__(self):
        self.buffer = ''

    def write(self, text):
        self.buffer += text
