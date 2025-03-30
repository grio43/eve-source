#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\common\challenge.py


class ChallengeData(object):
    challenge_id = None
    challenge_type_id = None
    character_id = None
    event_type = None
    expiration_date = None
    finish_date = None
    isk_awarded = None
    max_progress = None
    message_text = None
    name = None
    challenge_category = None
    points_awarded = None
    progress = None
    progress_text = None
    received_date = None
    season_id = None
    start_date = None
    should_be_active_on_season_start = None
    should_only_appear_once_per_season = None
    next_challenge = None
    is_chained = None
    should_not_expire_at_downtime = None
    reward_type = None
    reward_amount = None
    reward_type_soul_bound = None

    def __copy__(self):
        newone = ChallengeData()
        newone.__dict__.update(self.__dict__)
        return newone


class Challenge(ChallengeData):

    def __init__(self, challenge_fsd_data, challenge_db_row):
        if challenge_db_row.finishDate or challenge_db_row.rewardDate:
            progress = challenge_fsd_data['max_progress']
        else:
            progress = challenge_db_row.progress
        self.challenge_id = challenge_db_row.challengeID
        self.challenge_type_id = challenge_db_row.challengeTypeID
        self.character_id = challenge_db_row.characterID
        self.event_type = challenge_fsd_data['event_type']
        self.expiration_date = challenge_db_row.expirationDate
        self.finish_date = challenge_db_row.finishDate
        self.is_expired = challenge_db_row.isExpired
        self.max_progress = challenge_fsd_data['max_progress']
        self.message_text = challenge_fsd_data['message_text']
        self.challenge_category = challenge_fsd_data['challenge_category']
        self.challenge_security = challenge_fsd_data['challenge_security']
        self.name = challenge_fsd_data['name']
        self.points_awarded = challenge_fsd_data['points_awarded']
        self.isk_awarded = challenge_fsd_data['isk_awarded']
        self.progress = progress
        self.progress_text = challenge_fsd_data['progress_text']
        self.is_coop = challenge_fsd_data['is_coop']
        self.expiration_minutes = challenge_fsd_data['expiration_time_minutes']
        self.received_date = challenge_db_row.receivedDate
        self.season_id = challenge_db_row.seasonID
        self.start_date = challenge_db_row.startDate
        self.should_be_active_on_season_start = challenge_fsd_data['should_be_active_on_season_start']
        self.should_only_appear_once_per_season = challenge_fsd_data['should_only_appear_once_per_season']
        self.next_challenge = challenge_fsd_data['next_challenge']
        self.is_chained = challenge_fsd_data['is_chained']
        self.should_not_expire_at_downtime = challenge_fsd_data['should_not_expire_at_downtime']
        self.is_dormant = challenge_db_row.finishDate and not challenge_db_row.isExpired
        self.reward_type = challenge_fsd_data['reward_type']
        self.reward_amount = challenge_fsd_data['reward_amount']
        self.reward_date = challenge_db_row.rewardDate
        self.reward_type_soul_bound = challenge_fsd_data['reward_type_soul_bound']

    def has_completion_rewards(self):
        if self.points_awarded > 0:
            return True
        if self.isk_awarded > 0:
            return True
        if self.reward_type is not None and self.reward_amount > 0:
            return True
        return False

    def has_ungranted_completion_rewards(self):
        if not self.has_completion_rewards():
            return False
        return self.reward_date is None

    def has_unclaimed_completion_rewards(self):
        if not self.has_completion_rewards():
            return False
        return self.reward_date is not None and self.finish_date is None and not self.is_dormant

    def is_progress_complete(self):
        return self.progress >= self.max_progress
