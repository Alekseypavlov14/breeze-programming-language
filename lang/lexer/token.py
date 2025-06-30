from shared.tokens import TOKEN_NAMES
from shared.keywords import KEYWORDS
from shared.position import TokenPosition
from lexer.exceptions import LexerError

# token - standalone part of code
# represents identifiers, operators and others
class Token:
  def __init__(self, position: TokenPosition, type: str, code: str):
    self.position = position
    self.type = type
    self.code = code

  @property
  def type(self):
    return self._type
  
  @type.setter
  def type(self, type):
    if type not in TOKEN_NAMES and type not in KEYWORDS:
      raise LexerError(self.position, f'Token "{self.code}" has invalid type: {type}')
    self._type = type

  # overload equality operator
  # tokens are the same if they have same type and content
  def __eq__(self, other):
    # if other is not Token
    if not isinstance(other, Token):
      return None

    # compare tokens
    return self.type == other.type and self.code == other.code

  # defines mapping to string
  def __str__(self):
    return f"Token ({self.type}, {self.code!r}, ({self.position.row}:{self.position.column}))"
  
# checks if lexer Token class is of type by token tuple
def is_token_of_type(token: Token, type_tuple):
  return token.type == type_tuple[0]
