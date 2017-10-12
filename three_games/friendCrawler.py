import logging
from three_games.player import Player
from three_games.game import OwnedGame


class FriendCrawler(object):

    def __init__(self, steam_api):
        self.api = steam_api

        # Cache all retrieved players to minimize API hits
        self.player_cache = {}

    def build_friend_graph(self, steamid):

        # Start with the requested player
        center = Player.from_response(self.api.get_player_summary(steamid=steamid))
        self.player_cache[center.steamid] = center

        # Recurse over friends
        self._recurse_friends_(player=center)

        return center

    def _get_friend_list_(self, player):

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

                # If already found in the cache, no need to query
                friend = Player.from_response(
                    self.api.get_player_summary(steamid=friend_id))
                self.player_cache[friend_id] = friend
                results.append(friend)

        return results

    def _recurse_friends_(self, player):

        player_queue = [player]
        visited = {player.steamid: False}

        while player_queue:

            player = player_queue.pop(0)

            if visited.get(player.steamid, False):
                continue

            friends = self._get_friend_list_(player)

            # Connect all the player's friends
            for friend in friends:
                player.add_friend(friend)
                player_queue.append(friend)

            visited[player.steamid] = True
