#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\kiring\client\apigateway.py
import blue
import trinity
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
import carbonui.const as uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.control.button import Button
from carbonui.control.window import Window
from eve.common.lib import jwt
from eveprefs import prefs
from kiring.common.const import KIRING_GAME_ID, KIRING_SUCCESS_CODES, ANTI_ADDICTION_PASS_CODE
import logging
import random
import requests
import socket
import urllib
import uthread2
from localization import GetByLabel
import base64
import json
import os
import sys
from eveexceptions.exceptionEater import ExceptionEater
logger = logging.getLogger(__name__)
PAY_THROUGH_ALIPAY_WEBSITE = 'alipay'
PAY_THROUGH_SCANNING_ALIPAY_QR_CODE = 'alipayqr'
PAY_THROUGH_SCANNING_WEIXIN_QR_CODE = 'weixinpayqr'
TEST_GOODS_ID_1 = 'ma79test1'
TEST_GOODS_ID_2 = 'ma79test2'
TEST_URL = 'https://en.wikipedia.org/wiki/Tsundoku'
TEST_QR_1 = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQLoiYbvJOHAg38PCVZYKt4XL1m0Hn9Jijf5IMZySfrcQSDoJ_a'
TEST_QR_2 = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQEn8j5aPnz19OhzSfxl2_a7iR-ZrgK5wwl2i8tqT-D-dxSgIyTZw'
TEST_SERIAL_NUMBER = 'ThisIsWhereIWouldKeepMySerialNumberIfIHadOne'
KIRING_ORDER_STATUS_UNPAID = 0
KIRING_ORDER_STATUS_PAYING = 1
KIRING_ORDER_STATUS_COMPLETE = 4
KIRING_ORDER_STATUS_TIMEOUT = 7
KIRING_PAYMENT_OPTIONS = [(GetByLabel('UI/VirtualGoodsStore/Kiring/Alipay'), PAY_THROUGH_ALIPAY_WEBSITE), (GetByLabel('UI/VirtualGoodsStore/Kiring/AlipayQR'), PAY_THROUGH_SCANNING_ALIPAY_QR_CODE), (GetByLabel('UI/VirtualGoodsStore/Kiring/WeixinQR'), PAY_THROUGH_SCANNING_WEIXIN_QR_CODE)]
KIRING_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded',
 'Accept': '*/*'}
kiring_api_gateway = None

class KiringPaymentActionID(object):
    OPEN_WEBSITE = 1
    SCAN_QR_CODE = 2


class KiringOrderStatus(object):
    UNPAID = 0
    PAYING = 1
    COMPLETE = 4
    CLOSED_BY_TIMEOUT = 7


def get_url_with_parameters(url, parameters):
    return '?'.join([url, urllib.urlencode(parameters)])


class KiringPaymentAction(object):

    def __init__(self, actionID, url):
        self.actionID = actionID
        self.url = url


PAYMENT_METHOD_TO_ACTION_ID = {PAY_THROUGH_ALIPAY_WEBSITE: KiringPaymentActionID.OPEN_WEBSITE,
 PAY_THROUGH_SCANNING_ALIPAY_QR_CODE: KiringPaymentActionID.SCAN_QR_CODE,
 PAY_THROUGH_SCANNING_WEIXIN_QR_CODE: KiringPaymentActionID.SCAN_QR_CODE}

class KiringOrder(object):

    def __init__(self, characterID, goodsID, quantity, unixTimeStamp, on_success = None, on_failure = None):
        self.roleid = str(characterID)
        self.goodsid = goodsID
        self.goodscount = quantity
        self.timestamp = unixTimeStamp
        self.udid = get_unique_client_id()
        self.on_success = on_success
        self.on_failure = on_failure
        self.order_id = None

    def Initialize(self, order_id, payment_method):
        self.order_id = order_id
        self.payment_method = payment_method


class BaseKiringApiGateway(object):

    def __init__(self):
        pass

    def place_order(self, order, payment_method):
        return TEST_SERIAL_NUMBER

    def check_anti_addiction(self):
        pass

    def dismiss_order(self):
        pass

    def inquire_order_status(self, serialNumber):
        return KiringOrderStatus.UNPAID


