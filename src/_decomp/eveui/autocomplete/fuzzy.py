#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\fuzzy.py
from __future__ import absolute_import
import eveformat
import fuzzy
from eve.client.script.ui import eveThemeColor

def fuzzy_match(query, text, config = None):
    if config is None:
        config = DEFAULT_SCORE_CONFIG
    return fuzzy.sublime(query, text, config)


def get_highlighted_string(text, query, matcher = None, highlight = None):
    if not query:
        return text
    if matcher is None:
        matcher = lambda _query, _text: fuzzy_match(_query, _text)[2]
    matched_segments = matcher(query, text)
    if not matched_segments:
        return text
    if highlight is None:
        highlight = default_highlight
    return highlight_segments(text, matched_segments, highlight=highlight)


def highlight_segments(text, segments, highlight):
    parts = []
    last_segment_end = 0
    for start, end in segments:
        if start - last_segment_end > 0:
            parts.append(text[last_segment_end:start])
        parts.append(highlight(text[start:end]))
        last_segment_end = end

    if last_segment_end < len(text):
        parts.append(text[last_segment_end:])
    return u''.join(parts)


def default_highlight(text):
    return eveformat.bold(eveformat.color(text, eveThemeColor.THEME_ACCENT))


DEFAULT_SCORE_CONFIG = fuzzy.SublimeScoreConfig(sequential_bonus=15, separator_bonus=15, camel_bonus=0, first_letter_bonus=15, leading_letter_penalty=-5, max_leading_letter_penalty=-15, unmatched_letter_penalty=-1)
