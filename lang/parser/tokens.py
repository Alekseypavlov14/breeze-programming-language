from shared.tokens import *
from lexer.token import *

# list of literal tokens
LITERAL_TOKENS = [
  STRING_TOKEN,
  NUMBER_TOKEN,
]

# use to check if token is literal
def is_literal_token(token: Token):
  for literal_token in LITERAL_TOKENS:
    if is_token_of_type(token, literal_token):
      return True
    
  return False
