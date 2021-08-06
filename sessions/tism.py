#!/usr/bin/env python3

class TheInfamousStateMachine:
  def __init__(self):
    self.state = {}

  def getState(self, key):
    keyStr = str(key)
    return self.state[keyStr]

  def setState(self, key, val):
    keyStr = str(key)

    self.state.update({keyStr: val})
    return self.state[keyStr]

  def queue(self, queueKey, key, val):
    keyStr      = str(key)
    queueKeyStr = str(queueKey)

    l = self.state[queueKeyStr].get(keyStr)
    if not l:
      l = [val]
    else:
      l.append(val)
    self.state[queueKeyStr].update({keyStr: l})
    return self.state[queueKeyStr][keyStr]

  def dequeue(self, queueKey, key, val):
    keyStr      = str(key)
    queueKeyStr = str(queueKey)

    l = self.state[queueKeyStr].get(keyStr)
    if not l:
      return
    else:
      l.remove(val)
    self.state[queueKeyStr].update({keyStr: l})
    return self.state[queueKeyStr][keyStr]

class MoiraInfamousStateMachine(TheInfamousStateMachine):
  def __init__(self, **options):
    super().__init__()

    self.busyKey          = options.get('busyKey')
    self.promptHistoryKey = options.get('promptHistoryKey')
    self.sessionKey       = options.get('sessionKey')
    self.systemsKey       = options.get('systemsKey')

  def getBusyState(self, channelKey):
    channelKeyStr = str(channelKey)

    try:
      state = self.state[self.busyKey][channelKeyStr]
    except:
      return 'FALSE'
    else:
      return state

  def setBusyState(self, channelKey, userId):
    channelKeyStr = str(channelKey)
    userIdStr     = str(userId)

    self.state[self.busyKey][channelKeyStr] = userIdStr
    return self.state[self.busyKey][channelKeyStr]

  def resetBusyState(self):
    self.state[self.busyKey] = {}
    return self.state[self.busyKey]

  def addToPromptHistory(self, channelKey, key, prompt, response):
    channelKeyStr = str(channelKey)
    keyStr        = str(key)
    promptIdStr   = str(prompt.id)
    allHistory    = self.state[self.promptHistoryKey]

    response.update({
      'prompt': {
        'content': str(prompt.content),
        'author': {
          'id': str(prompt.author.id),
          'name': str(prompt.author.name)
        }
      }
    })

    if str(channelKey) in allHistory:
      if keyStr in allHistory[channelKeyStr]:
        self.state[self.promptHistoryKey][channelKeyStr][keyStr].append({promptIdStr: response})
      else:
        self.state[self.promptHistoryKey][channelKeyStr] = {keyStr: [{promptIdStr: response}]}
    else:
      self.state[self.promptHistoryKey] = {channelKeyStr: {keyStr: [{promptIdStr: response}]}}

    return self.state[self.promptHistoryKey][channelKeyStr][keyStr]

  def getPromptHistory(self):
    return self.state[self.promptHistoryKey]

  def getChannelPromptHistory(self, channelKey):
    channelKeyStr = str(channelKey)

    try:
      state = self.state[self.promptHistoryKey][channelKeyStr]
    except:
      return None
    else:
      return state

  def getChannelPromptHistoryEntry(self, channelKey, key):
    channelKeyStr = str(channelKey)
    keyStr        = str(key)

    try:
      state = self.state[self.promptHistoryKey][channelKeyStr][keyStr]
    except:
      return None
    else:
      return state

  def resetPromptHistory(self):
    self.state[self.promptHistoryKey] = {}
    return self.state[self.promptHistoryKey]

  def getSessionState(self, channelKey):
    channelKeyStr = str(channelKey)

    try:
      state = self.state[self.sessionKey][channelKeyStr]
    except:
      return None
    else:
      return state

  def setSessionState(self, channelKey, userRole, userId = None):
    channelKeyStr = str(channelKey)
    if userId:
      userIdStr   = str(userId)

    if not userRole:
      self.state[self.sessionKey][channelKeyStr] = None
    else:
      self.state[self.sessionKey][channelKeyStr] = {userRole: userIdStr}
    return self.state[self.sessionKey][channelKeyStr]

  def addToSessionState(self, channelKey, key, val):
    channelKeyStr = str(channelKey)
    keyStr        = str(key)
    state         = self.state[self.sessionKey][channelKeyStr]

    if keyStr in state:
      raise LookupError
    else:
      state.update({keyStr: val})

  def removeFromSessionState(self, channelKey, key):
    channelKeyStr = str(channelKey)
    keyStr        = str(key)

    return self.state[self.sessionKey][channelKeyStr].pop(keyStr)

  def updateSessionState(self, channelKey, key, val):
    channelKeyStr = str(channelKey)
    keyStr        = str(key)

    state         = self.state[self.sessionKey][channelKeyStr]

    if keyStr in state:
      state.update({keyStr: val})
    else:
      raise KeyError

  def resetSessionState(self):
    self.state[self.sessionKey] = {}
    return self.state[self.sessionKey]

  def getSystemState(self, key):
    keyStr = str(key)

    try:
      state = self.state['subroutines'][keyStr]
    except:
      return None
    else:
      return state

  def setSystemState(self, key, val):
    keyStr = str(key)

    self.state['subroutines'][keyStr] = val
    return self.state['subroutines'][keyStr]
