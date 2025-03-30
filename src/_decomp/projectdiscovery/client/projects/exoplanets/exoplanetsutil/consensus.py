#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\exoplanetsutil\consensus.py


def convert_consensus_response_to_consensus_data(consensus_response):
    try:
        vote_info = consensus_response['task']['voteInfo']
        bucket_count = vote_info['bucketCount']
        min_time = vote_info['minEpoch']
        max_time = vote_info['maxEpoch']
        bucket_votes = consensus_response['task']['votes']['transits']
        total_classifications = consensus_response['task']['classificationCount']
        bucket_percentages = {i:0.0 for i in xrange(bucket_count)}
        for bucket in bucket_votes:
            bucket_index = bucket['r']
            number_of_votes = bucket['vc']
            bucket_percentages[bucket_index] = float(number_of_votes) / total_classifications

        transit_buckets = [ (lerp(min_i, bucket_count, min_time, max_time), lerp(max_i, bucket_count, min_time, max_time), bucket_percentages[min_i]) for min_i, max_i in zip(range(bucket_count), range(1, bucket_count + 1)) ]
        return transit_buckets
    except:
        return None


def lerp(bucket_index, bucket_count, min_time, max_time):
    t = float(bucket_index) / bucket_count
    return (1.0 - t) * min_time + t * max_time


def get_vote_stats(consensus_response):
    total_classifications = consensus_response['task']['classificationCount']
    no_transits = consensus_response['task']['votes']['noTransit'] if 'votes' in consensus_response['task'] and 'noTransit' in consensus_response['task']['votes'] else 0
    no_transits = total_classifications if not no_transits and 'votes' not in consensus_response['task'] or 'transits' not in consensus_response['task']['votes'] else no_transits
    number_of_transit_marking_players = total_classifications - no_transits
    return (number_of_transit_marking_players, total_classifications)
