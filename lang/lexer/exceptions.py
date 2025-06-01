# error that raises when token is not valid
class LexerError(Exception):
  def __init__(self, message = ''):
    super().__init__(message)
