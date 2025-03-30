#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewShipLabelObject.py
from eve.client.script.ui.inflight.overview.overviewConst import LABEL_STATE, PRE, LABEL_TYPE, POST, LABEL_BOLD, LABEL_UNDERLINE, LABEL_COLOR, LABEL_SIZE, LABEL_ITALIC

class ShipLabel(object):

    def __init__(self, onState = None, preText = None, labelType = None, postText = None, bold = False, italic = False, underline = False, color = None, fontsize = None):
        self.onState = onState
        self.preText = preText
        self.labelType = labelType
        self.postText = postText
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.color = color
        self.fontsize = fontsize

    def GetDict(self):
        return {LABEL_STATE: self.onState,
         PRE: self.preText,
         LABEL_TYPE: self.labelType,
         POST: self.postText,
         LABEL_BOLD: self.bold,
         LABEL_ITALIC: self.italic,
         LABEL_UNDERLINE: self.underline,
         LABEL_COLOR: self.color,
         LABEL_SIZE: self.fontsize}
