#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\serenity\eveguard\client\eveguard_service.py
import os
import platform
import json
import base64
import time
import blue
import jwt
import uthread
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from carbonui.uicore import uicore
from localization import GetByLabel
MESSAGE_HANDSHAKE = 0
MESSAGE_HEARTBEAT_PING = 1
MESSAGE_HEARTBEAT_PONG = 2
MESSAGE_TERMINATE = 3
MAX_HEARTBEAT_RETRY_TIMES = 20
QUIT_GAME_DELAY_MSEC = 20000
HEARTBEAT_RATE_MSEC = 3000
MAX_SHAKE_HANDS_RETRY_TIMES = 10
HEARTBEAT_PING_TIMEOUT = 60.0
HEARTBEAT_CHECK_INTERVAL = 10.0
EVE_GUARD_MESSAGE_SIZE = 16
OPERATE_SUCCESS = 0

class EveGuardService(Service):
    __guid__ = 'svc.eveGuardSvc'
    __servicename__ = 'Eve Guard Service'
    eveGuardServerUrl = 'https://ac.evepc.163.com/'

    def Run(self, ms):
        super(EveGuardService, self).Run(ms)
        if platform.system() != 'Windows':
            raise RuntimeError('EVE Guard Service cannot run on non-Windows platforms')
        self.namedPipe = None
        self.heartbeatFailedTimes = 0
        self.shakeHandsFailedTimes = 0
        self.lastPongTime = 0
        self.isTerminating = False
        uthread.worker('TryToShakeHandsWithGuard', self.TryToShakeHandsWithGuard)

    def TryToShakeHandsWithGuard(self):
        while True:
            blue.synchro.SleepWallclock(2000)
            if session and session.userid:
                if self.ShakeHand():
                    self.StartHeartbeat()
                    break
                else:
                    self.shakeHandsFailedTimes += 1
                    if self.shakeHandsFailedTimes > MAX_SHAKE_HANDS_RETRY_TIMES:
                        self.LogWarn('Failed to shake hands with eve guard')
                        self.TryToKickCheater()
                        break

    def pipe_no_wait(self, pipeFd):
        if platform.name() != 'Windows':
            self.LogWarn('Not running on Windows, cannot connect to pipe.')
        import msvcrt
        from ctypes.wintypes import HANDLE, DWORD, BOOL
        from ctypes import windll, byref, WinError, POINTER
        LPDWORD = POINTER(DWORD)
        PIPE_NOWAIT = DWORD(1)
        SetNamedPipeHandleState = windll.kernel32.SetNamedPipeHandleState
        SetNamedPipeHandleState.argtypes = [HANDLE,
         LPDWORD,
         LPDWORD,
         LPDWORD]
        SetNamedPipeHandleState.restype = BOOL
        h = msvcrt.get_osfhandle(pipeFd)
        res = windll.kernel32.SetNamedPipeHandleState(h, byref(PIPE_NOWAIT), None, None)
        if res == 0:
            self.LogWarn('Failed to set pipe not wait winError=%s' % WinError())
            return False
        return True

    def ShakeHand(self):
        try:
            pipeName = base64.b64decode('XFwuXHBpcGVcNjg1NUJERDNBNUVGNDE1M0JFN0M5MjVGQTdGNTdCQzI=')
            self.namedPipe = os.open(pipeName, os.O_RDWR | os.O_BINARY)
            if not self.pipe_no_wait(self.namedPipe):
                return False
        except OSError as error:
            self.LogWarn('Failed to open named pipe errno=%d' % error.errno)
            return False

        if self.namedPipe:
            message = json.dumps({'type': MESSAGE_HANDSHAKE,
             'address': sm.RemoteSvc('kiringMgr').GetEveGuardServerAddress() or self.eveGuardServerUrl})
            self.__WriteToPipe(message)
            return True
        return False

    def StartHeartbeat(self):
        uthread.worker('Heartbeat', self.HeartbeatLoop)
        sm.RemoteSvc('eveguard_report').heartbeat_started()

    def HeartbeatLoop(self):
        self.lastPongTime = time.time()
        while self.IsPipeConnected() and not self.isTerminating:
            blue.synchro.SleepWallclock(HEARTBEAT_RATE_MSEC)
            if self.CheckTimeout():
                continue
            error = self.SendHeartbeat()
            error = self.CheckEveGuardNotify() if error == 0 else error
            if error != 0:
                self.heartbeatFailedTimes += 1
                if self.heartbeatFailedTimes >= MAX_HEARTBEAT_RETRY_TIMES:
                    if not self.ShakeHand():
                        if self.namedPipe:
                            os.close(self.namedPipe)
                        sm.RemoteSvc('eveguard_report').heartbeat_stopped()
                        self.TryToKickCheater()
                        return
                    self.heartbeatFailedTimes = 0
            elif self.heartbeatFailedTimes > 0:
                self.heartbeatFailedTimes = 0

    def CheckTimeout(self):
        if time.time() >= self.lastPongTime + HEARTBEAT_PING_TIMEOUT:
            self.LogWarn('ping is timeout, prepare to terminate')
            self.Terminate()
            return True
        return False

    def Terminate(self):
        self.isTerminating = True
        sm.RemoteSvc('eveguard_report').heartbeat_stopped()
        self.TryToKickCheater()

    def CheckEveGuardNotify(self):
        pipeError, notifyMsg = self.ReadNotifyFromEveGuard()
        if pipeError != 0:
            return pipeError
        if not notifyMsg:
            return 0
        self.lastPongTime = time.time()
        try:
            for msg in notifyMsg.split('\n'):
                if not msg:
                    continue
                notifyDict = json.loads(msg)
                messageType = notifyDict.get('type', None)
                if messageType == MESSAGE_TERMINATE:
                    self.Terminate()
                    break

        except Exception as e:
            self.LogError('Failed to decode notifyMsg from pipe error=%s' % e)

        return 0

    def ReadNotifyFromEveGuard(self):
        from ctypes import GetLastError
        pipeError = 0
        notifyMsg = None
        if self.namedPipe:
            try:
                notifyMsg = os.read(self.namedPipe, 1024)
            except OSError as error:
                lastError = GetLastError()
                if lastError != OPERATE_SUCCESS:
                    self.LogWarn('Failed to read message from pipe errno=%d GetLastError=%s' % (error.errno, GetLastError()))
                    return (lastError, None)

        return (pipeError, notifyMsg)

    def IsPipeConnected(self):
        return self.namedPipe is not None and self.heartbeatFailedTimes < MAX_HEARTBEAT_RETRY_TIMES

    def SendHeartbeat(self):
        name = ''
        user_id = ''
        if sm.GetService('connection'):
            jwtToken = sm.GetService('connection').GetLoginJWT()
            if jwtToken:
                unverified_payload = jwt.decode(jwtToken, verify=False)
                if unverified_payload:
                    user_id = unverified_payload.get('netease_userid', '')
                    name = unverified_payload.get('name', '')
        message = json.dumps({'type': MESSAGE_HEARTBEAT_PING,
         'userId': str(session.userid),
         'characterId': str(session.charid) if session.charid else '0',
         'ipAddress': session.address.split(':')[0],
         'neteaseID': user_id,
         'characterName': name})
        return self.__WriteToPipe(message)

    def TryToKickCheater(self):
        try:
            shouldKick = sm.RemoteSvc('kiringMgr').ShouldKickCheater()
        except:
            self.LogWarn("Failed to get monolith 'ShouldKickCheater' config")
            shouldKick = False

        if shouldKick:
            uthread.worker('DisplayMessage', self.DisplayMessageAndQuitGame)
            blue.synchro.SleepWallclock(QUIT_GAME_DELAY_MSEC)
            uicore.cmd.DoQuitGame()
        else:
            uthread.worker('DisplayMessage', self.DisplayMessageEnvirNotSafe)

    def DisplayMessageEnvirNotSafe(self):
        uicore.Message('CustomInfo', {'info': GetByLabel('UI/Kiring/GameEnvirNotSafe')})

    def DisplayMessageAndQuitGame(self):
        if uicore.Message('CustomInfo', {'info': GetByLabel('UI/Kiring/ClientNotSafe', seconds='{:}'.format(QUIT_GAME_DELAY_MSEC / 1000))}) == uiconst.ID_YES:
            uicore.cmd.DoQuitGame()

    def __WriteToPipe(self, jsonStr):
        pipeError = 0
        if self.namedPipe:
            try:
                os.write(self.namedPipe, bytearray(jsonStr))
            except OSError as error:
                pipeError = error.errno
                self.LogWarn('Failed to write message to pipe errno=%d times %d' % (pipeError, self.heartbeatFailedTimes + 1))

        return pipeError
