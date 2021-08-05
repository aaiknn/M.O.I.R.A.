#!/usr/bin/env python3

class TheInfamousStateMachine:
  def __init__(self):
    self.state = {}

  def getState(self, key):
    return self.state[str(key)]

  def setState(self, key, val):
    self.state.update({str(key): val})
    return self.state[str(key)]

  def queue(self, queueKey, key, val):
    l = self.state[str(queueKey)].get(str(key))
    if not l:
      l = [val]
    else:
      l.append(val)
    self.state[str(queueKey)].update({str(key): l})
    return self.state[str(queueKey)][str(key)]

  def dequeue(self, queueKey, key, val):
    l = self.state[str(queueKey)].get(str(key))
    if not l:
      return
    else:
      l.remove(val)
    self.state[str(queueKey)].update({str(key): l})
    return self.state[str(queueKey)][str(key)]

class MoiraInfamousStateMachine(TheInfamousStateMachine):
  def __init__(self, **options):
    super().__init__()

    self.busyKey          = options.get('busyKey')
    self.promptHistoryKey = options.get('promptHistoryKey')
    self.sessionKey       = options.get('sessionKey')
    self.systemsKey       = options.get('systemsKey')

  def getBusyState(self, channelKey):
    try:
      state = self.state[self.busyKey][str(channelKey)]
    except:
      return 'FALSE'
    else:
      return state

  def setBusyState(self, channelKey, userId):
    self.state[self.busyKey][str(channelKey)] = str(userId)
    return self.state[self.busyKey][str(channelKey)]

  def resetBusyState(self):
    self.state[self.busyKey] = {}
    return self.state[self.busyKey]

  def addToPromptHistory(self, channelKey, key, prompt, response):
    allHistory = self.state[self.promptHistoryKey]
    if str(channelKey) in allHistory:
      if str(key) in allHistory[str(channelKey)]:
        self.state[self.promptHistoryKey][str(channelKey)][str(key)].append({str(prompt.id): response})
      else:
        self.state[self.promptHistoryKey][str(channelKey)] = {str(key): [{str(prompt.id): response}]}
    else:
      self.state[self.promptHistoryKey] = {str(channelKey): {str(key): [{str(prompt.id): response}]}}

    return self.state[self.promptHistoryKey][str(channelKey)][str(key)]

  def getPromptHistory(self):
    return self.state[self.promptHistoryKey]

  def getChannelPromptHistory(self, channelKey):
    try:
      state = self.state[self.promptHistoryKey][str(channelKey)]
    except:
      return None
    else:
      return state

  def getChannelPromptHistoryEntry(self, channelKey, key):
    try:
      state = self.state[self.promptHistoryKey][str(channelKey)][str(key)]
    except:
      return None
    else:
      return state

  def resetPromptHistory(self):
    self.state[self.promptHistoryKey] = {}
    return self.state[self.promptHistoryKey]

  def getSessionState(self, channelKey):
    try:
      state = self.state[self.sessionKey][str(channelKey)]
    except:
      return None
    else:
      return state

  def setSessionState(self, channelKey, userRole, userId = None):
    if not userRole:
      self.state[self.sessionKey][str(channelKey)] = None
    else:
      self.state[self.sessionKey][str(channelKey)] = {userRole: str(userId)}
    return self.state[self.sessionKey][str(channelKey)]

  def addToSessionState(self, channelKey, key, val):
    state = self.state[self.sessionKey][str(channelKey)]
    if str(key) in state:
      raise LookupError
    else:
      state.update({str(key): val})

  def removeFromSessionState(self, channelKey, key):
    keyStr = str(key)
    return self.state[self.sessionKey][str(channelKey)].pop(keyStr)

  def updateSessionState(self, channelKey, key, val):
    state = self.state[self.sessionKey][str(channelKey)]
    if str(key) in state:
      state.update({str(key): val})
    else:
      raise KeyError

  def resetSessionState(self):
    self.state[self.sessionKey] = {}
    return self.state[self.sessionKey]

  def getSystemState(self, key):
    try:
      state = self.state['subroutines'][str(key)]
    except:
      return None
    else:
      return state

  def setSystemState(self, key, val):
    self.state['subroutines'][str(key)] = val
    return self.state['subroutines'][str(key)]
