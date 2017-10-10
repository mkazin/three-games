
from tests.mockSteamApi import MockSteamApi
from three_games.steamApi import SteamApi
from three_games.friendCrawler import FriendCrawler




def test_crawl():

    crawler = FriendCrawler(MockSteamApi())

    center = crawler.build_friend_graph(steamid=3, graph_depth=6)
    # output_player(player=center, level=0)

    assert(center.steamid == '3')
    assert(len(center.friends) == 2)
    assert([f.steamid for f in center.friends] == ['1', '4'])


def output_player(player, level):

    if level > 3:
        return

    print('\t' * level, player.steamid, player.personaname,
          player.realname, 'friends:', len(player.friends))
    for friend in player.friends:
        output_player(friend, level + 1)
