
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

    def add_friend(self, other_player):
        self.friends.append(other_player)

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

    # {
    #     "steamid": "76561198025093417",
    #     "communityvisibilitystate": 3,
    #     "profilestate": 1,
    #     "personaname": "mkazin",
    #     "lastlogoff": 1506984892,
    #     "profileurl": "http://steamcommunity.com/profiles/76561198025093417/",
    #     "avatar": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/ec/ec90f275c5045aa4de008a75ea9d0098a832575b.jpg",
    #     "avatarmedium": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/ec/ec90f275c5045aa4de008a75ea9d0098a832575b_medium.jpg",
    #     "avatarfull": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/ec/ec90f275c5045aa4de008a75ea9d0098a832575b_full.jpg",
    #     "personastate": 1,
    #     "realname": "Michael Kazin",
    #     "primaryclanid": "103582791435135156",
    #     "timecreated": 1273757737,
    #     "personastateflags": 0,
    #     "loccountrycode": "US",
    #     "locstatecode": "MA",
    #     "loccityid": 1840
    # }
