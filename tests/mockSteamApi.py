from three_games.steamApi import SteamApi


class MockSteamApi(SteamApi):

    def __init__(self):
        pass

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

    def get_owned_games(self, steamid):
        return MockSteamApi.GAMES_RESPONSE_PER_STEAMID[steamid]

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

    ACHIEVEMENTS_RESPONSE_PER_STEAMID = {
        "3": {
            "achievements": [
                {
                    "apiname": "NEW_ACHIEVEMENT_1_0",
                    "achieved": 1,
                    "unlocktime": 1447211351,
                    "name": "War Never Changes",
                    "description": ""
                },
                {
                    "apiname": "NEW_ACHIEVEMENT_8_0",
                    "achieved": 0,
                    "unlocktime": 0,
                    "name": "The Nuclear Option",
                    "description": ""
                },
                {
                    "apiname": "NEW_ACHIEVEMENT_9_0",
                    "achieved": 0,
                    "unlocktime": 0,
                    "name": "Institutionalized",
                    "description": ""
                },
                {
                    "apiname": "NEW_ACHIEVEMENT_12_0",
                    "achieved": 0,
                    "unlocktime": 0,
                    "name": "Nuclear Family",
                    "description": ""
                },
                {
                    "apiname": "NEW_ACHIEVEMENT_21_0",
                    "achieved": 0,
                    "unlocktime": 0,
                    "name": "Rockets' Red Glare",
                    "description": ""
                },
                {
                    "apiname": "NEW_ACHIEVEMENT_40_0",
                    "achieved": 1,
                    "unlocktime": 1448942430,
                    "name": "Masshole",
                    "description": ""
                }
            ]
        }
    }

    def get_player_achievements(self, steamid, app_id):
        return(MockSteamApi.ACHIEVEMENTS_RESPONSE_PER_STEAMID[
            str(steamid)]['achievements'])
