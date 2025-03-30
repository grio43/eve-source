#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\localization.py
from __future__ import absolute_import
import enum
import eveLocalization
import localization
from localization.parser import _Tokenize
from raffles.common import errors
from raffles.common.const import BlueprintType

class Text(str, enum.Enum):
    raffle_window_description = 'UI/HyperNet/WindowDescription'
    raffle_window_title = 'UI/HyperNet/WindowTitle'
    remaining_tickets = 'UI/HyperNet/RemainingTickets'
    available_tickets = 'UI/HyperNet/AvailableTickets'
    apply_filter = 'UI/HyperNet/Apply'
    reset = 'UI/HyperNet/Reset'
    refresh = 'UI/HyperNet/Refresh'
    market_estimate = 'UI/HyperNet/MarketEstimate'
    show_only_available = 'UI/HyperNet/ShowOnlyAvailable'
    owned_tickets = 'UI/HyperNet/OwnedTickets'
    player_owned_tickets = 'UI/HyperNet/PlayerOwnedTickets'
    player_owned_no_tickets = 'UI/HyperNet/PlayerOwnedNoTickets'
    unknown_error = 'UI/HyperNet/UnknownError'
    no_raffles_found_error = 'UI/HyperNet/NoRafflesFoundError'
    not_found_error = 'UI/HyperNet/NotFoundError'
    ticket_unavailable_error = 'UI/HyperNet/TicketUnavailableError'
    not_enough_isk_error = 'UI/HyperNet/NotEnoughISKError'
    card_expired = 'UI/HyperNet/CardExpired'
    card_winner = 'UI/HyperNet/CardWinner'
    card_completed = 'UI/HyperNet/CardCompleted'
    card_show_winner = 'UI/HyperNet/CardShowWinner'
    card_claim_prize = 'UI/HyperNet/CardClaimPrize'
    wallet_balance = 'UI/HyperNet/WalletBalance'
    location = 'UI/HyperNet/Location'
    created_by = 'UI/HyperNet/CreatedBy'
    expires_in = 'UI/HyperNet/ExpiresIn'
    similar_raffles = 'UI/HyperNet/SimilarRaffles'
    claim_reward = 'UI/HyperNet/ClaimReward'
    reward_claimed = 'UI/HyperNet/RewardClaimed'
    view_more = 'UI/HyperNet/ViewMore'
    expiration_date = 'UI/HyperNet/ExpirationDate'
    completion_date = 'UI/HyperNet/CompletionDate'
    tickets = 'UI/HyperNet/Tickets'
    tab_browse = 'UI/HyperNet/TabNameBrowse'
    tab_my_raffles = 'UI/HyperNet/TabNameMyRaffles'
    tab_create = 'UI/HyperNet/TabNameCreate'
    confirm_purchase = 'UI/HyperNet/ConfirmPurchaseButtonLabel'
    purchase_ticket_hint = 'UI/HyperNet/PurchaseTicketHint'
    ticket_owner_hint = 'UI/HyperNet/TicketOwnerHint'
    ticket_owned_by_me_hint = 'UI/HyperNet/TicketOwnedByMeHint'
    created = 'UI/HyperNet/Created'
    completed = 'UI/HyperNet/Completed'
    active = 'UI/HyperNet/Active'
    joined = 'UI/HyperNet/Joined'
    won = 'UI/HyperNet/Won'
    buy_button_label = 'UI/HyperNet/BuyButtonLabel'
    create_information_tooltip = 'UI/HyperNet/CreateInformationTooltip'
    sales_tax = 'UI/HyperNet/SalesTax'
    earnings = 'UI/HyperNet/Earnings'
    duration = 'UI/HyperNet/Duration'
    open_market = 'UI/HyperNet/OpenMarket'
    open_nes = 'UI/HyperNet/OpenNES'
    tokens_tooltip = 'UI/HyperNet/TokensTooltip'
    tokens_required = 'UI/HyperNet/TokensRequired'
    token_location = 'UI/HyperNet/TokenLocation'
    token_missing = 'UI/HyperNet/TokenMissing'
    private_raffle = 'UI/HyperNet/PrivateRaffle'
    private_raffle_tooltip = 'UI/HyperNet/PrivateRaffleTooltip'
    private_raffle_hint = 'UI/HyperNet/PrivateRaffleHint'
    ticket_price = 'UI/HyperNet/TicketPrice'
    total_price = 'UI/HyperNet/TotalPrice'
    number_of_tickets = 'UI/HyperNet/NumberOfTickets'
    ticket_count_label = 'UI/HyperNet/TicketCountLabel'
    ticket_count = 'UI/HyperNet/TicketCount'
    missing_item = 'UI/HyperNet/MissingItem'
    create_button = 'UI/HyperNet/CreateButton'
    clear_button = 'UI/HyperNet/ClearButton'
    filter_item_label = 'UI/HyperNet/FilterItemLabel'
    filter_item_placeholder = 'UI/HyperNet/FilterItemPlaceholder'
    filter_location_label = 'UI/HyperNet/FilterLocationLabel'
    filter_location_placeholder = 'UI/HyperNet/FilterLocationPlaceholder'
    filter_history_placeholder = 'UI/HyperNet/FilterHistoryPlaceholder'
    create_success_title = 'UI/HyperNet/CreateSuccessTitle'
    create_success_message = 'UI/HyperNet/CreateSuccessMessage'
    create_failed_title = 'UI/HyperNet/CreateFailedTitle'
    view_raffle = 'UI/HyperNet/ViewRaffle'
    create_another = 'UI/HyperNet/CreateAnother'
    confirm_creation_failed = 'UI/HyperNet/ConfirmCreationFailed'
    creating = 'UI/HyperNet/Creating'
    created_by_player_hint = 'UI/HyperNet/CreatedByPlayerHint'
    multi_buy = 'UI/HyperNet/MultiBuy'
    link = 'UI/HyperNet/Link'
    link_hint = 'UI/HyperNet/LinkHint'
    link_button_hint = 'UI/HyperNet/LinkButtonHint'
    quick_buy_button_hint = 'UI/HyperNet/QuickBuyButtonHint'
    browse_banner_title = 'UI/HyperNet/BrowseBannerTitle'
    browse_banner_description = 'UI/HyperNet/BrowseBannerDescription'
    skip = 'UI/HyperNet/Skip'
    token_type_error = 'UI/HyperNet/TokenTypeError'
    token_amount_error = 'UI/HyperNet/TokenAmountError'
    token_owner_error = 'UI/HyperNet/TokenOwnerError'
    token_location_error = 'UI/HyperNet/TokenLocationError'
    item_type_error = 'UI/HyperNet/ItemTypeError'
    item_owner_error = 'UI/HyperNet/ItemOwnerError'
    item_location_error = 'UI/HyperNet/ItemLocationError'
    item_singleton_error = 'UI/HyperNet/ItemSingletonError'
    item_system_faction_error = 'UI/HyperNet/ItemSystemFactionError'
    ticket_price_error = 'UI/HyperNet/TicketPriceError'
    ticket_count_error = 'UI/HyperNet/TicketCountError'
    type_mismatch_error = 'UI/HyperNet/TypeMismatchError'
    token_payment_error = 'UI/HyperNet/TokenPaymentError'
    item_escrow_error = 'UI/HyperNet/ItemEscrowError'
    filter_all = 'UI/HyperNet/FilterAll'
    filter_joined = 'UI/HyperNet/FilterJoined'
    filter_created = 'UI/HyperNet/FilterCreated'
    minimum_price = 'UI/HyperNet/MinimumPrice'
    maximum_price = 'UI/HyperNet/MaximumPrice'
    average_price = 'UI/HyperNet/AveragePrice'
    historical_statistics = 'UI/HyperNet/HistoricalStatistics'
    active_statistics = 'UI/HyperNet/ActiveStatistics'
    filter_type_context_menu = 'UI/HyperNet/FilterTypeContextMenu'
    filter_group_context_menu = 'UI/HyperNet/FilterGroupContextMenu'
    filter_solar_system_context_menu = 'UI/HyperNet/FilterSolarSystemContextMenu'
    browse_type_context_menu = 'UI/HyperNet/BrowseTypeContextMenu'
    show_winner_context_menu = 'UI/HyperNet/ShowWinnerContextMenu'
    good_value_hint = 'UI/HyperNet/GoodValueHint'
    bad_value_hint = 'UI/HyperNet/BadValueHint'
    page_title_browse = 'UI/HyperNet/PageTitleBrowse'
    page_title_create = 'UI/HyperNet/PageTitleCreate'
    page_title_details = 'UI/HyperNet/PageTitleDetails'
    page_title_history = 'UI/HyperNet/PageTitleHistory'
    tutorial_welcome_title = 'UI/HyperNet/Tutorial/WelcomeTitle'
    tutorial_welcome_text = 'UI/HyperNet/Tutorial/WelcomeText'
    tutorial_browse_title = 'UI/HyperNet/Tutorial/BrowseTitle'
    tutorial_browse_text = 'UI/HyperNet/Tutorial/BrowseText'
    tutorial_buy_title = 'UI/HyperNet/Tutorial/BuyTitle'
    tutorial_buy_text = 'UI/HyperNet/Tutorial/BuyText'
    tutorial_win_title = 'UI/HyperNet/Tutorial/WinTitle'
    tutorial_win_text = 'UI/HyperNet/Tutorial/WinText'
    tutorial_lets_go = 'UI/HyperNet/Tutorial/LetsGo'
    tutorial_next = 'UI/HyperNet/Tutorial/Next'
    tutorial_got_it = 'UI/HyperNet/Tutorial/GotIt'
    tutorial_confirm_hint_title = 'UI/HyperNet/Tutorial/ConfirmHintTitle'
    tutorial_confirm_hint_text = 'UI/HyperNet/Tutorial/ConfirmHintText'
    tutorial_history_tab_hint_title = 'UI/HyperNet/Tutorial/HistoryTabHintTitle'
    tutorial_history_tab_hint_text = 'UI/HyperNet/Tutorial/HistoryTabHintText'
    my_tickets = 'UI/HyperNet/MyTickets'
    show_joined = 'UI/HyperNet/ShowJoined'
    show_created = 'UI/HyperNet/ShowCreated'
    show_active = 'UI/HyperNet/ShowActive'
    show_finished = 'UI/HyperNet/ShowFinished'
    show_public = 'UI/HyperNet/ShowPublic'
    show_private = 'UI/HyperNet/ShowPrivate'
    chip_price = 'UI/HyperNet/ChipPrice'
    chip_ticket_count = 'UI/HyperNet/ChipTicketCount'
    tagline = 'UI/HyperNet/BrowseBannerTagline'
    quantity_stack_hint = 'UI/HyperNet/CreateQuantityStackHint'
    reward_claim_failed = 'UI/HyperNet/ClaimItemFailed'
    filter_meta_group_label = 'UI/HyperNet/FilterMetaGroupLabel'
    filter_checkboxes = 'UI/HyperNet/FilterCheckboxes'
    chip_checkboxes = 'UI/HyperNet/ChipCheckboxes'
    sort_direction = 'UI/HyperNet/SortDirection'
    sort_default = 'UI/HyperNet/SortDefault'
    sort_item_name = 'UI/HyperNet/SortItemName'
    sort_end_time = 'UI/HyperNet/SortEndTime'
    ticket_owners = 'UI/HyperNet/TicketOwners'
    filter_blueprint_label = 'UI/HyperNet/FilterBlueprintLabel'
    blueprint_chip = 'UI/HyperNet/BlueprintChip'
    showing_filtered = 'UI/HyperNet/ShowingFiltered'
    multi_chip = 'UI/HyperNet/MultiChip'
    low_price_warning = 'UI/HyperNet/LowPriceWarning'
    save_filter_hint = 'UI/HyperNet/SaveFilterHint'
    saved_filters = 'UI/HyperNet/SavedFilters'
    no_saved_filters_hint = 'UI/HyperNet/NoSavedFiltersHint'
    delete_saved_filter = 'UI/HyperNet/DeleteSavedFilter'
    filter_name_prompt_caption = 'UI/HyperNet/FilterNamePromptCaption'
    filter_name_prompt_hint = 'UI/HyperNet/FilterNamePromptHint'
    no_filter_selected = 'UI/HyperNet/NoFilterSelected'
    filters = 'UI/Calendar/CalendarWindow/Filters'
    unknown_value = 'UI/Common/Unknown'
    no_data_available = 'UI/Common/NoDataAvailable'
    history_back = 'UI/Common/Previous'
    history_forward = 'UI/Common/Next'
    all_meta_groups = 'UI/Common/All'
    sort = 'UI/Common/SortBy'
    blueprint_original = 'UI/Generic/Original'
    blueprint_copy = 'UI/Generic/Copy'
    blueprint_all = 'UI/Generic/All'

    def __call__(self, **kwargs):
        try:
            template = _temporary_unlocalized_labels[self.value]
            if not isinstance(template, unicode):
                template = template.decode('utf8')
            tokens = _Tokenize(template)
            return eveLocalization.Parse(template, localization.const.LOCALE_SHORT_ENGLISH, tokens, **kwargs)
        except KeyError:
            return localization.GetByLabel(self.value, **kwargs)


