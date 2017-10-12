from three_games.player import Player
from three_games.game import OwnedGame

class FriendCrawler(object):

    def __init__(self, steam_api):
        self.api = steam_api

        # Cache all retrieved players to minimize API hits
        self.player_cache = {}

    def build_friend_graph(self, steamid, graph_depth=3):

        # Start with the requested player
        center = Player.from_response(self.api.get_player_summary(steamid=steamid))
        self.player_cache[center.steamid] = center

        # Recurse over friends
        self.recurse_friends(player=center, graph_depth=graph_depth)

        # print('CACHE AFTER recurse_friends() :')
        # for player_key in self.player_cache.keys():
        #     player = self.player_cache[player_key]
        #     print('{} : {} has {} friends: ({})'.format(
        #         player.steamid, player.realname,
        #         len(player.friends), [f.steamid for f in player.friends]))

        return center

    def recurse_friends(self, player, graph_depth):

        if graph_depth < 1:
            return

        friends_response = self.api.get_friend_list(
            player.steamid, relationship='all')

        for curr in friends_response:

            # Check if we already have this friend
            friend_id = curr['steamid']

            try:
                friend = self.player_cache[friend_id]
                player.add_friend(friend)

            except KeyError:

                # If already found in the cache, no need to query
                friend = Player.from_response(
                    self.api.get_player_summary(steamid=friend_id))
                self.player_cache[friend_id] = friend

                player.add_friend(friend)

                # games_resp = self.api.get_owned_games(friend_id)
                # for curr in games_resp:
                #     friend.add_game(OwnedGame.from_response(curr))

                # We also don't want to recurse on already-handled players
                self.recurse_friends(friend, graph_depth - 1)
