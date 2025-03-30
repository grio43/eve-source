#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\ballparks.py
import evetypes
from eveexceptions import UserError
from inventorycommon.const import categoryShip
try:
    import geo2
except ImportError:
    geo2 = None

def check_ball_released(ball, raises = ReferenceError):
    if ball.broker is None:
        raise raises


def get_ball_position(task, ball_id):
    ball = task.context.ballpark.balls[ball_id]
    return (ball.x, ball.y, ball.z)


def get_ball_positions(task, ball_ids):
    return [ get_ball_position(task, ball_id) for ball_id in ball_ids if is_ball_in_park(task, ball_id) and not is_ball_cloaked(task, ball_id) ]


def get_ball_warp_to_position(task, ball_id):
    try:
        ball = get_ball(task, ball_id)
        return (ball.gotoX, ball.gotoY, ball.gotoZ)
    except (UserError, RuntimeError):
        return None


def is_ball_in_park(task, ball_id):
    return ball_id in task.context.ballpark.balls


def is_ball_in_range(task, ball1_id, ball2_id, required_range):
    distance = get_distance_between(task, ball1_id, ball2_id)
    if distance is not None and distance <= required_range:
        return True
    return False


def get_distance_between(task, ball1_id, ball2_id):
    return task.context.ballpark.GetSurfaceDist(ball1_id, ball2_id)


def is_coordinate_in_range(task, coordinate, required_range):
    my_coordinate = get_ball_position(task, task.context.myBall.id)
    distance = geo2.Vec3DistanceD(coordinate, my_coordinate)
    return distance <= required_range


def is_coordinate_in_range_of_ball(task, ball_id, coordinates, required_range):
    ball_coordinate = get_ball_position(task, ball_id)
    distance = geo2.Vec3DistanceD(ball_coordinate, coordinates)
    return distance <= required_range


def get_item_owner(task, item_id):
    slim_item = task.context.ballpark.slims.get(item_id)
    if slim_item is None:
        return
    return slim_item.ownerID


def is_ball_cloaked(task, ball_id):
    is_cloaked = False
    try:
        is_cloaked = task.context.ballpark.IsCloaked(ball_id)
    except (UserError, RuntimeError):
        pass

    return is_cloaked


def get_ball(task, ball_id):
    return task.context.ballpark.GetBall(ball_id)


def get_balls_in_bubble(task, bubble_id):
    return task.context.ballpark.bubbles.get(bubble_id)


def get_ship_balls_in_bubble(task, bubble_id):
    return task.context.ballpark.GetShipsInBubble(bubble_id)


def get_slim_item(task, ball_id):
    return task.context.ballpark.GetSlimItem(ball_id)


def get_ball_type_id(task, ball_id):
    slim_item = get_slim_item(task, ball_id)
    if slim_item is not None:
        return slim_item.typeID


def get_my_position(task):
    return (task.context.myBall.x, task.context.myBall.y, task.context.myBall.z)


def is_invulnerable(task, item_id):
    return task.context.ballpark.IsInvulnerable(item_id)


def is_target_valid(task, target_id, target_list = None, required_types = None, requires_groups = None, required_categories = None):
    if target_id is None:
        return False
    slim_item = get_slim_item(task, target_id)
    if slim_item is None:
        return False
    elif target_list is not None and target_id not in target_list:
        return False
    elif required_types and slim_item.typeID not in required_types:
        return False
    elif requires_groups and slim_item.groupID not in requires_groups:
        return False
    elif required_categories and slim_item.categoryID not in required_categories:
        return False
    elif is_ball_cloaked(task, target_id):
        return False
    else:
        return True


def is_ship(task, item_id):
    slim_item = get_slim_item(task, item_id)
    return slim_item is not None and slim_item.categoryID == categoryShip


def get_specific_globals(task, type_id = None, group_id = None, category_id = None):
    specific_globals = {}
    if type_id is None and group_id is None and category_id is None:
        return specific_globals
    for global_ball_id, ball in task.context.ballpark.globals.iteritems():
        slim_item = get_slim_item(task, global_ball_id)
        if slim_item.typeID == type_id or slim_item.groupID == group_id or slim_item.categoryID == category_id:
            specific_globals[global_ball_id] = ball

    return specific_globals


def get_id_and_types_in_bubble_by_typelist(ballpark, bubble_id, type_list_id):
    balls_of_interest = []
    balls_in_bubble = ballpark.bubbles.get(bubble_id)
    if not balls_in_bubble:
        return balls_of_interest
    get_slim = ballpark.slims.get
    types_of_interest = evetypes.GetTypeIDsByListID(type_list_id)
    for ball_id in balls_in_bubble.keys():
        if not ballpark.HasBall(ball_id):
            continue
        slim_item = get_slim(ball_id)
        if slim_item is None:
            continue
        if slim_item.typeID in types_of_interest:
            balls_of_interest.append((ball_id, slim_item.typeID))

    return balls_of_interest
