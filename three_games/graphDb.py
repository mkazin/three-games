from three_games.player import Player
from three_games.game import OwnedGame
from three_games.gameRecommendation import GameRecommendation
import networkx as nx

"""
Resources on graph databases to try:

* If scaling is needed, check out this AWS article on Graph databases, which provides
options running on EC2, often available from the marketplace:
https://aws.amazon.com/nosql/graph/
"""


class TraversalFilter(object):
    """ Interface for filters determining whether or not to traverse
        a friend
    """

    def traversible(self, object):
        """ Test function of the filter. Returns False if the item
            should be filtered out """
        raise NotImplemented('Must be implemented by subclasses')

    def _applies_to_thing_(self, thing):
        """ Test to determine if the filter applies to the thing
            it was passed """
        raise NotImplemented('Must be implemented by subclasses')

    @staticmethod
    def passes(thing, filters):
        for filter in filters:
            if filter._applies_to_thing_(thing) and \
                    not filter.traversible(thing):
                return False
        return True


class PlayerTraversalFilter(TraversalFilter):
    """ Traversal Filter for Player objects """

    def _applies_to_thing_(self, thing):
        return issubclass(type(thing), Player)


class OwnedGameTraversalFilter(TraversalFilter):
    """ Traversal Filter for OwnedGame objects """

    def _applies_to_thing_(self, thing):
        return issubclass(type(thing), OwnedGame)


class GamePlaytimeTraversalFilter(OwnedGameTraversalFilter):
    """ Filters out games not played at least a minimum time by a player,
        prior to adding:
        1) The gametime to the list of recommendations
        2) The playtime to the total playtime of the game
        3) The  player to the list of friends who own the recommended game """

    def __init__(self, minimum_playtime):
        self.minimum_playtime = minimum_playtime

    def traversible(self, owned_game):
        return owned_game.playtime_forever > self.minimum_playtime


class GameNameTraversalFilter(OwnedGameTraversalFilter):
    """ Includes only games which contain the 'subtext' value
        Setting reverse flag filters out matching game names
    """

    def __init__(self, subtext, reverse=False):
        self.subtext = subtext
        self.reverse = reverse

    def traversible(self, owned_game):
        found = self.subtext in owned_game.game.name
        return not found if self.reverse else found


class PlayerExclusionTraversalFilter(PlayerTraversalFilter):
    """ Allows filtering out of a list of players """

    def __init__(self, players):
        self.excluded = [player.steamid for player in players]

    def traversible(self, player):
        return player.steamid not in self.excluded


class ClanTraversalFilter(PlayerTraversalFilter):
    """ Allows filtering out friends who do not belong to a particular
    gaming clan
    """

    def __init__(self, clan):
        raise NotImplemented

    def traversible(self, object):
        # return object.clan == self.clan
        raise NotImplemented


# class DiminishingWeight(object):

#     def __init__(self, start_weight, reudction_rate):
#         self.weight = start_weight
#         self.round = 0
#         self.reudction_rate = reudction_rate

#     def weight(self):
#         return self.weight

#     def advance_round(self):
#         self.weight = self.weight * self.reudction_rate


class GraphDB():

    def __init__(self):
        self.graph = nx.Graph()
        self.live_players = {}

    def insert_players(self, players):

        for curr in players:

            # Skip players already in the db
            if self.live_players.get(str(curr.steamid), None):
                continue

            self.graph.add_node(curr)
            self.live_players[curr.steamid] = curr

        # Add paths
        for player in players:
            self.__insert_player_relationships__(player)


    def __insert_player_relationships__(self, player):
        """ Insert a player's relationships into the graph. """
        for friend in player.friends:
            self.graph.add_edge(player, friend)

    def nodes(self):
        return self.graph.nodes

    def edges(self):
        return self.graph.edges


class Recommender(object):

    def __init__(self, center, filters=[]):
        self.player_queue = []
        self.visited = {}
        self.game_hash = {}
        self.center = center
        self.filters = filters

    def get_recommendations(self):
                             # TODO: , weighter=None):
        """ Builds a list recommendations based on highest overall playtime
            Returns a sorted list of tuples in the form (appid, cumulative_playtime) """
        self.player_queue = [self.center]
        self.visited = {self.center.steamid: False}
        self.game_hash = {}

        while self.player_queue:
            self.__process_player__()

        return self.game_hash


    def __process_player__(self):
        player = self.player_queue.pop(0)

        # If already visited, skip
        if self.visited.get(player.steamid, False):
            return

        # Enqueue player's friends for BFS traversal
        self.player_queue += [friend for friend in player.friends]

        # Mark the player as visited to avoid endless recursion
        self.visited[player.steamid] = True

        # Process the current player, asusming they pass the filter
        if not TraversalFilter.passes(player, self.filters):
            return

        # Add the playtime of each of this players' games
        for game in player.games:
            self.__process_player_game__(player, game)


    def __process_player_game__(self, player, game):

        # Don't recommend games with no playtime, or add friends who never
        # played it. Use another function to determine which friends of a
        # player own a multiplayer game.
        if not TraversalFilter.passes(game, self.filters):
            return

        # Use lists to append the current player to either the friends
        # or non-friends list in the recommendation as appropriate
        friends = [player] if player in self.center.friends else []
        nonfriends = [player] if player not in self.center.friends else []

        try:
            self.game_hash[game.game.appid].total_playtime += game.playtime_forever
            self.game_hash[game.game.appid].friends_with_game += friends
            self.game_hash[game.game.appid].non_friend_owners += nonfriends
        except KeyError:
            self.game_hash[game.game.appid] = GameRecommendation(
                game.game, game.playtime_forever,
                friends_with_game=friends, non_friend_owners=nonfriends)




"""

Option A:
=========

a -> b skip (missing b)
b -> a add path
b -> c skip (missing c)
c -> b add path
(assumes input is complete)


Option B:
=========
a -> b add b first, then add path
    b -> a skip (already working on it)
    b -> c add c first, then add path
        c -> b add path


"""
