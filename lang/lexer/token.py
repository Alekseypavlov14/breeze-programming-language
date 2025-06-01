from shared.tokens import TOKEN_NAMES
from lexer.exceptions import LexerError

# token - standalone part of code
# represents identifiers, operators and others
class Token:
  def __init__(self, type: str, code: str):
    self.code = code
    self.type = type

  @property
  def type(self):
    return self._type
  
  @type.setter
  def type(self, type):
    if type not in TOKEN_NAMES:
      raise LexerError(f'Token "{self.code}" has invalid type: {type}')
    self._type = type

  # defines mapping to string
  def __str__(self):
    return f"Token ({self.type}, {self.code!r})"
  