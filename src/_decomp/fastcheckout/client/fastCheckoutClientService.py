#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\fastCheckoutClientService.py
import blue
from carbon.common.script.sys.service import Service
from carbonui.uicore import uicore
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.lib.vgsConst import CATEGORYTAG_PLEX
from eve.common.script.util.urlUtil import IsClientLaunchedThroughSteam
from eveexceptions import UserError
from fastcheckout.client.window import FastCheckoutWindow
from fastcheckout.client.eventlogging.eventLoggers import event_logger
from fastcheckout.common.errors import FastCheckoutDisabled
from logmodule import LogException
from journey.tracker import get_journey_id
import urlparse
import uuid
import webbrowser

class FastCheckoutClientService(Service):
    __guid__ = 'svc.FastCheckoutClientService'
    __notifyevents__ = ['OnFastCheckoutEnabledChanged', 'OnGlobalConfigChanged']

    def Run(self, *args):
        self.remote_service = sm.RemoteSvc('FastCheckoutService')
        self._is_fast_checkout_enabled = None
        self._fake_buy_plex_offer_url = None
        self._is_china_funnel_enabled = None
        self._use_shell_execute_to_buy_plex_offer = None
        self.offers = None
        self.plex_base_price = None
        self.plex_base_quantity = None
        self.purchase_trace_id = ''

    def start_purchase_flow(self):
        self.purchase_trace_id = str(uuid.uuid4())

    def stop_purchase_flow(self):
        self.purchase_trace_id = ''

    def get_purchase_trace_id(self):
        if not self.purchase_trace_id:
            self.start_purchase_flow()
        return self.purchase_trace_id

    def is_fast_checkout_enabled(self):
        if self._is_fast_checkout_enabled is None:
            if IsClientLaunchedThroughSteam():
                self._is_fast_checkout_enabled = False
            else:
                self._is_fast_checkout_enabled = self.remote_service.IsFastCheckoutEnabledForUser()
        return self._is_fast_checkout_enabled

    def clear_fast_checkout_enabled(self):
        self._is_fast_checkout_enabled = None
        self.remote_service.ClearFastCheckoutCacheForUser()

    def OnFastCheckoutEnabledChanged(self, is_fast_checkout_enabled):
        self._is_fast_checkout_enabled = is_fast_checkout_enabled

    def OnGlobalConfigChanged(self, *args, **kwargs):
        self.offers = None
        self._is_fast_checkout_enabled = None
        self._fake_buy_plex_offer_url = None
        self._is_china_funnel_enabled = None
        self._use_shell_execute_to_buy_plex_offer = None

    def _update_config(self):
        self._is_china_funnel_enabled, self._fake_buy_plex_offer_url, self._use_shell_execute_to_buy_plex_offer = self.remote_service.GetTestingConfiguration()

    def close_fast_checkout_nes(self):
        sm.GetService('vgsService').GetUiController().CloseFastCheckoutWindow()
        self.stop_purchase_flow()

    def close_fast_checkout_popup(self):
        fast_checkout_popup = FastCheckoutWindow.GetIfOpen()
        if fast_checkout_popup:
            fast_checkout_popup.Close()

    def is_china_funnel(self):
        if self._is_china_funnel_enabled is None:
            self._update_config()
        return self._is_china_funnel_enabled

    def _get_fake_buy_plex_offer_url(self):
        if self._fake_buy_plex_offer_url is None:
            self._update_config()
        return self._fake_buy_plex_offer_url

    def _should_use_shell_execute(self):
        if self._use_shell_execute_to_buy_plex_offer is None:
            self._update_config()
        return self._use_shell_execute_to_buy_plex_offer

    def should_use_plex(self):
        return self.is_fast_checkout_enabled() and not self.is_china_funnel()

    def get_plex_offers(self, context):
        try:
            offers = self._get_offers('plex')
            if not offers:
                raise KeyError()
            offer_ids = ','.join([ str(offer['id']) for offer in offers ])
            event_logger.log_plex_offers_received(context, offer_ids)
            return offers
        except KeyError:
            event_logger.log_plex_offers_retrieval_failed(context, 'max_transactions_reached')
            raise
        except FastCheckoutDisabled:
            event_logger.log_plex_offers_retrieval_failed(context, 'fast_checkout_disabled')
            raise
        except RuntimeError:
            event_logger.log_plex_offers_retrieval_failed(context, 'server_connection_failed')
            raise
        except UserError:
            event_logger.log_plex_offers_retrieval_failed(context, 'unexpected_user_error')
            raise
        except Exception:
            event_logger.log_plex_offers_retrieval_failed(context, 'unexpected_exception')
            raise

    def _get_offers(self, key):
        self._prime_offers_cache()
        return self.offers[key]

    def _prime_offers_cache(self):
        if self.offers:
            return
        self.offers = self.remote_service.GetOffersForUser()
        for offer in self.offers['plex']:
            if any((x.endswith('1.0') for x in offer['tags'])):
                self.plex_base_price = offer['price']
                self.plex_base_quantity = offer['baseQuantity']

    def get_plex_offers_base_price_and_quantity(self):
        self._prime_offers_cache()
        return (self.plex_base_price, self.plex_base_quantity)

    def buy_plex(self, log_context):
        self.start_purchase_flow()
        event_logger.log_buy_plex_clicked(log_context)
        if self.is_china_funnel():
            sm.GetService('vgsService').OpenStore(categoryTag=CATEGORYTAG_PLEX)
            return
        is_fast_checkout_enabled = self.is_fast_checkout_enabled()
        event_logger.log_credit_card_info_received(log_context, is_fast_checkout_enabled)
        if is_fast_checkout_enabled:
            self.buy_plex_via_fast_checkout(log_context)
        else:
            self.buy_plex_online(log_context=log_context)

    def buy_plex_via_fast_checkout(self, log_context):
        event_logger.log_buy_plex_in_game_started(log_context)
        if self._is_in_nes():
            self._open_nes_fast_checkout()
        else:
            self._open_in_game_fast_checkout(log_context)

    def _is_in_nes(self):
        return sm.GetService('viewState').IsViewActive(ViewState.VirtualGoodsStore)

    def _open_nes_fast_checkout(self):
        sm.GetService('vgsService').GetUiController().OpenFastCheckoutWindow()

    def _open_in_game_fast_checkout(self, log_context):
        FastCheckoutWindow.ToggleOpenClose(logContext=log_context)

    def buy_plex_online(self, origin = 'fastCheckout', reason = None, log_context = None):
        try:
            base_url = uicore.cmd.GetStoreServerUrl()
            plex_url = uicore.cmd.GetURLWithParameters(url=base_url, path='plex', origin=origin or '', reason=reason or '', journey_id=get_journey_id(), purchase_trace_id=self.get_purchase_trace_id(), utm_medium='app', utm_source='eveonline', utm_campaign='newedenstore', utm_content='cta_buyplex')
            if 'secure' in base_url.lower():
                urlparse.urljoin(base_url, 'store/plex')
                plex_url = uicore.cmd.GetURLWithParameters(url=base_url, origin=origin or '', reason=reason or '', journey_id=get_journey_id(), purchase_trace_id=self.get_purchase_trace_id(), utm_medium='app', utm_source='eveonline', utm_campaign='newedenstore', utm_content='cta_buyplex')
            if self._should_use_shell_execute():
                blue.os.ShellExecute(plex_url)
            else:
                webbrowser.open_new(plex_url)
            event_logger.log_buy_plex_in_web_started(log_context)
            self.LogNotice('buy_plex_online URL: %s' % plex_url)
            self.clear_fast_checkout_enabled()
        except Exception:
            LogException('Failed to open URL to buy PLEX online')
            raise UserError('FailedToOpenBuyPlexUrl')

    def _get_url_to_buy_plex_offer(self, offer_id, origin, reason):
        fake_url = self._get_fake_buy_plex_offer_url()
        if fake_url:
            return fake_url
        kwargs = {'goid': offer_id}
        plex_url = uicore.cmd.GetURLWithParameters(url=urlparse.urljoin(uicore.cmd.GetSecureServerUrl(), 'payment'), origin=(origin or ''), reason=(reason or ''), journey_id=get_journey_id(), purchase_trace_id=self.get_purchase_trace_id(), utm_medium='app', utm_source='eveonline', utm_campaign='newedenstore', utm_content=str(offer_id), **kwargs)
        return plex_url

    def buy_plex_offer_online(self, offer_id, offer_amount, log_context = None, origin = 'fastCheckout', reason = None):
        try:
            plex_url = self._get_url_to_buy_plex_offer(offer_id, origin, reason)
            if self._should_use_shell_execute():
                blue.os.ShellExecute(plex_url)
            else:
                webbrowser.open_new(plex_url)
            event_logger.log_buy_plex_offer_in_web_started(log_context, offer_id, offer_amount)
            self.LogNotice('buy_plex_offer_online URL: %s' % plex_url)
            self.clear_fast_checkout_enabled()
        except Exception:
            LogException('Failed to open URL to buy PLEX online')
            raise UserError('FailedToOpenBuyPlexUrl')

    def _is_payment_confirmed(self, ret):
        msg = ret.get('Message', None)
        return msg == 'OK'

    def buy_plex_offer(self, log_context, offer, password):
        event_logger.log_password_entered(log_context, offer.id, offer.quantity)
        try:
            ret = self.remote_service.BuyOffer(offer=offer, password=password, purchaseTraceID=self.get_purchase_trace_id(), journeyID=get_journey_id())
        except UserError as e:
            self._log_plex_offer_purchase_error(log_context, offer.id, offer.quantity, e.msg)
            raise

        is_payment_confirmed = self._is_payment_confirmed(ret)
        self._log_plex_offer_purchase_processed(log_context, offer.id, offer.quantity, is_payment_confirmed)
        return ret

    def _log_plex_offer_purchase_processed(self, log_context, offer_id, offer_amount, is_payment_confirmed):
        if is_payment_confirmed:
            logger = event_logger.log_plex_offer_purchase_confirmed
        else:
            logger = event_logger.log_plex_offer_purchase_needs_web_confirmation
        logger(log_context, offer_id, offer_amount)

    def _log_plex_offer_purchase_error(self, log_context, offer_id, offer_amount, error):
        error_string = {'AuthFailed': 'wrong_password',
         'OfferNotAvailable': 'offer_unavailable'}.get(error, 'purchase_failed')
        event_logger.log_plex_offer_purchase_error(log_context, offer_id, offer_amount, error_string)

    def request_password_recovery(self, log_context, offer_id, offer_amount):
        try:
            forgot_password_url = urlparse.urljoin(uicore.cmd.GetSecureServerUrl(), 'recoveraccount')
            blue.os.ShellExecute(forgot_password_url)
        except Exception:
            LogException('Failed to open URL to access password recovery online')
            raise UserError('FailedToOpenPasswordRecoveryUrl')
        finally:
            event_logger.log_password_reset_requested(log_context, offer_id, offer_amount)
