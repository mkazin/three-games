
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
    FUNCTION_FRIEND_LIST = 'ISteamUser/GetFriendList'
    FUNCTION_OWNED_GAMES = 'IPlayerService/GetOwnedGames'
    FUNCTION_PLAYER_ACHIEVEMENTS = 'ISteamUserStats/GetPlayerAchievements'
    FUNCTION_PLAYER_SUMMARIES = 'ISteamUser/GetPlayerSummaries'

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

        url = SteamApi.build_player_summaries_url(self.api_key, steamids)

        logging.debug('get_player_summaries({})'.format(steamids))
        resp = self.__get__(url, PLAYER_SUMARY_LIMIT_EXCEEDED)
        resp.raise_for_status()

        return resp.json()['response']['players']

    def get_owned_games(self, steamid):
        url = SteamApi.build_owned_games_url(self.api_key, steam_id, True, True)

        logging.debug('get_owned_games({})'.format(steamid))
        resp = self.__get__(url, OWNED_GAMES_LIMIT_EXCEEDED)
        resp.raise_for_status()

        # TODO: When we figure out error handling around privacy
        try:
            # Response for a private profile will be an empty hash
            if len(resp.json()['response'].keys()) == 0:
                return []

            # Response for a profile owning no games will not have a 'games'
            # section, only a game_count of 0
            if resp.json()['response']['game_count'] == 0:
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

        url = SteamApi.build_friend_list_url(self.api_key, steamid, relationship)

        logging.debug('get_friend_list({})'.format(steamid))
        resp = self.__get__(url, FRIEND_LIST_LIMIT_EXCEEDED)

        # TODO: When we figure out error handling around privacy
        if len(resp.json().keys()) == 0:
            return []

        resp.raise_for_status()
        return resp.json()['friendslist']['friends']

    def get_player_achievements(self, steamid, app_id):

        url = SteamApi.build_player_achievements_url(
            self.api_key, steamid, app_id, language='en')

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

    @staticmethod
    def build_player_summaries_url(api_key, steam_ids):

        builder = SteamApi.UrlBuilder.create(api_key)
        builder.with_function(SteamApi.FUNCTION_PLAYER_SUMMARIES)
        builder.with_steam_ids(steam_ids).with_version('0002')
        return builder.build()

    @staticmethod
    def build_owned_games_url(
            api_key, steam_id,
            include_appinfo=True, include_played_free_games=True):

        builder = SteamApi.UrlBuilder()
        builder.with_key(api_key)
        builder.with_steam_id(steam_id)
        builder.with_function(SteamApi.FUNCTION_OWNED_GAMES)
        builder.with_version('0001')
        builder.with_param('include_appinfo', 1 if include_appinfo else 0)
        builder.with_param('include_played_free_games',
                           1 if include_played_free_games else 0)
        return builder.build()

    @staticmethod
    def build_friend_list_url(
            api_key, steam_id, relationship):

        builder = SteamApi.UrlBuilder.create(api_key)
        builder.with_function(SteamApi.FUNCTION_FRIEND_LIST)
        builder.with_steam_id(steam_id)
        builder.with_version('0001')
        builder.with_param('relationship', relationship)
        return builder.build()

    @staticmethod
    def build_player_achievements_url(api_key, steam_id, app_id, language='en'):

        builder = SteamApi.UrlBuilder.create(api_key)
        builder.with_function(SteamApi.FUNCTION_PLAYER_ACHIEVEMENTS)
        builder.with_steam_id(steam_id)
        builder.with_version('0001')
        builder.with_param('appid', app_id)
        builder.with_param('l', language)
        return builder.build()

    class UrlBuilder(object):
        def __init__(self):
            self.function = None
            self.version = '0002'
            self.api_key = None
            self.steam_id = None
            self.steam_ids = None
            self.params = {}

        @staticmethod
        def create(api_key):
            instance = SteamApi.UrlBuilder()
            return instance.with_key(api_key)

        def with_param(self, key, value):
            self.params[key] = value

        def with_key(self, api_key):
            self.api_key = api_key
            return self

        def with_steam_id(self, steam_id):
            self.steam_id = steam_id
            return self

        def with_steam_ids(self, steam_ids):
            self.steam_ids = steam_ids
            return self

        def with_function(self, function):
            self.function = function
            return self

        def with_version(self, version):
            """ Expects a string, likely of format '0001' or '0002'. """
            self.version = version
            return self

        def build(self):
            """ Build and return the URL. """
            url = SteamApi.BASE_URI + \
                '{}/v{}?key={}&format=json'.format(
                    self.function,
                    self.version,
                    self.api_key)

            if self.steam_id:
                url += '&steamid={}'.format(self.steam_id)

            if self.steam_ids:
                url += '&steamids={}'.format(
                    ','.join((str(x) for x in self.steam_ids)))

            # Add free-form params
            url += ''.join(['&{}={}'.format(key, self.params[key])
                            for key in self.params])

            return url
