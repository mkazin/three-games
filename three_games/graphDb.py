from three_games.player import Player
from three_games.game import OwnedGame

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


class MinimumPlaytimeTraversalFilter(OwnedGameTraversalFilter):
    """ Filters out games not played at least a minimum time by a player,
        prior to adding:
        1) The gametime to the list of recommendations
        2) The playtime to the total playtime of the game
        3) The  player to the list of friends who own the recommended game """

    def __init__(self, minimum_playtime):
        self.minimum_playtime = minimum_playtime

    def traversible(self, owned_game):
        return owned_game.playtime_forever > self.minimum_playtime


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


class GameRecommendation(object):

    # Minimum time required to play before a recommendation is made and friend
    # is marked as having played the game. In seconds (to match Steam's forever_playtime)
    MIN_PLAY_TIME = 0  # 5 * 60

    def __init__(self, game, total_playtime,
                 friends_with_game=[], non_friend_owners=[]):
        """ NOTE: only 1st-degree friends should be listed in friends_with_game. """
        self.game = game
        self.total_playtime = total_playtime
        self.friends_with_game = friends_with_game
        self.non_friend_owners = non_friend_owners

    def __str__(self):
        return '{} - {} ({} hrs on average)'.format(
            self.game.name,
            # TODO: switch to personaname for Live?
            ' owned by: Friends: [{}] ; Non-Friends: [{}]'.format(
                ', '.join([friend.personaname for friend in self.friends_with_game]),
                ', '.join([friend.personaname for friend in self.non_friend_owners])),
            round((self.total_playtime /
                   len(self.friends_with_game + self.non_friend_owners)) / 60))

    def __repr__(self):
        return str(self)

    @staticmethod
    def sort_by_playtime(recs, reverse=False):

        sorted_games = sorted(recs.items(), key=lambda tuple: tuple[1].total_playtime)

        if reverse:
            sorted_games.reverse()

        # Convert list of tuples to a list of GameRecommendations

        return [the_tuple[1] for the_tuple in sorted_games]


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
            for friend in player.friends:
                self.graph.add_edge(player, friend)

    def nodes(self):
        return self.graph.nodes

    def edges(self):
        return self.graph.edges

    def game_recommendations(self, center, filters=[]):
                             # TODO: , weighter=None):
        """ Builds a list recommendations based on highest overall playtime
            Returns a sorted list of tuples in the form (appid, cumulative_playtime) """
        player_queue = [center]
        visited = {center.steamid: False}
        game_hash = {}

        while player_queue:

            player = player_queue.pop(0)

            # If already visited, skip
            if visited.get(player.steamid, False):
                continue

            # Enqueue player's friends for BFS traversal
            for friend in player.friends:
                player_queue.append(friend)

            # Process the current player, asusming they pass the filter
            if TraversalFilter.passes(player, filters):
                # Add the playtime of each of this players' games
                for game in player.games:

                    # Don't recommend games with no playtime, or add friends who never
                    # played it. Use another function to determine which friends of a
                    # player own a multiplayer game.
                    if not TraversalFilter.passes(game, filters):
                        continue

                    # Use lists to append the current player to either the friends
                    # or non-friends list in the recommendation as appropriate
                    friends = []
                    nonfriends = []
                    if player in center.friends:
                        friends = [player]
                    else:
                        nonfriends = [player]

                    try:
                        game_hash[game.game.appid].total_playtime += game.playtime_forever
                        game_hash[game.game.appid].friends_with_game += friends
                        game_hash[game.game.appid].non_friend_owners += nonfriends
                    except KeyError:
                        game_hash[game.game.appid] = GameRecommendation(
                            game.game, game.playtime_forever, friends, nonfriends)

            visited[player.steamid] = True

        return game_hash


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
