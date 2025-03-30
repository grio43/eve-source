#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveservices\roles.py
from cluster import SERVICE_ALL

def has_any_role(session, role):
    return bool(session.role & role)


def has_specific_role(session, role):
    return bool(session.role & role == role)


def remove_role(role, role_to_remove):
    role_mask = SERVICE_ALL ^ role_to_remove
    return role & role_mask


def add_role(role, role_to_add):
    return role | role_to_add
