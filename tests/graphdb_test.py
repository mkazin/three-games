import json
from three_games.graphDb import GraphDB
from three_games.graphDb import PlayerExclusionTraversalFilter
from three_games.friendCrawler import FriendCrawler
from tests.mockSteamApi import MockSteamApi


def test_graph():
    crawler = FriendCrawler(MockSteamApi())
    center = crawler.build_friend_graph(steamid=3)

    alice = center.friends[0]
    debra = center.friends[1]
    carl = center
    bob = debra.friends[0]
    eustace = debra.friends[2]

    graph = GraphDB()
    graph.insert_players([alice, bob, carl, debra, eustace])

    assert len(graph.nodes()) == 5
    assert len(graph.edges()) == 5

    # TODO: ,filters=[], weighter=None):
    exclude_debra = PlayerExclusionTraversalFilter([debra])
    recs = graph.game_recommendations(center, search_limit=30, filters=[exclude_debra])
    assert len(recs) == 3

    assert recs[0][0] == 33230
    assert recs[0][1] == 3000

    assert recs[1][0] == 7610
    assert recs[1][1] == 1100

    assert recs[2][0] == 24980
    assert recs[2][1] == 440
