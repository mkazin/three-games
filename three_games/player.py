
class Player(object):

    def __init__(self,
                 steamid, personaname, realname=None, avatar=None,
                 primaryclanid=None,
                 timecreated=None, lastlogoff=None,
                 loccountrycode=None, locstatecode=None, loccityid=None):

        self.steamid = steamid
        self.personaname = personaname
        self.avatar = avatar
        self.realname = realname
        self.primaryclanid = primaryclanid
        self.timecreated = timecreated
        self.lastlogoff = lastlogoff
        self.loccountrycode = loccountrycode
        self.locstatecode = locstatecode
        self.loccityid = loccityid

        self.friends = []
        # TODO: when we get to analyzing clan relationships...
        # self.clan_mates

        self.games = []

    def __str__(self):
        return '{}: {}'.format(self.steamid, self.realname)

    def __repr__(self):
        return str(self)

    def add_friend(self, other_player):
        self.friends.append(other_player)

    def add_game(self, owned_game):
        self.games.append(owned_game)

    def owns(self, app_id):
        """ Returns whether user owns an application.
            NOTE: does not query the API
                  Assumes Player has been populated via add_game() """
        return app_id in [game.game.appid for game in self.games]

    @staticmethod
    def from_response(response):

        return Player(
            steamid=response['steamid'],
            personaname=response['personaname'],

            realname=response.get('realname', None),

            avatar=response.get('avatar', None),
            primaryclanid=response.get('primaryclanid', None),
            timecreated=response.get('timecreated', None),
            lastlogoff=response.get('lastlogoff', None),
            loccountrycode=response.get('loccountrycode', None),
            locstatecode=response.get('locstatecode', None),
            loccityid=response.get('loccityid', None)
        )
