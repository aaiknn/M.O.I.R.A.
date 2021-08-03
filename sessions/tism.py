#!/usr/bin/env python3

class TheInfamousStateMachine:
  def __init__(self):
    self.state = {}

  def getState(self, key):
    return self.state[key]

  def setState(self, key, val):
    self.state.update({key: val})
    return self.state[key]

  def queue(self, queueKey, key, val):
    l = self.state[queueKey].get(key)
    if not l:
      l = [val]
    else:
      l.append(val)
    self.state[queueKey].update({key: l})
    return self.state[queueKey][key]

  def dequeue(self, queueKey, key, val):
    l = self.state[queueKey].get(key)
    if not l:
      return
    else:
      l.remove(val)
    self.state[queueKey].update({key: l})
    return self.state[queueKey][key]

class MoiraInfamousStateMachine(TheInfamousStateMachine):
  def __init__(self, **options):
    super().__init__()

    self.busyKey          = options.get('busyKey')
    self.promptHistoryKey = options.get('promptHistoryKey')
    self.sessionKey       = options.get('sessionKey')
    self.systemsKey       = options.get('systemsKey')

  def getBusyState(self, channelKey):
    try:
      state = self.state[self.busyKey][channelKey]
    except:
      return 'FALSE'
    else:
      return state

  def setBusyState(self, channelKey, userId):
    self.state[self.busyKey][channelKey] = userId
    return self.state[self.busyKey][channelKey]

  def resetBusyState(self):
    self.state[self.busyKey] = {}
    return self.state[self.busyKey]

  def addToPromptHistory(self, channelKey, key, prompt, response):
    allHistory = self.state[self.promptHistoryKey]
    if channelKey in allHistory:
      if key in allHistory[channelKey]:
        self.state[self.promptHistoryKey][channelKey][key].append({prompt.id: response})
      else:
        self.state[self.promptHistoryKey][channelKey] = {key: [{prompt.id: response}]}
    else:
      self.state[self.promptHistoryKey] = {channelKey: {key: [{prompt.id: response}]}}

    return self.state[self.promptHistoryKey][channelKey][key]

  def getPromptHistory(self):
    return self.state[self.promptHistoryKey]

  def getChannelPromptHistory(self, channelKey):
    try:
      state = self.state[self.promptHistoryKey][channelKey]
    except:
      return None
    else:
      return state

  def getChannelPromptHistoryEntry(self, channelKey, key):
    try:
      state = self.state[self.promptHistoryKey][channelKey][key]
    except:
      return None
    else:
      return state

  def resetPromptHistory(self):
    self.state[self.promptHistoryKey] = {}
    return self.state[self.promptHistoryKey]

  def getSessionState(self, channelKey):
    try:
      state = self.state[self.sessionKey][channelKey]
    except:
      return None
    else:
      return state

  def setSessionState(self, channelKey, userRole, userId = None):
    if not userRole:
      self.state[self.sessionKey][channelKey] = None
    else:
      self.state[self.sessionKey][channelKey] = {userRole: userId}
    return self.state[self.sessionKey][channelKey]

  def addToSessionState(self, channelKey, key, val):
    state = self.state[self.sessionKey][channelKey]
    if key in state:
      raise LookupError
    else:
      state.update({key: val})

  def removeFromSessionState(self, channelKey, key):
    return self.state[self.sessionKey][channelKey].pop(key)

  def updateSessionState(self, channelKey, key, val):
    state = self.state[self.sessionKey][channelKey]
    if key in state:
      state.update({key: val})
    else:
      raise KeyError

  def resetSessionState(self):
    self.state[self.sessionKey] = {}
    return self.state[self.sessionKey]

  def getSystemState(self, key):
    try:
      state = self.state['subroutines'][key]
    except:
      return None
    else:
      return state

  def setSystemState(self, key, val):
    self.state['subroutines'][key] = val
    return self.state['subroutines'][key]