class FakeKiringApiGateway(object):

    def __init__(self):
        payThroughAlipayWebsite = KiringPaymentAction(KiringPaymentActionID.OPEN_WEBSITE, TEST_URL)
        payThroughScanningAlipayQrCode = KiringPaymentAction(KiringPaymentActionID.SCAN_QR_CODE, TEST_QR_1)
        payThroughScanningWeixinQrCode = KiringPaymentAction(KiringPaymentActionID.SCAN_QR_CODE, TEST_QR_2)
        self.paymentMethodToAction = {PAY_THROUGH_ALIPAY_WEBSITE: payThroughAlipayWebsite,
         PAY_THROUGH_SCANNING_ALIPAY_QR_CODE: payThroughScanningAlipayQrCode,
         PAY_THROUGH_SCANNING_WEIXIN_QR_CODE: payThroughScanningWeixinQrCode}
        self.order_watch_thread = None
        self.account = 'bla@bla.is'

    def place_order(self, order, paymentMethod):
        if paymentMethod not in self.paymentMethodToAction:
            raise ValueError('Invalid payment method %s' % paymentMethod)
        self.order_watch_thread = uthread2.StartTasklet(self._watch_order, order)
        return self.paymentMethodToAction[paymentMethod]

    def inquire_order_status(self, serialNumber):
        return KiringOrderStatus.UNPAID

    def _watch_order(self, order):
        if order.on_success is None and order.on_failure is None:
            return
        self.dismiss_order()
        uthread2.sleep(3)
        while True:
            uthread2.Sleep(1)
            result = random.randint(0, 7)
            if result == KIRING_ORDER_STATUS_COMPLETE:
                if order.on_success is not None:
                    order.on_success()
                    return
            elif result == KIRING_ORDER_STATUS_TIMEOUT:
                if order.on_failure is not None:
                    order.on_failure(GetByLabel('UI/VirtualGoodsStore/Kiring/PaymentFailed'))
                    return
            logger.info('Waiting on payment')

    def dismiss_order(self):
        if self.order_watch_thread is not None:
            self.order_watch_thread.kill()
            self.order_watch_thread = None


class CodeInputWindow(Window):
    default_width = 200
    default_height = 100

    def ApplyAttributes(self, attributes):
        super(CodeInputWindow, self).ApplyAttributes(attributes)
        self.content = Container(parent=self.sr.main, align=uiconst.TOPLEFT, width=200, height=20, mode=uiconst.UI_PICKCHILDREN)
        self.result = ''
        self.textEdit = SingleLineEditText(parent=self.content, maxlength=100, setvalue='', align=uiconst.TOLEFT, width=150, height=20)
        self.button = Button(parent=self.content, align=uiconst.TOLEFT, label='Submit', width=50, height=20, func=self.OnSubmit)

    def OnSubmit(self, *args):
        self.result = self.textEdit.text
        self.Close()


