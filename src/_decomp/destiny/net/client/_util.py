#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\destiny\net\client\_util.py
import collections

def merge_state_into_history(state, history_list, wait_for_bubble):
    entries_by_time = collections.defaultdict(list)
    for entry in state:
        entries_by_time[entry[0]].append(entry)

    time_list = sorted(entries_by_time.iterkeys())
    time_list_idx = 0
    for history_idx, history_time_entries in enumerate(history_list):
        history_time = history_time_entries[0][0][0]
        entry_time = time_list[time_list_idx]
        if history_time < entry_time:
            wait_for_bubble = False
            continue
        if history_time == entry_time:
            history_time_entries[0].extend(entries_by_time[entry_time])
            history_time_entries[1] = False
        else:
            history_list.insert(history_idx, [entries_by_time[entry_time], wait_for_bubble])
            wait_for_bubble = False
        time_list_idx += 1
        if time_list_idx >= len(time_list):
            break

    for tl_idx in xrange(time_list_idx, len(time_list)):
        history_list.append([entries_by_time[time_list[tl_idx]], wait_for_bubble])
