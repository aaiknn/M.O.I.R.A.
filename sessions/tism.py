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
