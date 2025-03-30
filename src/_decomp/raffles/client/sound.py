#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\sound.py
import collections
import datetime
import eveui
import uthread2
button_hover = eveui.Sound.button_hover.value
button_click = eveui.Sound.button_click.value
browse_show_raffles = eveui.Sound.add_or_use.value
browse_hide_raffles = eveui.Sound.remove.value
browse_no_raffles = 'raffle_hypernode_all_owned_play'
card_hover = eveui.Sound.entry_hover.value
card_click = eveui.Sound.button_click.value
card_ticket_update = 'raffle_buy_ticket2_play'
card_ticket_update_urgent = 'raffle_buy_ticket3_play'
card_finished = 'raffle_item_highlight_play'
card_sweep = ''
ticket_hover = eveui.Sound.entry_hover.value
ticket_enter_confirm = 'raffle_item_select_play'
ticket_exit_confirm = eveui.Sound.collapse.value
ticket_confirmed = 'raffle_letter_selection_choice_play'
ticket_sold = 'raffle_buy_ticket4_play'
ticket_sold_to_other = eveui.Sound.close.value
ticket_error = 'raffle_hypernode_all_owned_play'
create_item_changed = 'raffle_item_select_play'
create_success = 'raffle_buy_ticket2_play'
create_failure = 'raffle_hypernode_all_owned_play'
confirm_button_on = 'raffle_item_select_play'
confirm_button_off = eveui.Sound.collapse.value
confirm_button_confirmed = 'raffle_letter_selection_choice_play'
filters_expand = eveui.Sound.expand.value
filters_collapse = eveui.Sound.collapse.value
fanfare_intro = 'raffle_enter_play'
fanfare_loop_play = 'raffle_atmo_loop_play'
fanfare_loop_stop = 'raffle_atmo_loop_stop'
fanfare_outro_win = 'raffle_celebration_win_play'
fanfare_outro_lose = 'raffle_lose_play'
fanfare_show_options = 'raffle_item_select_confirm_play'
fanfare_move_to_slot = 'raffle_letter_selection_choice_play'
fanfare_lock_in_slot = 'raffle_letter_fail_play'
fanfare_show_full_ticket = 'raffle_letter_fail_play'
fanfare_tickets_open = 'notify_slide_open_play'
fanfare_tickets_shrink = 'notify_slide_close_play'
throttled_sounds = {ticket_sold: 0.1,
 ticket_sold_to_other: 0.1,
 card_ticket_update: 0.1,
 card_ticket_update_urgent: 0.1}

class SoundController(object):

    def __init__(self, **throttled):
        self._throttled = {}
        for sound_event_name, throttle_duration in throttled.iteritems():
            self._throttled[sound_event_name] = datetime.timedelta(seconds=throttle_duration)

        self._last_played = collections.defaultdict(lambda : datetime.datetime.min)

    def play(self, sound_event_name, time_offset = None):
        if time_offset is not None:

            def sleeper():
                uthread2.sleep(time_offset)
                self.play(sound_event_name)

            uthread2.start_tasklet(sleeper)
            return
        if sound_event_name in self._throttled:
            now = datetime.datetime.now()
            throttle_duration = self._throttled[sound_event_name]
            last_played = self._last_played[sound_event_name]
            if now - last_played < throttle_duration:
                return
            self._last_played[sound_event_name] = now
        eveui.play_sound(sound_event_name)


_controller = SoundController(**throttled_sounds)
play = _controller.play
