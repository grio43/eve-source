#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\bugReporting.py
import carbonversion
import json
import os
import platform
import subprocess
import utillib
import yaml
import zipfile
import time
from carbon.common.script.sys import basesession
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util import timerstuff
from carbon.common.script.util.format import FmtDate
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.util.various_unsorted import GetWindowAbove
from eve.common.script.sys import eveCfg
from eveexceptions import UserError
from globalConfig.getFunctions import GetBugReportServer
import blue
import carbonversion
import uthread
import log
import trinity
import gatekeeper
import webbrowser
from localization import GetByLabel, GetByMessageID
from eveexceptions.exceptionEater import ExceptionEater
from carbon.common.lib.serverInfo import GetServerInfo
from shipfitting.exportFittingUtil import GetFittingEFTString
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.desktop import UIRoot
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall, Label
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.common.lib import appConst as const
from bugreporter import BugReporter, SendAttachmentError
from eveprefs import prefs, boot
LEFT_ARROW = 'res:/UI/Texture/BugReport_Arrow_Left.png'
RIGHT_ARROW = 'res:/UI/Texture/BugReport_Arrow_Right.png'
COLOR_GREEN = (0.0,
 1.0,
 0.0,
 1.0)
COLOR_RED = (1.0,
 0.0,
 0.0,
 1.0)
COLOR_BLUE = (0.0,
 0.0,
 1.0,
 1.0)
ARROW_HEIGHT = 28
BASEFONTSIZE = 18
NUMFONTSIZE = 26
BUGREPORT_SERVER = 'https://bugsservice.eveonline.com/api'
BUG_REPORTS_URL = 'https://community.eveonline.com/support/bug-reports/my-bug-reports/'
BUG_GUIDE_URL = 'https://community.eveonline.com/support/test-servers/bug-reporting/'
SCREENSHOT_NAME = 'igbr_%s.jpg'
NUM_SCREENSHOTS = 3
SAVE_NAME = 'igbr_save_%s.yaml'

def HIWORD(f):
    return (f & 4294901760L) >> 16


def LOWORD(f):
    return f & 65535


def HIPART(f):
    return (f & 18446744069414584320L) >> 32


def LOPART(f):
    return f & 4294967295L


def DecodeDriverVersion(version):
    try:
        highpart = HIPART(version)
        lowpart = LOPART(version)
        product = HIWORD(highpart)
        version = LOWORD(highpart)
        subVersion = HIWORD(lowpart)
        build = LOWORD(lowpart)
        return '%s.%s.%s.%s' % (product,
         version,
         subVersion,
         build)
    except:
        return ''


def AbsPath(path):
    return blue.paths.ResolvePathForWriting(path)


