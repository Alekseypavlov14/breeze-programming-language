from lexer.exceptions import LexerError
from lexer.token import Token
from shared.tokens import *
from shared.keywords import *

# standard modules
import re

# class that parses code to tokens
class Lexer:
  # parses code (module) to tokens
  def parse(self, code: str):
    # init tokens list
    tokens: list[Token] = []
    # init position
    position = 0

    # iterate through code
    while position < len(code):
      # flag that indicates if token found for current position
      current_position_match = False

      # check every token from specification
      for type, regex in TOKEN_SPECIFICATION:
        # check if token is matched
        match = re.search(f"^{regex}", code[position:])
      
        if match:
          # get whole match value
          token = match.group()
          
          # move position
          position += len(token)

          # handle extracting part of token for .code field
          # used to extract string content from string literal
          if match.groups():
            for group in match.groups():
              if group:
                token = group
                break

          # handle keywords
          if type == IDENTIFIER_TOKEN[0] and token in KEYWORDS:
            # type is a keyword itself
            type = token

          # escape special symbols in token
          token = token.encode("utf-8").decode("unicode_escape")

          # add token
          tokens.append(Token(type, token))

          # update flag to set current position matched
          current_position_match = True
          
          # continue with new token
          break
        
      if not current_position_match:
        raise LexerError(f'Invalid token on position {position}')

    # return list of found tokens      
    return tokens
