#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\factionwarfare\activity\client\noticeMessenger.py
from eveProto.generated.eve_public.faction.activity.activity_pb2 import ScoreContributionNotice
from eveProto.generated.eve_public.faction.activity.activity_pb2 import SolarSystemScoresNotice
from factionwarfare.activity import Score, SolarSystemScores
from signals import Signal

class NoticeMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(SolarSystemScoresNotice, self._on_solar_system_scores_notice)
        self.public_gateway.subscribe_to_notice(ScoreContributionNotice, self._on_score_contribution_notice)
        self.on_solar_system_scores_notice = Signal()
        self.on_score_contribution_notice = Signal()

    def _on_solar_system_scores_notice(self, solar_system_scores, _notice_primitive):
        scores = []
        for score in solar_system_scores.scores:
            scores.append(Score(score.faction.sequential, score.contribution, score.floor))

        self.on_solar_system_scores_notice(SolarSystemScores(solar_system_scores.solar_system.sequential, scores))

    def _on_score_contribution_notice(self, score_contribution, _notice_primitive):
        self.on_score_contribution_notice(score_contribution.solar_system.sequential, score_contribution.contributor.sequential, score_contribution.faction.sequential, score_contribution.contribution)