class BugReportingService(Service):
    __guid__ = 'svc.bugReporting'
    __startupdependencies__ = ['machoNet']

    def __init__(self):
        super(BugReportingService, self).__init__()
        self.dxDiagFileName = None
        self.categories = None
        self.startStages = None
        self.fixInStages = None
        self.assignees = None
        self.priorities = None
        self.severities = None
        self.serverUrl = ''
        self.windowsUserName = ''
        self.charName = ''
        self.userName = ''
        self.bugReportServer = None
        self.screenshots = []
        self.wnd = None
        self.categories = None

    def StartCreateBugReport(self):
        self.OpenWindow()

    def OpenWindow(self):
        self.Init()
        self.wnd = BugReportingWindow.Open()

    def Init(self):
        self.screenshots = []
        self.bugReportServer = GetBugReportServer(self.machoNet, BUGREPORT_SERVER)
        self.bugReporter = BugReporter(self.bugReportServer, os.path.join(blue.paths.ResolvePath('cache:'), 'IGBR'))
        self.LogNotice('Opening bug reporting', self.userName, self.charName)
        if session.charid:
            self.charName = cfg.eveowners.Get(session.charid).name
        self.userName = settings.public.ui.Get('username', '')
        try:
            self.windowsUserName = os.environ.get('USERNAME')
        except:
            self.LogError('Unable to get windows username from environment')

        self.collectedData = None
        self.collectedFiles = None
        self.outputFolder = ''
        self.settingsFolder = 'settings:/../../'
        self.outputFolder = self.settingsFolder + u'IGBR/'
        try:
            os.mkdir(AbsPath(self.outputFolder))
        except:
            pass

        if self.dxDiagFileName is None:
            self.dxDiagFileName = AbsPath(self.outputFolder + 'dxdiag.txt')
            try:
                os.remove(self.dxDiagFileName)
            except OSError:
                pass

            try:
                self.LogInfo('Getting DXDiag info...')
                subprocess.Popen(['dxdiag.exe', '/t', self.dxDiagFileName])
            except:
                self.dxDiagFileName = None

    def SaveToDisk(self, data):
        data['screenshots'] = self.screenshots
        f = open(AbsPath(self.outputFolder + self.GetSaveName()), 'w')
        yaml.safe_dump(data, f)
        f.close()

    def GetSaveName(self):
        name = SAVE_NAME
        name = name % 'br'
        return name

    def LoadFromDisk(self):
        path = AbsPath(self.outputFolder + self.GetSaveName())
        self.LogInfo('Loading data from disk', path)
        try:
            f = open(path, 'r')
        except:
            raise UserError('CustomInfo', {'info': 'No saved data found.'})

        data = yaml.safe_load(f)
        f.close()
        self.screenshots = data.get('screenshots', [])
        return data

    def CollectData(self):
        serverInfo = GetServerInfo()
        serverVersion, serverBuild = sm.RemoteSvc('cache').GetServerVersionAndBuild()
        collectedData = {'title': None,
         'description': None,
         'reproSteps': None,
         'session': str(session),
         'clientDateTime': FmtDate(blue.os.GetWallclockTime()),
         'clientVersion': boot.keyval['version'].split('=', 1)[1],
         'clientBuild': boot.build,
         'clientBranch': boot.branch,
         'serverName': serverInfo.name,
         'serverVersion': serverVersion,
         'serverBuild': serverBuild,
         'serverEspUrl': serverInfo.espUrl,
         'memoryFree': blue.sysinfo.GetMemory().availablePhysical / 1024}
        bitCount = blue.sysinfo.cpu.bitCount
        adapters = trinity.adapters
        ident = adapters.GetAdapterInfo(trinity.mainWindow.GetWindowState().adapter)
        driverVersion = DecodeDriverVersion(ident.driverVersion)
        computerInfo = {'memoryPhysical': blue.sysinfo.GetMemory().totalPhysical / 1024,
         'cpuArchitecture': blue.sysinfo.cpu.architecture,
         'cpuIdentifier': blue.sysinfo.cpu.identifier,
         'cpuLevel': blue.sysinfo.cpu.family,
         'cpuRevision': blue.sysinfo.cpu.revision,
         'cpuCount': blue.sysinfo.cpu.logicalCpuCount,
         'cpuMHz': blue.sysinfo.cpu.frequency,
         'cpuBitCount': bitCount,
         'osMajorVersion': blue.sysinfo.os.majorVersion,
         'osMinorVersion': blue.sysinfo.os.minorVersion,
         'osBuild': blue.sysinfo.os.buildNumber,
         'osPatch': blue.sysinfo.os.patch,
         'osPlatform': 2,
         'videoCardAdapter': ident.description.encode('ascii', 'ignore'),
         'videoCardIdentifier': ident.deviceIdentifier[1:-1],
         'videoDriverVersion': driverVersion,
         'clientBitCount': blue.sysinfo.processBitCount}
        try:
            driverInfo = ident.GetDriverInfo()
            computerInfo['videoDriverVersion'] = driverInfo.driverVersionString
            computerInfo['videoDriverDate'] = driverInfo.driverDate
            computerInfo['videoDriverVendor'] = driverInfo.driverVendor
            computerInfo['videoIsOptimus'] = 'Yes' if driverInfo.isOptimus else 'No'
            computerInfo['videoIsAmdDynamicSwitchable'] = 'Yes' if driverInfo.isAmdDynamicSwitchable else 'No'
        except RuntimeError:
            pass

        collectedData.update({'computerInfo': computerInfo})
        collectedFiles = self.GetAttachments()
        self.collectedData = utillib.KeyVal(data=collectedData, files=collectedFiles)
        return self.collectedData

    def GetScreenshotPath(self, n):
        if n is not None and n < len(self.screenshots):
            fileName = self.screenshots[n]
        else:
            fileName = self.outputFolder + SCREENSHOT_NAME % blue.os.GetTime()
        return fileName

    def GetScreenshot(self, n = None):
        if n > NUM_SCREENSHOTS - 1 or n is None and len(self.screenshots) >= NUM_SCREENSHOTS:
            raise UserError('CustomInfo', {'info': 'You have reached the maximum number of screenshots. Please delete a screenshot before grabbing abother one.'})
        fileName = self.GetScreenshotPath(n)
        self.LogInfo('Getting screenshot number', n, 'to', fileName, '...')
        self.wnd.HideAll()
        blue.pyos.synchro.SleepWallclock(300)
        trinity.SaveRenderTarget(AbsPath(fileName))
        if n is not None and n < len(self.screenshots):
            self.screenshots[n] = fileName
        else:
            n = len(self.screenshots)
            self.screenshots.append(fileName)
        self.LogInfo('Screenshot has been captured. I now have', len(self.screenshots), 'screenshots')
        self.wnd.Show()
        self.wnd.DoEditScreenshot(n)
        self.wnd.UpdateScreenshotButtons()

    def DeleteScreenshot(self, n):
        fileName = self.screenshots[n]
        del self.screenshots[n]
        try:
            os.remove(fileName)
        except OSError:
            pass

        self.wnd.UpdateScreenshotButtons()

    def GetAttachments(self):
        self.LogInfo('Getting Attachments...')
        files = []
        screenShots = []
        ret = []
        try:
            data = sm.GetService('monitor').GetInMemoryLogs()
            logs = ('logs.txt', data)
            files.append(logs)
            if len(data) > 250:
                ret += [logs]
        except:
            log.LogException('Error getting logs for bug reporting. Skipping.')

        for i, fileName in enumerate(self.screenshots):
            try:
                with open(AbsPath(fileName), 'rb') as ssfile:
                    data = ssfile.read()
            except IOError:
                data = ''

            f = (SCREENSHOT_NAME % i, data)
            screenShots.append(f)

        self._AppendProcessHealth(files)
        self._AppendMethodCalls(files)
        self._AppendOutstandingCalls(files)
        self._AppendShipFitting(files)
        self._AppendLatestCrashes(files)
        self._AppendPrefsIni(files)
        self._AppendSettings(files)
        self._AppendDxdiag(files)
        self._AppendPDMData(files)
        self._AppendCarbonInfo(files)
        ZIP_FILENAME = 'igbr.zip'
        zipName = AbsPath(self.outputFolder + ZIP_FILENAME)
        with zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED) as zipDataFile:
            for fileName, data in files:
                if not fileName.lower().endswith('.jpg'):
                    zipDataFile.writestr(fileName, data)

        zipData = open(zipName, 'rb').read()
        self.LogInfo('Done Getting Attachments!')
        ret += screenShots
        ret += [(ZIP_FILENAME, zipData)]
        return ret

    def _AppendProcessHealth(self, files):
        try:
            processHealthSvc = sm.GetService('processHealth')
            data = processHealthSvc.GetAllLogs()
            files.append(('processHealth.txt', data))
        except:
            log.LogException('Error getting processhealth data for bug reporting. Skipping.')

    def _AppendMethodCalls(self, files):
        try:
            data = sm.GetService('monitor').GetMethodCalls()
            files.append(('methodcalls.txt', data))
        except:
            log.LogException('Error getting method call timers for bug reporting. Skipping.')

    def _AppendOutstandingCalls(self, files):
        try:
            data = '\n'.join(('%s - %s' % (FmtDate(t), n) for n, t in basesession.outstandingCallTimers))
            files.append(('outstandingcalls.txt', data))
        except Exception:
            log.LogException('Failed to get outstanding calls')

    def _AppendShipFitting(self, files):
        try:
            fittingSvc = sm.GetService('fittingSvc')
            fitting = utillib.KeyVal()
            fitting.shipTypeID, fitting.fitData, _ = fittingSvc.GetFittingDictForActiveShip()
            fitting.name = cfg.evelocations.Get(eveCfg.GetActiveShip()).locationName
            data = GetFittingEFTString(fitting).encode('utf-8')
            files.append(('fitting.txt', data))
        except Exception:
            log.LogException('Failed to get ship fitting')

    def _AppendLatestCrashes(self, files):
        try:
            if platform.system() == 'Darwin':
                crash_folder = os.path.join(blue.sysinfo.GetUserApplicationDataDirectory(), 'CCP', 'EVE', 'completed')
            else:
                crash_folder = os.path.join(blue.sysinfo.GetUserApplicationDataDirectory(), 'CCP', 'EVE', 'reports')
            crashes = [ (os.path.splitext(i)[0], os.path.getmtime(os.path.join(crash_folder, i))) for i in os.listdir(crash_folder) if i.lower().endswith('.dmp') ]
        except StandardError:
            return

        crashes.sort(key=lambda x: x[1], reverse=True)
        data = '\n'.join(('%s - %s' % (time.strftime('%Y-%m-%d %H:%M', time.gmtime(date)), crash) for crash, date in crashes[:10]))
        files.append(('lastcrashes.txt', data))

    def _AppendPrefsIni(self, files):
        try:
            f = open(prefs.ini.filename, 'rb')
            data = f.read()
            f.close()
            files.append((os.path.basename(prefs.ini.filename), data))
        except:
            log.LogException('Error getting prefs for bug reporting. Skipping.')

    def _AppendSettings(self, files):
        allSettings = {}
        try:
            for settingsType in ('public', 'user', 'char'):
                allSettings[settingsType] = getattr(settings, settingsType).datastore

            data = yaml.dump(allSettings)
            files.append(('settings.yaml', data))
        except:
            log.LogException('Error getting settings for bug reporting. Skipping.')

    def _AppendDxdiag(self, files):
        try:
            if self.dxDiagFileName:
                i = 0
                data = ''
                while i < 30:
                    try:
                        f = open(self.dxDiagFileName, 'r')
                        data = f.read()
                        f.close()
                        if len(data) == 0:
                            raise IOError
                        break
                    except IOError:
                        i += 1
                        blue.pyos.synchro.SleepWallclock(1000)

                else:
                    self.LogError('Failed to get DXDiag file after 30 seconds', self.dxDiagFileName)
                    self.dxDiagFileName = None

                files.append(('dxdiag.txt', data))
        except:
            log.LogException('Error getting DxDiag for bug reporting. Skipping.')

    def _AppendPDMData(self, files):
        try:
            files.append(('PDMData.txt', blue.sysinfo.GetPDMData().encode('utf-8')))
        except:
            log.LogException('Error getting PDM data for bug reporting. Skipping.')

    def _AppendCarbonInfo(self, files):
        try:
            data = json.dumps(carbonversion.get_carbon_version().get_json_data())
            files.append(('carbon.json', data))
        except:
            log.LogException('Error getting carbon info for bug reporting. Skipping.')

    def GetLabelsForIssue(self, categoryID):
        ret = []
        categoryName = self.GetCategoryName(categoryID).lower()
        language = {'DE': 'German',
         'EN': None,
         'ES': 'Spanish',
         'FR': 'French',
         'JA': 'Japanese',
         'KO': 'Korean',
         'RU': 'Russian',
         'ZH': 'Chinese'}.get(session.languageID, None)
        if language is not None:
            ret.append(language)
        if 'graphic' in categoryName:
            ret.append(trinity.platform)
        if blue.sysinfo.isWine:
            if blue.sysinfo.wineHostOs.startswith('Darwin'):
                platformLabel = 'PlatformMacWine'
            else:
                platformLabel = 'PlatformLinuxWine'
            ret.append(blue.sysinfo.wineVersion)
        elif platform.system() == 'Darwin':
            platformLabel = 'PlatformMac'
        elif platform.system() == 'Windows':
            platformLabel = 'PlatformWin'
            if blue.sysinfo.os.majorVersion == 10 and blue.sysinfo.os.buildNumber >= 22000:
                ret.append('Windows11')
        else:
            platformLabel = 'PlatformUnknown'
        ret.append(platformLabel)
        if blue.sysinfo.computerName == 'GEFORCE-NOW':
            ret.append('GeforceNow')
        if blue.sysinfo.isRosetta:
            ret.append('Rosetta')
        ret.append('IsOmega' if sm.GetService('cloneGradeSvc').IsOmega() else 'IsAlpha')
        return ret

    def SendDefectOrBugReport(self, data):
        ret = self.CollectData()
        computer = self._GetComputerInfo(ret, ret.data['computerInfo'])
        sessionInfo = self._GetSessionInfo(self._GetEspUrl(ret))
        data['ServerName'] = ret.data['serverName']
        try:
            data['Title'] = data['Title'].encode('UTF-8')
            data['Description'] = data['Description'].encode('UTF-8')
            data['ReproductionSteps'] = data['ReproductionSteps'].encode('UTF-8')
        except Exception:
            self.LogError('For some reason I do not particularly care about failing to encode title, description or reproductionSteps')

        category = data['Category']
        labels = self.GetLabelsForIssue(category)
        return self.bugReporter.SendBugReport(category, data['Title'], data['Description'], data['ReproductionSteps'], sessionInfo, computer, session.userid, labels, ret.data['serverName'], GetServerVersion(ret.data['serverBuild'], ret.data['serverVersion']), ret.files)

    def _GetComputerInfo(self, ret, computerInfo):
        computer = 'Trinity platform: %(triPlatform)s\r\nProcess: %(bits)s\r\nOS: %(os)s.%(osminor)s, build: %(build)s, %(servicepack)s\r\nVideo Card: %(videocard)s (Driver: %(driverversion)s, Released: %(driverdate)s)\r\nIs Optimus: %(isoptimus)s\r\nIs AMD Dynamic Switchable: %(isamddynamicswitchable)s\r\nCPU: %(cpu)s @ %(ghz).2f GHz (%(numcpu)s CPUs)\r\nMemory: %(mem)s MB (%(memfree)s MB available)' % {'triPlatform': trinity.platform,
         'os': computerInfo.get('osMajorVersion', '-'),
         'osminor': computerInfo.get('osMinorVersion', '-'),
         'build': computerInfo.get('osBuild', '-'),
         'servicepack': computerInfo.get('osPatch', '-'),
         'videocard': computerInfo.get('videoCardAdapter', '-'),
         'driverversion': computerInfo.get('videoDriverVersion', '-'),
         'driverdate': computerInfo.get('videoDriverDate', '-'),
         'drivervendor': computerInfo.get('videoDriverVendor', '-'),
         'isoptimus': computerInfo.get('videoIsOptimus', '-'),
         'isamddynamicswitchable': computerInfo.get('videoIsAmdDynamicSwitchable', '-'),
         'cpu': computerInfo.get('cpuIdentifier', '-'),
         'ghz': int(computerInfo.get('cpuMHz', 0)) / 1000.0,
         'numcpu': computerInfo.get('cpuCount', '-'),
         'mem': int(computerInfo.get('memoryPhysical', 0)) / 1024,
         'memfree': int(ret.data.get('memoryFree', 0)) / 1024,
         'bits': 'x%s' % computerInfo.get('clientBitCount', 32)}
        return computer

    def _GetSessionInfo(self, espUrl):
        sessionInfo = ['Character: {charname} ({charid})'.format(charname=self.charName, charid=session.charid), 'Solar System: {solarsystemname} ({solarsystemid})'.format(solarsystemname=GetByMessageID(cfg.evelocations.Get(session.solarsystemid2).locationNameID, languageID='en-us'), solarsystemid=session.solarsystemid2)]
        cohorts = []
        with ExceptionEater('Error getting cohorts on bugreport generation'):
            cohorts = gatekeeper.character.GetCohorts()
        if len(cohorts) > 0:
            sessionInfo.append('Cohort IDs: {cohorts}'.format(cohorts=', '.join(map(str, cohorts))))
        if len(espUrl) > 0:
            sessionInfo.append(espUrl)
        return '\n'.join(sessionInfo)

    def _GetEspUrl(self, ret):
        espUrl = ''
        if session.role & ROLE_GML > 0:
            espUrl = 'ESP: http://%(serverEspUrl)s %(serverName)s' % {'serverName': ret.data['serverName'],
             'serverEspUrl': ret.data['serverEspUrl']}
        return espUrl

    def GetCategories(self):
        if self.categories is None:
            self.categories = self.bugReporter.GetCategories()
        return self.categories[:]

    def GetCategoryName(self, categoryID):
        for name, _categoryID in self.GetCategories():
            if _categoryID == categoryID:
                return name


