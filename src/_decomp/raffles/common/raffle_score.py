#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\common\raffle_score.py
import gametime
import mathext

def get_raffle_score(raffle):
    elapsed_percentage = _elapsed_percentage(raffle)
    sold_percentage = _sold_percentage(raffle)
    score = lerp_scoring(elapsed_percentage, sold_percentage)
    try:
        if raffle.estimated_price:
            score = _price_quality(score, raffle)
    except Exception:
        pass

    return score


def _price_quality(score, raffle):
    fraction = raffle.ticket_count * raffle.ticket_price / raffle.estimated_price
    threshold = 0.4
    score_adjuster = fraction + threshold
    score_adjuster = 1 / pow(max(1, score_adjuster), 2)
    return score * score_adjuster


def _elapsed_percentage(raffle):
    start = raffle.creation_time
    end = raffle.expiration_time
    now = gametime.GetWallclockTime()
    return (now - start) / float(end - start)


def _sold_percentage(raffle):
    return raffle.tickets_sold / float(raffle.ticket_count)


def lerp_scoring(elapsed_time, tickets):
    elapsed_time = min(1, elapsed_time)
    etime = 1 - elapsed_time
    l_score = 0.5 + 0.5 * mathext.lerp(tickets ** 2, -elapsed_time, elapsed_time)
    l_score = l_score + 0.5 * tickets * etime
    l_score = l_score * (etime + 1 + tickets)
    l_score = l_score ** 1.5
    return l_score
