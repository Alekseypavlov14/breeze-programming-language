from interpreter.containers import *

# defines error for stack (no scopes)
class StackError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)

# defines error when container is not found by name
class NameError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)

# defines type error
class TypeError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)

# defines error when incorrect value is used
class ValueError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)

# defines syntax error
class SyntaxError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)

# defines error for invalid statement 
class StatementError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)

# defines error during expression evaluation
class ExpressionError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)

# defines function parameter exception
class ParameterError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)

# defines import error
class ImportError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)


# inner tools built on exceptions
class BreakException(Exception):
  def __init__(self):
    super().__init__('Incorrect break usage')

class ContinueException(Exception):
  def __init__(self):
    super().__init__('Incorrect continue usage')

class ReturnException(Exception):
  def __init__(self, value: Container):
    super().__init__('Incorrect return usage')

    self.value = value
