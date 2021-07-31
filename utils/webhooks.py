#/usr/bin/env python3

from discord import Webhook as DiscordWebhook

class DiscordHooks:
  def __init__(self, webhook, adapter):
    id = webhook['id']
    token = webhook['token']
    self.hook = DiscordWebhook.from_url(
      f'https://discordapp.com/api/webhooks/{id}/{token}',
      adapter=adapter
    )
