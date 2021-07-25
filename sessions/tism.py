#!/usr/bin/env python3

class TheInfamousStateMachine:
  def __init__(self):
    self.state = {}

  def getState(self, key):
    return self.state[key]

  def setState(self, key, val):
    self.state.update({key: val})
