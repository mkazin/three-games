import json
from three_games.graphDb import GraphDB
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
