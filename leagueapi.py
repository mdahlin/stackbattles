import requests

class LolAPI:
    """League API"""
    endpoint = 'api.riotgames.com'

    def __init__(self, APIKEY: str, region: str):
        self.region=region
        self.headers={'X-Riot-Token': APIKEY}

    def _request(self, path: str) -> requests.models.Response:
        res = requests.get(
            f'https://{self.region}.{self.endpoint}' + path,
            headers=self.headers
        )
        return res

    def getPUUID(self, gameName: str, tagLine: str) -> dict:
        """get ID to make other requets"""
        base = f'/riot/account/v1/accounts/by-riot-id/'
        res = self._request(base + f'{gameName}/{tagLine}')
        return res.json()['puuid']

    def getMatchIdList(self, puuid: str, n: int=20) -> list:
        """get list of n most recent match by match id

        Notes
        -----
        API response returns at most 100 IDs per call
        Matches are kept for 2 years
        """

        base = f'/lol/match/v5/matches/by-puuid/{puuid}/ids/?'
        match_ids = []
        start = 0

        while n > 0:
            count = min(n, 100)
            res = self._request(base + f'start={start}&count={count}')
            match_ids += res.json()

            if len(res.json()) == 0:
                break

            start += 100
            n -= 100

        return match_ids

    def getMatchInfo(self, match_id: str) -> dict:
        res = self._request(f'/lol/match/v5/matches/{match_id}')
        return res.json()

    def getMatchTimeline(self, match_id: str) -> dict:
        res = self._request(f'/lol/match/v5/matches/{match_id}/timeline')
        return res.json()