class KiringApiGateway(BaseKiringApiGateway):

    def __init__(self, *args, **kwargs):
        super(KiringApiGateway, self).__init__(*args, **kwargs)
        self.kiringManager = sm.RemoteSvc('kiringMgr')
        self.nextOrderID = 1
        self.aid = None
        self.token = None
        self.device_id = None
        self.user_id = None
        self.account = None
        self.netease_account = None
        self.unique_client_id = get_unique_client_id()
        self.kiringChannelsAndEndpoints = self.kiringManager.GetKiringConfiguration()
        self.app_mode = self.kiringChannelsAndEndpoints['mode']
        self.kiring_client_id = self.kiringChannelsAndEndpoints['client_id']
        self.mpay_url = self.kiringChannelsAndEndpoints['endpoints']['mpay']
        self.billing_url = self.kiringChannelsAndEndpoints['endpoints']['billing']
        self.redirect_uri = self.kiringChannelsAndEndpoints['endpoints']['redirect_uri']
        self.login_channel = self.kiringChannelsAndEndpoints['channels']['login']
        self.pay_channel = self.kiringChannelsAndEndpoints['channels']['pay']
        self.app_channel = self.kiringChannelsAndEndpoints['channels']['app']
        self.name = ''
        self.order_watch_thread = None

    def _get_kiring_headers(self):
        headers = KIRING_HEADERS
        headers['Origin'] = self.redirect_uri
        return headers

    def _have_valid_token(self):
        if self.token is None or self.user_id is None or self.device_id is None:
            return False
        if self.aid is None or self.account is None or self.name is None:
            return False
        if not self._am_using_browser_authentication():
            return True
        return self._check_browser_token()

    def _check_browser_token(self):
        URL_4 = urllib.basejoin(self.mpay_url, 'login/check_token')
        data = {'game_id': KIRING_GAME_ID,
         'app_mode': self.app_mode,
         'device_id': self.device_id,
         'user_id': self.user_id,
         'token': self.token}
        try:
            r = requests.post(URL_4, headers=self._get_kiring_headers(), params=data)
        except requests.ConnectionError as e:
            logger.info("Failed to connect to Kiring server '%s'.", e.request.url)
            return False

        if not r.ok:
            return False
        r_json = r.json()
        return r_json['code'] == 0

    def _authenticate_with_browser(self):
        URL_2 = urllib.basejoin(self.mpay_url, 'login/oauth2/authorize')
        data = {'game_id': KIRING_GAME_ID,
         'app_mode': self.app_mode,
         'device_id': self.device_id,
         'client_id': self.kiring_client_id,
         'redirect_uri': self.redirect_uri,
         'response_type': 'code'}
        url_with_parameters = get_url_with_parameters(URL_2, data)
        blue.os.ShellExecute(url_with_parameters)
        window = CodeInputWindow(parent=uicore.layer.vgsabovesuppress)
        window.SetCaption('Please enter Kiring Code')
        while not window.destroyed:
            uthread2.Sleep(1)

        if not window.result:
            logger.info("Post the 'code' from the url in the address bar you get redirected to when you log in.")
        self.code = window.result
        auth_data = self.kiringManager.PerformKiringServerSideAuthenticationFromCode(self.code, self.device_id, self.unique_client_id)
        self.aid, self.user_id, self.token, self.account, self.name = auth_data
        settings.user.ui.Set('vgsKiringToken', self.token)
        settings.user.ui.Set('vgsKiringUserID', self.user_id)
        settings.user.ui.Set('vgsKiringAccount', self.account)
        settings.user.ui.Set('vgsKiringDeviceID', self.device_id)
        settings.user.ui.Set('vgsKiringAID', self.aid)

    def _authenticate_with_token(self):
        connectionSvc = sm.GetService('connection')
        jwtToken = connectionSvc.GetLoginJWT()
        if jwtToken is None:
            logger.warn('Unable to authenticate with Kiring. Login JWT missing.')
            return
        unverified_payload = jwt.decode(jwtToken, verify=False)
        user_id = unverified_payload.get('netease_userid', '')
        netease_account = unverified_payload.get('netease_token', '')
        account = unverified_payload.get('netease_account', '')
        name = unverified_payload.get('name', '')
        aid, base64EncodedData = account.split('-')
        decodedJSON = base64.decodestring(base64EncodedData)
        decodedDict = json.loads(decodedJSON)
        deviceID = decodedDict['odi']
        token = decodedDict['s']
        aid = int(self.kiringManager.GetSAuthAid(user_id, account, deviceID))
        logger.info('GetSAuthAid: %s', aid)
        self.aid = aid
        self.netease_account = netease_account
        self.user_id = user_id
        self.token = token
        self.account = account
        self.name = name
        self.device_id = deviceID

    def _am_using_browser_authentication(self):
        return prefs.GetValue('kiringBrowserAuthentication', False)

    def ensure_valid_token_data(self):
        if self._have_valid_token():
            return True
        useBrowserAuthentication = self._am_using_browser_authentication()
        if not useBrowserAuthentication:
            self._authenticate_with_token()
            return True
        if not session.role & ROLE_PROGRAMMER:
            return False
        return self._initialize_device_and_do_browser_authentication()

    def _initialize_device_and_do_browser_authentication(self):
        URL_1 = urllib.basejoin(self.mpay_url, 'device/init')
        windowsVersion = sys.getwindowsversion()
        data = {'game_id': KIRING_GAME_ID,
         'app_mode': self.app_mode,
         'device_type': 'pc',
         'system_name': os.getenv('computername'),
         'system_version': '{}.{}'.format(windowsVersion.major, windowsVersion.minor),
         'resolution': '{}x{}'.format(trinity.device.adapterWidth, trinity.device.adapterHeight),
         'device_model': os.getenv('PROCESSOR_IDENTIFIER')}
        try:
            r = requests.post(URL_1, headers=self._get_kiring_headers(), params=data)
        except requests.ConnectionError as e:
            logger.info("Failed to connect to Kiring server '%s'.", e.request.url)
            return False

        r_json = r.json()
        if r_json['code'] not in KIRING_SUCCESS_CODES:
            logger.error(u"Kiring system error: 'device/init' failed %s %s", r_json['code'], repr(r_json['msg']))
            return False
        device = r_json[u'device']
        self.device_id = device[u'id']
        self._authenticate_with_browser()
        if self.token is None:
            logger.warn('Unable to authenticate with Kiring servers.')
            return False
        return True

    def _initialize_order(self, order):
        orderID = str(self.nextOrderID)
        self.nextOrderID += 1
        order.Initialize(orderID)

    def _query_order_status(self, order):
        try:
            success = self.ensure_valid_token_data()
            if not success:
                return KIRING_ORDER_STATUS_UNPAID
            kiring_headers = self._get_kiring_headers()
            return query_by_token(order.order_id, self.user_id, self.device_id, self.token, self.mpay_url, self.app_channel, self.app_mode, kiring_headers, order.payment_method)
        except Exception:
            logger.warn('Failed to query order status')
            return KIRING_ORDER_STATUS_UNPAID

    def _watch_order(self, order):
        if order.on_success is None and order.on_failure is None:
            return
        while True:
            uthread2.Sleep(3)
            result = self._query_order_status(order)
            if result == KIRING_ORDER_STATUS_COMPLETE:
                _log_client_event('PaymentComplete', ['order_id', 'pay_method'], order.order_id, order.payment_method)
                if order.on_success is not None:
                    order.on_success()
                    return
            elif result == KIRING_ORDER_STATUS_TIMEOUT:
                _log_client_event('PaymentFailed', ['order_id', 'pay_method'], order.order_id, order.payment_method)
                if order.on_failure is not None:
                    order.on_failure(GetByLabel('UI/VirtualGoodsStore/Kiring/PaymentFailed'))
                    return
            logger.info('Waiting on payment')

    def check_anti_addiction(self):
        success = self.ensure_valid_token_data()
        if not success:
            return ANTI_ADDICTION_PASS_CODE
        return self.kiringManager.GetAntiAddictionCode(self.netease_account)

    def place_order(self, order, payment_method):
        self.dismiss_order()
        success = self.ensure_valid_token_data()
        if not success:
            return
        kiring_headers = self._get_kiring_headers()
        order_id = self.kiringManager.PlaceKiringOrder(self.device_id, self.unique_client_id, self.aid, order.goodsid, order.goodscount, self.user_id, self.netease_account, self.billing_url, self.app_channel, self.pay_channel, self.login_channel, kiring_headers, self.app_mode)
        if order_id is None:
            return
        URL_5 = urllib.basejoin(self.mpay_url, 'payment/init_by_token')
        data = {'game_id': KIRING_GAME_ID,
         'user_id': self.user_id,
         'order_id': order_id,
         'pay_method': payment_method,
         'app_channel': self.app_channel,
         'app_mode': self.app_mode,
         'device_id': self.device_id,
         'token': self.token}
        r = requests.post(URL_5, data, headers=kiring_headers)
        response_json = r.json()
        if response_json['code'] not in KIRING_SUCCESS_CODES:
            logger.error(u"Kiring system error: 'payment/init_by_token' failed %s %s", response_json['code'], repr(response_json['msg']))
            return
        payment_url = response_json[u'order'][u'pay_url']
        _log_client_event('PaymentInit', ['order_id', 'pay_method', 'pay_url'], order_id, payment_method, payment_url)
        order.Initialize(order_id, payment_method)
        self.order_watch_thread = uthread2.StartTasklet(self._watch_order, order)
        payment_action_id = PAYMENT_METHOD_TO_ACTION_ID[payment_method]
        payment_action = KiringPaymentAction(payment_action_id, payment_url)
        return payment_action

    def dismiss_order(self):
        if self.order_watch_thread is not None:
            self.order_watch_thread.kill()
            self.order_watch_thread = None

    def activate_redeeming_code(self, redeeming_code):
        success = self.ensure_valid_token_data()
        if not success:
            return None
        return self.kiringManager.ActivateRedeemingCode(redeeming_code, self.account, self.aid, self.user_id, self.name, get_current_ip(), self.device_id)


