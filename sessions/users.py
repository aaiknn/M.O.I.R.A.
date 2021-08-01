#!/usr/bin/env python3

class SessionUser:
  def __init__(self, id, activeSessions = ''):
    self.id = id
    self.role = 'regular'
    self.active_sessions = activeSessions

class SessionAdmin(SessionUser):
  def __init__(self, *args):
    SessionUser.__init__(self, *args)
    self.role = 'admin'
