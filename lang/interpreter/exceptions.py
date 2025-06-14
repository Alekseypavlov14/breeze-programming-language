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

# defines error during expression evaluation
class ExpressionError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)
