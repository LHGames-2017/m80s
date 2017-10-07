from flask import Flask, request
from structs import *
import json
import numpy

app = Flask(__name__)


def create_action(action_type, target):
    actionContent = ActionContent(action_type, target.__dict__)
    return json.dumps(actionContent.__dict__)


def create_move_action(target):
    return create_action("MoveAction", target)


def create_attack_action(target):
    return create_action("AttackAction", target)


def create_collect_action(target):
    return create_action("CollectAction", target)


def create_steal_action(target):
    return create_action("StealAction", target)


def create_heal_action():
    return create_action("HealAction", "")


def create_purchase_action(item):
    return create_action("PurchaseAction", item)


def create_upgrade_action(item):
    return create_action("UpgradeAction", item)


def deserialize_map(serialized_map):
    """
    Fonction utilitaire pour comprendre la map
    """
    serialized_map = serialized_map[1:]
    rows = serialized_map.split('[')
    column = rows[0].split('{')
    deserialized_map = [[Tile() for x in range(20)] for y in range(20)]
    for i in range(len(rows) - 1):
        column = rows[i + 1].split('{')

        for j in range(len(column) - 1):
            infos = column[j + 1].split(',')
            end_index = infos[2].find('}')
            content = int(infos[0])
            x = int(infos[1])
            y = int(infos[2][:end_index])
            deserialized_map[i][j] = Tile(content, x, y)

    return deserialized_map


def nearestResource(player, map):

    ressources =[]
    for i in range(0, 20):
        for j in range(0, 20):
            if map[i][j].Content == TileContent.Resource:
                ressources.append(Point(map[i][j].X, map[i][j].Y))

    shortest_distance = 10000000
    finalRessource = Point(-1,-1)
    for i in ressources:
        distanceCalculated = distance(i, player.Position)
        if distanceCalculated < shortest_distance :
            shortest_distance = distanceCalculated
            finalRessource = i
    return finalRessource


def bot():
    """
    Main de votre bot.
    """
    map_json = request.form["map"]

    # Player info

    encoded_map = map_json.encode()
    map_json = json.loads(encoded_map)
    p = map_json["Player"]
    pos = p["Position"]
    x = pos["X"]
    y = pos["Y"]
    house = p["HouseLocation"]
    player = Player(p["Health"], p["MaxHealth"], Point(x, y),
                    Point(house["X"], house["Y"]), p["Score"],
                    p["CarriedResources"], p["CarryingCapacity"])

    # Map
    serialized_map = map_json["CustomSerializedMap"]
    deserialized_map = deserialize_map(serialized_map)

    resource = nearestResource(player, deserialized_map)
    print(str(resource))
    otherPlayers = []

    for players in map_json["OtherPlayers"]:
        player_info = players["Value"]
        p_pos = player_info["Position"]
        player_info = PlayerInfo(player_info["Health"],
            player_info["MaxHealth"],
            Point(p_pos["X"], p_pos["Y"]))

        otherPlayers.append(player_info)

    # return decision
    print("current position: "+ str(player.Position))
    # should_fight, target = fight_flight(player, Point(player.Position.X + 1, player.Position.Y))
    # if should_fight:
    #     print("fighting: ")
    #     return create_attack_action(target)
    # else:
    #     print("not fighting")
    dest = get_next_move(player.Position, nearestResource(player,deserialized_map), deserialized_map)

    # dest = get_next_move(player.Position, player.HouseLocation, deserialized_map)
    print("dest: " + str(dest))
    return create_move_action(dest)

#return create_move_action(Point(x,y+1))

def fight_flight(player, other_player_position):
    should_fight = False
    print(other_player_position)
    if player.CarriedRessources == 0:
        print("carying nothing")
        should_fight = True
    elif player.Health < player.MaxHealth/3:
        print("low health")
        should_fight = False
    else:
        print("fight")
        should_fight = True
    if should_fight:
        target = Point(0, 0)
    else:
        target = get_next_move(player.Position, other_player_position) #to implement for realz
    return should_fight, target


def get_next_move(position, target, map):

    # finder = astar.pathfinder(Point.Distance, heuristic, neighbors)
    # print(finder(position, target))

    delta_x = position.X - target.X
    delta_y = position.Y - target.Y
    x = position.X
    y = position.Y
    print("deltaX: " + str(delta_x) + " deltaY: " + str(delta_y))
    if delta_x > 0:
        # right_safe = map[10][9].Content == TileContent.Empty
        down_safe = map[9][8].Content == TileContent.Empty
        up_safe = map[9][10].Content == TileContent.Empty
        left_safe = map[8][9].Content == TileContent.Empty
        if delta_y > 0:
            if left_safe:
                x = position.X - 1
                y = position.Y
            elif down_safe:
                x = position.X
                y = position.Y - 1
            elif up_safe:
                x = position.X
                y = position.Y + 1
            else:
                x = position.X - 1
                y = position.Y
        if delta_y < 0:
            if left_safe:
                x = position.X - 1
                y = position.Y
            elif up_safe:
                x = position.X
                y = position.Y + 1
            elif down_safe:
                x = position.X
                y = position.Y - 1
            else:
                x = position.X - 1
                y = position.Y
    elif delta_x < 0:
        right_safe = map[10][9].Content == TileContent.Empty
        down_safe = map[9][8].Content == TileContent.Empty
        up_safe = map[9][10].Content == TileContent.Empty
        # left_safe = map[8][9].Content == TileContent.Empty
        if delta_y > 0:
            if right_safe:
                x = position.X + 1
                y = position.Y
            elif down_safe:
                x = position.X
                y = position.Y - 1
            elif up_safe:
                x = position.X
                y = position.Y + 1
            else:
                x = position.X - 1
                y = position.Y
        if delta_y < 0:
            if right_safe:
                x = position.X + 1
                y = position.Y
            elif up_safe:
                x = position.X
                y = position.Y + 1
            elif down_safe:
                x = position.X
                y = position.Y - 1
            else:
                x = position.X - 1
                y = position.Y
    else:
        x = position.X
        down_safe = map[9][8].Content == TileContent.Empty
        up_safe = map[9][10].Content == TileContent.Empty
        if delta_y < 0 and up_safe:
            y = position.Y + 1
        elif down_safe:
            y = position.Y - 1
        else:
            x = position.X + 1
            y = position.Y

    return Point(x, y)


def distance(p1, p2):
    delta_x = p1.X - p2.X
    delta_y = p1.Y - p2.Y
    return delta_x + delta_y

@app.route("/", methods=["POST"])
def reponse():
    """
    Point d'entree appelle par le GameServer
    """
    return bot()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