class BugReportingWindow(Window):
    __guid__ = 'form.BugReportingWindow'
    default_windowID = 'BugReportingWindow'
    default_iconNum = 'res:/UI/Texture/WindowIcons/repairshop.png'
    default_height = 700
    default_minSize = (820, default_height)
    default_captionLabelPath = 'UI/BugReporting/ReportBug'

    def ApplyAttributes(self, attributes):
        self.screenshotWindow = None
        super(BugReportingWindow, self).ApplyAttributes(attributes)
        self.RegisterPositionTraceKeyEvents()
        self.bottomCont = ContainerAutoSize(parent=self.content, align=uiconst.TOBOTTOM, padding=const.defaultPadding)
        self.ConstructTopCont()
        self.ConstructBottomCont()
        self.ConstructMainCont()
        self.service = sm.GetService('bugReporting')
        self.service.Init()
        self.loadingWheel = LoadingWheel(parent=self.sr.maincontainer, align=uiconst.CENTER, width=64, height=64)
        self.content.opacity = 0.0
        uthread.new(self.FinishSettingUp)

    def FinishSettingUp(self):
        if not self.service.bugReporter.IsBugsServiceOnline():
            eve.Message('BugReportServerNotReachable')
            self.Close()
            return
        if self.destroyed:
            return
        self.loadingWheel.Close()
        self.UpdateScreenshotButtons()
        self.PopulateCategoryCombo()
        self.content.opacity = 1.0

    def PopulateCategoryCombo(self):
        categories = self.service.GetCategories()
        initialOption = GetByLabel('UI/BugReporting/SelectCategory')
        categories.insert(0, [initialOption, ''])
        self.categoryCombo.LoadOptions(categories)

    def HideAll(self):
        self.Hide()
        if self.screenshotWindow:
            self.screenshotWindow.Close()

    def GetScreenshot(self, n):
        self.service.GetScreenshot(n)

    def ConstructMainCont(self):
        self.mainCont = Container(name='mainCont', parent=self.content, align=uiconst.TOALL)
        descriptionCont = Container(name='descriptionCont', parent=self.mainCont, align=uiconst.TOTOP_PROP, height=0.5, padBottom=8)
        reproStepsCont = Container(name='reproStepsCont', parent=self.mainCont, align=uiconst.TOALL, padTop=8)
        EveLabelMedium(parent=descriptionCont, align=uiconst.TOTOP, padBottom=4, text=GetByLabel('UI/BugReporting/Description'))
        self.descriptionEdit = EditPlainText(name='descriptionEdit', parent=descriptionCont, align=uiconst.TOALL, hintText=GetByLabel('UI/BugReporting/DescriptionHintText'), setvalue='', maxLength=2900)
        EveLabelMedium(parent=reproStepsCont, align=uiconst.TOTOP, padBottom=4, text=GetByLabel('UI/BugReporting/ReproductionSteps'))
        self.reproStepsEdit = EditPlainText(name='reproStepsEdit', parent=reproStepsCont, align=uiconst.TOALL, hintText=GetByLabel('UI/BugReporting/ReproductionStepsHintText'), setvalue='', maxLength=2900)

    def ConstructTopCont(self):
        top_cont = ContainerAutoSize(name='topCont', parent=self.content, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT, padBottom=16)
        left_grid = LayoutGrid(parent=top_cont, align=uiconst.TOPLEFT, columns=2, cellSpacing=(8, 8))
        self.titleEdit = SingleLineEditText(name='titleEdit', parent=left_grid, align=uiconst.TOPLEFT, width=300, maxLength=250, hintText=GetByLabel('UI/BugReporting/Summary'), hint=GetByLabel('UI/BugReporting/SummaryHint'))
        self.categoryCombo = Combo(name='categoryCombo', parent=left_grid, width=0, options=[])
        self.moreInfoIcon = MoreInfoIcon(name='moreInfo', parent=top_cont, align=uiconst.CENTERRIGHT)
        self.moreInfoIcon.LoadTooltipPanel = self.LoadInfoTooltipPanel

    def ConstructBottomCont(self):
        buttonCont = Container(name='buttonCont', parent=self.bottomCont, align=uiconst.TOTOP, height=Button.default_height, top=16)
        self.btns = ButtonGroup(parent=self.bottomCont, align=uiconst.TOTOP, btns=[(GetByLabel('UI/BugReporting/Send'),
          self.ClickSend,
          (),
          84)], line=1)
        self.editScreenshotButtons = []
        self.takeScreenshotButtons = []
        for i in xrange(NUM_SCREENSHOTS):
            text = GetByLabel('UI/BugReporting/EditScreenshot', screenshotNum=i + 1)
            c = Button(name='editscreenshot_%s' % i, parent=buttonCont, align=uiconst.TOLEFT, left=8 if i > 0 else 0, label=text, func=self.EditScreenshot)
            self.editScreenshotButtons.append(c)

        for i in xrange(NUM_SCREENSHOTS):
            text = GetByLabel('UI/BugReporting/NewScreenshot', screenshotNum=i + 1)
            c = Button(name='newscreenshot_%s' % i, parent=buttonCont, align=uiconst.TOLEFT, left=8 if i > 0 else 0, label=text, func=self.NewScreenshot, hint=GetByLabel('UI/BugReporting/NewScreenshotHint'))
            self.takeScreenshotButtons.append(c)

        self.saveToDiskButton = Button(label=GetByLabel('UI/BugReporting/Save'), parent=buttonCont, func=self.SaveToDisk, align=uiconst.TORIGHT, hint=GetByLabel('UI/BugReporting/SaveHint'))
        self.loadFromDiskButton = Button(parent=buttonCont, align=uiconst.TORIGHT, left=8, label=GetByLabel('UI/BugReporting/Load'), func=self.LoadFromDisk, hint=GetByLabel('UI/BugReporting/LoadHint'))

    def LoadInfoTooltipPanel(self, tooltipPanel, *args):
        tooltipText = GetByLabel('UI/BugReporting/InfoTooltipText', url=BUG_GUIDE_URL)
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=tooltipText, bold=True, state=uiconst.UI_NORMAL, wrapWidth=250)

    def UpdateScreenshotButtons(self):
        for i, c in enumerate(self.editScreenshotButtons):
            c.state = uiconst.UI_HIDDEN

        for i, c in enumerate(self.takeScreenshotButtons):
            c.state = uiconst.UI_HIDDEN

        i = -1
        numScreenshots = len(self.service.screenshots)
        for i in xrange(numScreenshots):
            self.editScreenshotButtons[i].state = uiconst.UI_NORMAL

        if i == -1:
            self.takeScreenshotButtons[0].state = uiconst.UI_NORMAL
        elif i < NUM_SCREENSHOTS - 1:
            self.takeScreenshotButtons[i + 1].state = uiconst.UI_NORMAL

    def EnableSendButton(self, enable):
        try:
            btn = self.btns.GetChild('SEND_Btn')
            if enable:
                btn.Enable()
            else:
                btn.Disable()
        except:
            pass

    def ClickSend(self, *args):
        uthread.new(self.DoClickSend)

    def FormatString(self, txt):
        txt = txt.replace('<br>', '\r\n')
        return txt

    def GetDataFromForm(self):
        title = self.titleEdit.GetValue().strip()
        description = self.descriptionEdit.GetValue(html=0).strip()
        reproSteps = self.reproStepsEdit.GetValue(html=0).strip()
        category = self.categoryCombo.GetValue()
        description = self.FormatString(description)
        reproSteps = self.FormatString(reproSteps)
        data = {'Title': title,
         'Description': description,
         'ReproductionSteps': reproSteps,
         'Category': category}
        return data

    def DoClickSend(self):
        self.EnableSendButton(False)
        data = self.GetDataFromForm()
        if '' in (data['Title'], data['Description'], data['ReproductionSteps']) or not data['Category']:
            self.EnableSendButton(True)
            eve.Message('CustomInfo', {'info': GetByLabel('UI/BugReporting/AllFields')})
            return
        data['ClientBuildNumber'] = boot.build
        if len(self.service.screenshots) == 0:
            ret = eve.Message('CustomQuestion', {'header': GetByLabel('UI/BugReporting/NoScreenshotsHeader'),
             'question': GetByLabel('UI/BugReporting/NoScreenshotsMessage')}, uiconst.YESNO)
            if ret == uiconst.ID_YES:
                self.EnableSendButton(True)
                uthread.new(self.GetScreenshot, None)
                return
            if ret in (uiconst.ID_CANCEL, uiconst.ID_CLOSE):
                self.EnableSendButton(True)
                return
        result = False
        bugreportID = ''
        attachments = False
        self.loadingWheel = LoadingWheel(parent=self.content, align=uiconst.CENTER, width=64, height=64)
        self.mainCont.opacity = 0.3
        try:
            result = self.service.SendDefectOrBugReport(data)
        except SendAttachmentError:
            log.LogException()
            attachments = False
            result = True
        except Exception as e:
            log.LogException()
            self.EnableSendButton(True)
            self.mainCont.opacity = 1.0
            self.loadingWheel.Close()
            eve.Message('CustomInfo', {'info': GetByLabel('UI/BugReporting/SendError', errorMessage=e)})
        else:
            bugreportID = result['key']
            attachments = True

        if result:
            self.Close()
            self.MessageSuccess(attachments, bugreportID)
        else:
            self.EnableSendButton(True)

    def MessageSuccess(self, attachments, bugreportID):
        header = GetByLabel('UI/BugReporting/ReportSentHeader')
        if attachments:
            msg = GetByLabel('UI/BugReporting/ReportSent', bugreportID=bugreportID)
        else:
            msg = GetByLabel('UI/BugReporting/ReportSentAttFail')
        eve.Message('CustomWarning', {'header': header,
         'warning': msg})

    def OpenExternalBugs(self, *args):
        header = GetByLabel('UI/BugReporting/OpenBugsExternalHeader')
        question = GetByLabel('UI/BugReporting/OpenBugsExternal')
        if eve.Message('CustomQuestion', {'header': header,
         'question': question}, uiconst.YESNO, modal=False) == uiconst.ID_YES:
            webbrowser.open_new(BUG_REPORTS_URL)

    def NewScreenshot(self, button):
        n = int(button.name.split('_')[1])
        self.GetScreenshot(n)

    def EditScreenshot(self, button):
        n = int(button.name.split('_')[1])
        self.DoEditScreenshot(n)

    def DoEditScreenshot(self, n):
        self.screenshotWindow = ScreenshotEditingWnd.Open(n=n, service=self.service)

    def ClearLogs(self, *args):
        sm.GetService('monitor').ClearLogInMemory()

    def ViewLogs(self, *args):
        sm.GetService('monitor').ShowLogTab()

    def CopyException(self, *args):
        logs = blue.logInMemory.GetEntries()
        lastException = ''
        for l in logs:
            if 'EXCEPTION END' in l[4]:
                lastException = l[4]
                break

        if len(lastException):
            inf = 'Most recent exception has been copied to the clipboard'
            lastException = lastException.replace('\n', '\r\n')
            lastException = lastException.replace('<', '&lt;')
            blue.pyos.SetClipboardData(lastException)
        else:
            inf = 'No exceptions in the logs'
        eve.Message('CustomNotify', {'notify': inf})

    def SaveToDisk(self, *args):
        data = self.GetDataFromForm()
        self.service.SaveToDisk(data)
        eve.Message('CustomNotify', {'notify': GetByLabel('UI/BugReporting/SavedToDisk')})

    def LoadFromDisk(self, *args):
        ret = eve.Message('CustomQuestion', {'header': GetByLabel('UI/BugReporting/LoadFromDiskHeader'),
         'question': GetByLabel('UI/BugReporting/LoadFromDisk')}, uiconst.YESNO)
        if ret != uiconst.ID_YES:
            return
        data = self.service.LoadFromDisk()
        self.titleEdit.SetValue(data.get('Title', ''))
        self.descriptionEdit.SetValue(data.get('Description', ''))
        self.reproStepsEdit.SetValue(data.get('ReproductionSteps', ''))
        self.categoryCombo.SelectItemByValue(data.get('Category', None))
        self.UpdateScreenshotButtons()

    def RegisterPositionTraceKeyEvents(self):
        self.keyDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYDOWN, self.OnGlobalKeyDownCallback)

    def OnGlobalKeyDownCallback(self, wnd, eventID, (vkey, flag)):
        if self.destroyed:
            return False
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        alt = uicore.uilib.Key(uiconst.VK_MENU)
        p = uicore.uilib.Key(uiconst.VK_P)
        if ctrl and alt and shift and p:
            uthread.new(self.GetScreenshot, None)
        return True


