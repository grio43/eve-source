#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\xmppchannelmenu.py
import logging
import localization
from menu import MenuLabel
from carbonui import uiconst
from eve.client.script.ui.util.uix import HybridWnd
from eveservices.menu import GetMenuService
from eveservices.xmppchat import GetChatService
logger = logging.getLogger(__name__)

class XmppChannelMenu(list):

    def __init__(self, channelID, charID):
        self.channelID = channelID
        self.charID = charID
        commands = []
        if charID != const.ownerSystem and GetChatService().IsOperator(channelID, session.charid):
            if not GetChatService().IsOperator(channelID, charID):
                if GetChatService().IsMuted(channelID, charID):
                    commands.append((MenuLabel('UI/Chat/Unmute'), self._Unmute))
                else:
                    commands.append((MenuLabel('UI/Chat/Mute'), self._Mute))
                commands.append((MenuLabel('UI/Chat/Kick'), self._Kick))
        if charID != session.charid:
            self.append((MenuLabel('UI/Chat/ReportIskSpammer'), self.ReportISKSpammer))
        if commands:
            self.append((MenuLabel('UI/Chat/Channel'), commands))

    def ReportISKSpammer(self, *args):
        sm.GetService('chat').report_isk_spammer(self.charID, self.channelID)

    def _Mute(self, *args):
        format = []
        format.append({'type': 'bbline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'edit',
         'key': 'minutes',
         'setvalue': 30,
         'label': localization.GetByLabel('UI/Chat/LengthMinutes'),
         'frame': 1,
         'maxLength': 5,
         'intonly': [0, 43200]})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'textedit',
         'key': 'reason',
         'label': localization.GetByLabel('UI/Chat/Reason'),
         'frame': 1,
         'maxLength': 255})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        retval = HybridWnd(format, caption=localization.GetByLabel('UI/Chat/GagCharacter', char=self.charID), windowID='muteCharacterInChat', modal=1, buttons=uiconst.OKCANCEL, minW=300, minH=160)
        if retval is not None:
            if retval['minutes']:
                durationInSecs = retval['minutes'] * 60
            else:
                durationInSecs = None
            GetChatService().MuteUser(self.channelID, self.charID, retval['reason'], durationInSecs)

    def _Unmute(self, *args):
        GetChatService().UnmuteUser(self.channelID, self.charID)

    def _Kick(self, *args):
        format = []
        format.append({'type': 'bbline'})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'edit',
         'key': 'minutes',
         'setvalue': 30,
         'label': localization.GetByLabel('UI/Chat/LengthMinutes'),
         'frame': 1,
         'maxLength': 5,
         'intonly': [0, 43200]})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'textedit',
         'key': 'reason',
         'label': localization.GetByLabel('UI/Chat/Reason'),
         'frame': 1,
         'maxLength': 255})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'btline'})
        retval = HybridWnd(format, caption=localization.GetByLabel('UI/Chat/KickCharacter', char=self.charID), windowID='kickCharacterFromChat', modal=1, buttons=uiconst.OKCANCEL, minW=300, minH=160)
        if retval is not None:
            if retval['minutes']:
                durationInSecs = retval['minutes'] * 60
            else:
                durationInSecs = None
            GetChatService().BanUserFromChannel(self.channelID, self.charID, retval['reason'], durationInSecs)
