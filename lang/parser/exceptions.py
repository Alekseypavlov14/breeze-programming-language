# error that is raised when required token is not provided
class ParserError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)