class ScreenshotEditingWnd(Window):
    __guid__ = 'form.ScreenshotEditingWnd'
    default_windowID = 'ScreenshotEditingWnd'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption(GetByLabel('UI/BugReporting/ScreenshotEditor'))
        self.MakeUnstackable()
        self.service = attributes['service']
        self.n = attributes['n']
        self.screenshotPath = sm.GetService('bugReporting').GetScreenshotPath(self.n)
        self.service.LogInfo('Screenshot editing window using screenshot from', self.screenshotPath)
        w = h = 0
        try:
            surface = trinity.Tr2HostBitmap()
            surface.CreateFromFile(self.screenshotPath)
            w, h = surface.width, surface.height
        except:
            log.LogException()

        self.screenshotWidth = w or uicore.desktop.width
        self.screenshotHeight = h or uicore.desktop.height
        self.screenShotScaling = None
        maxWidth = max(self.screenshotWidth / 2, 955)
        self.SetMinSize([maxWidth, self.screenshotHeight / 2])
        topCont = Container(name='topCont', parent=self.content, align=uiconst.TOTOP, height=30, padding=const.defaultPadding)
        self.layoutAreaParent = Container(parent=self.content, padding=10)
        self.layoutAreaParent._OnSizeChange_NoBlock = self.RecalcLayout
        self.layoutArea = Container(parent=self.layoutAreaParent, align=uiconst.CENTER, width=self.screenshotWidth / 4, height=self.screenshotHeight / 4)
        self.overlays = Container(name='overlays', parent=self.layoutArea, align=uiconst.TOALL, clipChildren=True)
        self.screenshotSprite = Sprite(name='screenshotSprite', parent=self.layoutArea, texturePath=self.screenshotPath, align=uiconst.TOALL, padding=0)
        self.screenshotSprite.ReloadTexture()
        Button(label=GetByLabel('UI/BugReporting/ScreenshotSave'), parent=topCont, func=self.SaveScreenshot, left=8, align=uiconst.CENTERRIGHT)
        fb = Button(label=GetByLabel('UI/BugReporting/ScreenshotAddFrame'), func=self.AddFrame, parent=topCont, left=8, align=uiconst.CENTERLEFT)
        cfb = Button(label=GetByLabel('UI/BugReporting/ScreenshotAddCropFrame'), func=self.AddCropFrame, parent=topCont, left=fb.left + fb.width + 8, align=uiconst.CENTERLEFT)
        la = Button(label=GetByLabel('UI/BugReporting/ScreenshotAddLeftArrow'), func=self.AddLeftArrowFrame, parent=topCont, left=cfb.left + cfb.width + 8, align=uiconst.CENTERLEFT)
        ra = Button(label=GetByLabel('UI/BugReporting/ScreenshotAddRightArrow'), func=self.AddRightArrowFrame, parent=topCont, left=la.left + la.width + 8, align=uiconst.CENTERLEFT)
        tc = Button(label=GetByLabel('UI/BugReporting/ScreenshotAddText'), func=self.AddTextFrame, parent=topCont, left=ra.left + ra.width + 8, align=uiconst.CENTERLEFT)
        cb = Button(label=GetByLabel('UI/BugReporting/ScreenshotButtonNew'), func=self.NewScreenshot, parent=topCont, left=tc.left + tc.width + 20, align=uiconst.CENTERLEFT)
        cb = Button(label=GetByLabel('UI/BugReporting/ScreenshotDelete'), func=self.DeleteScreenshot, parent=topCont, left=cb.left + cb.width + 8, align=uiconst.CENTERLEFT)
        self.UpdateLayoutArea()

    def UpdateLayoutArea(self):
        prevScaling = self.screenShotScaling
        areaWidth, areaHeight = self.layoutAreaParent.GetAbsoluteSize()
        xFitScale = areaWidth / float(self.screenshotWidth)
        yFitScale = areaHeight / float(self.screenshotHeight)
        self.screenShotScaling = scaling = min(xFitScale, yFitScale)
        self.layoutArea.width = int(self.screenshotWidth * scaling)
        self.layoutArea.height = int(self.screenshotHeight * scaling)
        if prevScaling and prevScaling != scaling:
            for overlay in self.overlays.children:
                overlay.UpdateProportionalPosition(scaling)

    def NewScreenshot(self, *args):
        self.service.GetScreenshot(self.n)

    def DeleteScreenshot(self, *args):
        self.service.DeleteScreenshot(self.n)
        self.Close()

    def AddTextFrame(self, *args):
        initWidth = int(200 * self.screenShotScaling)
        initHeight = int(32 * self.screenShotScaling)
        initLeft = int(self.screenshotWidth * 0.5 * self.screenShotScaling) - initWidth / 2
        initTop = int(self.screenshotHeight * 0.5 * self.screenShotScaling) - initHeight / 2
        MoveableTextRect(name='Text', parent=self.overlays, pos=(initLeft,
         initTop,
         initWidth,
         initHeight), idx=0, showControls=True, scaling=self.screenShotScaling)

    def AddRightArrowFrame(self, *args):
        initWidth = int(ARROW_HEIGHT * 2 * self.screenShotScaling)
        initHeight = int(ARROW_HEIGHT * self.screenShotScaling)
        initLeft = int(self.screenshotWidth * 0.5 * self.screenShotScaling)
        initTop = int(self.screenshotHeight * 0.5 * self.screenShotScaling)
        container = MoveableRect(name='Arrow', parent=self.overlays, pos=(initLeft,
         initTop,
         initWidth,
         initHeight), showControls=False, idx=0)
        icon = Sprite(label='arrow', parent=container, texturePath=RIGHT_ARROW, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        container.AddColorObject(icon)
        container.ChangeColor(COLOR_GREEN)

    def AddLeftArrowFrame(self, *args):
        initWidth = int(ARROW_HEIGHT * 2 * self.screenShotScaling)
        initHeight = int(ARROW_HEIGHT * self.screenShotScaling)
        initLeft = int(self.screenshotWidth * 0.5 * self.screenShotScaling)
        initTop = int(self.screenshotHeight * 0.5 * self.screenShotScaling)
        container = MoveableRect(name='Arrow', parent=self.overlays, pos=(initLeft,
         initTop,
         initWidth,
         initHeight), showControls=False, idx=0)
        icon = Sprite(label='arrow', parent=container, texturePath=LEFT_ARROW, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        container.AddColorObject(icon)
        container.ChangeColor(COLOR_GREEN)

    def AddCropFrame(self, *args):
        for each in self.overlays.children[:]:
            if each.name == 'cropFrame':
                each.Close()

        initLeft = int(self.screenshotWidth * 0.25 * self.screenShotScaling)
        initTop = int(self.screenshotHeight * 0.25 * self.screenShotScaling)
        initWidth = int(self.screenshotWidth * 0.5 * self.screenShotScaling)
        initHeight = int(self.screenshotHeight * 0.5 * self.screenShotScaling)
        MoveableRect(name='Crop', parent=self.overlays, pos=(initLeft,
         initTop,
         initWidth,
         initHeight), maskColor=(0, 0, 0, 0.75), showControls=True)

    def AddFrame(self, *args):
        initLeft = int((self.screenshotWidth - 200) * self.screenShotScaling) / 2
        initTop = int((self.screenshotHeight - 200) * self.screenShotScaling) / 2
        initWidth = int(200 * self.screenShotScaling)
        initHeight = int(200 * self.screenShotScaling)
        MoveableRect(parent=self.overlays, name='Frame', pos=(initLeft,
         initTop,
         initWidth,
         initHeight), showFrame=True, showControls=True, idx=0)

    def Clear(self, *args):
        self.overlays.Flush()

    def SaveScreenshot(self, *args):
        self.Hide()
        baseTexture = trinity.Tr2RenderTarget(self.screenshotWidth, self.screenshotHeight, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
        renderJob = trinity.CreateRenderJob()
        desktop = UIRoot(name='screenshot', width=self.screenshotWidth, height=self.screenshotHeight, renderTarget=baseTexture, renderJob=renderJob)
        cropProportion = None
        for each in self.overlays.children:
            if each.name == 'Crop':
                cropProportion = each.proportionalPosition

        self.overlays.SetParent(desktop)
        self.screenshotSprite.SetParent(desktop)
        for overlay in self.overlays.children:
            overlay.UpdateProportionalPosition(1.0)

        desktop.UpdateAlignment()
        blue.pyos.synchro.Yield()
        renderJob.ScheduleOnce()
        renderJob.WaitForFinish()
        blue.pyos.synchro.Yield()
        path = AbsPath(self.screenshotPath)
        if cropProportion:
            cl, cr, ct, cb = cropProportion
            cr = min(1.0, cr)
            cb = min(1.0, cb)
            bmp = trinity.Tr2HostBitmap(baseTexture)
            bmp.Crop(int(cl * self.screenshotWidth), int(ct * self.screenshotHeight), int(cr * self.screenshotWidth), int(cb * self.screenshotHeight))
            bmp.Save(path)
        else:
            trinity.Tr2HostBitmap(baseTexture).Save(path)
        desktop.Close()
        self.CloseByUser()

    def OnScale_(self, *args):
        pass

    def RecalcLayout(self, *args):
        self.UpdateLayoutArea()


class MoveableRect(Container):
    __guid__ = 'MoveableRect'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    CONTROLS = (('topleft', uiconst.TOPLEFT),
     ('topright', uiconst.TOPRIGHT),
     ('bottomright', uiconst.BOTTOMRIGHT),
     ('bottomleft', uiconst.BOTTOMLEFT))

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.modifyThread = None
        self.frame = None
        self.colorObjects = []
        self.color = COLOR_GREEN
        self.controls = Container(parent=self, state=uiconst.UI_PICKCHILDREN)
        if attributes.showControls:
            for cornerName, align in self.CONTROLS:
                scalePoint = Fill(parent=self.controls, align=align, color=(1, 1, 1, 1), pos=(0, 0, 10, 10), state=uiconst.UI_NORMAL, name=cornerName)
                scalePoint.OnMouseDown = (self.StartScaling, scalePoint)
                scalePoint.OnMouseUp = (self.EndScaling, scalePoint)
                self.AddColorObject(scalePoint)

        self.maskColor = attributes.maskColor
        if self.maskColor:
            self.UpdateMask()
        if attributes.showFrame:
            self.frame = Frame(parent=self, frameConst=uiconst.FRAME_BORDER2_CORNER3, color=(1.0, 1.0, 1.0, 0.5))
            self.AddColorObject(self.frame)
        self.UpdateColor()
        self.RegisterProportionalValues()

    def AddColorObject(self, obj):
        self.colorObjects.append(obj)
        self.UpdateColor()

    def StartScaling(self, obj, *args):
        startProps = (obj.name,
         uicore.uilib.x,
         uicore.uilib.y,
         self.left,
         self.top,
         self.width,
         self.height)
        self.modifyThread = timerstuff.AutoTimer(1, self.ModifyRect, startProps)

    def EndScaling(self, obj, *args):
        self.modifyThread = None

    def OnMouseDown(self, *args):
        startProps = ('move',
         uicore.uilib.x,
         uicore.uilib.y,
         self.left,
         self.top,
         self.width,
         self.height)
        self.modifyThread = timerstuff.AutoTimer(1, self.ModifyRect, startProps)

    def OnMouseUp(self, *args):
        self.modifyThread = None

    def ModifyRect(self, startProps, *args):
        side, cursorX, cursorY, l, t, w, h = startProps
        dx = uicore.uilib.x - cursorX
        dy = uicore.uilib.y - cursorY
        if side == 'move':
            self.left = max(0, l + dx)
            self.top = max(0, t + dy)
        else:
            if 'left' in side:
                self.width = max(16, w - dx)
                self.left = max(0, min(l + dx, l + w - 16))
            else:
                self.width = max(16, w + dx)
            if 'top' in side:
                self.height = max(16, h - dy)
                self.top = max(0, min(t + dy, t + h - 16))
            else:
                self.height = max(16, h + dy)
        if self.maskColor:
            self.UpdateMask()
        self.RegisterProportionalValues()

    def RegisterProportionalValues(self):
        parWidth, parHeight = self.parent.GetAbsoluteSize()
        pl = self.left / float(parWidth)
        pr = (self.left + self.width) / float(parWidth)
        pt = self.top / float(parHeight)
        pb = (self.top + self.height) / float(parHeight)
        self.proportionalPosition = (pl,
         pr,
         pt,
         pb)

    def UpdateProportionalPosition(self, newScaling):
        parWidth, parHeight = self.parent.GetAbsoluteSize()
        pl, pr, pt, pb = self.proportionalPosition
        self.left = int(pl * parWidth)
        self.top = int(pt * parHeight)
        self.width = int((pr - pl) * parWidth)
        self.height = int((pb - pt) * parHeight)
        if newScaling == 1.0 and getattr(self, 'numLabel', None):
            self.numLabel.useSizeFromTexture = True
            self.numLabel.Layout()
            self.numLabel.top = -self.numLabel.textheight - 2
        if self.maskColor:
            self.UpdateMask()

    def UpdateMask(self):
        maskFills = getattr(self, 'maskFills', None)
        if not maskFills:
            self.maskFills = []
            for i in xrange(4):
                self.maskFills.append(Fill(parent=self, color=self.maskColor, align=uiconst.TOPLEFT))

        self.maskFills[0].top = -uicore.desktop.height
        self.maskFills[0].height = uicore.desktop.height
        self.maskFills[0].left = -uicore.desktop.width
        self.maskFills[0].width = uicore.desktop.width * 2
        self.maskFills[1].top = self.height
        self.maskFills[1].height = uicore.desktop.height
        self.maskFills[1].left = -uicore.desktop.width
        self.maskFills[1].width = uicore.desktop.width * 2
        self.maskFills[2].top = 0
        self.maskFills[2].height = self.height
        self.maskFills[2].left = -uicore.desktop.width
        self.maskFills[2].width = uicore.desktop.width
        self.maskFills[3].top = 0
        self.maskFills[3].height = self.height
        self.maskFills[3].left = self.width
        self.maskFills[3].width = uicore.desktop.width

    def OnMouseEnter(self, *args):
        self.ShowControls()
        self.mouseOverThread = timerstuff.AutoTimer(1, self.CheckMouseOver)

    def CheckMouseOver(self, *args):
        if self.destroyed:
            self.mouseOverThread = None
            return
        mo = uicore.uilib.mouseOver
        if mo is self or mo.IsUnder(self) or self.modifyThread:
            return
        self.mouseOverThread = None
        self.HideControls()

    def ShowControls(self):
        self.controls.Show()

    def HideControls(self):
        self.controls.Hide()

    def Numberate(self, *args):
        currentNumbers = []
        for each in self.parent.children:
            autoNumber = getattr(each, 'autoNumber', None)
            if autoNumber is not None:
                currentNumbers.append(autoNumber)

        tryNum = 1
        while tryNum in currentNumbers:
            tryNum += 1

        self.AssignNumber(tryNum)

    def AssignNumber(self, number):
        if getattr(self, 'numLabel', None) is None:
            self.numLabel = Label(parent=self, fontsize=NUMFONTSIZE, align=uiconst.TOPRIGHT, bold=1)
            self.numLabel.useSizeFromTexture = False
            self.numLabel._OnSizeChange_NoBlock = self.OnNumberSizeChange
        self.autoNumber = number
        self.numLabel.text = unicode(number)
        self.AddColorObject(self.numLabel)

    def OnNumberSizeChange(self, *args):
        screenShotWindow = GetWindowAbove(self)
        if screenShotWindow:
            self.numLabel.displayWidth = self.numLabel.textwidth * screenShotWindow.screenShotScaling
            self.numLabel.displayHeight = self.numLabel.textheight * screenShotWindow.screenShotScaling
            self.numLabel.top = -self.ReverseScaleDpi((self.numLabel.textheight + 2) * screenShotWindow.screenShotScaling)

    def GetMenu(self, *args):
        m = [(GetByLabel('UI/BugReporting/ScreenshotDeleteObject', object=self.name), self.Delete), (GetByLabel('UI/BugReporting/ScreenshotNumberate'), self.Numberate)]
        if self.maskColor:
            return m
        m = m + [None,
         (GetByLabel('UI/BugReporting/ScreenshotRed'), self.ChangeColor, ((1, 0, 0, 1),)),
         (GetByLabel('UI/BugReporting/ScreenshotGreen'), self.ChangeColor, ((0, 1, 0, 1),)),
         (GetByLabel('UI/BugReporting/ScreenshotBlue'), self.ChangeColor, ((0, 0, 1, 1),))]
        return m

    def Delete(self, *args):
        uthread.new(self.Close)

    def UpdateColor(self):
        self.ChangeColor(self.color)

    def ChangeColor(self, color):
        self.color = color
        for each in self.colorObjects:
            each.SetRGBA(*color)


class MoveableTextRect(MoveableRect):
    __guid__ = 'MoveableTextRect'
    DEFAULTTEXT = GetByLabel('UI/BugReporting/ScreenshotDefaultText')
    CONTROLS = ()

    def ApplyAttributes(self, attributes):
        MoveableRect.ApplyAttributes(self, attributes)
        self.originalScaling = attributes.get('scaling', 1.0)
        self.textEdit = None
        self.underlay = Fill(parent=self)
        self.sampleText = Label(parent=self, left=8, top=8, text=self.DEFAULTTEXT, fontsize=BASEFONTSIZE)
        self.sampleText.useSizeFromTexture = False
        self.sampleText._OnSizeChange_NoBlock = self.OnTextSizeChange
        self.UpdateColor()
        self.OnTextSizeChange()

    def OnTextSizeChange(self, *args):
        screenShotWindow = GetWindowAbove(self)
        if screenShotWindow:
            self.sampleText.displayWidth = self.sampleText.textwidth * screenShotWindow.screenShotScaling
            self.sampleText.displayHeight = self.sampleText.textheight * screenShotWindow.screenShotScaling
            self.width = self.ReverseScaleDpi(self.sampleText.displayWidth) + 16
            self.height = self.ReverseScaleDpi(self.sampleText.displayHeight) + 16

    def OnDblClick(self, *args):
        self.sampleText.Hide()
        setValue = ''
        if self.sampleText.text != self.DEFAULTTEXT:
            setValue = self.sampleText.text
        self.width = 200
        self.height = 100
        self.textEdit = EditPlainText(parent=self, maxLength=1000, align=uiconst.TOALL, idx=0, pos=(0, 0, 0, 0))
        self.textEdit.HideBackground()
        self.textEdit.RemoveActiveFrame()
        uicore.registry.SetFocus(self.textEdit)
        self.textEdit.SetValue(setValue, cursorPos=len(setValue))
        self.sr.cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDown)

    def OnGlobalMouseDown(self, *args):
        mo = uicore.uilib.mouseOver
        if mo is self or mo.IsUnder(self):
            return True
        if self.textEdit:
            val = self.textEdit.GetValue()
            self.sampleText.Show()
            self.sampleText.text = val or self.DEFAULTTEXT
            self.textEdit.Close()
            self.textEdit = None
        return False

    def ChangeColor(self, color):
        MoveableRect.ChangeColor(self, color)
        if getattr(self, 'sampleText', None):
            self.sampleText.SetTextColor(color)
            self.underlay.SetRGBA(*color)
            self.underlay.opacity = 0.1

    def UpdateProportionalPosition(self, newScaling):
        parWidth, parHeight = self.parent.GetAbsoluteSize()
        pl, pr, pt, pb = self.proportionalPosition
        self.left = int(pl * parWidth)
        self.top = int(pt * parHeight)
        self.sampleText.fontsize = int(BASEFONTSIZE * newScaling / self.originalScaling)
        if newScaling == 1.0:
            self.sampleText.useSizeFromTexture = True
            self.sampleText.Layout()
            self.width = self.sampleText.textwidth + 16
            self.height = self.sampleText.textheight + 16


def GetServerVersion(serverBuild, serverVersion):
    return '%s - %s.%s' % (boot.codename, serverVersion, serverBuild)
