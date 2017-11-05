
import configparser
import json
import logging
import requests
import requests_cache


ACHIEVEMENTS_LIMIT_EXCEEDED = b'{"playerstats":{"success":false}}'
FRIEND_LIST_LIMIT_EXCEEDED = b'{"friendslist":{"friends": []}}'
OWNED_GAMES_LIMIT_EXCEEDED = b'[]'
PLAYER_SUMARY_LIMIT_EXCEEDED = b'{"response":{"players": []}}'

# In seconds
CACHE_DURATION = 7.0 * 24.0 * 3600.0


class SteamApi(object):
    '''
    Introduction to the Steam Web API, and link to getting an API key here:
    http://steamcommunity.com/dev

    Steam Web API functions documented here:
    https://developer.valvesoftware.com/wiki/Steam_Web_API


    '''
    BASE_URI = 'http://api.steampowered.com/'

    def __init__(self, config_file):
        logging.basicConfig(level=logging.DEBUG)

        config = configparser.RawConfigParser()
        config.read(config_file)

        # Set up caching of web requets
        options = {'expire_after': CACHE_DURATION}
        self.cache = requests_cache.backends.create_backend(
            'sqlite', 'steamApi_cache', options)
        requests_cache.install_cache(backend=self.cache)

        self.api_key = config.get('Steam', 'apikey')
        self.query_limit = None

    def set_query_limit(self, limit):
        self.query_limit = limit

    def get_player_summary(self, steamid):
        try:
            return self.get_player_summaries([steamid])[0]
        except IndexError:
            return None

    def get_player_summaries(self, steamids):

        url = SteamApi.BASE_URI + \
            'ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}&format=json'.format(
                self.api_key, ','.join((str(x) for x in steamids)))

        logging.debug('get_player_summaries({})'.format(steamids))
        resp = self.__get__(url, PLAYER_SUMARY_LIMIT_EXCEEDED)
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

        logging.debug('get_owned_games({})'.format(steamid))
        resp = self.__get__(url, OWNED_GAMES_LIMIT_EXCEEDED)
        resp.raise_for_status()

        # TODO: When we figure out error handling around privacy
        try:
            if len(resp.json()['response'].keys()) == 0:
                print('{} has a private gamelist?'.format(steamid))
                return []

            if resp.json()['response']['game_count'] == 0:
                print('{} owns no games?'.format(steamid))
                return []

            return resp.json()['response']['games']
        except KeyError as e:
            print(resp.json())
            raise e

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

        logging.debug('get_friend_list({})'.format(steamid))
        resp = self.__get__(url, FRIEND_LIST_LIMIT_EXCEEDED)

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

        logging.debug('get_player_achievements({}, {})'.format(steamid, app_id))
        resp = self.__get__(url, ACHIEVEMENTS_LIMIT_EXCEEDED)

        if resp.json()['playerstats'].__contains__('error'):
            # resp.json()['playerstats']['error']
            resp.raise_for_status()

        return resp.json()['playerstats']['achievements']

    def __get__(self, url, limit_exceeded_body):
        if self.query_limit is not None:
            if self.query_limit < 1:
                logging.warn('Query limit exceeded. Returning empty result')

                the_response = requests.models.Response()
                the_response.code = "Too Many Requests"
                the_response.error_type = "Too Many Requests"
                the_response.status_code = 429
                the_response._content = limit_exceeded_body
                return the_response

            # Reduce remaining query counter only if not cached
            if not self.cache.has_url(url):
                self.query_limit -= 1

            logging.debug('{} queries left'.format(self.query_limit))

        return requests.get(url)
