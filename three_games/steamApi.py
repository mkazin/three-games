

import configparser
import json
import requests


class SteamApi(object):
    '''
    Introduction to the Steam Web API, and link to getting an API key here:
    http://steamcommunity.com/dev

    Steam Web API functions documented here:
    https://developer.valvesoftware.com/wiki/Steam_Web_API


    '''
    BASE_URI = 'http://api.steampowered.com/'

    def __init__(self, config_file):
        config = configparser.RawConfigParser()
        config.read(config_file)
        self.api_key = config.get('Steam', 'apikey')

    def get_player_summary(self, steamid):
        return self.get_player_summaries([steamid])[0]

    def get_player_summaries(self, steamids):

        url = SteamApi.BASE_URI + \
            'ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}&format=json'.format(
                self.api_key, ','.join((str(x) for x in steamids)))

        resp = requests.get(url)

        resp.raise_for_status()

        return resp.json()['response']['players']

    def get_owned_games(self, steamid):

        url = (SteamApi.BASE_URI +
               'IPlayerService/GetOwnedGames/v0001/' +
               '?key={}&steamid={}' +
               '&include_appinfo={}' +
               '&include_played_free_games={}' +
               '&format=json').format(
            self.api_key, steamid,
            1, 1)
        resp = requests.get(url)

        resp.raise_for_status()

        return resp.json()['response']['games']

    def get_friend_list(self, steamid, relationship='all'):
        """
        steamid : 64 bit Steam ID to return friend list for
        relationship : Relationship filter. Possibles values: all, friend
        """

        url = (SteamApi.BASE_URI +
               'ISteamUser/GetFriendList/v0001/' +
               '?key={}&steamid={}' +
               '&relationship={}' +
               '&format=json').format(
            self.api_key, steamid,
            relationship)

        resp = requests.get(url)

        # TODO: When we figure out error handling around privacy
        if len(resp.json().keys()) == 0:
            return []

        resp.raise_for_status()
        return resp.json()['friendslist']['friends']

    def get_player_achievements(self, steamid, app_id):

        url = (SteamApi.BASE_URI +
               'ISteamUserStats/GetPlayerAchievements/v0001/' +
               '?key={}&steamid={}' +
               '&appid={}' +
               '&l=en' +
               '&format=json').format(
            self.api_key, steamid, app_id)

        resp = requests.get(url)

        if resp.json()['playerstats'].__contains__('error'):
            # resp.json()['playerstats']['error']
            resp.raise_for_status()

        return resp.json()['playerstats']['achievements']
