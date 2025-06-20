from shared.tokens import TOKEN_NAMES
from shared.keywords import KEYWORDS
from lexer.exceptions import LexerError

# indicates position of first token symbol
class TokenPosition:
  def __init__(self, row: int, column: int):
    self.row = row
    self.column = column

  def __str__(self):
    return f"{self.row}:{self.column}"

# token - standalone part of code
# represents identifiers, operators and others
class Token:
  def __init__(self, type: str, code: str, position: TokenPosition):
    self.code = code
    self.type = type
    self.position = position

  @property
  def type(self):
    return self._type
  
  @type.setter
  def type(self, type):
    if type not in TOKEN_NAMES and type not in KEYWORDS:
      raise LexerError(f'Token "{self.code}" has invalid type: {type}')
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
