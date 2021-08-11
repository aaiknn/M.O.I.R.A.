#!/usr/bin/env python3

from sessions.situation import SessionSituation

class MoiraSession(SessionSituation):
  def __init__(self, discordCtx, moiraInstance, sessionUser):
    self.ctx      = discordCtx

    super().__init__(
      channelId   = self.ctx.channel.id,
      handler     = moiraInstance,
      sessionUser = sessionUser,
      userMessage = ''
    )

  async def createSession(self, **options):
    phrase = options.get('phrase')
    if phrase:
      await self.handler.send(self.ctx, phrase)
    self.handler.tism.setBusyState(self.channelId, self.sessionUser.id)
    self.handler.tism.setSessionState(self.channelId, self.sessionUser.role, self.sessionUser.id)
    return 'CREATIONSUCCESS'

  async def exitSession(self, **options):
    response = options.get('response')
    if response:
      await self.handler.send(self.ctx, response)
    self.handler.tism.setBusyState(self.channelId, 'FALSE')
    self.handler.tism.setSessionState(self.channelId, None)
    return 'EXITSUCCESS'

  def getState(self):
    return self.handler.tism.getSessionState(self.channelId)
