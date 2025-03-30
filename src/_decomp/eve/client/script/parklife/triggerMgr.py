#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\triggerMgr.py
import localization
from carbon.common.script.sys.service import Service
from eve.common.lib import appConst as const

class Triggers(Service):
    __guid__ = 'svc.trigger'
    __exportedcalls__ = {}
    __notifyevents__ = ['OnDungeonTriggerMessage', 'OnDungeonTriggerAudio']
    __dependencies__ = ['audio']

    def Run(self, memStream = None):
        super(Triggers, self).Run(memStream)
        self.audio = None

    def OnDungeonTriggerMessage(self, messageType, messageID):
        color = self.GetMessageColor(messageType)
        body = localization.GetByMessageID(messageID)
        sm.GetService('chat').add_game_message('<color=%s>%s</color>' % (color, body))

    def OnDungeonTriggerAudio(self, dungeonID, audioUrl):
        if not self.audio:
            self.audio = sm.StartService('audio')
        self.audio.SendUIEvent(audioUrl)

    def GetMessageColor(self, messageType):
        return {const.dunEventMessageMood: '0xffa3fc80',
         const.dunEventMessageStory: '0xffa3fc80',
         const.dunEventMessageMissionInstruction: '0xff48ff00',
         const.dunEventMessageMissionObjective: '0xff48ff00',
         const.dunEventMessageImminentDanger: '0xffff0000',
         const.dunEventMessageEnvironment: '0xffa3fc80',
         const.dunEventMessageNPC: '0xff80d8fc',
         const.dunEventMessageWarning: '0xffffd800'}.get(messageType, '0xffe0e0e0')
