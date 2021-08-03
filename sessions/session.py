#!/usr/bin/env python3

from random import choice

from phrases.default import initialPrompt
from utils.qualification import waitForQualificationInput

class MoiraSession:
  def __init__(self, discordCtx, moiraInstance, sessionUser):
    self.ctx      = discordCtx
    self.handler  = moiraInstance
    self.message  = ''
    self.user     = sessionUser

  async def createSession(self, *args, **options):
    await self.handler.send(self.ctx, choice(initialPrompt))
    self.message = await waitForQualificationInput(self.handler, self.ctx)
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
