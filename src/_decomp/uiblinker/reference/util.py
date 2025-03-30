#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\reference\util.py


def iter_element_tree(root):
    pending = [root]
    while pending:
        element = pending.pop(-1)
        yield element
        pending.extend(reversed(getattr(element, 'children', [])))
