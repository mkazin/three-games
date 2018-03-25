import json
from three_games.graphDb import *
from three_games.steamApi import SteamApi
from three_games.friendCrawler import FriendCrawler
from three_games.gameRecommendation import RecommendationSorting, \
    PlaytimeRecommendation, PlayerCountRecommendation
from tests.mockSteamApi import MockSteamApi
from requests.exceptions import HTTPError


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

    recommender = Recommender(center, filters=[exclude_debra])
    recs = recommender.get_recommendations()

    # Sort by playtime_forever and return the top results
    rec_system = RecommendationSorting(systems=[PlaytimeRecommendation()])
    sorted_games = GameRecommendation.sort_by_playtime(recs, rec_system, reverse=True)

    # Build the output recommendations
    top_games = sorted_games[0:3]

    assert len(top_games) == 3

    assert top_games[0].game.appid == 33230
    assert top_games[0].total_playtime == 3000

    assert top_games[1].game.appid == 7610
    assert top_games[1].total_playtime == 1100

    assert top_games[2].game.appid == 24980
    assert top_games[2].total_playtime == 440


def test_player_count_recommendation():

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
    recs = graph.game_recommendations(center, filters=[exclude_debra])

    # Sort by playtime_forever and return the top results
    rec_system = RecommendationSorting(systems=[PlayerCountRecommendation()])
    sorted_games = GameRecommendation.sort_by_playtime(recs, rec_system, reverse=True)

    # Build the output recommendations
    top_games = sorted_games[0:3]

    assert len(top_games) == 3

    assert top_games[0].game.appid in (7610, 24980)
    assert top_games[1].game.appid in (7610, 24980)
    assert top_games[2].game.appid in (234650, 33230, 102600)


def test_game_name_filter():

    returned_games = []
    api = MockSteamApi()

    games_resp = api.get_owned_games('1')
    for curr in games_resp:

        curr_game = OwnedGame.from_response(curr)
        returned_games.append(curr_game)

    # Filter out Mass Effect
    filters = [GameNameTraversalFilter('ffe', reverse=True)]

    # Fiter in Railroad Tycoon 3
    filters += [GameNameTraversalFilter('road')]

    matching = []
    for curr in returned_games:
        if TraversalFilter.passes(curr, filters):
            matching.append(curr)

    assert len(matching) == 1
    assert matching[0].game.name == "Railroad Tycoon 3"


def test_minimum_playtime_filter():

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
    minimum_playtime_filter = GamePlaytimeTraversalFilter(150)

    recommender = Recommender(center,
                              filters=[exclude_debra, minimum_playtime_filter])
    recs = recommender.get_recommendations()

    # Sort by playtime_forever and return the top results
    rec_system = RecommendationSorting(systems=[PlaytimeRecommendation()])
    sorted_games = GameRecommendation.sort_by_playtime(recs, rec_system, reverse=True)

    # Build the output recommendations
    top_games = sorted_games[0:3]

    assert len(top_games) == 3

    assert top_games[0].game.appid == 33230
    assert top_games[0].total_playtime == 3000
    assert bob in top_games[0].non_friend_owners

    assert top_games[1].game.appid == 7610
    assert top_games[1].total_playtime == 1000
    assert bob in top_games[1].non_friend_owners
    assert alice not in top_games[1].friends_with_game

    assert top_games[2].game.appid == 24980
    assert top_games[2].total_playtime == 400
    assert alice in top_games[2].friends_with_game
    assert carl not in top_games[2].non_friend_owners


def test_api_hit_limit():

    # Testing the query_limit set on the api
    # We'll use the sample config file (assuring failure if the API is queried)
    api = SteamApi('config/auth.conf.sample')
    api.set_query_limit(0)

    crawler = FriendCrawler(api)

    try:
        center = crawler.build_friend_graph(steamid=300)
    except HTTPError as e:
        assert '429' in str(e)

    # Shouldn't be anything cached
    assert len(crawler.player_cache.keys()) == 0
