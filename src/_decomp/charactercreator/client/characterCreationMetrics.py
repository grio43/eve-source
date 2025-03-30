#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\charactercreator\client\characterCreationMetrics.py
import requests
import hashlib
import log
import uthread
from eveprefs import boot
from carbonui.uicore import uicore
import charactercreator.const as ccConst
import utillib
STEP_NAMES = {ccConst.LOGIN: 'LOGIN',
 ccConst.HANGAR: 'HANGAR',
 ccConst.CANCEL: 'CANCEL',
 ccConst.COMPLETE: 'COMPLETE',
 ccConst.EMPIRESTEP: 'EMPIRE',
 ccConst.TECHNOLOGYSTEP: 'TECH',
 ccConst.BLOODLINESTEP: 'BLOODLINE',
 ccConst.CUSTOMIZATIONSTEP: 'CUSTOMIZATION',
 ccConst.PORTRAITSTEP: 'PORTRAIT',
 ccConst.NAMINGSTEP: 'NAMING',
 ccConst.DOLLSTEP: 'DOLL'}
MODE_NAMES = {ccConst.MODE_FULLINITIAL_CUSTOMIZATION: 'FULLINITIAL_CUSTOMIZATION',
 ccConst.MODE_LIMITED_RECUSTOMIZATION: 'LIMITED_RECUSTOMIZATION',
 ccConst.MODE_FULL_RECUSTOMIZATION: 'FULL_RECUSTOMIZATION',
 ccConst.MODE_FULL_BLOODLINECHANGE: 'FULL_BLOODLINECHANGE'}
PAGE_VIEW_TARGETS = [ccConst.EMPIRESTEP,
 ccConst.TECHNOLOGYSTEP,
 ccConst.BLOODLINESTEP,
 ccConst.CUSTOMIZATIONSTEP,
 ccConst.PORTRAITSTEP,
 ccConst.NAMINGSTEP]

def check_for_character_creation_exit():
    if hasattr(uicore, 'layer'):
        if hasattr(uicore.layer, 'charactercreation'):
            if getattr(uicore.layer.charactercreation, 'isopen', 0) and hasattr(uicore.layer.charactercreation.controller, 'metrics') and uicore.layer.charactercreation.controller.metrics is not None:
                uicore.layer.charactercreation.controller.metrics.exit_cc()


class CharacterCreationMetrics(object):

    def get_page_name(self, page):
        return 'characterCreation_%s' % STEP_NAMES[page]

    def __init__(self, mode, start_page):
        self.chars = None
        self.page = start_page
        self.mode = MODE_NAMES.get(mode)
        self.start_cc(start_page)

    @staticmethod
    def hash_uid(uid):
        uid_str = str(uid) + 'S3lmfi20jklnsfkl395jfmksl'
        return hashlib.sha1(uid_str).hexdigest()

    def new_page(self, to_page):
        page_name = self.get_page_name(to_page)
        req_params = self.get_req_params(self.page, {'t': 'pageview',
         'dh': 'eveonline',
         'dp': page_name,
         'dt': page_name})
        self.record_metric(req_params)
        self.page = to_page

    def cancel_cc(self):
        req_params = self.get_req_params(self.page, {'t': 'event',
         'ea': 'character_creation',
         'el': 'cancel',
         'ec': 'interaction',
         'sc': 'end'})
        self.record_metric(req_params)
        self.page = ccConst.CANCEL

    def exit_cc(self):
        req_params = self.get_req_params(self.page, {'t': 'event',
         'ea': 'exit_game',
         'el': 'logout',
         'ec': 'interaction',
         'sc': 'end'})
        self.record_metric(req_params, async=False)
        self.page = ccConst.CANCEL

    def complete_cc(self, charid):
        req_params = self.get_req_params(self.page, {'t': 'event',
         'ea': 'character_creation',
         'el': 'complete',
         'ec': 'milestone',
         'sc': 'end'})
        req_params['cd6'] = charid
        self.chars = sm.GetService('cc').GetCharacterSelectionData().GetChars()
        req_params['cd7'] = len(self.chars)
        self.record_metric(req_params)
        self.page = ccConst.CANCEL

    def start_cc(self, start_page):
        req_params = self.get_req_params(start_page, {'t': 'event',
         'ea': 'character_creation',
         'el': 'started',
         'ec': 'milestone'})
        self.record_metric(req_params, async=False)
        self.page = start_page

    def name_available_checked(self, name_available):
        if name_available == 1:
            label = 'name checked available'
        else:
            label = 'name checked unavailable'
        req_params = self.get_req_params(self.page, {'t': 'event',
         'ea': 'character_creation',
         'el': label,
         'ec': 'choose name'})
        self.record_metric(req_params)

    def first_name_focused(self):
        req_params = self.get_req_params(self.page, {'t': 'event',
         'ea': 'character_creation',
         'el': 'first name focused',
         'ec': 'choose name'})
        self.record_metric(req_params)

    def last_name_focused(self):
        req_params = self.get_req_params(self.page, {'t': 'event',
         'ea': 'character_creation',
         'el': 'last name focused',
         'ec': 'choose name'})
        self.record_metric(req_params)

    def last_name_randomized(self):
        req_params = self.get_req_params(self.page, {'t': 'event',
         'ea': 'character_creation',
         'el': 'last name randomized',
         'ec': 'choose name'})
        self.record_metric(req_params)

    def pick_school(self, schoolID):
        req_params = self.get_req_params(self.page, {'t': 'event',
         'ea': 'character_creation',
         'el': 'pick school %d' % schoolID,
         'ec': 'choose name'})
        self.record_metric(req_params)

    def get_req_params(self, page, extra_keys_dict):
        cluster_name = utillib.GetServerName()
        hashed_uid = self.hash_uid(session.userid)
        charid = session.charid
        if charid is None:
            charid = 0
        if self.chars is None:
            self.chars = sm.GetService('cc').GetCharacterSelectionData().GetChars()
        req_params = {'v': 1,
         'tid': 'UA-45583206-12',
         'cid': hashed_uid,
         'cd1': hashed_uid,
         'cd2': self.mode,
         'cd3': cluster_name,
         'cd4': session.sid,
         'cd5': self.get_page_name(page),
         'cd6': charid,
         'cd7': len(self.chars)}
        req_params.update(extra_keys_dict)
        return req_params

    def record_metric(self, req_params, async = True):
        if boot.region != 'optic':
            if async:
                uthread.new(self.record_metric_t, req_params)
            else:
                self.record_metric_t(req_params, timeout=2.0)

    @staticmethod
    def record_metric_t(req_params, timeout = 30.0):
        try:
            r = requests.post('https://www.google-analytics.com/collect', data=req_params, timeout=timeout)
            log.LogInfo('characterCreationMetrics: Sending POST %s' % req_params)
            r.raise_for_status()
        except requests.ConnectTimeout:
            log.LogWarn('characterCreationMetrics: TIMED OUT')
        except requests.HTTPError as e:
            log.LogWarn('characterCreationMetrics: HTTP Error %s' % e)
        except requests.ConnectionError as e:
            log.LogWarn('characterCreationMetrics: Connection Error %s' % e)
        except:
            pass
