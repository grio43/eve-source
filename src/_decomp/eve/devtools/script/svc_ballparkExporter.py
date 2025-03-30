#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_ballparkExporter.py
import urllib
import urllib2
import blue
import evetypes
import uthread
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from carbonui.control.window import Window

class BallparkExporter(Window):
    __guid__ = 'form.BallparkExporter'
    default_windowID = 'BallparkExporter'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption('Ballpark exporter')
        self.SetMinSize([360, 150])
        self.MakeUnResizeable()
        self.mainCont = Container(parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 110), padding=(5, 5, 5, 5))
        self.exportUrlEdit = SingleLineEditText(parent=self.mainCont, align=uiconst.TOTOP, top=15, label='Export URL:', setvalue=settings.user.ui.Get('ballparkExporterUrl'), readonly=True)
        buttonCont = Container(parent=self.mainCont, align=uiconst.TOTOP, pos=(0, 10, 0, 30), name='buttonCont')
        Button(parent=buttonCont, align=uiconst.TOLEFT, label='Start', func=self.StartExport)
        Button(parent=buttonCont, align=uiconst.TOLEFT, label='Stop', func=self.StopExport)
        self.statusLabel = eveLabel.Label(parent=self.mainCont, align=uiconst.TOTOP, top=10, text='', state=uiconst.UI_NORMAL)

    def StartExport(self, *args):
        url = self.exportUrlEdit.GetText()
        if url:
            settings.user.ui.Set('ballparkExporterUrl', url)
            sm.GetService('ballparkExporter').StartExport(url)

    def StopExport(self, *args):
        sm.GetService('ballparkExporter').StopExport()

    def UpdateState(self, state):
        self.statusLabel.SetText(state)


class BallparkExporterSvc(Service):
    __guid__ = 'svc.ballparkExporter'

    def Run(self, *args):
        self.exportActive = False

    def Show(self):
        BallparkExporter.Open()

    def UpdateState(self, state):
        wnd = BallparkExporter.GetIfOpen()
        if wnd:
            wnd.UpdateState(state)

    def StartExport(self, url):
        if not self.exportActive:
            self.exportActive = True
            uthread.new(self.ExportTask, url)

    def StopExport(self):
        self.exportActive = False

    def ExportTask(self, url):
        try:
            self.UpdateState('Exporter loop starting')
            bp = sm.GetService('michelle').GetBallpark()
            self.exportCategories = (6, 18)
            self.exportGroups = (12, 186)
            lastTime = -1
            while self.exportActive:
                if lastTime != bp.currentTime:
                    lastTime = bp.currentTime
                    self.ExportToUrl(bp, url)
                blue.pyos.synchro.SleepSim(300)

            self.UpdateState('Export stopped')
        except Exception as e:
            self.UpdateState('<color=red>Something went wrong! %s' % e)
        finally:
            self.exportActive = False

    def ExportToUrl(self, bp, url):
        url = str(url)
        self.UpdateState('<color=green>Exporting frame %d to %s' % (bp.currentTime, url))
        data = urllib.urlencode({'data': self.DumpToString(bp)})
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        result = response.read()

    def DumpToString(self, ballpark):
        str_list = []
        str_list.append('%d\n' % ballpark.currentTime)
        egoball = ballpark.GetBall(ballpark.ego)
        str_list.append('%f,%f,%f\n' % (egoball.x, egoball.y, egoball.z))
        for ball, slim in ballpark.GetBallsAndItems():
            if slim.categoryID in self.exportCategories or slim.groupID in self.exportGroups:
                str_list.append('%d,%f,%f,%f,%f,%f,%f,' % (ball.id,
                 ball.x,
                 ball.y,
                 ball.z,
                 ball.vx,
                 ball.vy,
                 ball.vz))
                str_list.append('%d,%s,' % (slim.ownerID, cfg.eveowners.Get(slim.ownerID).ownerName))
                str_list.append('%d,%s,' % (slim.typeID, evetypes.GetName(slim.typeID)))
                str_list.append('%d,%s,' % (slim.groupID, evetypes.GetGroupNameByGroup(slim.groupID)))
                str_list.append('%d,%s,' % (slim.categoryID, evetypes.GetCategoryNameByCategory(slim.categoryID)))
                if slim.corpID:
                    str_list.append('%d,%s,%s,' % (slim.corpID, cfg.eveowners.Get(slim.corpID).ownerName, cfg.corptickernames.Get(slim.corpID).tickerName))
                else:
                    str_list.append('0,0,0,')
                if slim.allianceID:
                    str_list.append('%d,%s,%s,' % (slim.allianceID, cfg.eveowners.Get(slim.allianceID).ownerName, cfg.allianceshortnames.Get(slim.allianceID).shortName))
                else:
                    str_list.append('0,0,0,')
                str_list.append('\n')

        return ''.join(str_list)
