#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\skinListingsPaginationController.py
from cosmetics.client.ships.skins.errors import get_listing_error_text
from cosmetics.client.ships.skins.live_data.paginationController import BasePaginationController
from eve.client.script.ui.control.message import ShowQuickMessage
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class SkinListingsPaginationController(BasePaginationController):

    def __init__(self, get_page_method):
        super(SkinListingsPaginationController, self).__init__()
        self._get_page_method = get_page_method
        self._ship_type_filter = None
        self._sort_method = None
        self._ascending = None
        self._listing_target_type = None
        self._seller_membership_type = None
        self._pages_loaded = None

    @property
    def initialized(self):
        return self._pages_loaded is not None

    def reset(self, ship_type_filter, sort_method, ascending, num_per_page, listing_target_type = None, seller_membership_type = None):
        self._ship_type_filter = ship_type_filter
        self._sort_method = sort_method
        self._ascending = ascending
        self._listing_target_type = listing_target_type
        self._seller_membership_type = seller_membership_type
        self.num_per_page = num_per_page
        self._pages_loaded = []
        try:
            error = self._get_more_pages_from_server()
            if error is not None:
                ShowQuickMessage(GetByLabel(get_listing_error_text(error)))
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))

    def clear(self, ship_type_filter, sort_method, ascending, num_per_page, listing_target = None, seller_membership_type = None):
        self.reset(ship_type_filter, sort_method, ascending, num_per_page, listing_target, seller_membership_type)
        self.page_num = 0

    def _is_last_page_loaded(self):
        if not self._pages_loaded:
            return False
        return self._pages_loaded[-1].is_last_page()

    def _get_more_pages_from_server(self, num_pages = 3):
        for i in range(0, num_pages):
            listings, next_page_token, error = self._get_page_method(self._ship_type_filter, self._sort_method, self._ascending, self._listing_target_type, self._seller_membership_type, self._get_last_token(), self.num_per_page)
            if error is not None:
                return error
            new_page = SkinListingPage(listings, next_page_token)
            self._pages_loaded.append(new_page)
            if next_page_token is None:
                break

    def _get_last_token(self):
        if not self._pages_loaded:
            return None
        return self._pages_loaded[-1].next_page_token

    def get_page(self, page_num):
        _page = self._get_page(page_num)
        self.page_num = page_num
        return _page.listings

    def _get_page(self, page_num):
        self._check_load_more_pages(page_num)
        if page_num >= len(self._pages_loaded):
            raise ValueError("Unable to return page that hasn't been loaded")
        _page = self._pages_loaded[page_num]
        return _page

    def _check_load_more_pages(self, page_num):
        if self._is_last_page_loaded():
            return
        num_loaded = len(self._pages_loaded)
        if page_num >= num_loaded:
            try:
                error = self._get_more_pages_from_server()
                if error is not None:
                    ShowQuickMessage(GetByLabel(get_listing_error_text(error)))
            except (GenericException, TimeoutException):
                ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))

    def is_num_pages_known(self):
        return self._is_last_page_loaded()

    def has_more_than_one_page(self):
        if not self._pages_loaded:
            return False
        return not self._pages_loaded[0].is_last_page()

    def has_next_page(self):
        page = self._get_page(self.page_num)
        return not page.is_last_page()

    def has_prev_page(self):
        return self.page_num > 0


class SkinListingPage(object):

    def __init__(self, listings, next_page_token):
        self._listings = listings
        self._next_page_token = next_page_token

    @property
    def listings(self):
        return self._listings

    @property
    def nb_listings(self):
        return len(self._listings)

    @property
    def next_page_token(self):
        return self._next_page_token

    def is_last_page(self):
        return self._next_page_token is None
