#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\sequencing_job.py
import datetime
from cosmetics.client.ships.skins.errors import convert_sequencing_error_to_proto, convert_sequencing_error_from_proto
from datetimeutils import datetime_to_filetime
from eve.common.lib import appConst
from itertoolsext.Enum import Enum
from google.protobuf.timestamp_pb2 import Timestamp
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.sequencing.job.job_pb2 import Attributes
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.thirdparty_pb2 import Identifier as SkinIdentifier
from eveProto.generated.eve_public.character.character_pb2 import Identifier as CharacterIdentifier
from localization import GetByLabel, formatters
from localization.formatters import dateTimeFormatters, timeIntervalFormatters

@Enum

class SequencingJobState(object):
    PENDING = 'PENDING'
    STARTED = 'STARTED'
    FAILED = 'FAILED'
    COMPLETED = 'COMPLETED'


class SequencingJob(object):

    def __init__(self, job_id, hex_id, char_id, nb_runs):
        self._job_id = job_id
        self._skin_hex = hex_id
        self._character_id = char_id
        self._nb_runs = nb_runs
        self._state = None
        self._time_started = None
        self._time_completed = None
        self._planned_completion_time = None
        self._failure_error = None

    @property
    def job_id(self):
        return self._job_id

    @property
    def character_id(self):
        return self._character_id

    @property
    def skin_hex(self):
        return self._skin_hex

    @property
    def nb_runs(self):
        return self._nb_runs

    @property
    def state(self):
        return self._state

    @property
    def time_started(self):
        if self._state != SequencingJobState.PENDING:
            return self._time_started

    @property
    def time_completed(self):
        if self._state in [SequencingJobState.COMPLETED, SequencingJobState.FAILED]:
            return self._time_completed

    @property
    def time_remaining(self):
        if self.state != SequencingJobState.STARTED:
            return None
        time_remaining = self.planned_completion_time - datetime.datetime.now()
        if time_remaining < datetime.timedelta(0):
            return None
        return time_remaining

    def get_completed_ratio(self):
        if self.state == SequencingJobState.COMPLETED:
            return 1.0
        elif self.state == SequencingJobState.STARTED:
            seconds_total = (self.planned_completion_time - self.time_started).total_seconds()
            if self.time_remaining:
                ratio = 1.0 - self.time_remaining.total_seconds() / float(seconds_total)
            else:
                ratio = 1.0
            return max(0.0, min(ratio, 1.0))
        else:
            return 0.0

    def get_time_remaining_text(self):
        if not self.time_remaining:
            return None
        seconds = int(self.time_remaining.total_seconds() * appConst.SEC)
        if seconds > appConst.HOUR:
            time_left = timeIntervalFormatters.FormatTimeIntervalShortWritten(seconds, showTo='minute')
        else:
            time_left = timeIntervalFormatters.FormatTimeIntervalShortWritten(seconds)
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/TimeLeft', time_left=time_left)

    @property
    def planned_completion_time(self):
        return self._planned_completion_time

    @property
    def failure_error(self):
        return self._failure_error

    def is_active(self):
        return self.state in [SequencingJobState.STARTED]

    def copy_data_from_other(self, job):
        self._skin_hex = job.skin_hex
        self._character_id = job.character_id
        self._nb_runs = job.nb_runs
        self._state = job.state
        self._time_started = job.time_started
        self._time_completed = job.time_completed
        self._planned_completion_time = job.planned_completion_time
        self._failure_error = job.failure_error

    def admin_set_state(self, state):
        self._state = state

    def admin_set_started_time(self, time):
        self._time_started = time

    def admin_set_completed_time(self, time):
        self._time_completed = time

    def admin_set_planned_completion_time(self, time):
        self._planned_completion_time = time

    def admin_set_failure_error(self, value):
        self._failure_error = value

    def __eq__(self, other):
        return self.job_id == other.job_id and self.character_id == other.character_id and self.skin_hex == other.skin_hex and self.nb_runs == other.nb_runs and self.state == other.state

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def build_from_proto(job_id, payload):
        job = SequencingJob(job_id=job_id, hex_id=payload.skin.hex, char_id=payload.sequencer.sequential, nb_runs=payload.quantity)
        if payload.HasField('pending'):
            job._state = SequencingJobState.PENDING
        elif payload.HasField('started'):
            job._state = SequencingJobState.STARTED
            job._time_started = datetime.datetime.fromtimestamp(payload.started.seconds)
        elif payload.HasField('failed'):
            job._state = SequencingJobState.FAILED
            job._failure_error = convert_sequencing_error_from_proto(payload.failed)
        elif payload.HasField('completed'):
            job._state = SequencingJobState.COMPLETED
            job._time_completed = datetime.datetime.fromtimestamp(payload.completed.seconds)
        job._planned_completion_time = datetime.datetime.fromtimestamp(payload.planned_completion.seconds)
        return job

    @staticmethod
    def build_proto_from_job(sequencing_job, hex_id):
        planned_completion = Timestamp()
        planned_completion.FromDatetime(sequencing_job.planned_completion_time)
        proto_job = Attributes(skin=SkinIdentifier(hex=hex_id), sequencer=CharacterIdentifier(sequential=sequencing_job.character_id), quantity=sequencing_job.nb_runs, planned_completion=planned_completion)
        if sequencing_job.state == SequencingJobState.PENDING:
            proto_job.pending = True
        elif sequencing_job.state == SequencingJobState.STARTED:
            started_time = Timestamp()
            started_time.FromDatetime(sequencing_job.time_started)
            proto_job.started.CopyFrom(started_time)
        elif sequencing_job.state == SequencingJobState.FAILED:
            proto_job.failed = convert_sequencing_error_to_proto(sequencing_job.failure_error)
        elif sequencing_job.state == SequencingJobState.COMPLETED:
            completed_time = Timestamp()
            completed_time.FromDatetime(sequencing_job.time_completed)
            proto_job.completed.CopyFrom(completed_time)
        return proto_job
