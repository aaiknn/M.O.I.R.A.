#!/usr/bin/env python3

class Loggers():
  def __init__(self, **options):
    self.log_level  = options.get('log_level')
    self.members    = []
    self.terminal   = None

    if options.get('members'):
      for logger in options.get('members'):
        self.registerLogger(logger)

  def setTerminalLogger(self, logger):
    if not self.terminal:
      self.terminal = logger
    else:
      raise Warning('A primary terminal logger has already been registered.')

  def unsetTerminalLogger(self, logger):
    if self.terminal == logger:
      self.terminal = None
    else:
      raise Warning(f'Logger {logger} was never set up for primary terminal logging.')

  def registerLogger(self, logger):
    if logger in self.members:
      raise KeyError(f'Logger {logger} has already been registered.')

    self.members.append(logger)

    if logger.type == 'terminal':
      if not self.terminal:
        self.setTerminalLogger(logger)

    return logger

  def unregisterLogger(self, logger):
    if not logger in self.members:
      raise KeyError(f'This logger {logger} was never registered in the first place.')

    self.members.remove(logger)

    if logger.type == 'terminal':
      if self.terminal == logger:
        self.unsetTerminalLogger(logger)

    return logger

class Logger():
  def __init__(self, **options):
    self.log_level  = options.get('log_level')
    self.type       = options.get('type')

class TerminalLogger(Logger):
  def __init__(self, **options):
    super().__init__(**options)

    self.type = 'terminal'
