import networkx as nx

"""
Resources on graph databases to try:

* If scaling is needed, check out this AWS article on Graph databases, which provides
options running on EC2, often available from the marketplace:
https://aws.amazon.com/nosql/graph/
"""


class GraphDB():

    def __init__(self):
        self.graph = nx.Graph()
        self.live_players = {}

    def insert_players(self, players):

        added_paths = []

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

    def game_recommendations(self, center, search_limit=30):
        """ Builds a list of the players found in a player graph """
        results = []

        searches_left = search_limit
        player_queue = [center]
        visited = {center.steamid: False}

        while player_queue:

            player = player_queue.pop(0)

            if visited.get(player.steamid, False):
                continue

            for friend in player.friends:
                if player not in results:
                    results.append(player)

                player_queue.append(friend)
                visited[player.steamid] = True

        return results
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
