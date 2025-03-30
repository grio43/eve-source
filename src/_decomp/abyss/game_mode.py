#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\abyss\game_mode.py
import abc
from abyss.error import Error
import evetypes
import abyss.const

class GameModeID(object):
    UNKNOWN = -1
    SOLO = 1
    COOP = 2
    TWO_PLAYER = 3


class AbyssGameModeBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def id(self):
        pass

    @classmethod
    def get_allowed_ships(cls):
        return evetypes.GetTypeIDsByListID(cls.allowed_ships_list_id)

    @classmethod
    def is_ship_allowed(cls, type_id):
        if cls.allowed_ships_list_id == -1:
            return True
        return type_id in cls.get_allowed_ships()

    @abc.abstractproperty
    def allowed_ships_list_id(self):
        pass

    @abc.abstractproperty
    def content_type(self):
        pass

    @abc.abstractproperty
    def jump_description_label(self):
        pass

    @abc.abstractproperty
    def key_stack_size(self):
        pass

    @abc.abstractproperty
    def max_players(self):
        pass

    @abc.abstractproperty
    def ship_restriction_error_id(self):
        pass

    @abc.abstractproperty
    def should_jump_on_deploy(self):
        pass

    @property
    def is_fleet_required(self):
        return self.is_multiplayer

    @property
    def is_locked_to_creator(self):
        return True

    @property
    def is_multiplayer(self):
        return self.max_players > 1


class AbyssSoloGameMode(AbyssGameModeBase):
    id = GameModeID.SOLO
    allowed_ships_list_id = 57
    content_type = abyss.const.CRUISER_SOLO_CONTENT
    max_players = 1
    key_stack_size = 1
    ship_restriction_error_id = Error.INVALID_SHIP_TYPE
    should_jump_on_deploy = True
    jump_description_label = 'UI/Abyss/AbyssSoloEntranceShortDescription'


class AbyssCoOpGameMode(AbyssGameModeBase):
    id = GameModeID.COOP
    allowed_ships_list_id = 92
    content_type = abyss.const.FRIGATE_FLEET_CONTENT
    max_players = 3
    key_stack_size = 3
    ship_restriction_error_id = Error.INVALID_SHIP_TYPE_THREE_PLAYER
    should_jump_on_deploy = False
    jump_description_label = 'UI/Abyss/AbyssFleetEntranceShortDescription'


class AbyssTwoPlayerGameMode(AbyssGameModeBase):
    id = GameModeID.TWO_PLAYER
    allowed_ships_list_id = 233
    content_type = abyss.const.TWO_PLAYER_DESTROYERS
    max_players = 2
    key_stack_size = 2
    ship_restriction_error_id = Error.INVALID_SHIP_TYPE_TWO_PLAYER
    should_jump_on_deploy = False
    jump_description_label = 'UI/Abyss/AbyssTwoPlayerEntranceShortDescription'


class UnknownGameMode(AbyssGameModeBase):
    id = GameModeID.UNKNOWN
    allowed_ships_list_id = -1
    content_type = -1
    max_players = -1
    key_stack_size = -1
    ship_restriction_error_id = -1
    should_jump_on_deploy = False
    jump_description_label = 'UI/Abyss/AbyssFleetEntranceShortDescription'


def get_game_mode(game_mode_id):
    if game_mode_id == GameModeID.SOLO:
        return AbyssSoloGameMode()
    if game_mode_id == GameModeID.COOP:
        return AbyssCoOpGameMode()
    if game_mode_id == GameModeID.TWO_PLAYER:
        return AbyssTwoPlayerGameMode()
    if game_mode_id == GameModeID.UNKNOWN:
        return UnknownGameMode()
