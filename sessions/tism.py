#!/usr/bin/env python3

class TheInfamousStateMachine:
  def __init__(self):
    self.state = {}

  def getState(self, key):
    return self.state[key]

  def setState(self, key, val):
    self.state.update({key: val})
    return self.state[key]

  def getBusyState(self, channelKey):
    try:
      state = self.state['busy'][channelKey]
    except:
      return 'FALSE'
    else:
      return state

  def setBusyState(self, channelKey, userId):
    self.state['busy'][channelKey] = userId
    return self.state['busy'][channelKey]

  def resetBusyState(self):
    self.state['busy'] = {}
    return self.state['busy']

  def addToPromptHistory(self, channelKey, key, prompt, response):
    allHistory = self.state['promptHistory']
    if channelKey in allHistory:
      if key in allHistory[channelKey]:
        self.state['promptHistory'][channelKey][key].append({prompt.id: response})
      else:
        self.state['promptHistory'][channelKey] = {key: [{prompt.id: response}]}
    else:
      self.state['promptHistory'] = {channelKey: {key: [{prompt.id: response}]}}

    return self.state['promptHistory'][channelKey][key]

  def getPromptHistory(self):
    return self.state['promptHistory']

  def getChannelPromptHistory(self, channelKey):
    try:
      state = self.state['promptHistory'][channelKey]
    except:
      return None
    else:
      return state

  def getChannelPromptHistoryEntry(self, channelKey, key):
    try:
      state = self.state['promptHistory'][channelKey][key]
    except:
      return None
    else:
      return state

  def resetPromptHistory(self):
    self.state['promptHistory'] = {}
    return self.state['promptHistory']

  def getSessionState(self, channelKey):
    try:
      state = self.state['busyWith'][channelKey]
    except:
      return None
    else:
      return state

  def setSessionState(self, channelKey, userRole, userId = None):
    if not userRole:
      self.state['busyWith'][channelKey] = None
    else:
      self.state['busyWith'][channelKey] = {userRole: userId}
    return self.state['busyWith'][channelKey]

  def addToSessionState(self, channelKey, key, val):
    state = self.state['busyWith'][channelKey]
    if key in state:
      raise LookupError
    else:
      state.update({key: val})

  def removeFromSessionState(self, channelKey, key):
    return self.state['busyWith'][channelKey].pop(key)

  def updateSessionState(self, channelKey, key, val):
    state = self.state['busyWith'][channelKey]
    if key in state:
      state.update({key: val})
    else:
      raise KeyError

  def resetSessionState(self):
    self.state['busyWith'] = {}
    return self.state['busyWith']

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
