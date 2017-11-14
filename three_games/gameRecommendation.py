# s = sorted(s, key = lambda x: (x[1], x[2]))
from abc import ABCMeta, abstractmethod


class RecommendationSorting(object):

    """ Provides a flexible list of metrics on which to sort recommended games """

    def __init__(self, systems):
        """ systems - list of RecommendationSystem objects """
        self.systems = systems
        self.sort_lambda = lambda game_tuple: tuple(
            sys.get_metric(game_tuple) for sys in self.systems)


class RecommendationSystem(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_metric(game_tuple):
        pass


class PlaytimeRecommendation(RecommendationSystem):

    def get_metric(self, game_tuple):
        return game_tuple[1].total_playtime


class PlayerCountRecommendation(RecommendationSystem):

    def get_metric(self, game_tuple):
        return (len(game_tuple[1].friends_with_game) +
                len(game_tuple[1].non_friend_owners))


class GameRecommendation(object):

    # Minimum time required to play before a recommendation is made and friend
    # is marked as having played the game. In seconds (to match Steam's forever_playtime)
    MIN_PLAY_TIME = 0  # 5 * 60

    def __init__(self, game, total_playtime, **kwargs):
        """ NOTE: only 1st-degree friends should be listed in friends_with_game. """
        self.game = game
        self.total_playtime = total_playtime
        self.friends_with_game = kwargs.pop('friends_with_game', [])
        self.non_friend_owners = kwargs.pop('non_friend_owners', [])

    def __str__(self):
        return '{} - {} ({} hrs on average)'.format(
            self.game.name,
            ' owned by: Friends: [{}] ; Non-Friends: [{}]'.format(
                ', '.join([friend.personaname for friend in self.friends_with_game]),
                ', '.join([friend.personaname for friend in self.non_friend_owners])),
            round((self.total_playtime /
                   len(self.friends_with_game + self.non_friend_owners)) / 60))

    def __repr__(self):
        return str(self)

    @staticmethod
    def sort_by_playtime(recs, recommendation_system, reverse=False):

        # sorted_games = sorted(recs.items(), key=lambda tuple: tuple[1].total_playtime)
        sorted_games = sorted(recs.items(), key=recommendation_system.sort_lambda)

        if reverse:
            sorted_games.reverse()

        # Convert list of tuples to a list of GameRecommendations

        return [the_tuple[1] for the_tuple in sorted_games]
