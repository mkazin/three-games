import logging
from three_games.player import Player
from three_games.game import OwnedGame


class FriendCrawler(object):

    def __init__(self, steam_api):
        self.api = steam_api

        # Cache all retrieved objects to minimize API hits
        self.player_cache = {}
        self.game_cache = {}

    def build_friend_graph(self, steamid):

        # Start with the requested player
        center = Player.from_response(self.api.get_player_summary(steamid=steamid))
        self.player_cache[center.steamid] = center

        # Recurse over friends
        self._recurse_friends_(player=center)

        return center

    def _get_friend_list_(self, player):
        """ Query the provided player's list of friends on Steam
            For each one, builds a Player() object, using the cached copy if already seen
            A list of these are returned """

        results = []
        friends_response = self.api.get_friend_list(
            player.steamid, relationship='all')

        for curr in friends_response:

            # Check if we already have this friend
            friend_id = curr['steamid']

            try:
                friend = self.player_cache[friend_id]
                results.append(friend)

            except KeyError:

                friend = Player.from_response(
                    self.api.get_player_summary(steamid=friend_id))
                self.player_cache[friend_id] = friend
                results.append(friend)

        return results

    def _get_owned_games_(self, player):
        """ Query the provided player's list of games owned on Steam
            For each one, builds an OwnedGame() object, using the cached copy if already seen
            A list of these are returned """

        results = []

        games_response = self.api.get_owned_games(player.steamid)

        for curr in games_response:

            # Check if we already have this friend
            game_id = curr['appid']

            try:
                game = self.game_cache[game_id]
                results.append(game)

            except KeyError:

                game = OwnedGame.from_response(curr)

                self.game_cache[game_id] = game
                results.append(game)

        return results

    def _recurse_friends_(self, player):

        player_queue = [player]
        visited = {player.steamid: False}

        while player_queue:

            player = player_queue.pop(0)

            if visited.get(player.steamid, False):
                continue

            friends = self._get_friend_list_(player)

            # Add owned games
            games = self._get_owned_games_(player)
            for game in games:
                player.add_game(game)

            # Connect all the player's friends
            for friend in friends:
                player.add_friend(friend)
                player_queue.append(friend)

            visited[player.steamid] = True
