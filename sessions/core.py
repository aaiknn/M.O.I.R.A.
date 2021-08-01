#!/usr/bin/env python3

from discord import Intents
from discord.ext.commands import Bot

from utils.general import texting

intents = Intents.default()
intents.members = True

class MOIRA(Bot):
  def __init__(self, prefix, nickname, admin, regularUser, patience, **options):
    super().__init__(
      prefix,
      case_insensitive=True,
      intents=intents
    )

    self.nickname = nickname
    self.administrator = admin
    self.regularUser = regularUser
    self.patience = patience
    self.subroutines = options.get('subroutines')

  async def send(self, ctx, m, duration=1):
    await texting(ctx, duration)
    await ctx.send(m)
