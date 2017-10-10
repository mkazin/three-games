from three_games.game import OwnedGame
from three_games.steamApi import SteamApi

STEAM_ID_MKAZIN = 76561198025093417
APP_ID_FALLOUT_4 = 377160

GAMES_RESPONSE_PER_STEAMID = {
    '1': [
        {"appid": 7610, "name": "Railroad Tycoon 3", "playtime_forever": 100},
        {"appid": 24980, "name": "Mass Effect 2",  "playtime_forever": 400},
        {"appid": 234650, "name": "Shadowrun Returns",  "playtime_forever": 200,
         'has_community_visible_stats': True,
         'img_logo_url': "70f084857297d5fdd96d019db3a990d6d9ec64f1",
         'img_icon_url': "64eec20c9375e7473b964f0d0bc41d19f03add3b"}
    ],
    '2': [
        {"appid": 7610, "name": "Railroad Tycoon 3",  "playtime_forever": 1000},
        {"appid": 33230, "name": "Assassin's Creed II",  "playtime_forever": 3000},
    ],
    '3': [
        {"appid": 24980, "name": "Mass Effect 2",  "playtime_forever": 40},
    ]
}


# TODO: merge with the Mock class in friendCrawler_test and use in both
#       this is because I added querying of the games during the friend crawl,
#       but neglected to override the function there
class MockSteamApi(SteamApi):

    def __init__(self):
        pass

    def get_owned_games(self, steamid):
        return GAMES_RESPONSE_PER_STEAMID[steamid]


def test_get_player_summaries():

    api = SteamApi('config/auth.conf')

    single_result = api.get_player_summary(STEAM_ID_MKAZIN)
    assert single_result['realname'] == 'Michael Kazin'

    multiple_results = api.get_player_summaries([STEAM_ID_MKAZIN])
    assert multiple_results[0]['realname'] == 'Michael Kazin'


def test_get_owned_games():

    api = MockSteamApi()

    games_resp = api.get_owned_games('1')

    games = []
    found = False
    for curr in games_resp:

        curr_game = OwnedGame.from_response(curr)
        games.append(curr_game)
        if curr_game.game.appid != 234650:
            continue

        found = True
        assert curr['appid'] == 234650
        assert curr['name'] == "Shadowrun Returns"
        assert curr['has_community_visible_stats'] == True
        assert curr['img_logo_url'] == "70f084857297d5fdd96d019db3a990d6d9ec64f1"
        assert curr['img_icon_url'] == "64eec20c9375e7473b964f0d0bc41d19f03add3b"
        assert curr['playtime_forever'] == 200

    assert(found)
    assert(len(games) == 3)

    games_by_playtime = sorted(games, key=lambda k: k.playtime_forever, reverse=True)

    assert(games_by_playtime[0].game.name == "Mass Effect 2")
    assert(games_by_playtime[0].playtime_forever == 400)
    assert(games_by_playtime[-1].game.name == "Railroad Tycoon 3")
    assert(games_by_playtime[-1].playtime_forever == 100)


def test_get_player_achievements():
    api = SteamApi('config/auth.conf')

    achievements = api.get_player_achievements(STEAM_ID_MKAZIN, APP_ID_FALLOUT_4)

    # Transform into a simple list of achivement names
    achivement_names = [a['name'] for a in achievements]

    assert("War Never Changes" in achivement_names)
    assert("The Nuclear Option" in achivement_names)
    assert("Institutionalized" in achivement_names)
    assert("Nuclear Family" in achivement_names)
    assert("Rockets' Red Glare" in achivement_names)
    assert("Masshole" in achivement_names)


def test_get_friend_list():
    api = SteamApi('config/auth.conf')

    friends = api.get_friend_list(STEAM_ID_MKAZIN, relationship='all')

    # Sort by time- oldest first
    friends_by_time = sorted(friends,
                             key=lambda k: k['friend_since'], reverse=False)

    assert(friends_by_time[0]['steamid'] == "76561197996829576")
    assert(friends_by_time[0]['relationship'] == "friend")
    assert(friends_by_time[0]['friend_since'] == 1321052248)
