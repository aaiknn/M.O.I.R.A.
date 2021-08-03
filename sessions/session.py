#!/usr/bin/env python3

class MoiraSession:
  def __init__(self, discordCtx, moiraInstance, sessionUser):
    self.ctx      = discordCtx
    self.handler  = moiraInstance
    self.message  = ''
    self.user     = sessionUser

  async def createSession(self, chid, **options):
    phrase = options.get('phrase')
    if phrase:
      await self.handler.send(self.ctx, phrase)
    self.handler.tism.setBusyState(chid, self.user.id)
    self.handler.tism.setSessionState(chid, self.user.role, self.user.id)
    return 'CREATIONSUCCESS'

  async def exitSession(self, chid, **options):
    response = options.get('response')
    if response:
      await self.handler.send(self.ctx, response)
    self.handler.tism.setBusyState(chid, 'FALSE')
    self.handler.tism.setSessionState(chid, None)
    return 'EXITSUCCESS'

  def getState(self, chid):
    return self.handler.tism.getSessionState(chid)
