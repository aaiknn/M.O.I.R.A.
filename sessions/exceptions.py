#!/usr/bin/env python3

# *-- Exception (BUILT-IN)
#     |
#     *-- MoiraException
#     |   |
#     |   *-- DatabaseException
#     |   *-- SubroutineException
#     |   |   |
#     |   |   *-- MetaNotFoundException
#     |   |   *-- UnreachableException
#     |   |
#     |   *-- WebhookException
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
#     *-- TypeError (BUILT-IN)
#     |   |
#     |   *-- MoiraTypeError
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
  def __init__(self, errorMessage=''):
    super().__init__(errorMessage)

class MoiraTypeError(TypeError):
  def __init__(self, errorMessage=''):
    super().__init__(errorMessage)

class MoiraWarning(RuntimeWarning):
  def __init__(self, warnMessage=''):
    super().__init__(warnMessage)

class SubroutineException(MoiraException):
  def __init__(self, *args):
    super().__init__(*args)

class SubroutineWarning(MoiraWarning):
  def __init__(self, *args):
    super().__init__(*args)

class MetaNotFoundException(SubroutineException):
  def __init__(self, *args):
    super().__init__(*args)

class MetaNotFoundWarning(SubroutineWarning):
  def __init__(self, *args):
    super().__init__(*args)

class UnreachableException(SubroutineException):
  def __init__(self, *args):
    super().__init__(*args)

class UnreachableWarning(SubroutineWarning):
  def __init__(self, *args):
    super().__init__(*args)

class DatabaseException(MoiraException):
  def __init__(self, *args):
    super().__init__(*args)

class DatabaseError(MoiraError):
  def __init__(self, *args):
    super().__init__(*args)

class DatabaseWarning(MoiraWarning):
  def __init__(self, *args):
    super().__init__(*args)

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

class WebhookException(MoiraException):
  def __init__(self, *args):
    super().__init__(*args)
