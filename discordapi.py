import requests

class DiscordAPI:
    """Discord API"""
    endpoint = 'https://discord.com/api'

    def __init__(self, TOKEN: str):
        self.headers={'Authorization': f'Bot {TOKEN}'}

    def sendMessage(self, channel_id: str, body: dict) -> None:
        requests.post(self.endpoint + f'/channels/{channel_id}/messages',
                      data=body, headers=self.headers)
        return None
