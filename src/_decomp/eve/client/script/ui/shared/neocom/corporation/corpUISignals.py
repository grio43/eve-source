#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corpUISignals.py
from signals import Signal
on_corporation_changed = Signal('corpUISignals.on_corporation_changed(corp_id)')
on_corporation_application_changed = Signal('corpUISignals.on_corporation_application_changed')
on_corporation_recruitment_ad_changed = Signal('corpUISignals.on_corporation_recruitment_ad_changed')
on_corporation_medal_added = Signal('corpUISignals.on_corporation_medal_added')
on_sanctioned_action_changed = Signal('corpUISignals.on_sanctioned_action_changed')
on_vote_case_changed = Signal('corpUISignals.on_vote_case_changed')
on_vote_cast = Signal('corpUISignals.on_vote_cast')
on_war_changed = Signal('corpUISignals.on_war_changed')
on_title_changed = Signal('corpUISignals.on_title_changed')
on_alliance_application_changed = Signal('corpUISignals.on_alliance_application_changed')
on_alliance_member_changed = Signal('corpUISignals.on_alliance_member_changed')
on_alliance_relationship_changed = Signal('corpUISignals.on_alliance_relationship_changed')
on_alliance_changed = Signal('corpUISignals.on_alliance_changed(alliance_id, change)')
