# error that is raised when required token is not provided
class ParserError(Exception):
  def __init__(self, position, message):
    super().__init__(position, message)
