import requests

class DiscordAPI:
    """Discord API"""
    endpoint = 'https://discord.com/api'

    def __init__(self, TOKEN: str):
        self.headers={'Authorization': f'Bot {TOKEN}'}

    def _expandPathToUrl(self, path: str, params: dict = {}) -> str:
        """adds onto the `path` with additional query `params`"""
        url = path
        url += '?' if params else ''
        return url + '&'.join([key + '=' + str(params[key]) for key in params])

    def sendMessage(self, channel_id: str, body: dict) -> None:
        requests.post(self.endpoint + f'/channels/{channel_id}/messages',
                      data=body, headers=self.headers)
        return None

    def getChannelMessages(self, channel_id: str, params: dict = {}) -> list:
        """valid params are `around`, `before`, `after`, `limit`"""
        base_path = self.endpoint + f'/channels/{channel_id}/messages'
        path = self._expandPathToUrl(base_path, params)
        res = requests.get(path, headers=self.headers)
        return res.json()

if __name__ == "__main__":
    from secrets import TOKEN
    api = DiscordAPI(TOKEN)
    channel_id = '894438526580555817'

    res = api.getChannelMessages(channel_id, {"limit": 5})
    print(res)

