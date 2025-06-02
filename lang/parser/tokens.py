from shared.tokens import *
from lexer.token import *

# list of literal tokens
LITERAL_TOKENS = [
  STRING_TOKEN,
  NUMBER_TOKEN,
]

# use to check if token is literal
def is_literal_token(token: Token):
  for name, regex in LITERAL_TOKENS:
    if token.type == name:
      return True
    
  return False
