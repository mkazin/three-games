
class Game(object):

    def __init__(self,
                 appid, name,
                 img_icon_url=None, img_logo_url=None,
                 has_community_visible_stats=None):

        self.appid = appid
        self.name = name
        self.img_icon_url = img_icon_url
        self.img_logo_url = img_logo_url
        self.has_community_visible_stats = has_community_visible_stats

    @staticmethod
    def from_response(response):

        return Game(
            appid=response['appid'],
            name=response['name'],

            img_icon_url=response.get('img_icon_url', None),
            img_logo_url=response.get('img_logo_url', None),
            has_community_visible_stats=response.get('has_community_visible_stats', None)
        )


class OwnedGame(Game):

    def __init__(self, game, playtime_forever=None):
        self.game = game
        self.playtime_forever = playtime_forever

    def __str__(self):
        return '{}: {} ({} hrs)'.format(
            self.game.appid, self.game.name,
            round(self.playtime_forever / 60))

    def __repr__(self):
        return str(self)

    @staticmethod
    def from_response(response):

        game = Game.from_response(response)
        return OwnedGame(
            game=game,
            playtime_forever=response.get('playtime_forever', None)
        )
