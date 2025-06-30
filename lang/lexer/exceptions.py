from shared.exceptions import *

# error that raises when token is not valid
class LexerError(Error):
  def __init__(self, position, message):
    super().__init__(position, message)
