#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fuzzy\levenshtein.py


def levenshtein(left, right):
    if left == right:
        return 0
    rows = len(left) + 1
    cols = len(right) + 1
    if not left:
        return cols - 1
    if not right:
        return rows - 1
    previous = None
    current = range(cols)
    for r in range(1, rows):
        previous, current = current, [r] + [0] * (cols - 1)
        for c in range(1, cols):
            deletion = previous[c] + 1
            insertion = current[c - 1] + 1
            edit = previous[c - 1] + (0 if left[r - 1] == right[c - 1] else 1)
            current[c] = min(edit, deletion, insertion)

    return current[-1]
