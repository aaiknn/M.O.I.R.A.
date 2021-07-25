#!/usr/bin/env python3

class TheInfamousStateMachine:
  def __init__(self):
    self.state = {}

  def getState(self, key):
    return self.state[key]

  def setState(self, key, val):
    self.state.update({key: val})

  def queue(self, queueKey, key, val):
    l = self.state[queueKey].get(key)
    if not l:
      l = [val]
    else:
      l.append(val)
    self.state[queueKey].update({key: l})

  def dequeue(self, queueKey, key, val):
    l = self.state[queueKey].get(key)
    if not l:
      return
    else:
      l.remove(val)
    self.state[queueKey].update({key: l})
