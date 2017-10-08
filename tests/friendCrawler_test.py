
from three_games.steamApi import SteamApi
from three_games.friendCrawler import FriendCrawler


class MockSteamApi(SteamApi):

    def __init__(self):
        pass

    PLAYER_LIST = {
        '1': {"steamid": "1", "personaname": "player_one", "realname": "Player One"},
        '2': {"steamid": "2", "personaname": "player_two", "realname": "Player Two"},
        '3': {"steamid": "3", "personaname": "player_three", "realname": "Player Three"},
        '4': {"steamid": "4", "personaname": "player_four", "realname": "Player Four"},
        '5': {"steamid": "5", "personaname": "player_five", "realname": "Player Five"},
    }

    def get_player_summaries(self, steamids):
        response = []

        for curr in steamids:
            response.append(MockSteamApi.PLAYER_LIST[str(curr)])
        return response

    FRIENDS_RESPONSE = {
        '1': [
            {"steamid": "2", "relationship": "friend", "friend_since": 1447349026},
            {"steamid": "3", "relationship": "friend", "friend_since": 1325266988},
        ],
        '2': [
            {"steamid": "1", "relationship": "friend", "friend_since": 1447349026},
            {"steamid": "4", "relationship": "friend", "friend_since": 1325266988},
        ],
        '3':
        [
            {"steamid": "1", "relationship": "friend", "friend_since": 1447349026},
            {"steamid": "4", "relationship": "friend", "friend_since": 1325266988},
        ],
        '4':
        [
            {"steamid": "2", "relationship": "friend", "friend_since": 1447349026},
            {"steamid": "3", "relationship": "friend", "friend_since": 1325266988},
            {"steamid": "5", "relationship": "friend", "friend_since": 1325266988}
        ],
        '5':
        [
            {"steamid": "4", "relationship": "friend", "friend_since": 1447349026},
        ]
    }

    def get_friend_list(self, steamid, relationship='all'):
        return(MockSteamApi.FRIENDS_RESPONSE[str(steamid)])


def test_crawl():

    crawler = FriendCrawler(MockSteamApi())

    center = crawler.build_friend_graph(steamid=3, graph_depth=6)
    # output_player(player=center, level=0)

    assert(center.steamid == '3')
    assert(len(center.friends) == 2)
    assert([f.steamid for f in center.friends] == ['1', '4'])


def output_player(player, level):

    if level > 3:
        return

    print('\t' * level, player.steamid, player.personaname,
          player.realname, 'friends:', len(player.friends))
    for friend in player.friends:
        output_player(friend, level + 1)
