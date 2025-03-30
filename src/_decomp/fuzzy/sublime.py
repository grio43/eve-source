#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fuzzy\sublime.py


def sublime(pattern, string, config = None):
    if config is None:
        config = SublimeScoreConfig()
    matched, score, matches = _match_recursive(pattern=pattern, string=string, pattern_current_index=0, string_current_index=0, source_matches=None, matches=[], max_matches=256, recursion_count=0, recursion_limit=10, config=config)
    matches = [ (start, end) for start, end in _iter_segments(matches) ]
    return (matched, score, matches)


class SublimeScoreConfig(object):

    def __init__(self, sequential_bonus = 15, separator_bonus = 30, camel_bonus = 30, first_letter_bonus = 15, leading_letter_penalty = -5, max_leading_letter_penalty = -15, unmatched_letter_penalty = -1, reset_sequence_on_space = True):
        self.sequential_bonus = sequential_bonus
        self.separator_bonus = separator_bonus
        self.camel_bonus = camel_bonus
        self.first_letter_bonus = first_letter_bonus
        self.leading_letter_penalty = leading_letter_penalty
        self.max_leading_letter_penalty = max_leading_letter_penalty
        self.unmatched_letter_penalty = unmatched_letter_penalty
        self.reset_sequence_on_space = reset_sequence_on_space


def _match_recursive(pattern, string, pattern_current_index, string_current_index, source_matches, matches, max_matches, recursion_count, recursion_limit, config):
    out_score = 0
    recursion_count += 1
    if recursion_count >= recursion_limit:
        return (False, out_score, matches)
    if pattern_current_index == len(pattern) or string_current_index == len(string):
        return (False, out_score, matches)
    recursive_match = False
    best_recursive_matches = []
    best_recursive_score = 0
    first_match = True
    while pattern_current_index < len(pattern) and string_current_index < len(string):
        if pattern[pattern_current_index].lower() == string[string_current_index].lower():
            if len(matches) >= max_matches:
                return (False, out_score, matches)
            if first_match and source_matches:
                matches = source_matches[:]
                first_match = False
            matched, recursive_score, recursive_matches = _match_recursive(pattern=pattern, string=string, pattern_current_index=pattern_current_index, string_current_index=string_current_index + 1, source_matches=matches, matches=[], max_matches=max_matches, recursion_count=recursion_count, recursion_limit=recursion_limit, config=config)
            if matched:
                if not recursive_match or recursive_score > best_recursive_score:
                    best_recursive_matches = recursive_matches[:]
                    best_recursive_score = recursive_score
                recursive_match = True
            matches.append(string_current_index)
            pattern_current_index += 1
        string_current_index += 1

    matched = pattern_current_index == len(pattern)
    if matched:
        out_score = 100
        out_score += min(config.leading_letter_penalty * matches[0], config.max_leading_letter_penalty)
        unmatched = len(string) - len(matches)
        out_score += config.unmatched_letter_penalty * unmatched
        adjacency_multiplier = 1
        for i in range(len(matches)):
            current_index = matches[i]
            if i > 0:
                previous_index = matches[i - 1]
                is_space = string[current_index] == ' '
                sequence_broken = config.reset_sequence_on_space and is_space
                if current_index == previous_index + 1 and not sequence_broken:
                    out_score += config.sequential_bonus * adjacency_multiplier
                    adjacency_multiplier *= 2
                else:
                    adjacency_multiplier = 1
            if current_index == 0:
                out_score += config.first_letter_bonus
            else:
                neighbor = string[current_index - 1]
                current = string[current_index]
                if neighbor == neighbor.lower() and current == current.lower():
                    out_score += config.camel_bonus
                if neighbor in '_ ':
                    out_score += config.separator_bonus

    if recursive_match and (not matched or best_recursive_score > out_score):
        return (True, best_recursive_score, best_recursive_matches)
    return (matched, out_score, matches)


def _iter_segments(indices):
    if not indices:
        return
    start = None
    previous = None
    for index in indices:
        if start is None:
            start = index
            previous = index
            continue
        if index > previous + 1:
            yield (start, previous + 1)
            start = index
        previous = index

    if start is not None:
        yield (start, previous + 1)