def _log_client_event(event, columns, *args):
    with ExceptionEater('eventLog'):
        uthread2.StartTasklet(sm.ProxySvc('eventLog').LogClientEvent, 'kiringstore', columns, event, *args)


def get_current_ip():
    return socket.gethostbyname(socket.gethostname())


def query_by_token(order_id, user_id, device_id, token, mpay_url, app_channel, app_mode, kiring_headers, payment_method):
    URL_6 = urllib.basejoin(mpay_url, 'payment/query_by_token')
    data = {'game_id': KIRING_GAME_ID,
     'order_id': order_id,
     'app_channel': app_channel,
     'app_mode': app_mode,
     'device_id': device_id,
     'token': token,
     'user_id': user_id,
     'pay_method': payment_method}
    r = requests.post(URL_6, headers=kiring_headers, params=data)
    response_json = r.json()
    if response_json['code'] not in KIRING_SUCCESS_CODES:
        logger.error(u"Kiring system error: 'payment/query_by_token' failed %s %s", response_json['code'], repr(response_json['msg']))
        return KIRING_ORDER_STATUS_UNPAID
    return response_json[u'order'][u'status']


def get_unique_client_id():
    return unicode(blue.sysinfo.machineUuid)


def get_kiring_api_gateway():
    global kiring_api_gateway
    if kiring_api_gateway is None:
        kiring_api_gateway = KiringApiGateway()
    return kiring_api_gateway


def clear_cached_token_data():
    settings.user.ui.Delete('vgsKiringToken')
    settings.user.ui.Delete('vgsKiringUserID')
    settings.user.ui.Delete('vgsKiringAccount')
    settings.user.ui.Delete('vgsKiringDeviceID')
    settings.user.ui.Delete('vgsKiringAID')