error_messages = {errors.RaffleNotFoundError: Text.not_found_error,
 errors.TicketUnavailableError: Text.ticket_unavailable_error,
 errors.NotEnoughISKError: Text.not_enough_isk_error,
 errors.CreateErrorReason.token_payment: Text.token_payment_error,
 errors.CreateErrorReason.item_escrow: Text.item_escrow_error,
 errors.CreateErrorReason.token_type: Text.token_type_error,
 errors.CreateErrorReason.token_amount: Text.token_amount_error,
 errors.CreateErrorReason.token_owner: Text.token_owner_error,
 errors.CreateErrorReason.token_location: Text.token_location_error,
 errors.CreateErrorReason.token_inventory: Text.token_location_error,
 errors.CreateErrorReason.item_type: Text.item_type_error,
 errors.CreateErrorReason.item_owner: Text.item_owner_error,
 errors.CreateErrorReason.item_location: Text.item_location_error,
 errors.CreateErrorReason.item_inventory: Text.item_location_error,
 errors.CreateErrorReason.item_singleton: Text.item_singleton_error,
 errors.CreateErrorReason.item_triglavian_system: Text.item_system_faction_error,
 errors.CreateErrorReason.ticket_price: Text.ticket_price_error,
 errors.CreateErrorReason.ticket_count: Text.ticket_count_error,
 errors.CreateErrorReason.type_mismatch: Text.type_mismatch_error}

def get_error_message(error, **kwargs):
    if isinstance(error, errors.RafflesError):
        key = error.__class__
    else:
        key = error
    text = error_messages.get(key, None)
    if text:
        return text(**kwargs)
    return Text.unknown_error()


blueprint_types = {BlueprintType.all: Text.blueprint_all,
 BlueprintType.original: Text.blueprint_original,
 BlueprintType.copy: Text.blueprint_copy}

def get_blueprint_type_name(blueprint_type):
    return blueprint_types[blueprint_type]()


_temporary_unlocalized_labels = {}
