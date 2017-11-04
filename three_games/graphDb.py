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
        raise NotImplemented

    @staticmethod
    def passes(player, filters):
        for filter in filters:
            if not filter.traversible(player):
                return False
        return True


class PlayerExclusionTraversalFilter(TraversalFilter):
    """ Allows filtering out of a list of players """

    def __init__(self, players):
        self.excluded = [player.steamid for player in players]

    def traversible(self, player):
        return player.steamid not in self.excluded


class ClanTraversalFilter(TraversalFilter):
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
            for friend in player.friends:
                self.graph.add_edge(player, friend)

    def nodes(self):
        return self.graph.nodes

    def edges(self):
        return self.graph.edges

    def game_recommendations(self, center, search_limit=30, filters=[]):
                             # TODO: , weighter=None):
        """ Builds a list recommendations based on highest overall playtime
            Returns a sorted list of tuples in the form (appid, cumulative_playtime) """
        results = []

        searches_left = search_limit
        player_queue = [center]
        visited = {center.steamid: False}
        game_durations = {}

        while player_queue:

            player = player_queue.pop(0)

            # If already visited, skip
            if visited.get(player.steamid, False):
                continue

            # Enqueue player's friends for BFS traversal
            for friend in player.friends:
                player_queue.append(friend)

            if TraversalFilter.passes(player, filters):
                # Add the playtime of each of this players' games
                for game in player.games:
                    try:
                        game_durations[game.game.appid] += game.playtime_forever
                    except KeyError:
                        game_durations[game.game.appid] = game.playtime_forever

            print(player, game_durations)
            visited[player.steamid] = True

        # Sort by playtime_forever and return the top results
        sorted_games = sorted(game_durations.items(), key=lambda x: x[1])
        sorted_games.reverse()

        return sorted_games[:3]


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
