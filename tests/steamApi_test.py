from three_games.game import OwnedGame
from three_games.steamApi import SteamApi
from tests.mockSteamApi import MockSteamApi

APP_ID_FALLOUT_4 = 377160


def test_get_player_summaries():

    api = MockSteamApi()

    single_result = api.get_player_summary(3)
    assert single_result['realname'] == 'Carl'

    multiple_results = api.get_player_summaries([2, 3])
    assert multiple_results[0]['realname'] == 'Bob'
    assert multiple_results[1]['realname'] == 'Carl'


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


def test_build_player_summaries_url():

    expected = (
        'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002'
        '?key=DUMMY_KEY&format=json&steamids=100,200,300'
    )

    url = SteamApi.build_player_summaries_url("DUMMY_KEY", [100, 200, 300])

    assert url == expected


def test_build_owned_games_url():

    expected = (
        'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001'
        '?key=DUMMY_KEY&format=json&steamid=100'
    )

    url = SteamApi.build_owned_games_url("DUMMY_KEY", 100, True, True)

    assert expected in url
    assert '&include_appinfo=1' in url
    assert '&include_played_free_games=1' in url


def test_build_friend_list_url():

    expected = (
        'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/'
        '?key=DUMMY_KEY&format=json&steamid=100'
        '&relationship=all'
    )

    url = SteamApi.build_friend_list_url("DUMMY_KEY", 100, 'all')
