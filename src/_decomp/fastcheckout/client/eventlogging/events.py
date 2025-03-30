#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\eventlogging\events.py


class Event(object):
    BUY_PLEX_CLICKED = 'BuyPlexOnlineClicked'
    CREDIT_CARD_INFO_RECEIVED = 'credit_card_info_received'
    BUY_PLEX_IN_GAME_STARTED = 'buy_plex_in_game_started'
    BUY_PLEX_IN_WEB_STARTED = 'buy_plex_in_web_started'
    FAST_CHECKOUT_WINDOW_OPENED = 'window_opened'
    OFFERS_RECEIVED = 'offers_received'
    OFFERS_RETRIEVAL_FAILED = 'offers_retrieval_failed'
    OFFER_SELECTED = 'offer_selected'
    BUY_PLEX_OFFER_IN_WEB_STARTED = 'buy_plex_offer_in_web_started'
    PASSWORD_ENTER_CANCELLED = 'password_enter_cancelled'
    PASSWORD_RESET_REQUESTED = 'password_reset_requested'
    PASSWORD_ENTERED = 'password_entered'
    PURCHASE_CONFIRMED = 'offer_bought'
    PURCHASE_NEEDS_WEB_CONFIRMATION = 'offer_purchase_needs_web_confirmation'
    PURCHASE_ERROR = 'offer_purchase_failed'
    SELL_NOW_CLICKED = 'plex_sell_now_pressed'


class BaseEventLogger(object):

    def _log_event(self, event, data):
        raise NotImplementedError('Must implement _log_event in derived class')

    def log_buy_plex_clicked(self, context):
        data = {'context': context}
        self._log_event(Event.BUY_PLEX_CLICKED, data)

    def log_credit_card_info_received(self, context, has_fast_checkout):
        data = {'context': context,
         'has_fast_checkout': has_fast_checkout}
        self._log_event(Event.CREDIT_CARD_INFO_RECEIVED, data)

    def log_buy_plex_in_game_started(self, context):
        data = {'context': context}
        self._log_event(Event.BUY_PLEX_IN_GAME_STARTED, data)

    def log_buy_plex_in_web_started(self, context):
        data = {'context': context}
        self._log_event(Event.BUY_PLEX_IN_WEB_STARTED, data)

    def log_fast_checkout_window_opened(self, context):
        data = {'context': context}
        self._log_event(Event.FAST_CHECKOUT_WINDOW_OPENED, data)

    def log_plex_offers_received(self, context, offer_ids):
        data = {'context': context,
         'offerIDs': offer_ids}
        self._log_event(Event.OFFERS_RECEIVED, data)

    def log_plex_offers_retrieval_failed(self, context, error):
        data = {'context': context,
         'error': error}
        self._log_event(Event.OFFERS_RETRIEVAL_FAILED, data)

    def log_plex_offer_selected(self, context, offer_id, offer_amount):
        data = {'context': context,
         'offerID': offer_id,
         'amount': offer_amount}
        self._log_event(Event.OFFER_SELECTED, data)

    def log_buy_plex_offer_in_web_started(self, context, offer_id, offer_amount):
        data = {'context': context,
         'offerID': offer_id,
         'amount': offer_amount}
        self._log_event(Event.BUY_PLEX_OFFER_IN_WEB_STARTED, data)

    def log_password_enter_cancelled(self, context, offer_id, offer_amount):
        data = {'context': context,
         'offerID': offer_id,
         'amount': offer_amount}
        self._log_event(Event.PASSWORD_ENTER_CANCELLED, data)

    def log_password_reset_requested(self, context, offer_id, offer_amount):
        data = {'context': context,
         'offerID': offer_id,
         'amount': offer_amount}
        self._log_event(Event.PASSWORD_RESET_REQUESTED, data)

    def log_password_entered(self, context, offer_id, offer_amount):
        data = {'context': context,
         'offerID': offer_id,
         'amount': offer_amount}
        self._log_event(Event.PASSWORD_ENTERED, data)

    def log_plex_offer_purchase_confirmed(self, context, offer_id, offer_amount):
        data = {'context': context,
         'offerID': offer_id,
         'amount': offer_amount}
        self._log_event(Event.PURCHASE_CONFIRMED, data)

    def log_plex_offer_purchase_needs_web_confirmation(self, context, offer_id, offer_amount):
        data = {'context': context,
         'offerID': offer_id,
         'amount': offer_amount}
        self._log_event(Event.PURCHASE_NEEDS_WEB_CONFIRMATION, data)

    def log_plex_offer_purchase_error(self, context, offer_id, offer_amount, error):
        data = {'context': context,
         'offerID': offer_id,
         'amount': offer_amount,
         'error': error}
        self._log_event(Event.PURCHASE_ERROR, data)

    def log_plex_sell_now_button_pressed(self, context, offer_id, offer_amount):
        data = {'context': context,
         'offerID': offer_id,
         'amount': offer_amount}
        self._log_event(Event.SELL_NOW_CLICKED, data)
