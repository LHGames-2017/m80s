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
    valid = True
    range = 3
    while(valid):
        firstColCase = player.Position.X-((range - 1)/2)
        lastColCase = player.Position.X-((range - 1)/2)

        firstRowCase = player.Position.Y-((range - 1) / 2)
        lastRowCase = player.Position.Y-((range - 1) / 2)


        if firstColCase < 0 :
            firstCase = 0

        if lastColCase >= len(player.Position.X):
            lastColCase = len(player.Position.X)-1


        if firstRowCase < 0 :
            firstRowCase = 0
        if lastRowCase >= len(player.Position.Y):
            lastRowCase = len(player.Position.Y)-1


        for i in range(firstColCase, lastColCase):
            for j in range(firstRowCase, lastRowCase):
                if map.Position.Tile.Content[i][j] == TileContent.Resource:
                    return map.Position

        range += 2

        if ((firstRowCase == 0) and (firstColCase == 0) and (lastColCase == len(player.Position.X)-1) and (lastRowCase == (len(player.Position.Y)-1))):
            valid = False

    return player.Position

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
    player = Player(p["Health"], p["MaxHealth"], Point(x,y),
                    Point(house["X"], house["Y"]),
                    p["CarriedResources"], p["CarryingCapacity"])

    # Map
    serialized_map = map_json["CustomSerializedMap"]
    deserialized_map = deserialize_map(serialized_map)

    otherPlayers = []

    for player_dict in map_json["OtherPlayers"]:
        for player_name in player_dict.keys():
            player_info = player_dict[player_name]
            p_pos = player_info["Position"]
            player_info = PlayerInfo(player_info["Health"],
                                     player_info["MaxHealth"],
                                     Point(p_pos["X"], p_pos["Y"]))

            otherPlayers.append({player_name: player_info })

    # return decision
    fight_flight(player, player_info)
    return create_move_action(Point(0,1))

def fight_flight(player, other_player):
    should_fight = False
    if player.CarriedRessources == 0:
        should_fight = True
    elif player.Health < player.MaxHealth/3:
        should_fight = False
    if should_fight:
        target = get_next_move(player.Position, other_player.Position)
        create_move_action(target)

    return should_fight


def get_next_move(position, target):
    delta_x = position.X - target.X
    delta_y = position.Y - target.Y
    if delta_x > 0:
        x = position.X + 1
    elif delta_x < 0:
        x = position.X - 1
    else:
        x = 0
    if delta_y > 0:
        y = position.Y + 1
    elif delta_y < 0:
        y = position.Y - 1
    else:
        y = 0
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

