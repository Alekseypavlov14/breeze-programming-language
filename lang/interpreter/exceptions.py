# defines error for stack (no scopes)
class StackError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)

# defines error when container is not found by name
class NameError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)
    