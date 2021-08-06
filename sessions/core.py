#!/usr/bin/env python3

from discord import Intents
from discord.ext.commands import Bot
from random import choice

from phrases.default import emptyMessage
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
    self.webhook = options.get('webhook')

  async def send(self, ctx, m, duration=1, **options):
    isDM = options.get('dm')

    if len(m) > 1800:
      mList = [m[i:i+1800] for i in range(0, len(m), 1800)]
      for entry in mList:
        await sendMessage(ctx, duration, entry, isDM)
    else:
      await sendMessage(ctx, duration, m, isDM)

async def sendMessage(ctx, duration, m, isDM):
  if len(m) == 0:
    await texting(ctx)
    await ctx.send(choice(emptyMessage))
    return

  if isDM:
    await ctx.author.send(m)
  else:
    await texting(ctx, duration)
    await ctx.send(m)
