#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireTechnologyViews\propagandaView.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import StreamingVideoSprite
from eve.common.lib import appConst
from charactercreator.client import scalingUtils
import uthread2
SECONDS_TO_WAIT_AFTER_VIDEO_FINISHES = 1.0
PROPAGANDA_RES_PATHS = {appConst.raceCaldari: 'res:/video/charactercreation/caldari.webm',
 appConst.raceMinmatar: 'res:/video/charactercreation/minmatar.webm',
 appConst.raceAmarr: 'res:/video/charactercreation/amarr.webm',
 appConst.raceGallente: 'res:/video/charactercreation/gallente.webm'}

class PropagandaView(Container):

    def AdvanceToNextView(self):
        uthread2.call_after_wallclocktime_delay(self.parent.SetTechAuto, SECONDS_TO_WAIT_AFTER_VIDEO_FINISHES, techOrder=self.parent.techOrder + 1)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.raceID = attributes.Get('raceID', None)
        videoPath = PROPAGANDA_RES_PATHS.get(self.raceID, '')
        padding = scalingUtils.GetTopNavHeight()
        self.movie = StreamingVideoSprite(parent=self, align=uiconst.TOALL, videoPath=videoPath, videoAutoPlay=True, padding=(padding,
         padding,
         padding,
         padding))
        self.movie.OnVideoFinished = self.AdvanceToNextView
