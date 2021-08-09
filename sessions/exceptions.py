#!/usr/bin/env python3

# *-- Exception (BUILT-IN)
#     |
#     *-- MoiraException
#     |   |
#     |   *-- DatabaseException
#     |   *-- SubroutineException
#     |       |
#     |       *-- MetaNotFoundException
#     |       *-- UnreachableException
#     |
#     *-- RuntimeError (BUILT-IN)
#     |   |
#     |   *-- MoiraError
#     |       |
#     |       *-- DatabaseError
#     |
#     *-- SessionException
#     *-- SituationException
#     |
#     *-- Warning (BUILT-IN)
#         |
#         *-- RuntimeWarning (BUILT-IN)
#         |   |
#         |   *-- MoiraWarning
#         |       |
#         |       *-- DatabaseWarning
#         |       *-- SubroutineWarning
#         |           |
#         |           *-- MetaNotFoundWarning
#         |           *-- UnreachableWarning
#         |
#         *-- SessionWarning
#         *-- SituationWarning

class MoiraException(Exception):
  def __init__(self, exceptionMessage=''):
    super().__init__(exceptionMessage)

class MoiraError(RuntimeError):
  def __init__(self, exceptionMessage=''):
    super().__init__(exceptionMessage)

class MoiraWarning(RuntimeWarning):
  def __init__(self, warnMessage=''):
    super().__init__(warnMessage)

class SubroutineException(MoiraException):
  def __init__(self, exceptionMessage=''):
    super().__init__(exceptionMessage)

class SubroutineWarning(MoiraWarning):
  def __init__(self, warnMessage=''):
    super().__init__(warnMessage)

class MetaNotFoundException(SubroutineException):
  def __init__(self, exceptionMessage=''):
    super().__init__(exceptionMessage)

class MetaNotFoundWarning(SubroutineWarning):
  def __init__(self, warnMessage=''):
    super().__init__(warnMessage)

class UnreachableException(SubroutineException):
  def __init__(self, exceptionMessage=''):
    super().__init__(exceptionMessage)

class UnreachableWarning(SubroutineWarning):
  def __init__(self, warnMessage=''):
    super().__init__(warnMessage)

class DatabaseException(MoiraException):
  def __init__(self, exceptionMessage=''):
    super().__init__(exceptionMessage)

class DatabaseError(MoiraError):
  def __init__(self, errorMessage=''):
    super().__init__(errorMessage)

class DatabaseWarning(MoiraWarning):
  def __init__(self, warnMessage=''):
    super().__init__(warnMessage)

class SituationException(Exception):
  def __init__(self, exceptionMessage=''):
    super().__init__(exceptionMessage)

class SituationWarning(Warning):
  def __init__(self, warnMessage=''):
    super().__init__(warnMessage)

class SessionException(Exception):
  def __init__(self, exceptionMessage=''):
    super().__init__(exceptionMessage)

class SessionWarning(Warning):
  def __init__(self, warnMessage=''):
    super().__init__(warnMessage)
