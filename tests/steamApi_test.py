from three_games.game import OwnedGame
from tests.mockSteamApi import MockSteamApi

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


def test_get_player_summaries():

    api = MockSteamApi()

    single_result = api.get_player_summary(3)
    assert single_result['realname'] == 'Player Three'

    multiple_results = api.get_player_summaries([2, 3])
    assert multiple_results[0]['realname'] == 'Player Two'
    assert multiple_results[1]['realname'] == 'Player Three'


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
    api = MockSteamApi()

    achievements = api.get_player_achievements(3, APP_ID_FALLOUT_4)

    # Transform into a simple list of achivement names
    achivement_names = [a['name'] for a in achievements]

    assert("War Never Changes" in achivement_names)
    assert("The Nuclear Option" in achivement_names)
    assert("Institutionalized" in achivement_names)
    assert("Nuclear Family" in achivement_names)
    assert("Rockets' Red Glare" in achivement_names)
    assert("Masshole" in achivement_names)


def test_get_friend_list():
    api = MockSteamApi()

    friends = api.get_friend_list(3, relationship='all')

    assert(len(friends) == 2)

    # Sort by time- oldest first
    friends_by_time = sorted(friends,
                             key=lambda k: k['friend_since'], reverse=False)

    assert(friends_by_time[0]['steamid'] == "4")
    assert(friends_by_time[0]['relationship'] == "friend")
    assert(friends_by_time[0]['friend_since'] == 1325266988)

    assert(friends_by_time[1]['steamid'] == "1")
    assert(friends_by_time[1]['relationship'] == "friend")
    assert(friends_by_time[1]['friend_since'] == 1447349026)
