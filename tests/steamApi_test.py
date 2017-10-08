
from three_games.steamApi import SteamApi

STEAM_ID_MKAZIN = 76561198025093417
APP_ID_FALLOUT_4 = 377160


def test_get_player_summaries():

    api = SteamApi('config/auth.conf')

    single_result = api.get_player_summary(STEAM_ID_MKAZIN)
    assert single_result['realname'] == 'Michael Kazin'

    multiple_results = api.get_player_summaries([STEAM_ID_MKAZIN])
    assert multiple_results[0]['realname'] == 'Michael Kazin'


def test_get_owned_games():

    api = SteamApi('config/auth.conf')

    games = api.get_owned_games(STEAM_ID_MKAZIN)
    print(games)

    found = False
    for curr in games:
        if curr['appid'] != 40800:
            continue

        found = True
        assert curr['appid'] == 40800
        assert curr['name'] == "Super Meat Boy"
        assert curr['has_community_visible_stats']
        assert curr['img_logo_url'] == "70f084857297d5fdd96d019db3a990d6d9ec64f1"
        assert curr['img_icon_url'] == "64eec20c9375e7473b964f0d0bc41d19f03add3b"
        assert curr['playtime_forever'] == 40

    assert(found)

    games_by_playtime = sorted(games, key=lambda k: k['playtime_forever'], reverse=True)
    print('High:', games_by_playtime[0])
    print('Low:', games_by_playtime[-1])


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
