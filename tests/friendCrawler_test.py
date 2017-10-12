
from tests.mockSteamApi import MockSteamApi
from three_games.steamApi import SteamApi
from three_games.friendCrawler import FriendCrawler

# RocketLeague player and all-around awesome dude who suggestsed that
# game (^^) as a good userbase for testing this project.
STEAM_USER_CRNXX = "crnxx"


def test_crawl():

    GRAPH_DEPTH = 6

    crawler = FriendCrawler(MockSteamApi())

    center = crawler.build_friend_graph(steamid=3)
    output_player(player=center, level=0)

    perform_graph_assertions(center)


def perform_graph_assertions(center):
    # The entry node of the graph is Carl
    assert(center.steamid == '3')
    assert(center.realname == 'Carl')
    carl = center

    # Carl should have two friends: 1 (Alice) and 4 (Debra)
    assert(len(carl.friends) == 2)
    assert([f.steamid for f in center.friends] == ['1', '4'])

    # Alice should be a friend of Carl and a node
    alice = get_friend_by_steamid(carl, '1')
    assert(alice.realname == 'Alice')
    # Alice should have two friends: 2 (Bob), 3 (Carl)
    assert([f.steamid for f in alice.friends] == ['2', '3'])

    # Debra should be a friend of Carl and a node
    debra = get_friend_by_steamid(carl, '4')
    assert(debra.realname == 'Debra')
    # Debra should have three friends: 2 (Bob), 3 (Carl), and 5 (Eustace)
    assert([f.steamid for f in debra.friends] == ['2', '3', '5'])

    # Bob should be a friend of Debra and a node
    bob = get_friend_by_steamid(debra, '2')
    assert(bob.realname == 'Bob')
    # Bob should have two friends: 1 (Alice), 4 (Debra)
    assert([f.steamid for f in bob.friends] == ['1', '4'])

    # Carl should be Debra's friend
    assert(carl == get_friend_by_steamid(debra, '3'))

    # Eustace should be a friend of Debra and a node
    eustace = get_friend_by_steamid(debra, '5')
    # Debra should be her only friend
    assert([f.steamid for f in eustace.friends] == ['4'])
    assert(eustace.realname == 'Eustace')
    # Debra should be Eustace's friend
    assert(debra == get_friend_by_steamid(eustace, '4'))


def get_friend_by_steamid(player, steamid):
    for friend in player.friends:
        if friend.steamid == steamid:
            return friend
    return None


def output_player(player, level):
    if level > 3:
        return
    print('{} {} has {} friends'.format(
        '\t' * level, player, len(player.friends)))
    for friend in player.friends:
        output_player(friend, level + 1)
