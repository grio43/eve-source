#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fuzzy\jaro.py


def jaro(left, right):
    return _jaro_winkler(left, right, winklerize=False)


def jaro_winkler(left, right, long_tolerance = False):
    return _jaro_winkler(left, right, long_tolerance=long_tolerance)


def _jaro_winkler(left, right, long_tolerance = False, winklerize = True):
    left_len = len(left)
    right_len = len(right)
    if not left_len or not right_len:
        return 0.0
    min_len = max(left_len, right_len)
    search_range = min_len // 2 - 1
    if search_range < 0:
        search_range = 0
    left_flags = [False] * left_len
    right_flags = [False] * right_len
    common_chars = 0
    for i, left_ch in enumerate(left):
        low = i - search_range if i > search_range else 0
        hi = i + search_range if i + search_range < right_len else right_len - 1
        for j in range(low, hi + 1):
            if not right_flags[j] and right[j] == left_ch:
                left_flags[i] = right_flags[j] = True
                common_chars += 1
                break

    if not common_chars:
        return 0.0
    k = trans_count = 0
    for i, left_f in enumerate(left_flags):
        if left_f:
            for j in range(k, right_len):
                if right_flags[j]:
                    k = j + 1
                    break

            if left[i] != right[j]:
                trans_count += 1

    trans_count /= 2
    common_chars = float(common_chars)
    weight = (common_chars / left_len + common_chars / right_len + (common_chars - trans_count) / common_chars) / 3
    if winklerize and weight > 0.7 and left_len > 3 and right_len > 3:
        j = min(min_len, 4)
        i = 0
        while i < j and left[i] == right[i] and left[i]:
            i += 1

        if i:
            weight += i * 0.1 * (1.0 - weight)
        if long_tolerance and min_len > 4 and common_chars > i + 1 and 2 * common_chars >= min_len + i:
            weight += (1.0 - weight) * (float(common_chars - i - 1) / float(left_len + right_len - i * 2 + 2))
    return weight
